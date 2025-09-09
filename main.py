from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
import os
import sqlite3

from screens.home import HomeScreen
from screens.restaurant import RestaurantScreen
from screens.cart import CartScreen

DB_PATH = "data/database.db"


class FoodDeliveryApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Orange"
        self.theme_cls.theme_style = "Light"

        sm = ScreenManager()
        sm.add_widget(Screen(name="home"))
        sm.add_widget(Screen(name="restaurant"))
        sm.add_widget(Screen(name="cart"))

        sm.get_screen("home").add_widget(HomeScreen(app=self))
        return sm

    def open_restaurant(self, restaurant_id):
        screen = self.root.get_screen("restaurant")
        screen.clear_widgets()
        screen.add_widget(RestaurantScreen(restaurant_id=restaurant_id, app=self))
        self.root.current = "restaurant"

    def open_cart(self):
        screen = self.root.get_screen("cart")
        screen.clear_widgets()
        screen.add_widget(CartScreen(app=self))
        self.root.current = "cart"


if __name__ == "__main__":
    if not os.path.exists("data"):
        os.makedirs("data")

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS restaurants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        category TEXT,
        rating REAL,
        distance REAL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS menu (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        restaurant_id INTEGER,
        name TEXT,
        description TEXT,
        price REAL,
        image TEXT,
        FOREIGN KEY (restaurant_id) REFERENCES restaurants (id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        restaurant_id INTEGER,
        username TEXT,
        comment TEXT,
        rating REAL,
        FOREIGN KEY (restaurant_id) REFERENCES restaurants (id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cart (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        restaurant_id INTEGER,
        item_id INTEGER,
        quantity INTEGER,
        FOREIGN KEY (restaurant_id) REFERENCES restaurants (id),
        FOREIGN KEY (item_id) REFERENCES menu (id)
    )
    """)

    conn.commit()
    conn.close()

    FoodDeliveryApp().run()