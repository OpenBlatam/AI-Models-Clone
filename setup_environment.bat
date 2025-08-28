@echo off
echo ========================================
echo   INSTAGRAM CAPTIONS API v10.0 SETUP
echo ========================================
echo.

echo [1/5] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Python is already installed
    python --version
) else (
    echo ✗ Python is not installed
    echo.
    echo Please install Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo.
echo [2/5] Installing required packages...
pip install fastapi uvicorn pydantic transformers torch numba orjson cachetools pyyaml

echo.
echo [3/5] Installing additional dependencies...
pip install pytest pytest-asyncio httpx

echo.
echo [4/5] Creating virtual environment (recommended)...
python -m venv venv
echo ✓ Virtual environment created
echo.
echo To activate the virtual environment, run:
echo   venv\Scripts\activate

echo.
echo [5/5] Running basic tests...
python test_enhanced_modules.py

echo.
echo ========================================
echo   SETUP COMPLETED SUCCESSFULLY!
echo ========================================
echo.
echo To start the API server, run:
echo   python api_v10.py
echo.
echo To run tests, use:
echo   python test_enhanced_modules.py
echo.
pause
