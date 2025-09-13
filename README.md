# Food Delivery App

This is an Android food delivery application written in Java with full Yandex Maps integration via WebView.

## Features
- Restaurant feed with random restaurant names
- Restaurant detail pages with menus
- Shopping cart functionality
- Full Yandex Maps web interface for delivery visualization
- Delivery route calculation and time estimation
- Search and navigation capabilities

## How to Build and Run

### Method 1: Using Android Studio (Recommended)
1. Open Android Studio
2. Select "Open an existing Android Studio project"
3. Navigate to this project folder and select it
4. Let Android Studio sync the project (this will automatically generate the Gradle wrapper files)
5. Build and run the application

### Method 2: Using Command Line
1. Open command prompt/terminal
2. Navigate to the project directory
3. Run `build_app.bat` (Windows) or `./build_app.sh` (Linux/Mac)

For detailed instructions, see [HOW_TO_BUILD.md](HOW_TO_BUILD.md)

## Map Features

The application includes WebView implementation with full Yandex Maps:

- **WebView with Yandex Maps**:
  - Full Yandex Maps web interface
  - Advanced search capabilities
  - Street view and satellite imagery
  - Public transport and traffic information
  - Routing and navigation features
  - Interactive map with zoom and pan

When users proceed to checkout, they are immediately presented with the full Yandex Maps interface showing their location, restaurant locations, and delivery route.

## Requirements
- Android Studio (preferably the latest version)
- Android SDK API level 34
- Java Development Kit (JDK) 8 or higher

## Notes
- All UI elements are in Russian
- Restaurants are positioned in St. Petersburg with fixed coordinates
- The map functionality uses WebView to display the full Yandex Maps web interface
- After successful build, APK will be located at `app/build/outputs/apk/debug/app-debug.apk`