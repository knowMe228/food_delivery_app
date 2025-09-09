from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.scatter import Scatter
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.uix.popup import Popup
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivy.clock import Clock
from kivy.vector import Vector
import sqlite3
import os
import sys
import json
import math
import random
import webbrowser
import tempfile

# Add utils to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DB_PATH = "data/database.db"


class InteractiveMapCanvas(Scatter):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.do_rotation = False  # Disable rotation
        self.restaurants = []
        self.user_location = [55.7558, 37.6176]  # Moscow center
        self.routes = []
        self.selected_restaurant = None
        
        # Map bounds (Moscow area)
        self.map_bounds = {
            'min_lat': 55.70, 'max_lat': 55.80,
            'min_lon': 37.50, 'max_lon': 37.80
        }
        
        self.draw_map()
        self.bind(on_touch_down=self.on_map_touch)
        
    def coords_to_pixels(self, lat, lon):
        """Convert geographic coordinates to pixel coordinates"""
        lat_norm = (lat - self.map_bounds['min_lat']) / (self.map_bounds['max_lat'] - self.map_bounds['min_lat'])
        lon_norm = (lon - self.map_bounds['min_lon']) / (self.map_bounds['max_lon'] - self.map_bounds['min_lon'])
        
        x = lon_norm * 600
        y = (1 - lat_norm) * 400  # Invert Y axis
        
        return x, y
    
    def pixels_to_coords(self, x, y):
        """Convert pixel coordinates to geographic coordinates"""
        lon_norm = x / 600
        lat_norm = 1 - (y / 400)  # Invert Y axis
        
        lat = self.map_bounds['min_lat'] + lat_norm * (self.map_bounds['max_lat'] - self.map_bounds['min_lat'])
        lon = self.map_bounds['min_lon'] + lon_norm * (self.map_bounds['max_lon'] - self.map_bounds['min_lon'])
        
        return lat, lon
    
    def draw_map(self):
        """Draw the map background and elements"""
        with self.canvas:
            self.canvas.clear()
            
            # Map background
            Color(0.9, 0.95, 0.9, 1)  # Light green
            Rectangle(pos=(0, 0), size=(600, 400))
            
            # Draw grid (streets)
            Color(0.7, 0.7, 0.7, 1)  # Gray
            for i in range(0, 601, 60):  # Vertical lines
                Line(points=[i, 0, i, 400], width=1)
            for i in range(0, 401, 40):  # Horizontal lines
                Line(points=[0, i, 600, i], width=1)
            
            # Draw some buildings
            Color(0.8, 0.8, 0.8, 1)  # Light gray
            for _ in range(15):
                x = random.randint(10, 580)
                y = random.randint(10, 380)
                w = random.randint(15, 30)
                h = random.randint(15, 30)
                Rectangle(pos=(x, y), size=(w, h))
            
            # Draw user location
            self.draw_user_location()
            
            # Draw restaurants
            self.draw_restaurants()
            
            # Draw routes
            self.draw_routes()
    
    def draw_user_location(self):
        """Draw user location marker"""
        x, y = self.coords_to_pixels(self.user_location[0], self.user_location[1])
        with self.canvas:
            Color(0, 0.5, 1, 1)  # Blue
            Ellipse(pos=(x-10, y-10), size=(20, 20))
            Color(1, 1, 1, 1)  # White center
            Ellipse(pos=(x-5, y-5), size=(10, 10))
    
    def draw_restaurants(self):
        """Draw restaurant markers"""
        for restaurant in self.restaurants:
            x, y = self.coords_to_pixels(restaurant['lat'], restaurant['lon'])
            with self.canvas:
                Color(1, 0.2, 0.2, 1)  # Red
                Ellipse(pos=(x-8, y-8), size=(16, 16))
                Color(1, 1, 1, 1)  # White center
                Ellipse(pos=(x-4, y-4), size=(8, 8))
    
    def draw_routes(self):
        """Draw routes to restaurants"""
        user_x, user_y = self.coords_to_pixels(self.user_location[0], self.user_location[1])
        
        for route in self.routes:
            rest_x, rest_y = self.coords_to_pixels(route['lat'], route['lon'])
            with self.canvas:
                Color(1, 0.6, 0, 0.8)  # Orange
                Line(points=[user_x, user_y, rest_x, rest_y], width=3)
    
    def on_map_touch(self, instance, touch):
        """Handle map touch events"""
        if self.collide_point(*touch.pos):
            local_pos = self.to_local(*touch.pos)
            
            # Check if touched near a restaurant
            for restaurant in self.restaurants:
                x, y = self.coords_to_pixels(restaurant['lat'], restaurant['lon'])
                distance = Vector(local_pos).distance((x, y))
                
                if distance < 20:
                    self.show_restaurant_popup(restaurant)
                    return True
            
            # Check if touched near user location
            user_x, user_y = self.coords_to_pixels(self.user_location[0], self.user_location[1])
            if Vector(local_pos).distance((user_x, user_y)) < 20:
                self.show_location_popup()
                return True
            
            # Otherwise, move user location
            lat, lon = self.pixels_to_coords(local_pos[0], local_pos[1])
            if self.is_valid_coordinate(lat, lon):
                self.user_location = [lat, lon]
                self.redraw()
                return True
        
        return False
    
    def is_valid_coordinate(self, lat, lon):
        """Check if coordinates are within map bounds"""
        return (self.map_bounds['min_lat'] <= lat <= self.map_bounds['max_lat'] and 
                self.map_bounds['min_lon'] <= lon <= self.map_bounds['max_lon'])
    
    def show_restaurant_popup(self, restaurant):
        """Show restaurant information popup"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        content.add_widget(MDLabel(
            text=f"[b]{restaurant['name']}[/b]",
            markup=True,
            theme_text_color="Primary",
            size_hint_y=None,
            height="40dp"
        ))
        
        content.add_widget(MDLabel(
            text=f"Категория: {restaurant['category']}",
            theme_text_color="Secondary",
            size_hint_y=None,
            height="30dp"
        ))
        
        content.add_widget(MDLabel(
            text=f"Рейтинг: ⭐ {restaurant['rating']}",
            theme_text_color="Secondary",
            size_hint_y=None,
            height="30dp"
        ))
        
        distance = self.calculate_distance(
            self.user_location[0], self.user_location[1],
            restaurant['lat'], restaurant['lon']
        )
        
        content.add_widget(MDLabel(
            text=f"Расстояние: {distance:.1f} км",
            theme_text_color="Secondary",
            size_hint_y=None,
            height="30dp"
        ))
        
        buttons = BoxLayout(spacing=10, size_hint_y=None, height="50dp")
        
        route_btn = Button(text="📍 Маршрут")
        route_btn.bind(on_release=lambda x: self.build_route(restaurant))
        buttons.add_widget(route_btn)
        
        menu_btn = Button(text="🍽️ Меню")
        menu_btn.bind(on_release=lambda x: self.open_restaurant_menu(restaurant))
        buttons.add_widget(menu_btn)
        
        content.add_widget(buttons)
        
        close_btn = Button(
            text="Закрыть",
            size_hint_y=None,
            height="40dp"
        )
        
        popup = Popup(
            title=restaurant['name'],
            content=content,
            size_hint=(0.8, 0.6),
            auto_dismiss=True
        )
        
        close_btn.bind(on_release=popup.dismiss)
        content.add_widget(close_btn)
        
        popup.open()
    
    def show_location_popup(self):
        """Show user location popup"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        content.add_widget(MDLabel(
            text="📍 Ваше местоположение",
            theme_text_color="Primary",
            size_hint_y=None,
            height="40dp"
        ))
        
        content.add_widget(MDLabel(
            text=f"Координаты: {self.user_location[0]:.4f}, {self.user_location[1]:.4f}",
            theme_text_color="Secondary",
            size_hint_y=None,
            height="30dp"
        ))
        
        content.add_widget(MDLabel(
            text="Коснитесь карты для изменения местоположения",
            theme_text_color="Secondary",
            size_hint_y=None,
            height="30dp"
        ))
        
        close_btn = Button(
            text="Закрыть",
            size_hint_y=None,
            height="40dp"
        )
        
        popup = Popup(
            title="Местоположение",
            content=content,
            size_hint=(0.7, 0.5),
            auto_dismiss=True
        )
        
        close_btn.bind(on_release=popup.dismiss)
        content.add_widget(close_btn)
        
        popup.open()
    
    def build_route(self, restaurant):
        """Build route to restaurant"""
        route = {
            'restaurant_id': restaurant['id'],
            'name': restaurant['name'],
            'lat': restaurant['lat'],
            'lon': restaurant['lon']
        }
        
        self.routes = [r for r in self.routes if r['restaurant_id'] != restaurant['id']]
        self.routes.append(route)
        
        self.redraw()
        
        distance = self.calculate_distance(
            self.user_location[0], self.user_location[1],
            restaurant['lat'], restaurant['lon']
        )
        
        time_minutes = int((distance / 5) * 60)
        
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        content.add_widget(MDLabel(
            text=f"Маршрут до {restaurant['name']}",
            theme_text_color="Primary",
            size_hint_y=None,
            height="40dp"
        ))
        
        content.add_widget(MDLabel(
            text=f"📏 Расстояние: {distance:.1f} км",
            theme_text_color="Secondary",
            size_hint_y=None,
            height="30dp"
        ))
        
        content.add_widget(MDLabel(
            text=f"⏱️ Время пешком: ~{time_minutes} мин",
            theme_text_color="Secondary",
            size_hint_y=None,
            height="30dp"
        ))
        
        close_btn = Button(text="OK", size_hint_y=None, height="40dp")
        
        popup = Popup(
            title="Маршрут построен",
            content=content,
            size_hint=(0.7, 0.4),
            auto_dismiss=True
        )
        
        close_btn.bind(on_release=popup.dismiss)
        content.add_widget(close_btn)
        
        popup.open()
    
    def open_restaurant_menu(self, restaurant):
        """Open restaurant menu"""
        # Find root app reference
        current = self
        while current.parent and not hasattr(current, 'app'):
            current = current.parent
            if hasattr(current, 'app') and current.app:
                current.app.open_restaurant(restaurant['id'])
                return
        
        print(f"Opening restaurant {restaurant['name']} (ID: {restaurant['id']})")
    
    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two coordinates in km"""
        R = 6371
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat/2) * math.sin(delta_lat/2) +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon/2) * math.sin(delta_lon/2))
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = R * c
        
        return distance
    
    def redraw(self):
        """Redraw the entire map"""
        Clock.schedule_once(lambda dt: self.draw_map(), 0)
    
    def load_restaurants(self, restaurants_data):
        """Load restaurants data"""
        self.restaurants = []
        base_lat, base_lon = 55.7558, 37.6176
        
        for i, restaurant in enumerate(restaurants_data):
            lat = base_lat + random.uniform(-0.03, 0.03)
            lon = base_lon + random.uniform(-0.04, 0.04)
            
            self.restaurants.append({
                'id': restaurant[0],
                'name': restaurant[1],
                'category': restaurant[2],
                'rating': restaurant[3],
                'distance': restaurant[4],
                'lat': lat,
                'lon': lon
            })
        
        self.redraw()
    
    def clear_routes(self):
        """Clear all routes"""
        self.routes = []
        self.redraw()


class InteractiveMapWidget(BoxLayout):
    def __init__(self, app=None, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        self.app = app
        
        # Title
        title_layout = BoxLayout(size_hint_y=None, height="50dp", padding=5)
        title_layout.add_widget(MDLabel(
            text="🗺️ Интерактивная карта",
            halign="center",
            theme_text_color="Primary",
            font_style="H6"
        ))
        self.add_widget(title_layout)
        
        # Controls
        controls = BoxLayout(size_hint_y=None, height="40dp", spacing=5, padding=5)
        
        location_btn = Button(text="📍 GPS", size_hint_x=0.2)
        location_btn.bind(on_release=self.show_location_controls)
        controls.add_widget(location_btn)
        
        restaurants_btn = Button(text="🍽️ Все", size_hint_x=0.2)
        restaurants_btn.bind(on_release=self.show_all_restaurants)
        controls.add_widget(restaurants_btn)
        
        clear_btn = Button(text="🗑️ Очистить", size_hint_x=0.2)
        clear_btn.bind(on_release=self.clear_routes)
        controls.add_widget(clear_btn)
        
        browser_btn = Button(text="🌐 Браузер", size_hint_x=0.2)
        browser_btn.bind(on_release=self.open_in_browser)
        controls.add_widget(browser_btn)
        
        back_btn = Button(text="← Назад", size_hint_x=0.2)
        back_btn.bind(on_release=self.go_back)
        controls.add_widget(back_btn)
        
        self.add_widget(controls)
        
        # Map
        self.map_canvas = InteractiveMapCanvas(size_hint=(1, 1))
        self.map_canvas.app = app  # Pass app reference
        self.add_widget(self.map_canvas)
        
        # Load restaurants
        self.load_restaurants()
    
    def load_restaurants(self):
        """Load restaurants from database"""
        if not os.path.exists(DB_PATH):
            return
        
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM restaurants LIMIT 10")
            data = cursor.fetchall()
            conn.close()
            
            self.map_canvas.load_restaurants(data)
        except Exception as e:
            print(f"Error loading restaurants: {e}")
    
    def show_location_controls(self, instance):
        """Show location control popup"""
        self.map_canvas.show_location_popup()
    
    def show_all_restaurants(self, instance):
        """Show all restaurants on map"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        content.add_widget(MDLabel(
            text="🍽️ Рестораны на карте",
            theme_text_color="Primary",
            size_hint_y=None,
            height="40dp"
        ))
        
        for restaurant in self.map_canvas.restaurants:
            rest_layout = BoxLayout(size_hint_y=None, height="40dp")
            
            rest_layout.add_widget(MDLabel(
                text=f"{restaurant['name']} ({restaurant['category']})",
                theme_text_color="Secondary"
            ))
            
            route_btn = Button(
                text="📍",
                size_hint_x=None,
                width="40dp"
            )
            route_btn.bind(on_release=lambda x, r=restaurant: self.map_canvas.build_route(r))
            rest_layout.add_widget(route_btn)
            
            content.add_widget(rest_layout)
        
        close_btn = Button(text="Закрыть", size_hint_y=None, height="40dp")
        
        popup = Popup(
            title="Рестораны",
            content=content,
            size_hint=(0.8, 0.7),
            auto_dismiss=True
        )
        
        close_btn.bind(on_release=popup.dismiss)
        content.add_widget(close_btn)
        
        popup.open()
    
    def clear_routes(self, instance):
        """Clear all routes"""
        self.map_canvas.clear_routes()
    
    def open_in_browser(self, instance):
        """Open interactive map in browser"""
        try:
            html_content = self.create_browser_map()
            html_file = os.path.join(tempfile.gettempdir(), 'interactive_map.html')
            
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            webbrowser.open(f'file://{html_file}')
        except Exception as e:
            print(f"Error opening in browser: {e}")
    
    def create_browser_map(self):
        """Create HTML for browser map"""
        restaurants_json = json.dumps([{
            'id': r['id'],
            'name': r['name'], 
            'category': r['category'],
            'rating': r['rating'],
            'lat': r['lat'],
            'lon': r['lon']
        } for r in self.map_canvas.restaurants])
        
        return f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Интерактивная карта ресторанов</title>
    <script src="https://api-maps.yandex.ru/2.1/?apikey=c045d2a8-bc9f-46c5-95ab-d41879ea8136&lang=ru_RU"></script>
    <style>
        body, html {{ margin: 0; padding: 0; height: 100%; }}
        #map {{ width: 100%; height: 100%; }}
        .controls {{ position: absolute; top: 10px; left: 10px; z-index: 1000; background: white; padding: 10px; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="controls">
        <button onclick="getCurrentLocation()">📍 Мое местоположение</button>
        <button onclick="showAllRestaurants()">🍽️ Все рестораны</button>
    </div>
    <div id="map"></div>
    
    <script>
        let map, userMark;
        const restaurants = {restaurants_json};
        
        ymaps.ready(init);
        
        function init() {{
            map = new ymaps.Map('map', {{
                center: [55.7558, 37.6176],
                zoom: 12,
                controls: ['zoomControl', 'searchControl', 'routeButtonControl']
            }});
            
            addUserLocation();
            addRestaurants();
        }}
        
        function addUserLocation() {{
            userMark = new ymaps.Placemark([55.7558, 37.6176], {{
                balloonContent: 'Ваше местоположение'
            }}, {{
                preset: 'islands#blueCircleDotIcon',
                draggable: true
            }});
            map.geoObjects.add(userMark);
        }}
        
        function addRestaurants() {{
            restaurants.forEach(restaurant => {{
                const mark = new ymaps.Placemark([restaurant.lat, restaurant.lon], {{
                    balloonContent: `
                        <div>
                            <h3>${{restaurant.name}}</h3>
                            <p>Категория: ${{restaurant.category}}</p>
                            <p>⭐ ${{restaurant.rating}}</p>
                            <button onclick="buildRoute(${{restaurant.lat}}, ${{restaurant.lon}})">Построить маршрут</button>
                        </div>
                    `
                }}, {{
                    preset: 'islands#redRestaurantIcon'
                }});
                map.geoObjects.add(mark);
            }});
        }}
        
        function getCurrentLocation() {{
            if (navigator.geolocation) {{
                navigator.geolocation.getCurrentPosition(function(position) {{
                    const coords = [position.coords.latitude, position.coords.longitude];
                    map.setCenter(coords, 15);
                    userMark.geometry.setCoordinates(coords);
                }});
            }} else {{
                alert('Геолокация не поддерживается');
            }}
        }}
        
        function showAllRestaurants() {{
            const bounds = restaurants.map(r => [r.lat, r.lon]);
            bounds.push(userMark.geometry.getCoordinates());
            map.setBounds(bounds, {{ checkZoomRange: true }});
        }}
        
        function buildRoute(restLat, restLon) {{
            const userCoords = userMark.geometry.getCoordinates();
            
            ymaps.route([userCoords, [restLat, restLon]], {{
                routingMode: 'pedestrian'
            }}).then(function (route) {{
                map.geoObjects.removeAll();
                map.geoObjects.add(userMark);
                addRestaurants();
                map.geoObjects.add(route);
                
                route.getPaths().options.set({{
                    strokeColor: '#ff9800',
                    strokeWidth: 4,
                    strokeOpacity: 0.8
                }});
                
                const distance = route.getLength();
                const duration = route.getJamesTime() || route.getTime();
                
                map.balloon.open(map.getCenter(), {{
                    contentBody: `
                        <div>
                            <p>📏 Расстояние: ${{Math.round(distance/1000*100)/100}} км</p>
                            <p>⏱️ Время пешком: ${{Math.round(duration/60)}} мин</p>
                        </div>
                    `
                }});
            }}).catch(function(error) {{
                console.error('Routing error:', error);
                alert('Не удалось построить маршрут');
            }});
        }}
    </script>
</body>
</html>'''
    
    def go_back(self, instance):
        """Go back to home screen"""
        if self.app and hasattr(self.app, 'root'):
            self.app.root.current = "home"


class MapWidget(BoxLayout):
    def __init__(self, restaurants, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        
        try:
            from utils.yandex_maps import YandexMapWidget, generate_restaurant_coordinates
            
            self.yandex_maps = YandexMapWidget()
            restaurant_coords = generate_restaurant_coordinates(count=len(restaurants))
            
            markers = []
            for i, (r, coords) in enumerate(zip(restaurants, restaurant_coords)):
                markers.append({
                    'lat': coords['lat'], 
                    'lon': coords['lon'], 
                    'color': 'red',
                    'style': 'pm2'
                })
            
            if markers:
                center_lat = sum(m['lat'] for m in markers) / len(markers)
                center_lon = sum(m['lon'] for m in markers) / len(markers)
            else:
                center_lat, center_lon = 55.7558, 37.6176
            
            map_url = self.yandex_maps.get_static_map(
                center_lat, center_lon, 
                zoom=12, 
                width=380, 
                height=200,
                markers=markers
            )
            
            self.add_widget(MDLabel(
                text="🗺️ Карта ресторанов",
                halign="center",
                theme_text_color="Primary",
                size_hint_y=None,
                height=30
            ))
            
            try:
                map_image = Image(
                    source=map_url,
                    size_hint_y=None,
                    height=200
                )
                self.add_widget(map_image)
            except Exception as e:
                print(f"Error loading map image: {e}")
                self.add_widget(MDLabel(
                    text="🗺️ Карта недоступна (проверьте подключение)",
                    halign="center",
                    theme_text_color="Secondary",
                    size_hint_y=None,
                    height=200
                ))
            
        except Exception as e:
            print(f"Error loading Yandex Maps: {e}")
            self.add_widget(MDLabel(
                text="🗺️ Карта ресторанов (загрузка...)",
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
        self.current_view = "list"

        self.add_widget(MDLabel(
            text="🍔 Food Delivery",
            halign="center",
            theme_text_color="Primary",
            font_style="H5",
            size_hint_y=None,
            height=50
        ))

        # Toggle buttons
        toggle_layout = BoxLayout(size_hint_y=None, height=50, padding=5)
        
        self.list_btn = Button(
            text="📋 Список ресторанов",
            size_hint_x=0.5
        )
        self.list_btn.bind(on_release=self.show_list_view)
        toggle_layout.add_widget(self.list_btn)
        
        self.map_btn = Button(
            text="🗺️ Интерактивная карта", 
            size_hint_x=0.5
        )
        self.map_btn.bind(on_release=self.show_map_view)
        toggle_layout.add_widget(self.map_btn)
        
        self.add_widget(toggle_layout)

        # Container for switching between views
        self.content_container = BoxLayout(orientation="vertical")
        self.add_widget(self.content_container)
        
        # Initialize with list view
        self.show_list_view(None)

    def show_list_view(self, instance):
        """Show restaurant list view"""
        self.current_view = "list"
        self.content_container.clear_widgets()
        
        # Update button states
        self.list_btn.text = "📋 Список ресторанов ✓"
        self.map_btn.text = "🗺️ Интерактивная карта"
        
        # Original static map widget
        self.content_container.add_widget(MapWidget(self.restaurants, size_hint_y=0.3))

        # Filter bar
        filter_bar = BoxLayout(size_hint_y=None, height=50, spacing=5, padding=5)
        filter_bar.add_widget(Button(text="Пицца"))
        filter_bar.add_widget(Button(text="Суши"))
        filter_bar.add_widget(Button(text="Бургеры"))
        self.content_container.add_widget(filter_bar)

        # Restaurant list
        scroll = ScrollView(size_hint=(1, 0.7))
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
        self.content_container.add_widget(scroll)

    def show_map_view(self, instance):
        """Show interactive map view"""
        self.current_view = "map"
        self.content_container.clear_widgets()
        
        # Update button states
        self.list_btn.text = "📋 Список ресторанов"
        self.map_btn.text = "🗺️ Интерактивная карта ✓"
        
        # Enhanced interactive map widget with embedded browser
        try:
            from utils.yandex_maps import YandexMapsWebView
            map_widget = YandexMapsWebView(app=self.app)
            self.content_container.add_widget(map_widget)
        except Exception as e:
            print(f"Error loading YandexMapsWebView: {e}")
            # Fallback to original interactive map
            map_widget = InteractiveMapWidget(app=self.app)
            self.content_container.add_widget(map_widget)

    def load_restaurants(self):
        if not os.path.exists(DB_PATH):
            return []
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM restaurants LIMIT 5")
        data = cursor.fetchall()
        conn.close()
        return data
