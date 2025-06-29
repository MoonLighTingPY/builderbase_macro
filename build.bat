@echo off
setlocal

REM Ensure we are in the script's directory
cd /d "%~dp0"

REM Clean previous build
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build

REM Build with PyInstaller (add icon)
pyinstaller --onefile --noconsole --add-data "2k;2k" --add-data "fullhd;fullhd" --icon "coc-icon.ico" --name "builderbase_farmer" main.py

REM Copy README and requirements.txt for distribution
if exist dist (
    copy README.md dist\
    copy requirements.txt dist\
)

echo Build complete! Find builderbase_farmer.exe in the dist\ folder.
pause