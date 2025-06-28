@echo off
REM Build the Clash of Clans Builder Base Farming Bot

REM Clean previous build/dist folders
rmdir /s /q build
rmdir /s /q dist

REM Run PyInstaller to build the executable
pyinstaller --onefile --noconsole --add-data "2k;2k" --add-data "fullhd;fullhd" --name "builderbase_farmer" main.py

echo.
echo Build complete! The executable is in the dist\ folder.
pause