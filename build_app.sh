#!/bin/bash
echo "Building Food Delivery App..."
echo "This script will attempt to build the Android application using Gradle."

if [ -f "gradlew" ]; then
    echo "Found gradlew, attempting to build..."
    ./gradlew assembleDebug
    if [ $? -eq 0 ]; then
        echo "Build successful!"
        echo "The APK should be located in app/build/outputs/apk/debug/"
    else
        echo "Build failed"
        echo "Please check the error messages above"
    fi
else
    echo "gradlew not found in current directory"
    echo "Make sure you are running this script from the project root directory"
fi