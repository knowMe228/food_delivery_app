import os
import json
import threading
import time
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivymd.uix.label import MDLabel
from kivy.clock import Clock
import sqlite3
import tempfile
import webbrowser

# Try to import webview, fallback if not available
try:
    import webview
    WEBVIEW_AVAILABLE = True
except ImportError:
    WEBVIEW_AVAILABLE = False
    print("Warning: pywebview not available. Map will open in browser.")

DB_PATH = "data/database.db"


class WebMapWidget(BoxLayout):
    def __init__(self, app=None, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        self.app = app
        self.restaurants = []
        self.user_location = [55.7558, 37.6176]  # Moscow center
        self.html_file_path = None
        self.webview_window = None
        
        self.setup_ui()
        self.load_restaurants()
    
    def setup_ui(self):
        """Setup the UI components"""
        # Title
        title_layout = BoxLayout(size_hint_y=None, height="50dp", padding=5)
        title_layout.add_widget(MDLabel(
            text="🗺️ Интерактивная карта",
            halign="center",
            theme_text_color="Primary"
        ))
        self.add_widget(title_layout)
        
        # Controls
        controls = BoxLayout(size_hint_y=None, height="60dp", spacing=5, padding=5)
        
        # First row of controls
        controls_row1 = BoxLayout(size_hint_y=None, height="30dp", spacing=5)
        
        location_btn = Button(text="📍 GPS", size_hint_x=0.25)
        location_btn.bind(on_release=self.show_location_popup)
        controls_row1.add_widget(location_btn)
        
        restaurants_btn = Button(text="🍽️ Все", size_hint_x=0.25)
        restaurants_btn.bind(on_release=self.show_restaurants_list)
        controls_row1.add_widget(restaurants_btn)
        
        optimal_btn = Button(text="🚚 Ближайший", size_hint_x=0.25)
        optimal_btn.bind(on_release=self.find_optimal_route)
        controls_row1.add_widget(optimal_btn)
        
        refresh_btn = Button(text="🔄 Обновить", size_hint_x=0.25)
        refresh_btn.bind(on_release=self.refresh_map)
        controls_row1.add_widget(refresh_btn)
        
        controls.add_widget(controls_row1)
        
        # Second row of controls
        controls_row2 = BoxLayout(size_hint_y=None, height="30dp", spacing=5)
        
        embedded_btn = Button(text="🗺️ Полная карта", size_hint_x=0.5)
        embedded_btn.bind(on_release=self.open_embedded_map)
        controls_row2.add_widget(embedded_btn)
        
        browser_btn = Button(text="🌐 Браузер", size_hint_x=0.5)
        browser_btn.bind(on_release=self.open_in_browser)
        controls_row2.add_widget(browser_btn)
        
        back_btn = Button(text="← Назад", size_hint_x=0.5)
        back_btn.bind(on_release=self.go_back)
        controls_row2.add_widget(back_btn)
        
        controls.add_widget(controls_row2)
        self.add_widget(controls)
        
        # Map placeholder (will show embedded map or instructions)
        self.map_container = BoxLayout()
        
        # Instructions for the new improved map
        instructions = MDLabel(
            text="🗺️ Нажмите 'Полная карта' для открытия интерактивной карты\\n\\n"
                 "✨ Полноценные возможности:\\n"
                 "• 📍 Интерактивное местоположение (перетаскивание)\\n"
                 "• 🍽️ Клик по ресторанам для заказа\\n"
                 "• 🚚 Построение маршрутов с расчётом\\n"
                 "• ⏱️ Показ времени доставки\\n"
                 "• 🚐 Пробки и трафик\\n"
                 "• 📱 GPS геолокация\\n\\n"
                 "🎯 Теперь карта работает полноценно!",
            halign="center",
            theme_text_color="Secondary",
            markup=True
        )
        
        self.map_container.add_widget(instructions)
        self.add_widget(self.map_container)
    
    def load_restaurants(self):
        """Load restaurants from database"""
        if not os.path.exists(DB_PATH):
            self.create_default_restaurants()
            return
        
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM restaurants LIMIT 20")
            data = cursor.fetchall()
            conn.close()
            
            self.restaurants = []
            base_lat, base_lon = 55.7558, 37.6176
            
            for i, restaurant in enumerate(data):
                # Generate realistic coordinates around Moscow center
                import random
                lat = base_lat + random.uniform(-0.05, 0.05)
                lon = base_lon + random.uniform(-0.06, 0.06)
                
                self.restaurants.append({
                    'id': restaurant[0],
                    'name': restaurant[1],
                    'category': restaurant[2],
                    'rating': restaurant[3],
                    'distance': restaurant[4] if len(restaurant) > 4 else "1.5 км",
                    'lat': lat,
                    'lon': lon
                })
                
        except Exception as e:
            print(f"Error loading restaurants: {e}")
            self.create_default_restaurants()
    
    def create_default_restaurants(self):
        """Create default restaurants for demonstration"""
        base_lat, base_lon = 55.7558, 37.6176
        import random
        
        default_restaurants = [
            {"name": "Пицца Маргарита", "category": "Пицца", "rating": 4.5},
            {"name": "Суши Токио", "category": "Суши", "rating": 4.7},
            {"name": "Бургер Кинг", "category": "Фаст-фуд", "rating": 4.2},
            {"name": "Паста Италия", "category": "Итальянская", "rating": 4.6},
            {"name": "Шаурма Экспресс", "category": "Восточная", "rating": 4.1},
        ]
        
        self.restaurants = []
        for i, rest_data in enumerate(default_restaurants):
            lat = base_lat + random.uniform(-0.03, 0.03)
            lon = base_lon + random.uniform(-0.04, 0.04)
            
            self.restaurants.append({
                'id': i + 1,
                'name': rest_data['name'],
                'category': rest_data['category'],
                'rating': rest_data['rating'],
                'distance': f"{random.uniform(0.5, 3.0):.1f} км",
                'lat': lat,
                'lon': lon
            })
    
    def create_html_content(self):
        """Create HTML content with current restaurants data"""
        restaurants_json = json.dumps(self.restaurants)
        user_lat, user_lon = self.user_location
        
        # Read the HTML template
        html_template_path = os.path.join(os.path.dirname(__file__), "embedded_map.html")
        
        try:
            with open(html_template_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Replace the ymaps.ready(init); call with our data initialization
            html_content = html_content.replace(
                "// Для обратной совместимости\n        ymaps.ready(init);",
                f"// Initialize with app data\n        restaurants = {restaurants_json};\n        userLocation = [{user_lat}, {user_lon}];\n        ymaps.ready(init);"
            )
            
            return html_content
            
        except Exception as e:
            print(f"Error reading HTML template: {e}")
            return self.get_fallback_html()
    
    def get_fallback_html(self):
        """Fallback HTML if template file is not available"""
        restaurants_json = json.dumps(self.restaurants)
        user_lat, user_lon = self.user_location
        
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Карта ресторанов</title>
            <script src="https://api-maps.yandex.ru/2.1/?apikey=c045d2a8-bc9f-46c5-95ab-d41879ea8136&lang=ru_RU"></script>
        </head>
        <body>
            <div id="map" style="width: 100%; height: 100vh;"></div>
            <script>
                const restaurants = {restaurants_json};
                const userLocation = [{user_lat}, {user_lon}];
                
                ymaps.ready(function() {{
                    const map = new ymaps.Map('map', {{
                        center: userLocation,
                        zoom: 12
                    }});
                    
                    // Add user location
                    const userMark = new ymaps.Placemark(userLocation, {{
                        balloonContent: 'Ваше местоположение'
                    }}, {{
                        preset: 'islands#blueCircleDotIcon'
                    }});
                    map.geoObjects.add(userMark);
                    
                    // Add restaurants
                    restaurants.forEach(restaurant => {{
                        const mark = new ymaps.Placemark([restaurant.lat, restaurant.lon], {{
                            balloonContent: `<h3>${{restaurant.name}}</h3><p>${{restaurant.category}} - ${{restaurant.rating}}⭐</p>`
                        }}, {{
                            preset: 'islands#redRestaurantIcon'
                        }});
                        map.geoObjects.add(mark);
                    }});
                }});
            </script>
        </body>
        </html>
        '''
    
    def open_embedded_map(self, instance):
        """Open embedded map - now opens in browser for better compatibility"""
        try:
            # Create HTML content
            html_content = self.create_html_content()
            
            # Save to temporary file with a better name
            html_file = os.path.join(tempfile.gettempdir(), 'food_delivery_embedded_map.html')
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Open in default browser (more reliable than webview)
            webbrowser.open(f'file://{html_file}')
            
            # Update UI
            self.update_map_status("🗺️ Карта открыта в браузере")
            
        except Exception as e:
            print(f"Error opening embedded map: {e}")
            self.show_error_popup(f"Ошибка при открытии карты: {e}")
    
    def open_in_browser(self, instance):
        """Open interactive map in browser"""
        try:
            html_content = self.create_html_content()
            
            # Save to temporary file
            html_file = os.path.join(tempfile.gettempdir(), 'food_delivery_map_browser.html')
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Open in browser
            webbrowser.open(f'file://{html_file}')
            
            # Update UI
            self.update_map_status("🌐 Карта открыта в браузере")
            
        except Exception as e:
            self.show_error_popup(f"Ошибка при открытии в браузере: {e}")
    
    def update_map_status(self, message):
        """Update map container with status message"""
        self.map_container.clear_widgets()
        status_label = MDLabel(
            text=f"{message}\\n\\n✨ Доступные функции:\\n"
                 "• 📍 Интерактивное перемещение\\n"
                 "• 🍽️ Клик по ресторанам для заказа\\n"
                 "• 🚚 Построение маршрутов\\n"
                 "• ⏱️ Расчёт времени доставки\\n"
                 "• 🚦 Отображение пробок\\n"
                 "• 🗺️ Полноценное управление картой",
            halign="center",
            theme_text_color="Primary",
            markup=True
        )
        self.map_container.add_widget(status_label)
    
    def show_location_popup(self, instance):
        """Show location control popup"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=20)
        
        content.add_widget(MDLabel(
            text="📍 Управление местоположением",
            theme_text_color="Primary",
            size_hint_y=None,
            height="40dp",
            halign="center"
        ))
        
        current_location = MDLabel(
            text=f"Текущее: {self.user_location[0]:.4f}, {self.user_location[1]:.4f}",
            theme_text_color="Secondary",
            size_hint_y=None,
            height="30dp",
            halign="center"
        )
        content.add_widget(current_location)
        
        # GPS button
        gps_btn = Button(
            text="📡 Получить GPS координаты",
            size_hint_y=None,
            height="40dp"
        )
        
        def get_gps_location(btn):
            # Simulate GPS (in real app, use plyer.gps or similar)
            import random
            self.user_location = [
                55.7558 + random.uniform(-0.1, 0.1),
                37.6176 + random.uniform(-0.1, 0.1)
            ]
            current_location.text = f"Обновлено: {self.user_location[0]:.4f}, {self.user_location[1]:.4f}"
        
        gps_btn.bind(on_release=get_gps_location)
        content.add_widget(gps_btn)
        
        # Moscow center button
        moscow_btn = Button(
            text="🏛️ Центр Москвы",
            size_hint_y=None,
            height="40dp"
        )
        
        def set_moscow_center(btn):
            self.user_location = [55.7558, 37.6176]
            current_location.text = f"Москва: {self.user_location[0]:.4f}, {self.user_location[1]:.4f}"
        
        moscow_btn.bind(on_release=set_moscow_center)
        content.add_widget(moscow_btn)
        
        close_btn = Button(text="Закрыть", size_hint_y=None, height="40dp")
        
        popup = Popup(
            title="Местоположение",
            content=content,
            size_hint=(0.8, 0.6),
            auto_dismiss=True
        )
        
        close_btn.bind(on_release=popup.dismiss)
        content.add_widget(close_btn)
        popup.open()
    
    def show_restaurants_list(self, instance):
        """Show list of restaurants"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        content.add_widget(MDLabel(
            text="🍽️ Список ресторанов",
            theme_text_color="Primary",
            size_hint_y=None,
            height="40dp"
        ))
        
        for restaurant in self.restaurants[:10]:  # Show first 10
            rest_layout = BoxLayout(size_hint_y=None, height="50dp")
            
            rest_info = MDLabel(
                text=f"{restaurant['name']}\\n{restaurant['category']} • ⭐{restaurant['rating']}",
                theme_text_color="Secondary",
                markup=True
            )
            rest_layout.add_widget(rest_info)
            
            select_btn = Button(
                text="📍 Показать",
                size_hint_x=None,
                width="100dp"
            )
            # In real implementation, this would focus the map on the restaurant
            rest_layout.add_widget(select_btn)
            
            content.add_widget(rest_layout)
        
        close_btn = Button(text="Закрыть", size_hint_y=None, height="40dp")
        
        popup = Popup(
            title="Рестораны",
            content=content,
            size_hint=(0.9, 0.8),
            auto_dismiss=True
        )
        
        close_btn.bind(on_release=popup.dismiss)
        content.add_widget(close_btn)
        popup.open()
    
    def find_optimal_route(self, instance):
        """Find and display optimal route to nearest restaurant"""
        if not self.restaurants:
            self.show_error_popup("Нет доступных ресторанов")
            return
        
        # Simple distance calculation (in real app, use proper routing)
        import math
        
        def calculate_distance(lat1, lon1, lat2, lon2):
            R = 6371  # Earth's radius in km
            dlat = math.radians(lat2 - lat1)
            dlon = math.radians(lon2 - lon1)
            a = (math.sin(dlat/2) * math.sin(dlat/2) + 
                 math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
                 math.sin(dlon/2) * math.sin(dlon/2))
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            return R * c
        
        user_lat, user_lon = self.user_location
        closest_restaurant = min(
            self.restaurants,
            key=lambda r: calculate_distance(user_lat, user_lon, r['lat'], r['lon'])
        )
        
        distance = calculate_distance(user_lat, user_lon, closest_restaurant['lat'], closest_restaurant['lon'])
        delivery_time = int(distance * 3) + 15  # 3 min/km + 15 min preparation
        
        message = (f"🎯 Ближайший ресторан найден!\\n\\n"
                  f"🍽️ {closest_restaurant['name']}\\n"
                  f"📍 {closest_restaurant['category']}\\n"
                  f"⭐ {closest_restaurant['rating']}\\n"
                  f"📏 Расстояние: {distance:.1f} км\\n"
                  f"⏱️ Время доставки: ~{delivery_time} мин\\n\\n"
                  f"Откройте карту для построения маршрута!")
        
        self.show_info_popup("Оптимальный маршрут", message)
    
    def refresh_map(self, instance):
        """Refresh map data"""
        self.load_restaurants()
        self.update_map_status("🔄 Данные карты обновлены")
    
    def show_error_popup(self, message):
        """Show error popup"""
        popup = Popup(
            title="Ошибка",
            content=Label(text=message, text_size=(300, None)),
            size_hint=(None, None),
            size=(400, 200)
        )
        popup.open()
    
    def show_info_popup(self, title, message):
        """Show info popup"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=20)
        
        info_label = MDLabel(
            text=message,
            theme_text_color="Secondary",
            markup=True,
            halign="center"
        )
        content.add_widget(info_label)
        
        close_btn = Button(text="ОК", size_hint_y=None, height="40dp")
        
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.8, 0.7),
            auto_dismiss=True
        )
        
        close_btn.bind(on_release=popup.dismiss)
        content.add_widget(close_btn)
        popup.open()
    
    def go_back(self, instance):
        """Go back to home screen"""
        if self.app and hasattr(self.app, 'root'):
            self.app.root.current = "home"
    
    def cleanup(self):
        """Cleanup resources when widget is destroyed"""
        if self.html_file_path and os.path.exists(self.html_file_path):
            try:
                os.remove(self.html_file_path)
            except:
                pass
        
        if self.webview_window:
            try:
                webview.destroy_window()
            except:
                pass
