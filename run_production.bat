@echo off
echo ========================================
echo HeyGen AI Production System
echo ========================================

REM Set environment variables
set ENVIRONMENT=production
set DATABASE_URL=postgresql://user:pass@localhost/heygen_ai
set REDIS_URL=redis://localhost:6379
set SENTRY_DSN=https://your-sentry-dsn@sentry.io/project

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found. Please install Python 3.8+ and add it to PATH.
    pause
    exit /b 1
)

REM Install dependencies if needed
echo Installing dependencies...
pip install -r requirements-production.txt

REM Run the production system
echo Starting HeyGen AI Production System...
python main_production.py

pause 