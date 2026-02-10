@echo off
REM ============================================================================
REM Run API with Debugging (Windows)
REM Runs the Dermatology AI API with debugging enabled
REM ============================================================================

setlocal

set HOST=0.0.0.0
set PORT=8000
set LOG_LEVEL=debug
set RELOAD=true

echo ==========================================
echo Starting Dermatology AI API
echo ==========================================
echo.
echo Configuration:
echo   Host: %HOST%
echo   Port: %PORT%
echo   Log Level: %LOG_LEVEL%
echo   Reload: %RELOAD%
echo.

REM Check for virtual environment
if exist "venv\Scripts\activate.bat" (
    echo [OK] Virtual environment found
    call venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    echo [OK] Virtual environment found
    call .venv\Scripts\activate.bat
) else (
    echo [WARN] No virtual environment found
    echo   Running with system Python
)

REM Check dependencies
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo [WARN] FastAPI not found, installing dependencies...
    pip install -r requirements-optimized.txt
)

echo.
echo Starting server...
echo.

REM Run with uvicorn
if "%RELOAD%"=="true" (
    uvicorn main:app --host %HOST% --port %PORT% --reload --log-level %LOG_LEVEL%
) else (
    uvicorn main:app --host %HOST% --port %PORT% --log-level %LOG_LEVEL%
)

endlocal



