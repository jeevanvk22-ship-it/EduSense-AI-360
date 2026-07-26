#!/usr/bin/env bash
# EduSense AI 360 - run (macOS / Linux)
set -e
cd "$(dirname "$0")/.."
[ -d venv ] && source venv/bin/activate
python main.py
