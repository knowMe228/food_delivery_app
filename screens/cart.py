from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
import sqlite3
import os

DB_PATH = "data/database.db"


class CartScreen(BoxLayout):
    def __init__(self, app=None, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        self.app = app

        self.add_widget(MDLabel(
            text="🛒 Корзина",
            halign="center",
            theme_text_color="Primary",
            font_style="H5",
            size_hint_y=None,
            height=50
        ))

        scroll = ScrollView(size_hint=(1, 0.9))
        grid = GridLayout(cols=1, spacing=10, size_hint_y=None, padding=10)
        grid.bind(minimum_height=grid.setter("height"))

        items, total = self.load_cart()

        for item in items:
            card = MDCard(orientation="vertical", size_hint_y=None, height=100, padding=10)
            card.add_widget(MDLabel(text=f"{item[0]} x{item[1]}", theme_text_color="Primary"))
            card.add_widget(MDLabel(text=f"Цена: {item[2]}₽", theme_text_color="Secondary"))
            grid.add_widget(card)

        grid.add_widget(MDLabel(text=f"Итого: {total}₽", theme_text_color="Primary"))

        order_btn = Button(text="Оформить заказ", size_hint_y=None, height=40)
        order_btn.bind(on_release=self.make_order)
        grid.add_widget(order_btn)

        scroll.add_widget(grid)
        self.add_widget(scroll)

    def load_cart(self):
        if not os.path.exists(DB_PATH):
            return [], 0
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
        SELECT m.name, c.quantity, m.price * c.quantity
        FROM cart c
        JOIN menu m ON m.id = c.item_id
        """)
        data = cursor.fetchall()
        total = sum([row[2] for row in data])
        conn.close()
        return data, total

    def make_order(self, instance):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cart")
        conn.commit()
        conn.close()
        print("✅ Заказ оформлен!")
