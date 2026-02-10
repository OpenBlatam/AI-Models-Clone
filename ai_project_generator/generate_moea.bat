@echo off
REM Script to generate MOEA project
echo ========================================
echo MOEA Project Generator
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.8+ and add it to your PATH
    pause
    exit /b 1
)

echo [1/3] Checking server status...
curl -s http://localhost:8020/health >nul 2>&1
if errorlevel 1 (
    echo Server is not running. Starting server in background...
    start /B python main.py
    echo Waiting for server to start...
    timeout /t 5 /nobreak >nul
)

echo [2/3] Generating MOEA project...
python generate_moea.py

if errorlevel 1 (
    echo.
    echo ERROR: Generation failed!
    echo Trying direct generation method...
    python generate_moea_direct.py
)

echo.
echo [3/3] Checking generated project...
if exist "generated_projects\moea_optimization_system" (
    echo.
    echo ========================================
    echo SUCCESS! Project generated at:
    echo generated_projects\moea_optimization_system
    echo ========================================
    echo.
    echo Next steps:
    echo 1. cd generated_projects\moea_optimization_system\backend
    echo 2. pip install -r requirements.txt
    echo 3. cd ..\frontend
    echo 4. npm install
    echo.
) else (
    echo.
    echo Project directory not found. Check logs above for errors.
    echo.
)

pause

