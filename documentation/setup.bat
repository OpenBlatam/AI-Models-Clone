@echo off
REM Setup script for Instagram Captions API Documentation System
REM This script helps set up the Python environment and install dependencies

echo ========================================
echo Instagram Captions API Documentation Setup
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    echo.
    echo After installing Python, run this script again
    pause
    exit /b 1
)

echo Python found: 
python --version
echo.

REM Check if pip is available
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo pip is not available
    echo Please ensure pip is installed with Python
    pause
    exit /b 1
)

echo pip found:
pip --version
echo.

REM Install required dependencies
echo Installing required dependencies...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Dependencies installed successfully!
echo.

REM Test the documentation system
echo Testing the documentation system...
python test_docs.py

if %errorlevel% neq 0 (
    echo.
    echo Tests failed. Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Setup completed successfully!
echo ========================================
echo.
echo You can now use the documentation system:
echo.
echo 1. Generate Instagram API docs:
echo    python generate_docs.py
echo.
echo 2. Use the CLI interface:
echo    python cli.py --help
echo.
echo 3. Run tests:
echo    python test_docs.py
echo.
pause






