import requests
import json
import random
import base64
import tempfile
import os
import webbrowser
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivy.core.image import Image as CoreImage
from io import BytesIO
from PIL import Image as PILImage, ImageDraw, ImageFont
import threading
import time
from kivy.clock import Clock

# Optional GPS import
try:
    from plyer import gps
    GPS_AVAILABLE = True
except ImportError:
    GPS_AVAILABLE = False


class YandexMapWidget:
    def __init__(self, api_key="c045d2a8-bc9f-46c5-95ab-d41879ea8136"):
        self.api_key = api_key
        self.static_maps_url = "https://static-maps.yandex.ru/1.x/"
        self.geocoder_url = "https://geocode-maps.yandex.ru/1.x/"
        self.router_url = "https://api.routing.yandex.net/v2/route"
        
    def get_static_map(self, lat, lon, zoom=13, width=400, height=300, markers=None):
        """Generate static map URL with markers"""
        try:
            params = {
                'l': 'map',
                'll': f"{lon},{lat}",
                'z': zoom,
                'size': f"{width},{height}",
                'lang': 'ru_RU'
            }
            
            if markers:
                # Format: pt=lon,lat,color+style
                pt_params = []
                for marker in markers:
                    m_lon, m_lat = marker.get('lon'), marker.get('lat')
                    color = marker.get('color', 'red')
                    style = marker.get('style', 'pm2')
                    pt_params.append(f"{m_lon},{m_lat},{color}{style}")
                params['pt'] = '~'.join(pt_params)
            
            # Only add API key if it exists and is not default
            if self.api_key and self.api_key != "your_api_key_here":
                params['apikey'] = self.api_key
                
            url = self.static_maps_url + '&'.join([f"{k}={v}" for k, v in params.items()])
            
            # Test if URL is accessible
            import urllib.request
            try:
                with urllib.request.urlopen(url, timeout=5) as response:
                    if response.getcode() == 200:
                        return url
            except:
                pass
                
            # Return fallback placeholder image URL if API fails
            return self._get_fallback_map_url(width, height)
            
        except Exception as e:
            print(f"Error generating map URL: {e}")
            return self._get_fallback_map_url(width, height)
        
    def _get_fallback_map_url(self, width=400, height=300):
        """Generate a fallback placeholder image when maps are not available"""
        return self._create_placeholder_image(width, height)
        
    def _create_placeholder_image(self, width=400, height=300):
        """Create a placeholder map image"""
        try:
            # Create a simple map-like placeholder using PIL
            img = PILImage.new('RGB', (width, height), color='#E8F5E8')
            draw = ImageDraw.Draw(img)
            
            # Draw some map-like elements
            # Draw streets
            for i in range(5):
                y = height // 6 * (i + 1)
                draw.line([(0, y), (width, y)], fill='#CCCCCC', width=2)
                
            for i in range(5):
                x = width // 6 * (i + 1)
                draw.line([(x, 0), (x, height)], fill='#CCCCCC', width=2)
            
            # Draw some buildings
            for _ in range(8):
                x = random.randint(10, width-40)
                y = random.randint(10, height-40)
                w = random.randint(20, 30)
                h = random.randint(20, 30)
                draw.rectangle([x, y, x+w, y+h], fill='#DDDDDD', outline='#AAAAAA')
            
            # Draw restaurant markers
            for _ in range(3):
                x = random.randint(20, width-20)
                y = random.randint(20, height-20)
                draw.ellipse([x-8, y-8, x+8, y+8], fill='#FF4444', outline='#CC0000')
            
            # Add text
            try:
                # Try to use a simple font, fallback to default if not available
                font = ImageFont.load_default()
                text = "Карта ресторанов"
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                draw.text(((width-text_width)//2, height-text_height-10), text, 
                         fill='#666666', font=font)
            except:
                pass
            
            # Convert to base64 data URL
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            img_data = buffer.getvalue()
            buffer.close()
            
            # Create data URL
            img_base64 = base64.b64encode(img_data).decode('utf-8')
            return f"data:image/png;base64,{img_base64}"
            
        except Exception as e:
            print(f"Error creating placeholder image: {e}")
            # Return a simple colored rectangle as ultimate fallback
            return "data:image/svg+xml;base64," + base64.b64encode(
                f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">'
                f'<rect width="{width}" height="{height}" fill="#E8F5E8"/>'
                f'<text x="{width//2}" y="{height//2}" text-anchor="middle" fill="#666">Карта</text>'
                f'</svg>'.encode('utf-8')
            ).decode('utf-8')
        
    def get_route_map(self, start_coords, end_coords, zoom=14, width=400, height=300):
        """Get static map with route between two points"""
        try:
            start_lon, start_lat = start_coords
            end_lon, end_lat = end_coords
            
            # Center map between start and end points
            center_lat = (start_lat + end_lat) / 2
            center_lon = (start_lon + end_lon) / 2
            
            markers = [
                {'lat': start_lat, 'lon': start_lon, 'color': 'blue', 'style': 'pm2'},
                {'lat': end_lat, 'lon': end_lon, 'color': 'red', 'style': 'pm2'}
            ]
            
            return self.get_static_map(center_lat, center_lon, zoom, width, height, markers)
        except Exception as e:
            print(f"Error generating route map: {e}")
            return self._get_fallback_map_url(width, height)
        
    def get_route_instructions(self, start_coords, end_coords):
        """Get route instructions between two points"""
        try:
            start_lon, start_lat = start_coords
            end_lon, end_lat = end_coords
            
            params = {
                'waypoints': f"{start_lon},{start_lat}|{end_lon},{end_lat}",
                'mode': 'pedestrian',
                'apikey': self.api_key,
                'format': 'json'
            }
            
            response = requests.get(self.router_url, params=params, timeout=10)
            if response.status_code == 200:
                route_data = response.json()
                return self._extract_instructions(route_data)
        except Exception as e:
            print(f"Error getting route: {e}")
            
        return self._get_mock_instructions()
    
    def _extract_instructions(self, route_data):
        """Extract turn-by-turn instructions from Yandex route response"""
        instructions = []
        try:
            if 'route' in route_data and 'legs' in route_data['route']:
                for leg in route_data['route']['legs']:
                    if 'steps' in leg:
                        for step in leg['steps']:
                            if 'instruction' in step:
                                instructions.append(step['instruction'])
                            elif 'maneuver' in step:
                                instructions.append(step['maneuver'].get('instruction', 'Продолжайте движение'))
        except:
            pass
            
        if not instructions:
            return self._get_mock_instructions()
            
        return instructions[:5]  # Limit to 5 instructions
    
    def _get_mock_instructions(self):
        """Fallback mock route instructions"""
        return [
            "Выйдите из здания и поверните направо",
            f"Идите прямо {random.randint(100, 400)} метров",
            "Поверните налево на перекрестке", 
            f"Пройдите еще {random.randint(50, 200)} метров",
            "Вы прибыли к месту назначения"
        ]
        
    def geocode_address(self, address):
        """Get coordinates for an address"""
        try:
            params = {
                'geocode': address,
                'apikey': self.api_key,
                'format': 'json',
                'results': 1
            }
            
            response = requests.get(self.geocoder_url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                try:
                    coords = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
                    lon, lat = map(float, coords.split())
                    return lat, lon
                except:
                    pass
        except Exception as e:
            print(f"Geocoding error: {e}")
            
        # Return Moscow center as fallback
        return 55.7558, 37.6176


def generate_restaurant_coordinates(base_lat=55.7558, base_lon=37.6176, count=5):
    """Generate random coordinates around a base location for restaurants"""
    coordinates = []
    for i in range(count):
        # Generate coordinates within ~2km radius
        lat_offset = random.uniform(-0.015, 0.015)
        lon_offset = random.uniform(-0.02, 0.02)
        coordinates.append({
            'lat': base_lat + lat_offset,
            'lon': base_lon + lon_offset
        })
    return coordinates


class YandexMapsWebView(BoxLayout):
    """Enhanced Yandex Maps integration with embedded browser capabilities"""
    
    def __init__(self, app=None, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        self.app = app
        self.api_key = "c045d2a8-bc9f-46c5-95ab-d41879ea8136"
        self.restaurants = []
        self.user_location = [55.7558, 37.6176]  # Moscow center
        self.current_html_file = None
        
        # Create control panel
        self.create_controls()
        
        # Create map container
        self.create_map_container()
        
        # Load initial map
        self.load_map()
    
    def create_controls(self):
        """Create control buttons for map interactions"""
        controls = BoxLayout(size_hint_y=None, height="60dp", spacing=5, padding=5)
        
        location_btn = Button(
            text="🌐 Браузер",
            size_hint_x=0.3,
            size_hint_y=None,
            height="50dp"
        )
        location_btn.bind(on_release=self.open_in_browser)
        controls.add_widget(location_btn)
        
        restaurants_btn = Button(
            text="🍽️ Рестораны",
            size_hint_x=0.35,
            size_hint_y=None,
            height="50dp"
        )
        restaurants_btn.bind(on_release=self.show_restaurants)
        controls.add_widget(restaurants_btn)
        
        route_btn = Button(
            text="🗺️ Маршрут",
            size_hint_x=0.35,
            size_hint_y=None,
            height="50dp"
        )
        route_btn.bind(on_release=self.calculate_delivery_route)
        controls.add_widget(route_btn)
        
        self.add_widget(controls)
    
    def create_map_container(self):
        """Create container for map display"""
        # Map info panel
        self.info_panel = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height="100dp",
            padding=5
        )
        
        self.location_label = MDLabel(
            text="📍 Местоположение: Москва (центр)",
            theme_text_color="Primary",
            size_hint_y=None,
            height="30dp"
        )
        self.info_panel.add_widget(self.location_label)
        
        self.delivery_info = MDLabel(
            text="🚚 Время доставки: Выберите ресторан",
            theme_text_color="Secondary",
            size_hint_y=None,
            height="30dp"
        )
        self.info_panel.add_widget(self.delivery_info)
        
        self.route_info = MDLabel(
            text="🗺️ Нажмите 'Браузер' для интерактивной карты",
            theme_text_color="Secondary",
            size_hint_y=None,
            height="30dp"
        )
        self.info_panel.add_widget(self.route_info)
        
        self.add_widget(self.info_panel)
        
        # Map display area
        self.map_display = BoxLayout(orientation="vertical")
        self.add_widget(self.map_display)
    
    def load_map(self):
        """Load map with restaurants"""
        try:
            self.load_restaurants_data()
            self.create_embedded_map()
        except Exception as e:
            print(f"Error loading map: {e}")
            self.show_fallback_map()
    
    def load_restaurants_data(self):
        """Load restaurants from database"""
        import sqlite3
        db_path = "data/database.db"
        
        if not os.path.exists(db_path):
            return
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM restaurants LIMIT 10")
            data = cursor.fetchall()
            conn.close()
            
            # Generate coordinates for restaurants
            base_lat, base_lon = self.user_location
            self.restaurants = []
            
            for i, restaurant in enumerate(data):
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
        except Exception as e:
            print(f"Error loading restaurants: {e}")
    
    def create_embedded_map(self):
        """Create embedded map with Yandex Maps"""
        html_content = self.generate_map_html()
        
        # Create temporary HTML file
        temp_dir = tempfile.gettempdir()
        self.current_html_file = os.path.join(temp_dir, 'yandex_map_embedded.html')
        
        with open(self.current_html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Create map display
        map_container = BoxLayout(orientation="vertical")
        
        # Map preview info
        map_info = MDLabel(
            text="🗺️ Интерактивная карта Yandex (откроется в браузере)",
            halign="center",
            theme_text_color="Primary",
            size_hint_y=None,
            height="40dp"
        )
        map_container.add_widget(map_info)
        
        # Preview image (static map)
        try:
            yandex_maps = YandexMapWidget(self.api_key)
            
            markers = []
            for restaurant in self.restaurants:
                markers.append({
                    'lat': restaurant['lat'],
                    'lon': restaurant['lon'],
                    'color': 'red',
                    'style': 'pm2'
                })
            
            # Add user location marker
            markers.append({
                'lat': self.user_location[0],
                'lon': self.user_location[1],
                'color': 'blue',
                'style': 'pm2'
            })
            
            map_url = yandex_maps.get_static_map(
                self.user_location[0], self.user_location[1],
                zoom=12,
                width=400,
                height=300,
                markers=markers
            )
            
            preview_image = Image(
                source=map_url,
                size_hint_y=None,
                height="300dp"
            )
            map_container.add_widget(preview_image)
            
        except Exception as e:
            print(f"Error creating map preview: {e}")
            self.show_fallback_map()
            return
        
        self.map_display.clear_widgets()
        self.map_display.add_widget(map_container)
        
        # Update location info
        self.update_location_info()
    
    def generate_map_html(self):
        """Generate HTML content with Yandex Maps"""
        restaurants_json = json.dumps(self.restaurants)
        user_lat, user_lon = self.user_location
        
        return f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Интерактивная карта ресторанов - Food Delivery</title>
    <script src="https://api-maps.yandex.ru/2.1/?apikey={self.api_key}&lang=ru_RU"></script>
    <style>
        body, html {{ margin: 0; padding: 0; height: 100%; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}
        #map {{ width: 100%; height: 80vh; }}
        .controls {{ position: absolute; top: 10px; left: 10px; z-index: 1000; background: white; padding: 15px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.2); max-width: 300px; }}
        .control-btn {{ margin: 5px 0; padding: 10px 15px; border: none; border-radius: 5px; cursor: pointer; font-size: 14px; width: 100%; }}
        .primary-btn {{ background: #FF9800; color: white; }}
        .secondary-btn {{ background: #f0f0f0; color: #333; }}
        .info-panel {{ position: absolute; bottom: 10px; left: 10px; z-index: 1000; background: white; padding: 15px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.2); max-width: 350px; }}
        .delivery-time {{ font-size: 18px; font-weight: bold; color: #FF9800; }}
    </style>
</head>
<body>
    <div class="controls">
        <h3>🍔 Food Delivery</h3>
        <button class="control-btn primary-btn" onclick="getCurrentLocation()">📍 Мое местоположение</button>
        <button class="control-btn secondary-btn" onclick="showAllRestaurants()">🍽️ Все рестораны</button>
        <button class="control-btn secondary-btn" onclick="calculateOptimalRoute()">🚚 Оптимальный маршрут</button>
        <button class="control-btn secondary-btn" onclick="toggleTraffic()">🚦 Пробки</button>
    </div>
    
    <div class="info-panel" id="infoPanel" style="display: none;">
        <div class="delivery-time" id="deliveryTime">⏱️ Время доставки: расчёт...</div>
        <div id="routeInfo">Выберите ресторан для расчёта маршрута</div>
    </div>
    
    <div id="map"></div>
    
    <script>
        let map, userMark, currentRoute, trafficControl;
        const restaurants = {restaurants_json};
        const userLocation = [{user_lat}, {user_lon}];
        let selectedRestaurant = null;
        
        ymaps.ready(init);
        
        function init() {{
            map = new ymaps.Map('map', {{
                center: userLocation,
                zoom: 12,
                controls: ['zoomControl', 'searchControl', 'routeButtonControl', 'fullscreenControl']
            }});
            
            trafficControl = new ymaps.control.TrafficControl();
            map.controls.add(trafficControl);
            
            addUserLocation();
            addRestaurants();
            
            setTimeout(calculateAllDeliveryTimes, 1000);
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
                userLocation[0] = coords[0];
                userLocation[1] = coords[1];
                calculateAllDeliveryTimes();
            }});
            
            map.geoObjects.add(userMark);
        }}
        
        function addRestaurants() {{
            restaurants.forEach(restaurant => {{
                const mark = new ymaps.Placemark([restaurant.lat, restaurant.lon], {{
                    balloonContent: `
                        <h3>🍽️ ${{restaurant.name}}</h3>
                        <p>Категория: ${{restaurant.category}}</p>
                        <p>Рейтинг: ⭐ ${{restaurant.rating}}</p>
                        <div id="delivery-${{restaurant.id}}">Расчёт времени...</div>
                        <button onclick="buildRoute(${{restaurant.lat}}, ${{restaurant.lon}}, '${{restaurant.name}}', ${{restaurant.id}})">Заказать доставку</button>
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
                deliveryElement.innerHTML = `⏱️ Время доставки: ${{estimatedTime}} мин<br>📏 ${{distance.toFixed(1)}} км`;
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
                alert('Не удалось построить маршрут');
            }});
        }}
        
        function updateInfoPanel(restName, totalTime, distance) {{
            document.getElementById('deliveryTime').textContent = `⏱️ Время доставки: ${{totalTime}} мин`;
            document.getElementById('routeInfo').innerHTML = `🍽️ ${{restName}}<br>📏 ${{Math.round(distance/1000*100)/100}} км`;
            document.getElementById('infoPanel').style.display = 'block';
        }}
        
        function getCurrentLocation() {{
            if (navigator.geolocation) {{
                navigator.geolocation.getCurrentPosition(function(position) {{
                    const coords = [position.coords.latitude, position.coords.longitude];
                    map.setCenter(coords, 15);
                    userMark.geometry.setCoordinates(coords);
                    userLocation[0] = coords[0];
                    userLocation[1] = coords[1];
                    calculateAllDeliveryTimes();
                }});
            }}
        }}
        
        function showAllRestaurants() {{
            const bounds = restaurants.map(r => [r.lat, r.lon]);
            bounds.push(userMark.geometry.getCoordinates());
            map.setBounds(bounds);
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
            trafficControl.state.set('trafficShown', !trafficControl.state.get('trafficShown'));
        }}
        
        function getDirectDistance(coords1, coords2) {{
            const R = 6371;
            const dLat = (coords2[0] - coords1[0]) * Math.PI / 180;
            const dLon = (coords2[1] - coords1[1]) * Math.PI / 180;
            const a = Math.sin(dLat/2) * Math.sin(dLat/2) + Math.cos(coords1[0] * Math.PI / 180) * Math.cos(coords2[0] * Math.PI / 180) * Math.sin(dLon/2) * Math.sin(dLon/2);
            const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
            return R * c;
        }}
    </script>
</body>
</html>'''
    
    def show_fallback_map(self):
        """Show fallback map when web map fails"""
        fallback_label = MDLabel(
            text="🗺️ Карта временно недоступна\nИспользуйте кнопку 'Браузер' для просмотра",
            halign="center",
            theme_text_color="Secondary",
            size_hint_y=None,
            height="200dp"
        )
        
        self.map_display.clear_widgets()
        self.map_display.add_widget(fallback_label)
    
    def update_location_info(self):
        """Update location information"""
        lat, lon = self.user_location
        self.location_label.text = f"📍 Координаты: {lat:.4f}, {lon:.4f}"
    
    def open_in_browser(self, instance):
        """Open interactive map in browser"""
        try:
            if self.current_html_file and os.path.exists(self.current_html_file):
                webbrowser.open(f'file://{self.current_html_file}')
            else:
                # Create HTML file if not exists
                self.create_embedded_map()
                if self.current_html_file:
                    webbrowser.open(f'file://{self.current_html_file}')
        except Exception as e:
            print(f"Error opening browser: {e}")
    
    def show_restaurants(self, instance):
        """Show restaurants selection popup"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        content.add_widget(MDLabel(
            text="🍽️ Рестораны:",
            theme_text_color="Primary",
            size_hint_y=None,
            height="40dp"
        ))
        
        from kivy.uix.scrollview import ScrollView
        from kivy.uix.gridlayout import GridLayout
        
        scroll = ScrollView()
        grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))
        
        for restaurant in self.restaurants:
            rest_btn = Button(
                text=f"{restaurant['name']} ({restaurant['category']}) ⭐{restaurant['rating']}",
                size_hint_y=None,
                height="50dp"
            )
            rest_btn.bind(on_release=lambda x, r=restaurant: self.select_restaurant(r, popup))
            grid.add_widget(rest_btn)
        
        scroll.add_widget(grid)
        content.add_widget(scroll)
        
        close_btn = Button(text="Закрыть", size_hint_y=None, height="40dp")
        
        popup = Popup(
            title="Рестораны",
            content=content,
            size_hint=(0.8, 0.8)
        )
        
        close_btn.bind(on_release=popup.dismiss)
        content.add_widget(close_btn)
        
        popup.open()
    
    def select_restaurant(self, restaurant, popup):
        """Select restaurant and calculate route"""
        popup.dismiss()
        
        distance = self.calculate_distance(
            self.user_location[0], self.user_location[1],
            restaurant['lat'], restaurant['lon']
        )
        
        delivery_time = int(distance * 3) + 15
        
        self.delivery_info.text = f"🚚 {restaurant['name']}: ~{delivery_time} мин"
        self.route_info.text = f"🗺️ Расстояние: {distance:.1f} км"
        
        if self.app and hasattr(self.app, 'open_restaurant'):
            self.app.open_restaurant(restaurant['id'])
    
    def calculate_delivery_route(self, instance):
        """Calculate optimal delivery route"""
        if not self.restaurants:
            return
        
        min_distance = float('inf')
        closest_restaurant = None
        
        user_lat, user_lon = self.user_location
        
        for restaurant in self.restaurants:
            distance = self.calculate_distance(
                user_lat, user_lon,
                restaurant['lat'], restaurant['lon']
            )
            
            if distance < min_distance:
                min_distance = distance
                closest_restaurant = restaurant
        
        if closest_restaurant:
            delivery_time = int(min_distance * 3) + 15
            self.delivery_info.text = f"🚚 {closest_restaurant['name']}: ~{delivery_time} мин"
            self.route_info.text = f"🗺️ Расстояние: {min_distance:.1f} км"
    
    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two coordinates in km"""
        import math
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


class EmbeddedYandexMapWidget(BoxLayout):
    """Embedded interactive Yandex Maps - same as browser version but within app"""
    
    def __init__(self, app=None, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        self.app = app
        self.api_key = "c045d2a8-bc9f-46c5-95ab-d41879ea8136"
        self.restaurants = []
        self.user_location = [55.7558, 37.6176]
        self.current_html_file = None
        
        self.create_ui()
        self.load_restaurants_data()
        self.setup_map()
    
    def create_ui(self):
        # Controls
        controls = BoxLayout(size_hint_y=None, height="50dp", spacing=5, padding=5)
        
        browser_btn = Button(text="🌐 Открыть в браузере", size_hint_x=0.6)
        browser_btn.bind(on_release=self.open_in_browser)
        controls.add_widget(browser_btn)
        
        refresh_btn = Button(text="🔄 Обновить", size_hint_x=0.2)
        refresh_btn.bind(on_release=self.refresh_map)
        controls.add_widget(refresh_btn)
        
        list_btn = Button(text="🍽️ Список", size_hint_x=0.2)
        list_btn.bind(on_release=self.show_restaurants)
        controls.add_widget(list_btn)
        
        self.add_widget(controls)
        
        # Info panel
        info = BoxLayout(orientation="vertical", size_hint_y=None, height="80dp", padding=5)
        
        self.status_label = MDLabel(
            text="🗺️ Интерактивная карта Yandex - Полная функциональность!",
            halign="center", theme_text_color="Primary", size_hint_y=None, height="25dp"
        )
        info.add_widget(self.status_label)
        
        self.feature_label = MDLabel(
            text="🎮 Масштабирование, маршруты, пробки, расчёт времени доставки",
            halign="center", theme_text_color="Secondary", size_hint_y=None, height="25dp"
        )
        info.add_widget(self.feature_label)
        
        self.instruction_label = MDLabel(
            text="🔍 Кликните 'Открыть в браузере' для полной интерактивности",
            halign="center", theme_text_color="Secondary", size_hint_y=None, height="25dp"
        )
        info.add_widget(self.instruction_label)
        
        self.add_widget(info)
        
        # Map container
        self.map_container = BoxLayout(orientation="vertical")
        self.add_widget(self.map_container)
    
    def load_restaurants_data(self):
        import sqlite3
        db_path = "data/database.db"
        
        if not os.path.exists(db_path):
            return
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM restaurants LIMIT 10")
            data = cursor.fetchall()
            conn.close()
            
            base_lat, base_lon = self.user_location
            self.restaurants = []
            
            for i, restaurant in enumerate(data):
                lat = base_lat + random.uniform(-0.03, 0.03)
                lon = base_lon + random.uniform(-0.04, 0.04)
                
                self.restaurants.append({
                    'id': restaurant[0], 'name': restaurant[1], 'category': restaurant[2],
                    'rating': restaurant[3], 'distance': restaurant[4], 'lat': lat, 'lon': lon
                })
        except Exception as e:
            print(f"Error loading restaurants: {e}")
    
    def setup_map(self):
        # Generate HTML for browser
        html_content = self.generate_map_html()
        temp_dir = tempfile.gettempdir()
        self.current_html_file = os.path.join(temp_dir, 'food_delivery_full_map.html')
        
        with open(self.current_html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Create in-app preview
        self.create_preview()
    
    def create_preview(self):
        try:
            self.map_container.clear_widgets()
            
            # Static map preview
            yandex_maps = YandexMapWidget(self.api_key)
            markers = []
            for r in self.restaurants:
                markers.append({'lat': r['lat'], 'lon': r['lon'], 'color': 'red', 'style': 'pm2'})
            markers.append({'lat': self.user_location[0], 'lon': self.user_location[1], 'color': 'blue', 'style': 'pm2'})
            
            map_url = yandex_maps.get_static_map(self.user_location[0], self.user_location[1], zoom=12, width=400, height=250, markers=markers)
            
            preview_image = Image(source=map_url, size_hint_y=None, height="250dp")
            self.map_container.add_widget(preview_image)
            
            # Restaurant list
            self.add_restaurant_list()
            
        except Exception as e:
            print(f"Error creating preview: {e}")
            self.show_fallback()
    
    def add_restaurant_list(self):
        from kivy.uix.scrollview import ScrollView
        from kivy.uix.gridlayout import GridLayout
        
        title = MDLabel(text="🍽️ Рестораны (кликните для заказа):", theme_text_color="Primary", size_hint_y=None, height="35dp")
        self.map_container.add_widget(title)
        
        scroll = ScrollView(size_hint_y=0.6)
        grid = GridLayout(cols=1, spacing=5, size_hint_y=None, padding=10)
        grid.bind(minimum_height=grid.setter('height'))
        
        for restaurant in self.restaurants:
            distance = self.calculate_distance(self.user_location[0], self.user_location[1], restaurant['lat'], restaurant['lon'])
            delivery_time = int(distance * 3) + 15
            
            time_color = "🟢" if delivery_time <= 20 else "🟡" if delivery_time <= 35 else "🔴"
            
            rest_btn = Button(
                text=f"{time_color} {restaurant['name']} ({restaurant['category']})\n⭐{restaurant['rating']} • ~{delivery_time} мин • {distance:.1f} км",
                size_hint_y=None, height="60dp"
            )
            rest_btn.bind(on_release=lambda x, r=restaurant: self.select_restaurant(r))
            grid.add_widget(rest_btn)
        
        scroll.add_widget(grid)
        self.map_container.add_widget(scroll)
    
    def generate_map_html(self):
        restaurants_json = json.dumps(self.restaurants)
        user_lat, user_lon = self.user_location
        
        return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Food Delivery Map</title>
<script src="https://api-maps.yandex.ru/2.1/?apikey={self.api_key}&lang=ru_RU"></script>
<style>body,html{{margin:0;padding:0;height:100%;font-family:Arial}}
#map{{width:100%;height:90vh}}.controls{{position:absolute;top:10px;left:10px;z-index:1000;background:rgba(255,255,255,0.95);padding:15px;border-radius:10px;box-shadow:0 4px 8px rgba(0,0,0,0.2)}}
.info-panel{{position:absolute;bottom:10px;left:10px;z-index:1000;background:rgba(255,255,255,0.95);padding:15px;border-radius:10px;box-shadow:0 4px 8px rgba(0,0,0,0.2);display:none}}
.btn{{margin:5px 0;padding:10px 15px;border:none;border-radius:5px;cursor:pointer;width:100%}}
.primary{{background:#FF9800;color:white}}.secondary{{background:#f0f0f0;color:#333}}</style></head>
<body><div class="controls"><h3>🍔 Food Delivery</h3>
<button class="btn primary" onclick="getCurrentLocation()">📍 Мое местоположение</button>
<button class="btn secondary" onclick="showAllRestaurants()">🍽️ Все рестораны</button>
<button class="btn secondary" onclick="calculateOptimalRoute()">🚚 Оптимальный</button>
<button class="btn secondary" onclick="toggleTraffic()">🚦 Пробки</button></div>
<div class="info-panel" id="infoPanel"><div id="deliveryTime">⏱️ Расчёт...</div><div id="routeInfo">Выберите ресторан</div></div>
<div id="map"></div><script>let map,userMark,currentRoute,trafficControl;const restaurants={restaurants_json};const userLocation=[{user_lat},{user_lon}];
ymaps.ready(init);function init(){{map=new ymaps.Map('map',{{center:userLocation,zoom:13,controls:['zoomControl','searchControl','routeButtonControl','fullscreenControl']}});trafficControl=new ymaps.control.TrafficControl();map.controls.add(trafficControl);addUserLocation();addRestaurants();setTimeout(calculateAllDeliveryTimes,1000);}}
function addUserLocation(){{userMark=new ymaps.Placemark(userLocation,{{balloonContent:'📍 Ваше местоположение'}},{{preset:'islands#blueCircleDotIcon',draggable:true}});userMark.events.add('dragend',()=>{{const coords=userMark.geometry.getCoordinates();userLocation[0]=coords[0];userLocation[1]=coords[1];calculateAllDeliveryTimes();}});map.geoObjects.add(userMark);}}
function addRestaurants(){{restaurants.forEach(restaurant=>{{const mark=new ymaps.Placemark([restaurant.lat,restaurant.lon],{{balloonContent:`<h3>🍽️ ${{restaurant.name}}</h3><p>${{restaurant.category}} • ⭐${{restaurant.rating}}</p><div id="delivery-${{restaurant.id}}">...</div><button onclick="buildRoute(${{restaurant.lat}},${{restaurant.lon}},'${{restaurant.name}}',${{restaurant.id}})">🚚 Заказать</button>`}},{{preset:'islands#redRestaurantIcon'}});map.geoObjects.add(mark);}});}}
function calculateAllDeliveryTimes(){{restaurants.forEach(restaurant=>{{const userCoords=userMark.geometry.getCoordinates();const distance=getDirectDistance(userCoords,[restaurant.lat,restaurant.lon]);const time=Math.round(distance*3)+15;const el=document.getElementById(`delivery-${{restaurant.id}}`);if(el)el.innerHTML=`⏱️ ${{time}} мин • ${{distance.toFixed(1)}} км`;}});}}
function buildRoute(lat,lon,name,id){{const userCoords=userMark.geometry.getCoordinates();if(currentRoute)map.geoObjects.remove(currentRoute);ymaps.route([userCoords,[lat,lon]],{{routingMode:'auto'}}).then(route=>{{currentRoute=route;map.geoObjects.add(route);route.getPaths().options.set({{strokeColor:'#FF9800',strokeWidth:6}});const distance=route.getLength();const duration=route.getJamesTime()||route.getTime();const totalTime=Math.round(duration/60)+15;document.getElementById('deliveryTime').textContent=`⏱️ ${{totalTime}} мин`;document.getElementById('routeInfo').innerHTML=`🍽️ ${{name}}<br>📏 ${{Math.round(distance/1000*100)/100}} км`;document.getElementById('infoPanel').style.display='block';map.setBounds(route.getBounds());}}).catch(()=>alert('Маршрут не найден'));}}
function getCurrentLocation(){{if(navigator.geolocation)navigator.geolocation.getCurrentPosition(pos=>{{const coords=[pos.coords.latitude,pos.coords.longitude];map.setCenter(coords,15);userMark.geometry.setCoordinates(coords);userLocation[0]=coords[0];userLocation[1]=coords[1];calculateAllDeliveryTimes();}});}}
function showAllRestaurants(){{const bounds=restaurants.map(r=>[r.lat,r.lon]).concat([userMark.geometry.getCoordinates()]);map.setBounds(bounds);}}
function calculateOptimalRoute(){{const userCoords=userMark.geometry.getCoordinates();let closest=restaurants[0],minDist=getDirectDistance(userCoords,[closest.lat,closest.lon]);restaurants.forEach(r=>{{const dist=getDirectDistance(userCoords,[r.lat,r.lon]);if(dist<minDist){{minDist=dist;closest=r;}}}});buildRoute(closest.lat,closest.lon,closest.name,closest.id);}}
function toggleTraffic(){{trafficControl.state.set('trafficShown',!trafficControl.state.get('trafficShown'));}}
function getDirectDistance(coords1,coords2){{const R=6371,dLat=(coords2[0]-coords1[0])*Math.PI/180,dLon=(coords2[1]-coords1[1])*Math.PI/180;const a=Math.sin(dLat/2)*Math.sin(dLat/2)+Math.cos(coords1[0]*Math.PI/180)*Math.cos(coords2[0]*Math.PI/180)*Math.sin(dLon/2)*Math.sin(dLon/2);return R*2*Math.atan2(Math.sqrt(a),Math.sqrt(1-a));}}</script></body></html>'''
    
    def refresh_map(self, instance):
        self.setup_map()
        self.status_label.text = "🔄 Карта обновлена!"
    
    def open_in_browser(self, instance):
        try:
            if self.current_html_file and os.path.exists(self.current_html_file):
                webbrowser.open(f'file://{self.current_html_file}')
                self.status_label.text = "🌐 Карта открыта в браузере!"
        except Exception as e:
            print(f"Browser error: {e}")
    
    def show_restaurants(self, instance):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(MDLabel(text="🍽️ Рестораны:", theme_text_color="Primary", size_hint_y=None, height="40dp"))
        
        from kivy.uix.scrollview import ScrollView
        from kivy.uix.gridlayout import GridLayout
        
        scroll = ScrollView()
        grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))
        
        for restaurant in self.restaurants:
            distance = self.calculate_distance(self.user_location[0], self.user_location[1], restaurant['lat'], restaurant['lon'])
            delivery_time = int(distance * 3) + 15
            
            rest_btn = Button(
                text=f"{restaurant['name']} ({restaurant['category']})\n⭐{restaurant['rating']} • ~{delivery_time} мин",
                size_hint_y=None, height="60dp"
            )
            rest_btn.bind(on_release=lambda x, r=restaurant: self.select_restaurant(r, popup))
            grid.add_widget(rest_btn)
        
        scroll.add_widget(grid)
        content.add_widget(scroll)
        
        close_btn = Button(text="Закрыть", size_hint_y=None, height="40dp")
        popup = Popup(title="Рестораны", content=content, size_hint=(0.8, 0.8))
        close_btn.bind(on_release=popup.dismiss)
        content.add_widget(close_btn)
        popup.open()
    
    def select_restaurant(self, restaurant, popup=None):
        if popup: popup.dismiss()
        
        distance = self.calculate_distance(self.user_location[0], self.user_location[1], restaurant['lat'], restaurant['lon'])
        delivery_time = int(distance * 3) + 15
        
        self.feature_label.text = f"🚚 {restaurant['name']}: ~{delivery_time} мин ({distance:.1f} км)"
        
        if self.app and hasattr(self.app, 'open_restaurant'):
            self.app.open_restaurant(restaurant['id'])
    
    def show_fallback(self):
        self.map_container.clear_widgets()
        fallback = MDLabel(
            text="🗺️ Карта недоступна\nКликните 'Открыть в браузере'",
            halign="center", theme_text_color="Secondary", size_hint_y=None, height="200dp"
        )
        self.map_container.add_widget(fallback)
        self.add_restaurant_list()
    
    def calculate_distance(self, lat1, lon1, lat2, lon2):
        import math
        R = 6371
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        a = (math.sin(delta_lat/2) * math.sin(delta_lat/2) + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2) * math.sin(delta_lon/2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c