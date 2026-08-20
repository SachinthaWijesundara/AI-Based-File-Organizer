@echo off
if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
)

echo Installing dependencies...
.venv\Scripts\python.exe -m pip install -r requirements.txt

echo Starting File Organizer...
.venv\Scripts\python.exe main.py

pause
