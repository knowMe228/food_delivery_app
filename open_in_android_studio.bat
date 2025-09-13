@echo off
echo Opening project in Android Studio...
echo Make sure Android Studio is installed and added to PATH

if exist "C:\Program Files\Android\Android Studio\bin\studio64.exe" (
    echo Found Android Studio, opening project...
    "C:\Program Files\Android\Android Studio\bin\studio64.exe" .
) else (
    echo Android Studio not found in default location
    echo Please open Android Studio manually and import the project
)

pause