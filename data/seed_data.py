import sqlite3
import random

DB_PATH = "data/database.db"

restaurants = [
    ("Pizza House", "Пицца", 4.5, 1.2),
    ("Sushi World", "Суши", 4.7, 2.1),
    ("Burger Town", "Бургеры", 4.3, 0.8),
    ("Coffee Break", "Кофе", 4.8, 0.5),
    ("Vegan Life", "Вегетарианское", 4.6, 1.5),
]

menu_items = [
    ("Маргарита", "Традиционная пицца с томатами и сыром", 450, "pizza.jpg"),
    ("Филадельфия", "Ролл с лососем и сыром", 600, "sushi.jpg"),
    ("Чизбургер", "Классический бургер с сыром", 350, "burger.jpg"),
    ("Латте", "Кофе с молоком", 200, "coffee.jpg"),
    ("Салат", "Овощной салат с соусом", 300, "salad.jpg"),
]

reviews = [
    ("Иван", "Очень вкусно, понравилось!", 5.0),
    ("Мария", "Хорошее обслуживание", 4.0),
    ("Алексей", "Быстрая доставка", 4.5),
]

def seed():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for r in restaurants:
        cursor.execute("INSERT INTO restaurants (name, category, rating, distance) VALUES (?, ?, ?, ?)", r)
        rest_id = cursor.lastrowid

        for item in random.sample(menu_items, 3):
            cursor.execute("INSERT INTO menu (restaurant_id, name, description, price, image) VALUES (?, ?, ?, ?, ?)",
                           (rest_id, *item))

        for review in random.sample(reviews, 2):
            cursor.execute("INSERT INTO reviews (restaurant_id, username, comment, rating) VALUES (?, ?, ?, ?)",
                           (rest_id, *review))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    seed()
    print("✅ Демо-данные добавлены в базу")
