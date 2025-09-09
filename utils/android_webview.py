from kivy.utils import platform
from kivy.clock import Clock

# Android WebView integration using pyjnius
try:
    if platform == 'android':
        from jnius import autoclass, cast
        from android.runnable import run_on_ui_thread
        ANDROID_AVAILABLE = True
    else:
        ANDROID_AVAILABLE = False
except Exception:
    ANDROID_AVAILABLE = False


def build_map_html(restaurants, user_lat=55.7558, user_lon=37.6176):
    import json
    restaurants_json = json.dumps(restaurants, ensure_ascii=False)
    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset=\"UTF-8\">\n  <title>Интерактивная карта - Android WebView</title>\n  <script src=\"https://api-maps.yandex.ru/2.1/?apikey=c045d2a8-bc9f-46c5-95ab-d41879ea8136&lang=ru_RU\"></script>\n  <style>html,body,#map {{height:100%;margin:0;padding:0}}</style>\n</head>
<body>
  <div id=\"map\"></div>
  <script>
    let map, userMark, currentRoute, trafficControl;\n    const restaurants = {restaurants_json};\n    let userLocation = [{user_lat}, {user_lon}];\n    ymaps.ready(function() {{\n      map = new ymaps.Map('map', {{ center: userLocation, zoom: 12, controls: ['zoomControl','routeButtonControl','fullscreenControl'] }});\n      trafficControl = new ymaps.control.TrafficControl();\n      map.controls.add(trafficControl);\n      userMark = new ymaps.Placemark(userLocation, {{balloonContent:'📍 Ваше местоположение'}}, {{preset:'islands#blueCircleDotIcon',draggable:true}});\n      map.geoObjects.add(userMark);\n      restaurants.forEach(r => {{\n        const m = new ymaps.Placemark([r.lat, r.lon], {{\n          balloonContent: `<h3>🍽️ ${'{'}r.name{'}'}</h3><p>${'{'}r.category{'}'} • ⭐ ${'{'}r.rating{'}'}</p>\n            <button onclick=\\\"(function(){{buildRoute(${ '{' }r.lat{ '}' }, ${ '{' }r.lon{ '}' }, '${ '{' }r.name{ '}' }')}})()\\\">Маршрут</button>`\n        }}, {{preset:'islands#redRestaurantIcon'}});\n        map.geoObjects.add(m);\n      }});\n    }});\n    function buildRoute(lat, lon, name) {{\n      const u = userMark.geometry.getCoordinates();\n      ymaps.route([u, [lat, lon]], {{routingMode:'auto'}}).then(function(route) {{\n        if (currentRoute) map.geoObjects.remove(currentRoute);\n        currentRoute = route;\n        route.getPaths().options.set({{strokeColor:'#FF9800', strokeWidth:6, strokeOpacity:0.9}});\n        map.geoObjects.add(route);\n        map.setBounds(route.getBounds());\n      }});\n    }}
  </script>
</body>
</html>"""


class AndroidWebViewMap:
    def __init__(self):
        self.webview = None

    @run_on_ui_thread
    def _create_webview(self, html):
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        activity = PythonActivity.mActivity
        WebView = autoclass('android.webkit.WebView')
        WebViewClient = autoclass('android.webkit.WebViewClient')
        WebChromeClient = autoclass('android.webkit.WebChromeClient')
        LayoutParams = autoclass('android.view.ViewGroup$LayoutParams')

        self.webview = WebView(activity)
        settings = self.webview.getSettings()
        settings.setJavaScriptEnabled(True)
        settings.setDomStorageEnabled(True)
        settings.setDatabaseEnabled(True)
        settings.setGeolocationEnabled(True)

        self.webview.setWebViewClient(WebViewClient())
        self.webview.setWebChromeClient(WebChromeClient())

        self.webview.loadDataWithBaseURL('https://local/', html, 'text/html', 'utf-8', None)
        params = LayoutParams(LayoutParams.MATCH_PARENT, LayoutParams.MATCH_PARENT)
        activity.addContentView(self.webview, params)

    def open(self, restaurants):
        if not ANDROID_AVAILABLE:
            raise RuntimeError('Android WebView not available on this platform')
        html = build_map_html(restaurants)
        self._create_webview(html)

    @run_on_ui_thread
    def _destroy(self):
        if self.webview is None:
            return
        parent = cast(autoclass('android.view.ViewGroup'), self.webview.getParent())
        if parent:
            parent.removeView(self.webview)
        self.webview = None

    def close(self):
        if not ANDROID_AVAILABLE:
            return
        self._destroy()

