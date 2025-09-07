from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
import sqlite3
import os
import random

DB_PATH = "data/database.db"


class RouteMap(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.add_widget(MDLabel(text="🗺️ Маршрут (демо)", halign="center", theme_text_color="Primary"))
        steps = [f"Шаг {i+1}: пройти {random.randint(50, 300)} м" for i in range(3)]
        for step in steps:
            self.add_widget(MDLabel(text=step, theme_text_color="Secondary"))


class RestaurantScreen(BoxLayout):
    def __init__(self, restaurant_id=None, app=None, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        self.restaurant_id = restaurant_id
        self.app = app
        self.restaurant = None
        self.menu = []
        self.reviews = []

        if restaurant_id:
            self.load_data()

        if self.restaurant:
            self.add_widget(MDLabel(
                text=f"{self.restaurant[1]} ({self.restaurant[2]})",
                halign="center",
                theme_text_color="Primary",
                font_style="H5",
                size_hint_y=None,
                height=50
            ))

        self.add_widget(RouteMap(size_hint_y=0.3))

        scroll = ScrollView(size_hint=(1, 0.7))
        grid = GridLayout(cols=1, spacing=10, size_hint_y=None, padding=10)
        grid.bind(minimum_height=grid.setter("height"))

        for item in self.menu:
            card = MDCard(orientation="vertical", size_hint_y=None, height=120, padding=10)
            card.add_widget(MDLabel(text=f"{item[2]} - {item[4]}₽", theme_text_color="Primary"))
            card.add_widget(MDLabel(text=item[3], theme_text_color="Secondary"))
            add_btn = Button(text="В корзину", size_hint_y=None, height=30)
            add_btn.bind(on_release=lambda inst, iid=item[0]: self.add_to_cart(iid))
            card.add_widget(add_btn)
            grid.add_widget(card)

        grid.add_widget(MDLabel(text="Отзывы:", theme_text_color="Primary"))
        for review in self.reviews:
            card = MDCard(orientation="vertical", size_hint_y=None, height=80, padding=10)
            card.add_widget(MDLabel(text=f"{review[2]}: {review[3]} (⭐{review[4]})",
                                    theme_text_color="Secondary"))
            grid.add_widget(card)

        grid.add_widget(MDLabel(text="Добавить отзыв:", theme_text_color="Primary"))
        self.review_input = MDTextField(hint_text="Ваш отзыв")
        self.rating_input = MDTextField(hint_text="Оценка (1-5)", input_filter="int")
        submit_btn = Button(text="Оставить отзыв", size_hint_y=None, height=40)
        submit_btn.bind(on_release=self.add_review)

        grid.add_widget(self.review_input)
        grid.add_widget(self.rating_input)
        grid.add_widget(submit_btn)

        cart_btn = Button(text="Перейти в корзину", size_hint_y=None, height=40)
        cart_btn.bind(on_release=lambda inst: self.app.open_cart())
        grid.add_widget(cart_btn)

        scroll.add_widget(grid)
        self.add_widget(scroll)

    def load_data(self):
        if not os.path.exists(DB_PATH):
            return
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM restaurants WHERE id=?", (self.restaurant_id,))
        self.restaurant = cursor.fetchone()
        cursor.execute("SELECT * FROM menu WHERE restaurant_id=?", (self.restaurant_id,))
        self.menu = cursor.fetchall()
        cursor.execute("SELECT * FROM reviews WHERE restaurant_id=?", (self.restaurant_id,))
        self.reviews = cursor.fetchall()
        conn.close()

    def add_review(self, instance):
        text = self.review_input.text.strip()
        rating = self.rating_input.text.strip()
        if not text or not rating:
            return
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO reviews (restaurant_id, username, comment, rating)
            VALUES (?, ?, ?, ?)
        """, (self.restaurant_id, "User", text, float(rating)))
        conn.commit()
        conn.close()
        self.review_input.text = ""
        self.rating_input.text = ""

    def add_to_cart(self, item_id):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM cart WHERE item_id=? AND restaurant_id=?", (item_id, self.restaurant_id))
        row = cursor.fetchone()
        if row:
            cursor.execute("UPDATE cart SET quantity = quantity + 1 WHERE id=?", (row[0],))
        else:
            cursor.execute("INSERT INTO cart (restaurant_id, item_id, quantity) VALUES (?, ?, ?)",
                           (self.restaurant_id, item_id, 1))
        conn.commit()
        conn.close()
