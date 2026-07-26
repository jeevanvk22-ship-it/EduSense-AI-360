#!/usr/bin/env bash
# EduSense AI 360 - build a standalone executable with PyInstaller (macOS / Linux)
set -e
cd "$(dirname "$0")/.."
[ -d venv ] && source venv/bin/activate
pip install pyinstaller
pyinstaller --noconfirm --name EduSenseAI360 \
  --add-data "config/default_config.json:config" \
  --add-data "assets:assets" \
  main.py
echo "Build complete -> dist/EduSenseAI360/"
