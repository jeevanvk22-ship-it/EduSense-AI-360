@echo off
REM EduSense AI 360 - build a standalone executable with PyInstaller (Windows)
cd /d "%~dp0\.."
if exist venv\Scripts\activate call venv\Scripts\activate
pip install pyinstaller
pyinstaller --noconfirm --name EduSenseAI360 ^
  --add-data "config/default_config.json;config" ^
  --add-data "assets;assets" ^
  main.py
echo Build complete -> dist\EduSenseAI360\
