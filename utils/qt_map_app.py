import sys
import os
import json
import sqlite3
import random
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QApplication
from PySide6.QtWebEngineWidgets import QWebEngineView

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "database.db")


def load_restaurants_from_db(limit=20):
    if not os.path.exists(DB_PATH):
        return []
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM restaurants LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()
        base_lat, base_lon = 55.7558, 37.6176
        data = []
        for i, r in enumerate(rows):
            lat = base_lat + random.uniform(-0.05, 0.05)
            lon = base_lon + random.uniform(-0.06, 0.06)
            data.append({
                "id": r[0],
                "name": r[1],
                "category": r[2],
                "rating": r[3],
                "distance": r[4] if len(r) > 4 else 1.5,
                "lat": lat,
                "lon": lon,
            })
        return data
    except Exception:
        return []


def build_html(restaurants, user_lat=55.7558, user_lon=37.6176):
    restaurants_json = json.dumps(restaurants, ensure_ascii=False)
    # Re-use the embedded HTML template but inject data directly
    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset=\"UTF-8\">\n  <title>Интерактивная карта ресторанов - Qt</title>\n  <script src=\"https://api-maps.yandex.ru/2.1/?apikey=c045d2a8-bc9f-46c5-95ab-d41879ea8136&lang=ru_RU\"></script>\n  <style>html,body,#map {{height:100%;margin:0;padding:0}}</style>\n</head>
<body>
  <div id=\"map\"></div>
  <script>
    let map, userMark, currentRoute, trafficControl;\n    const restaurants = {restaurants_json};\n    let userLocation = [{user_lat}, {user_lon}];\n    ymaps.ready(function() {{\n      map = new ymaps.Map('map', {{ center: userLocation, zoom: 12, controls: ['zoomControl','routeButtonControl','fullscreenControl'] }});\n      trafficControl = new ymaps.control.TrafficControl();\n      map.controls.add(trafficControl);\n      userMark = new ymaps.Placemark(userLocation, {{balloonContent:'📍 Ваше местоположение'}}, {{preset:'islands#blueCircleDotIcon',draggable:true}});\n      map.geoObjects.add(userMark);\n      restaurants.forEach(r => {{\n        const m = new ymaps.Placemark([r.lat, r.lon], {{\n          balloonContent: `<h3>🍽️ ${'{'}r.name{'}'}</h3><p>${'{'}r.category{'}'} • ⭐ ${'{'}r.rating{'}'}</p>\n            <button onclick=\\\"(function(){{buildRoute(${ '{' }r.lat{ '}' }, ${ '{' }r.lon{ '}' }, '${ '{' }r.name{ '}' }')}})()\\\">Маршрут</button>`\n        }}, {{preset:'islands#redRestaurantIcon'}});\n        map.geoObjects.add(m);\n      }});\n    }});\n    function buildRoute(lat, lon, name) {{\n      const u = userMark.geometry.getCoordinates();\n      ymaps.route([u, [lat, lon]], {{routingMode:'auto'}}).then(function(route) {{\n        if (currentRoute) map.geoObjects.remove(currentRoute);\n        currentRoute = route;\n        route.getPaths().options.set({{strokeColor:'#FF9800', strokeWidth:6, strokeOpacity:0.9}});\n        map.geoObjects.add(route);\n        map.setBounds(route.getBounds());\n      }});\n    }}
  </script>
</body>
</html>"""


def run_qt_map(restaurants=None):
    app = QApplication(sys.argv)
    view = QWebEngineView()
    view.setWindowTitle("🗺️ Интерактивная карта - встроенный браузер (Qt)")
    if restaurants is None:
        restaurants = load_restaurants_from_db()
    html = build_html(restaurants)
    view.setHtml(html, baseUrl=QUrl("https://local/"))
    view.resize(1100, 750)
    view.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    # If a json file path is given in argv, load restaurants from it
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            data = json.load(f)
        run_qt_map(data)
    else:
        run_qt_map()

