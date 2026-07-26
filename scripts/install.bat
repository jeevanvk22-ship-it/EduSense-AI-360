@echo off
REM EduSense AI 360 - install (Windows)
cd /d "%~dp0\.."
python -m venv venv
call venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
echo Install complete. Run:  scripts\run.bat
