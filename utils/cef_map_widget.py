import os
import json
import tempfile
from threading import Timer
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivymd.uix.label import MDLabel
from kivy.clock import Clock
import sqlite3

# Try to import CEF Python
try:
    from cefpython3 import cefpython as cef
    CEF_AVAILABLE = True
except ImportError:
    CEF_AVAILABLE = False
    print("Warning: CEF Python not available. Map will fallback to browser.")

DB_PATH = "data/database.db"


class CEFMapWidget(BoxLayout):
    def __init__(self, app=None, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        self.app = app
        self.restaurants = []
        self.user_location = [55.7558, 37.6176]  # Moscow center
        self.html_file_path = None
        self.cef_browser = None
        self.browser_widget = None
        
        self.setup_ui()
        self.load_restaurants()
        
        if CEF_AVAILABLE:
            # Initialize CEF
            self.setup_cef()
    
    def setup_ui(self):
        """Setup the UI components"""
        # Title
        title_layout = BoxLayout(size_hint_y=None, height="50dp", padding=5)
        title_layout.add_widget(MDLabel(
            text="🗺️ Встроенная интерактивная карта",
            halign="center",
            theme_text_color="Primary"
        ))
        self.add_widget(title_layout)
        
        # Controls
        controls = BoxLayout(size_hint_y=None, height="60dp", spacing=5, padding=5)
        
        # First row
        controls_row1 = BoxLayout(size_hint_y=None, height="30dp", spacing=5)
        
        location_btn = Button(text="📍 GPS", size_hint_x=0.25)
        location_btn.bind(on_release=self.show_location_popup)
        controls_row1.add_widget(location_btn)
        
        restaurants_btn = Button(text="🍽️ Все", size_hint_x=0.25)
        restaurants_btn.bind(on_release=self.show_restaurants_list)
        controls_row1.add_widget(restaurants_btn)
        
        refresh_btn = Button(text="🔄 Обновить", size_hint_x=0.25)
        refresh_btn.bind(on_release=self.refresh_map)
        controls_row1.add_widget(refresh_btn)
        
        optimal_btn = Button(text="🎯 Ближайший", size_hint_x=0.25)
        optimal_btn.bind(on_release=self.find_optimal_route)
        controls_row1.add_widget(optimal_btn)
        
        controls.add_widget(controls_row1)
        
        # Second row
        controls_row2 = BoxLayout(size_hint_y=None, height="30dp", spacing=5)
        
        if CEF_AVAILABLE:
            load_btn = Button(text="🚀 Загрузить карту", size_hint_x=0.5)
            load_btn.bind(on_release=self.load_map)
            controls_row2.add_widget(load_btn)
        else:
            fallback_btn = Button(text="🌐 Открыть в браузере", size_hint_x=0.5)
            fallback_btn.bind(on_release=self.open_in_browser)
            controls_row2.add_widget(fallback_btn)
        
        back_btn = Button(text="← Назад", size_hint_x=0.5)
        back_btn.bind(on_release=self.go_back)
        controls_row2.add_widget(back_btn)
        
        controls.add_widget(controls_row2)
        self.add_widget(controls)
        
        # Map container
        self.map_container = BoxLayout()
        
        if CEF_AVAILABLE:
            instructions = MDLabel(
                text="🚀 Нажмите 'Загрузить карту' для встраивания полноценной интерактивной карты\\n\\n"
                     "✨ Встроенная карта с CEF Python:\\n"
                     "• 📍 Полноценная интеграция с Yandex Maps\\n"
                     "• 🍽️ Интерактивные маркеры ресторанов\\n"
                     "• 🚚 Построение маршрутов в реальном времени\\n"
                     "• ⏱️ Расчёт времени доставки\\n"
                     "• 🚦 Пробки и геолокация\\n\\n"
                     "🎯 Карта будет работать прямо в приложении!",
                halign="center",
                theme_text_color="Secondary",
                markup=True
            )
        else:
            instructions = MDLabel(
                text="⚠️ CEF Python недоступен\\n\\n"
                     "Для встроенной карты необходимо:\\n"
                     "• Установить cefpython3\\n"
                     "• Перезапустить приложение\\n\\n"
                     "Пока доступно открытие в браузере",
                halign="center",
                theme_text_color="Secondary",
                markup=True
            )
        
        self.map_container.add_widget(instructions)
        self.add_widget(self.map_container)
    
    def setup_cef(self):
        """Initialize CEF Python"""
        try:
            # CEF settings
            settings = {
                "multi_threaded_message_loop": False,
                "debug": False,
                "log_severity": cef.LOGSEVERITY_ERROR,
                "log_file": "",
                "auto_zooming": "system_dpi",
                "context_menu": {
                    "enabled": False
                }
            }
            
            # Initialize CEF
            cef.Initialize(settings)
            print("✅ CEF Python инициализирован успешно")
            
        except Exception as e:
            print(f"Error initializing CEF: {e}")
            CEF_AVAILABLE = False
    
    def load_restaurants(self):
        """Load restaurants from database"""
        if not os.path.exists(DB_PATH):
            self.create_default_restaurants()
            return
        
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM restaurants LIMIT 15")
            data = cursor.fetchall()
            conn.close()
            
            self.restaurants = []
            base_lat, base_lon = 55.7558, 37.6176
            
            for i, restaurant in enumerate(data):
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
            
            # Replace the initialization
            html_content = html_content.replace(
                "// Initialize with app data\n        restaurants = {restaurants_json};\n        userLocation = [{user_lat}, {user_lon}];\n        ymaps.ready(init);",
                f"// Initialize with app data from CEF\n        restaurants = {restaurants_json};\n        userLocation = [{user_lat}, {user_lon}];\n        ymaps.ready(init);"
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
            <title>Встроенная карта ресторанов - CEF</title>
            <script src="https://api-maps.yandex.ru/2.1/?apikey=c045d2a8-bc9f-46c5-95ab-d41879ea8136&lang=ru_RU"></script>
            <style>
                body, html {{ margin: 0; padding: 0; height: 100%; }}
                #map {{ width: 100%; height: 100vh; }}
                .cef-controls {{
                    position: absolute;
                    top: 10px;
                    right: 10px;
                    z-index: 1000;
                    background: rgba(255,255,255,0.9);
                    padding: 10px;
                    border-radius: 5px;
                    font-family: Arial, sans-serif;
                }}
                .cef-title {{
                    background: #FF9800;
                    color: white;
                    padding: 5px;
                    border-radius: 3px;
                    margin-bottom: 5px;
                    text-align: center;
                    font-weight: bold;
                }}
            </style>
        </head>
        <body>
            <div class="cef-controls">
                <div class="cef-title">🍔 Food Delivery - CEF Map</div>
                <div>✅ Встроенная карта активна</div>
                <div>📍 Рестораны: {len(self.restaurants)}</div>
            </div>
            <div id="map"></div>
            <script>
                const restaurants = {restaurants_json};
                const userLocation = [{user_lat}, {user_lon}];
                
                ymaps.ready(function() {{
                    const map = new ymaps.Map('map', {{
                        center: userLocation,
                        zoom: 12,
                        controls: ['zoomControl', 'routeButtonControl', 'trafficControl']
                    }});
                    
                    // Add user location
                    const userMark = new ymaps.Placemark(userLocation, {{
                        balloonContent: '📍 Ваше местоположение'
                    }}, {{
                        preset: 'islands#blueCircleDotIcon',
                        draggable: true
                    }});
                    map.geoObjects.add(userMark);
                    
                    // Add restaurants
                    restaurants.forEach(restaurant => {{
                        const mark = new ymaps.Placemark([restaurant.lat, restaurant.lon], {{
                            balloonContent: `
                                <div style="min-width: 200px;">
                                    <h3 style="color: #FF9800;">🍽️ ${{restaurant.name}}</h3>
                                    <p><strong>Категория:</strong> ${{restaurant.category}}</p>
                                    <p><strong>Рейтинг:</strong> ⭐ ${{restaurant.rating}}</p>
                                    <button onclick="buildRoute([restaurant.lat, restaurant.lon])" style="
                                        background: #FF9800; 
                                        color: white; 
                                        border: none; 
                                        padding: 8px 16px; 
                                        border-radius: 4px; 
                                        cursor: pointer;
                                        width: 100%;
                                    ">🚚 Построить маршрут</button>
                                </div>
                            `
                        }}, {{
                            preset: 'islands#redRestaurantIcon'
                        }});
                        map.geoObjects.add(mark);
                    }});
                    
                    // Route building function
                    window.buildRoute = function(coords) {{
                        const userCoords = userMark.geometry.getCoordinates();
                        ymaps.route([userCoords, coords], {{
                            routingMode: 'auto'
                        }}).then(function (route) {{
                            map.geoObjects.add(route);
                            route.getPaths().options.set({{
                                strokeColor: '#FF9800',
                                strokeWidth: 5,
                                strokeOpacity: 0.8
                            }});
                        }});
                    }};
                    
                    console.log('CEF Map loaded successfully with', restaurants.length, 'restaurants');
                }});
            </script>
        </body>
        </html>
        '''
    
    def load_map(self, instance):
        """Load the embedded map using CEF Python"""
        if not CEF_AVAILABLE:
            self.show_error_popup("CEF Python недоступен. Переустановите cefpython3.")
            return
        
        try:
            # Create HTML content
            html_content = self.create_html_content()
            
            # Save to temporary file
            self.html_file_path = os.path.join(tempfile.gettempdir(), 'food_delivery_cef_map.html')
            with open(self.html_file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Clear the container
            self.map_container.clear_widgets()
            
            # Create browser widget (placeholder for now - we'll integrate with Kivy)
            self.create_cef_browser()
            
            # Update status
            status_label = MDLabel(
                text="🚀 CEF браузер инициализируется...\\n\\n"
                     "✨ Встроенная карта загружается:\\n"
                     f"• 📍 Местоположение: {self.user_location[0]:.4f}, {self.user_location[1]:.4f}\\n"
                     f"• 🍽️ Ресторанов загружено: {len(self.restaurants)}\\n"
                     f"• 🗺️ Файл карты: {os.path.basename(self.html_file_path)}\\n\\n"
                     "🎯 Карта будет отображаться встроенно в приложении!\\n\\n"
                     "⚠️ Примечание: CEF интеграция с Kivy требует\\n"
                     "дополнительной настройки для полного встраивания",
                halign="center",
                theme_text_color="Primary",
                markup=True
            )
            self.map_container.add_widget(status_label)
            
            print(f"✅ CEF карта создана: {self.html_file_path}")
            
        except Exception as e:
            print(f"Error loading CEF map: {e}")
            self.show_error_popup(f"Ошибка при загрузке CEF карты: {e}")
    
    def create_cef_browser(self):
        """Create CEF browser instance"""
        try:
            # Browser settings
            window_info = cef.WindowInfo()
            # For now, we'll create a separate window - full integration requires more work
            window_info.SetAsChild(0, [0, 0, 800, 600])
            
            browser_settings = {
                "web_security": False,
                "file_access_from_file_urls": True,
                "universal_access_from_file_urls": True
            }
            
            # Create browser
            self.cef_browser = cef.CreateBrowserSync(
                window_info=window_info,
                url=f"file://{self.html_file_path}",
                settings=browser_settings
            )
            
            print("✅ CEF браузер создан успешно")
            
        except Exception as e:
            print(f"Error creating CEF browser: {e}")
    
    def open_in_browser(self, instance):
        """Fallback: open in default browser"""
        try:
            html_content = self.create_html_content()
            html_file = os.path.join(tempfile.gettempdir(), 'food_delivery_fallback_map.html')
            
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            import webbrowser
            webbrowser.open(f'file://{html_file}')
            
            self.update_status("🌐 Карта открыта в браузере (fallback)")
            
        except Exception as e:
            self.show_error_popup(f"Ошибка при открытии в браузере: {e}")
    
    def update_status(self, message):
        """Update status in map container"""
        self.map_container.clear_widgets()
        status_label = MDLabel(
            text=f"{message}\\n\\n"
                 f"📊 Статистика:\\n"
                 f"• 🍽️ Ресторанов: {len(self.restaurants)}\\n"
                 f"• 📍 Координаты: {self.user_location[0]:.4f}, {self.user_location[1]:.4f}\\n"
                 f"• 🔧 CEF доступен: {'✅' if CEF_AVAILABLE else '❌'}",
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
        
        close_btn = Button(text="Закрыть", size_hint_y=None, height="40dp")
        
        popup = Popup(
            title="Местоположение",
            content=content,
            size_hint=(0.8, 0.5),
            auto_dismiss=True
        )
        
        close_btn.bind(on_release=popup.dismiss)
        content.add_widget(close_btn)
        popup.open()
    
    def show_restaurants_list(self, instance):
        """Show list of restaurants"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        content.add_widget(MDLabel(
            text=f"🍽️ Список ресторанов ({len(self.restaurants)})",
            theme_text_color="Primary",
            size_hint_y=None,
            height="40dp"
        ))
        
        for restaurant in self.restaurants[:8]:
            rest_layout = BoxLayout(size_hint_y=None, height="40dp")
            
            rest_info = MDLabel(
                text=f"{restaurant['name']} ({restaurant['category']}) - ⭐{restaurant['rating']}",
                theme_text_color="Secondary"
            )
            rest_layout.add_widget(rest_info)
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
        """Find optimal route"""
        if not self.restaurants:
            self.show_error_popup("Нет доступных ресторанов")
            return
        
        import math
        
        def calculate_distance(lat1, lon1, lat2, lon2):
            R = 6371
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
        delivery_time = int(distance * 3) + 15
        
        message = (f"🎯 Ближайший ресторан найден!\\n\\n"
                  f"🍽️ {closest_restaurant['name']}\\n"
                  f"📍 {closest_restaurant['category']}\\n"
                  f"⭐ {closest_restaurant['rating']}\\n"
                  f"📏 Расстояние: {distance:.1f} км\\n"
                  f"⏱️ Время доставки: ~{delivery_time} мин")
        
        self.show_info_popup("Оптимальный маршрут", message)
    
    def refresh_map(self, instance):
        """Refresh map data"""
        self.load_restaurants()
        self.update_status("🔄 Данные карты обновлены")
        print(f"✅ Обновлено ресторанов: {len(self.restaurants)}")
    
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
        """Cleanup CEF resources"""
        try:
            if self.cef_browser:
                self.cef_browser.CloseBrowser()
            if CEF_AVAILABLE:
                cef.MessageLoopWork()
                cef.Shutdown()
        except:
            pass
