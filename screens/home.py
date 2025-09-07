from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
import sqlite3
import os

DB_PATH = "data/database.db"


class MapWidget(BoxLayout):
    def __init__(self, restaurants, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.add_widget(MDLabel(
            text="🗺️ Карта-заглушка",
            halign="center",
            theme_text_color="Primary"
        ))
        for r in restaurants:
            self.add_widget(MDLabel(
                text=f"📍 {r[1]} ({r[4]} км)",
                halign="left",
                theme_text_color="Secondary"
            ))


class HomeScreen(BoxLayout):
    def __init__(self, app=None, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        self.app = app
        self.restaurants = self.load_restaurants()

        self.add_widget(MDLabel(
            text="🍔 Food Delivery",
            halign="center",
            theme_text_color="Primary",
            font_style="H5",
            size_hint_y=None,
            height=50
        ))

        self.add_widget(MapWidget(self.restaurants, size_hint_y=0.3))

        filter_bar = BoxLayout(size_hint_y=None, height=50, spacing=5, padding=5)
        filter_bar.add_widget(Button(text="Пицца"))
        filter_bar.add_widget(Button(text="Суши"))
        filter_bar.add_widget(Button(text="Бургеры"))
        self.add_widget(filter_bar)

        scroll = ScrollView(size_hint=(1, 0.5))
        grid = GridLayout(cols=1, spacing=10, size_hint_y=None, padding=10)
        grid.bind(minimum_height=grid.setter("height"))

        for r in self.restaurants:
            card = MDCard(orientation="vertical", size_hint_y=None, height=100, padding=10)
            card.add_widget(MDLabel(text=f"{r[1]} ({r[2]})", theme_text_color="Primary"))
            card.add_widget(MDLabel(text=f"⭐ {r[3]} • {r[4]} км", theme_text_color="Secondary"))

            btn = Button(text="Открыть", size_hint_y=None, height=30)
            btn.bind(on_release=lambda instance, rid=r[0]: self.app.open_restaurant(rid))
            card.add_widget(btn)

            grid.add_widget(card)

        scroll.add_widget(grid)
        self.add_widget(scroll)

    def load_restaurants(self):
        if not os.path.exists(DB_PATH):
            return []
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM restaurants LIMIT 5")
        data = cursor.fetchall()
        conn.close()
        return data
