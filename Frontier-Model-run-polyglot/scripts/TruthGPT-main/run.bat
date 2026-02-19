@echo off
echo ============================================================
echo   TRUTHGPT - STARTING...
echo ============================================================
echo.

if not exist .venv (
    echo [ERROR] Virtual environment not found!
    echo Please run 'install.bat' first.
    pause
    exit /b 1
)

:: Activate environment
call .venv\Scripts\activate.bat

:: Execute
echo Launching Frontier Model Run...
:: Replace this with the actual entry point of your application
:: If it's a CLI tool:
frontier %*
:: If it's a specific script:
:: python optimization_core/cli.py

echo.
pause
