import tkinter as tk
from tkinter import ttk, messagebox
import tkinterweb
import json
import os
import tempfile
import sqlite3
import threading
import random

DB_PATH = "data/database.db"


class FoodDeliveryTkinterApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🍔 Food Delivery - Встроенная карта")
        self.root.geometry("1200x800")
        self.root.configure(bg='white')
        
        self.restaurants = []
        self.user_location = [55.7558, 37.6176]  # Moscow center
        self.web_frame = None
        
        self.setup_ui()
        self.load_restaurants()
        
    def setup_ui(self):
        """Setup the main UI"""
        # Title frame
        title_frame = tk.Frame(self.root, bg='#FF9800', height=60)
        title_frame.pack(fill=tk.X, padx=5, pady=5)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame, 
            text="🍔 Food Delivery - Интерактивная карта встроена в приложение!",
            font=("Arial", 16, "bold"),
            fg="white",
            bg="#FF9800"
        )
        title_label.pack(expand=True)
        
        # Main container
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel for controls
        left_panel = tk.Frame(main_frame, width=250, bg='lightgray')
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        left_panel.pack_propagate(False)
        
        # Controls in left panel
        controls_label = tk.Label(left_panel, text="🎮 Управление", font=("Arial", 14, "bold"), bg='lightgray')
        controls_label.pack(pady=10)
        
        # Location controls
        location_frame = tk.LabelFrame(left_panel, text="📍 Местоположение", bg='lightgray')
        location_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(
            location_frame, 
            text="🎯 Центр Москвы", 
            command=self.set_moscow_center,
            bg='lightblue',
            width=20
        ).pack(pady=2)
        
        tk.Button(
            location_frame, 
            text="🔄 Обновить координаты", 
            command=self.update_location,
            bg='lightgreen',
            width=20
        ).pack(pady=2)
        
        # Restaurants controls
        restaurants_frame = tk.LabelFrame(left_panel, text="🍽️ Рестораны", bg='lightgray')
        restaurants_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(
            restaurants_frame, 
            text="📋 Показать список", 
            command=self.show_restaurants_list,
            bg='lightyellow',
            width=20
        ).pack(pady=2)
        
        tk.Button(
            restaurants_frame, 
            text="🎯 Ближайший", 
            command=self.find_nearest_restaurant,
            bg='lightcoral',
            width=20
        ).pack(pady=2)
        
        # Map controls
        map_frame = tk.LabelFrame(left_panel, text="🗺️ Карта", bg='lightgray')
        map_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(
            map_frame, 
            text="🚀 Загрузить карту", 
            command=self.load_embedded_map,
            bg='orange',
            fg='white',
            width=20,
            font=("Arial", 10, "bold")
        ).pack(pady=2)
        
        tk.Button(
            map_frame, 
            text="🔄 Обновить карту", 
            command=self.refresh_map,
            bg='lightsteelblue',
            width=20
        ).pack(pady=2)
        
        # Statistics
        stats_frame = tk.LabelFrame(left_panel, text="📊 Статистика", bg='lightgray')
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.stats_label = tk.Label(
            stats_frame,
            text="🍽️ Ресторанов: 0\n📍 Координаты: N/A",
            bg='lightgray',
            justify=tk.LEFT
        )
        self.stats_label.pack(pady=5)
        
        # Right panel for the map
        self.map_panel = tk.Frame(main_frame, bg='white', relief=tk.SUNKEN, borderwidth=2)
        self.map_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Initial instructions
        self.show_instructions()
        
        # Status bar
        self.status_bar = tk.Label(
            self.root, 
            text="✅ Приложение запущено. Нажмите 'Загрузить карту' для встраивания интерактивной карты.",
            relief=tk.SUNKEN,
            anchor=tk.W,
            bg='lightgray'
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def show_instructions(self):
        """Show initial instructions"""
        instructions_text = (
            "🗺️ ВСТРОЕННАЯ ИНТЕРАКТИВНАЯ КАРТА\n\n"
            "✨ Возможности:\n"
            "• 📍 Полноценная Yandex Maps API\n"
            "• 🍽️ Интерактивные маркеры ресторанов\n"
            "• 🚚 Построение маршрутов в реальном времени\n"
            "• ⏱️ Расчёт времени доставки\n"
            "• 🚐 Пробки и геолокация\n"
            "• 🎯 Полное управление картой\n\n"
            "🚀 Нажмите 'Загрузить карту' для встраивания!\n\n"
            "💡 Карта будет работать прямо в этом окне\n"
            "без открытия браузера!"
        )
        instructions_label = tk.Label(
            self.map_panel,
            text=instructions_text,
            font=("Arial", 12),
            justify=tk.CENTER,
            bg='white',
            fg='darkblue'
        )
        instructions_label.pack(expand=True)
    
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
                lat = base_lat + random.uniform(-0.05, 0.05)
                lon = base_lon + random.uniform(-0.06, 0.06)
                
                self.restaurants.append({
                    'id': restaurant[0],
                    'name': restaurant[1],
                    'category': restaurant[2],
                    'rating': restaurant[3],
                    'distance': restaurant[4] if len(restaurant) > 4 else f"{random.uniform(0.5, 3.0):.1f} км",
                    'lat': lat,
                    'lon': lon
                })
                
        except Exception as e:
            print(f"Error loading restaurants: {e}")
            self.create_default_restaurants()
        
        self.update_stats()
    
    def create_default_restaurants(self):
        """Create default restaurants for demonstration"""
        base_lat, base_lon = 55.7558, 37.6176
        
        default_restaurants = [
            {"name": "Пицца Маргарита", "category": "Пицца", "rating": 4.5},
            {"name": "Суши Токио", "category": "Суши", "rating": 4.7},
            {"name": "Бургер Кинг", "category": "Фаст-фуд", "rating": 4.2},
            {"name": "Паста Италия", "category": "Итальянская", "rating": 4.6},
            {"name": "Шаурма Экспресс", "category": "Восточная", "rating": 4.1},
            {"name": "Стейк-хаус", "category": "Мясные блюда", "rating": 4.8},
            {"name": "Вегетарианский рай", "category": "Здоровая еда", "rating": 4.4},
            {"name": "Китайский дракон", "category": "Китайская", "rating": 4.3}
        ]
        
        self.restaurants = []
        for i, rest_data in enumerate(default_restaurants):
            lat = base_lat + random.uniform(-0.04, 0.04)
            lon = base_lon + random.uniform(-0.05, 0.05)
            
            self.restaurants.append({
                'id': i + 1,
                'name': rest_data['name'],
                'category': rest_data['category'],
                'rating': rest_data['rating'],
                'distance': f"{random.uniform(0.5, 3.0):.1f} км",
                'lat': lat,
                'lon': lon
            })
        
        self.update_stats()
    
    def update_stats(self):
        """Update statistics display"""
        coords_text = f"{self.user_location[0]:.4f}, {self.user_location[1]:.4f}"
        self.stats_label.config(
            text=f"🍽️ Ресторанов: {len(self.restaurants)}\n📍 Координаты: {coords_text}"
        )
    
    def create_map_html(self):
        """Create HTML content for the embedded map"""
        restaurants_json = json.dumps(self.restaurants)
        user_lat, user_lon = self.user_location
        
        html_content = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Встроенная карта - Tkinter</title>
            <script src="https://api-maps.yandex.ru/2.1/?apikey=c045d2a8-bc9f-46c5-95ab-d41879ea8136&lang=ru_RU"></script>
            <style>
                body, html {{ 
                    margin: 0; 
                    padding: 0; 
                    height: 100%; 
                    font-family: Arial, sans-serif;
                    background: #f0f0f0;
                }}
                #map {{ 
                    width: 100%; 
                    height: 100vh; 
                }}
                .tkinter-header {{
                    position: absolute;
                    top: 10px;
                    left: 50%;
                    transform: translateX(-50%);
                    z-index: 1000;
                    background: linear-gradient(135deg, #FF9800, #FF5722);
                    color: white;
                    padding: 10px 20px;
                    border-radius: 20px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                    font-weight: bold;
                    text-align: center;
                }}
                .tkinter-controls {{
                    position: absolute;
                    top: 10px;
                    right: 10px;
                    z-index: 1000;
                    background: rgba(255,255,255,0.95);
                    padding: 15px;
                    border-radius: 10px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                    max-width: 250px;
                }}
                .control-btn {{
                    display: block;
                    width: 100%;
                    margin: 5px 0;
                    padding: 8px 12px;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                    font-size: 12px;
                    transition: all 0.3s ease;
                }}
                .primary-btn {{ background: #FF9800; color: white; }}
                .secondary-btn {{ background: #f0f0f0; color: #333; }}
                .control-btn:hover {{ transform: translateY(-1px); box-shadow: 0 2px 4px rgba(0,0,0,0.2); }}
                .info-panel {{
                    position: absolute;
                    bottom: 10px;
                    left: 10px;
                    z-index: 1000;
                    background: white;
                    padding: 15px;
                    border-radius: 10px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                    max-width: 350px;
                    display: none;
                }}
                .delivery-time {{
                    font-size: 16px;
                    font-weight: bold;
                    color: #FF9800;
                    margin-bottom: 5px;
                }}
            </style>
        </head>
        <body>
            <div class="tkinter-header">
                🍔 Food Delivery - Встроенная карта в Tkinter
            </div>
            
            <div class="tkinter-controls">
                <div style="font-weight: bold; margin-bottom: 10px; color: #FF9800;">🎮 Управление картой</div>
                <button class="control-btn primary-btn" onclick="getCurrentLocation()">📍 Моё местоположение</button>
                <button class="control-btn secondary-btn" onclick="showAllRestaurants()">🍽️ Показать все</button>
                <button class="control-btn secondary-btn" onclick="calculateOptimalRoute()">🚚 Ближайший</button>
                <button class="control-btn secondary-btn" onclick="toggleTraffic()">🚦 Пробки</button>
                <button class="control-btn secondary-btn" onclick="clearRoutes()">🗑️ Очистить</button>
            </div>
            
            <div class="info-panel" id="infoPanel">
                <button style="position: absolute; top: 5px; right: 5px; background: #ff4444; color: white; border: none; border-radius: 3px; cursor: pointer; width: 20px; height: 20px; font-size: 12px;" onclick="closeInfoPanel()">×</button>
                <div class="delivery-time" id="deliveryTime">⏱️ Время доставки: расчёт...</div>
                <div id="routeInfo">Выберите ресторан для расчёта маршрута</div>
            </div>
            
            <div id="map"></div>
            
            <script>
                let map, userMark, currentRoute, trafficControl;
                const restaurants = {restaurants_json};
                let userLocation = [{user_lat}, {user_lon}];
                let selectedRestaurant = null;
                
                ymaps.ready(init);
                
                function init() {{
                    map = new ymaps.Map('map', {{
                        center: userLocation,
                        zoom: 12,
                        controls: ['zoomControl', 'fullscreenControl']
                    }});
                    
                    trafficControl = new ymaps.control.TrafficControl();
                    map.controls.add(trafficControl);
                    
                    addUserLocation();
                    addRestaurants();
                    setTimeout(calculateAllDeliveryTimes, 1000);
                    
                    console.log('🎯 Tkinter embedded map loaded with', restaurants.length, 'restaurants');
                }}
                
                function addUserLocation() {{
                    userMark = new ymaps.Placemark(userLocation, {{
                        balloonContent: '📍 Ваше местоположение'
                    }}, {{
                        preset: 'islands#blueCircleDotIcon',
                        draggable: true
                    }});
                    
                    userMark.events.add('dragend', function() {{
                        const coords = userMark.geometry.getCoordinates();
                        userLocation = [coords[0], coords[1]];
                        calculateAllDeliveryTimes();
                    }});
                    
                    map.geoObjects.add(userMark);
                }}
                
                function addRestaurants() {{
                    restaurants.forEach(restaurant => {{
                        const mark = new ymaps.Placemark([restaurant.lat, restaurant.lon], {{
                            balloonContent: `
                                <div style="min-width: 220px;">
                                    <h3 style="margin: 0 0 10px 0; color: #FF9800;">🍽️ ${{restaurant.name}}</h3>
                                    <p style="margin: 5px 0;"><strong>Категория:</strong> ${{restaurant.category}}</p>
                                    <p style="margin: 5px 0;"><strong>Рейтинг:</strong> ⭐ ${{restaurant.rating}}</p>
                                    <div id="delivery-${{restaurant.id}}" style="margin: 10px 0; padding: 8px; background: #f0f8ff; border-radius: 4px;">Расчёт времени доставки...</div>
                                    <button onclick="buildRoute(${{restaurant.lat}}, ${{restaurant.lon}}, '${{restaurant.name}}', ${{restaurant.id}})" 
                                            style="background: linear-gradient(135deg, #FF9800, #FF5722); color: white; border: none; padding: 10px 16px; border-radius: 6px; cursor: pointer; width: 100%; font-weight: bold;">
                                        🚚 Заказать доставку
                                    </button>
                                </div>
                            `
                        }}, {{
                            preset: 'islands#redRestaurantIcon'
                        }});
                        map.geoObjects.add(mark);
                    }});
                }}
                
                function calculateAllDeliveryTimes() {{
                    restaurants.forEach(restaurant => {{
                        calculateDeliveryTime(restaurant);
                    }});
                }}
                
                function calculateDeliveryTime(restaurant) {{
                    const userCoords = userMark.geometry.getCoordinates();
                    const distance = getDirectDistance(userCoords, [restaurant.lat, restaurant.lon]);
                    const estimatedTime = Math.round(distance * 3) + 15;
                    
                    const deliveryElement = document.getElementById(`delivery-${{restaurant.id}}`);
                    if (deliveryElement) {{
                        deliveryElement.innerHTML = `
                            <div style="text-align: center;">
                                <div style="font-weight: bold; color: #FF9800;">⏱️ ${{estimatedTime}} мин</div>
                                <div style="font-size: 12px; color: #666;">📏 ${{distance.toFixed(1)}} км</div>
                            </div>
                        `;
                    }}
                }}
                
                function buildRoute(restLat, restLon, restName, restId) {{
                    const userCoords = userMark.geometry.getCoordinates();
                    
                    if (currentRoute) {{
                        map.geoObjects.remove(currentRoute);
                    }}
                    
                    ymaps.route([userCoords, [restLat, restLon]], {{
                        routingMode: 'auto'
                    }}).then(function (route) {{
                        currentRoute = route;
                        map.geoObjects.add(route);
                        
                        route.getPaths().options.set({{
                            strokeColor: '#FF9800',
                            strokeWidth: 6,
                            strokeOpacity: 0.9
                        }});
                        
                        const distance = route.getLength();
                        const duration = route.getJamesTime() || route.getTime();
                        const totalTime = Math.round(duration / 60) + 15;
                        
                        updateInfoPanel(restName, totalTime, distance);
                        map.setBounds(route.getBounds());
                        
                    }}).catch(function(error) {{
                        console.error('Ошибка построения маршрута:', error);
                        alert('Не удалось построить маршрут. Проверьте подключение к интернету.');
                    }});
                }}
                
                function updateInfoPanel(restName, totalTime, distance) {{
                    document.getElementById('deliveryTime').textContent = `⏱️ Время доставки: ${{totalTime}} мин`;
                    document.getElementById('routeInfo').innerHTML = `
                        <div style="margin-top: 10px;">
                            <div style="font-weight: bold;">🍽️ ${{restName}}</div>
                            <div>📏 Расстояние: ${{Math.round(distance/1000*100)/100}} км</div>
                            <div style="margin-top: 8px; padding: 8px; background: linear-gradient(135deg, #e8f5e8, #d4edd4); border-radius: 4px; text-align: center;">
                                <div style="color: #FF9800; font-weight: bold;">🎯 Маршрут построен!</div>
                                <div style="font-size: 11px; color: #666; margin-top: 3px;">Курьер уже готовится к выезду</div>
                            </div>
                        </div>
                    `;
                    document.getElementById('infoPanel').style.display = 'block';
                }}
                
                function closeInfoPanel() {{
                    document.getElementById('infoPanel').style.display = 'none';
                    if (currentRoute) {{
                        map.geoObjects.remove(currentRoute);
                        currentRoute = null;
                    }}
                }}
                
                function clearRoutes() {{
                    if (currentRoute) {{
                        map.geoObjects.remove(currentRoute);
                        currentRoute = null;
                    }}
                    closeInfoPanel();
                }}
                
                function getCurrentLocation() {{
                    if (navigator.geolocation) {{
                        navigator.geolocation.getCurrentPosition(function(position) {{
                            const coords = [position.coords.latitude, position.coords.longitude];
                            map.setCenter(coords, 15);
                            userMark.geometry.setCoordinates(coords);
                            userLocation = coords;
                            calculateAllDeliveryTimes();
                        }}, function(error) {{
                            console.error('Ошибка геолокации:', error);
                            alert('Не удалось определить местоположение');
                        }});
                    }} else {{
                        alert('Геолокация не поддерживается браузером');
                    }}
                }}
                
                function showAllRestaurants() {{
                    if (restaurants.length === 0) return;
                    
                    const bounds = restaurants.map(r => [r.lat, r.lon]);
                    bounds.push(userMark.geometry.getCoordinates());
                    map.setBounds(bounds, {{ checkZoomRange: true }});
                }}
                
                function calculateOptimalRoute() {{
                    if (restaurants.length === 0) return;
                    
                    const userCoords = userMark.geometry.getCoordinates();
                    let closestRestaurant = restaurants[0];
                    let minDistance = getDirectDistance(userCoords, [closestRestaurant.lat, closestRestaurant.lon]);
                    
                    restaurants.forEach(restaurant => {{
                        const distance = getDirectDistance(userCoords, [restaurant.lat, restaurant.lon]);
                        if (distance < minDistance) {{
                            minDistance = distance;
                            closestRestaurant = restaurant;
                        }}
                    }});
                    
                    buildRoute(closestRestaurant.lat, closestRestaurant.lon, closestRestaurant.name, closestRestaurant.id);
                }}
                
                function toggleTraffic() {{
                    const isShown = trafficControl.state.get('trafficShown');
                    trafficControl.state.set('trafficShown', !isShown);
                }}
                
                function getDirectDistance(coords1, coords2) {{
                    const R = 6371;
                    const dLat = (coords2[0] - coords1[0]) * Math.PI / 180;
                    const dLon = (coords2[1] - coords1[1]) * Math.PI / 180;
                    const a = Math.sin(dLat/2) * Math.sin(dLat/2) + 
                             Math.cos(coords1[0] * Math.PI / 180) * Math.cos(coords2[0] * Math.PI / 180) * 
                             Math.sin(dLon/2) * Math.sin(dLon/2);
                    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
                    return R * c;
                }}
            </script>
        </body>
        </html>
        '''
        return html_content
    
    def load_embedded_map(self):
        """Load the embedded map using tkinterweb"""
        try:
            # Clear the map panel
            for widget in self.map_panel.winfo_children():
                widget.destroy()
            
            # Create HTML content
            html_content = self.create_map_html()
            
            # Save HTML to temporary file
            html_file = os.path.join(tempfile.gettempdir(), 'tkinter_food_delivery_map.html')
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Create tkinterweb HtmlFrame
            self.web_frame = tkinterweb.HtmlFrame(
                self.map_panel,
                messages_enabled=False
            )
            self.web_frame.pack(fill=tk.BOTH, expand=True)
            
            # Load the HTML file
            self.web_frame.load_file(html_file)
            
            self.status_bar.config(text=f"🚀 Встроенная карта загружена! Ресторанов: {len(self.restaurants)}")
            print(f"✅ Tkinter embedded map loaded: {html_file}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при загрузке встроенной карты: {e}")
            print(f"Error loading embedded map: {e}")
    
    def refresh_map(self):
        """Refresh the map"""
        if self.web_frame:
            self.load_embedded_map()
        self.status_bar.config(text="🔄 Карта обновлена")
    
    def set_moscow_center(self):
        """Set user location to Moscow center"""
        self.user_location = [55.7558, 37.6176]
        self.update_stats()
        self.status_bar.config(text="📍 Местоположение установлено: Центр Москвы")
    
    def update_location(self):
        """Update user location randomly around Moscow"""
        base_lat, base_lon = 55.7558, 37.6176
        self.user_location = [
            base_lat + random.uniform(-0.1, 0.1),
            base_lon + random.uniform(-0.1, 0.1)
        ]
        self.update_stats()
        coords_text = f"{self.user_location[0]:.4f}, {self.user_location[1]:.4f}"
        self.status_bar.config(text=f"📍 Координаты обновлены: {coords_text}")
    
    def show_restaurants_list(self):
        """Show restaurants list in a popup"""
        list_window = tk.Toplevel(self.root)
        list_window.title("🍽️ Список ресторанов")
        list_window.geometry("500x400")
        
        # Create scrollable frame
        canvas = tk.Canvas(list_window)
        scrollbar = ttk.Scrollbar(list_window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Add restaurants to the list
        for i, restaurant in enumerate(self.restaurants):
            restaurant_frame = tk.Frame(scrollable_frame, relief=tk.RIDGE, borderwidth=1, bg='lightyellow')
            restaurant_frame.pack(fill=tk.X, padx=5, pady=2)
            
            info_text = f"🍽️ {restaurant['name']} ({restaurant['category']}) - ⭐{restaurant['rating']}"
            tk.Label(restaurant_frame, text=info_text, bg='lightyellow', anchor='w').pack(fill=tk.X, padx=5, pady=2)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def find_nearest_restaurant(self):
        """Find and show the nearest restaurant"""
        if not self.restaurants:
            messagebox.showinfo("Информация", "Нет доступных ресторанов")
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
        
        message = (f"🎯 Ближайший ресторан найден!\n\n"
                  f"🍽️ {closest_restaurant['name']}\n"
                  f"📍 {closest_restaurant['category']}\n"
                  f"⭐ {closest_restaurant['rating']}\n"
                  f"📏 Расстояние: {distance:.1f} км\n"
                  f"⏱️ Время доставки: ~{delivery_time} мин")
        
        messagebox.showinfo("Ближайший ресторан", message)
    
    def run(self):
        """Run the application"""
        print("🚀 Launching Tkinter Food Delivery App with embedded map...")
        self.root.mainloop()


if __name__ == "__main__":
    app = FoodDeliveryTkinterApp()
    app.run()
