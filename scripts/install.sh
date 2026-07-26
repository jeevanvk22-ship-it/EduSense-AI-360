#!/usr/bin/env bash
# EduSense AI 360 - install (macOS / Linux)
set -e
cd "$(dirname "$0")/.."
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
echo "Install complete. Run:  ./scripts/run.sh"
