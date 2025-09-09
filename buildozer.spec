[app]
# (str) Title of your application
title = Food Delivery

# (str) Package name
package.name = food_delivery

# (str) Package domain (needed for android/ios packaging)
package.domain = org.example

# (str) Source code where the main.py live
source.dir = .

# (str) Application versioning (method 1)
version = 1.0.0

# (str) Application entry point
entrypoint = main.py

# (list) Permissions
android.permissions = INTERNET, ACCESS_NETWORK_STATE, ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION

# (list) Application requirementsequirements = python3,kivy,kivymd,requests,plyer

# (str) Supported orientation (one of: landscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (str) Android API to use
android.api = 33

# (int) Minimum API your APK will support
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (str) Android SDK version to use
android.sdk = 26

# (list) Architectures to build for
android.archs = arm64-v8a, armeabi-v7a

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (str) Bootstrap to use
android.bootstrap = sdl2

# (list) Include patterns
source.include_exts = py,kv,png,jpg,ttf,ini,xml,html,json


[buildozer]
log_level = 2
warn_on_root = 0


