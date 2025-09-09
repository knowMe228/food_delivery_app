import json
import os
import subprocess
import sys
import tempfile

# Write restaurants data to a JSON file and launch the Qt map app in a subprocess

def launch_qt_map(restaurants):
    try:
        tmp = os.path.join(tempfile.gettempdir(), 'food_delivery_restaurants.json')
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(restaurants, f, ensure_ascii=False)
        # Launch in a new process so it doesn't block Kivy loop
        py = sys.executable
        module_path = os.path.join(os.path.dirname(__file__), 'qt_map_app.py')
        subprocess.Popen([py, module_path, tmp], close_fds=True)
        return True
    except Exception as e:
        print(f"Failed to launch Qt map: {e}")
        return False

