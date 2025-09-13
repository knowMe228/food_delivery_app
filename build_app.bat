@echo off
echo Building Food Delivery App...
echo This script will attempt to build the Android application using Gradle.

if exist "gradlew.bat" (
    echo Found gradlew.bat, attempting to build...
    call gradlew.bat assembleDebug
    if %errorlevel% == 0 (
        echo Build successful!
        echo The APK should be located in app\build\outputs\apk\debug\
    ) else (
        echo Build failed with error code %errorlevel%
        echo Please check the error messages above
    )
) else (
    echo gradlew.bat not found in current directory
    echo Make sure you are running this script from the project root directory
)

pause