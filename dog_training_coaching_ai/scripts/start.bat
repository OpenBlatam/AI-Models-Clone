@echo off
REM Start script for Dog Training Coaching AI (Windows)

echo Starting Dog Training Coaching AI...

REM Check if .env exists
if not exist .env (
    echo Warning: .env file not found. Using environment variables.
)

REM Install dependencies if needed
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat
pip install -r requirements.txt

REM Start server
python main.py

