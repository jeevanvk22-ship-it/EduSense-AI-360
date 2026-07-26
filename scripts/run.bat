@echo off
REM EduSense AI 360 - run (Windows)
cd /d "%~dp0\.."
if exist venv\Scripts\activate call venv\Scripts\activate
python main.py
