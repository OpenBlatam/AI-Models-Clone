@echo off
setlocal

echo Starting Robot Maintenance AI...

if "%OPENROUTER_API_KEY%"=="" (
    echo ERROR: OPENROUTER_API_KEY environment variable is not set!
    echo Please set it with: set OPENROUTER_API_KEY=your-key-here
    exit /b 1
)

if not exist "logs" mkdir logs
if not exist "data" mkdir data

python -m uvicorn main:app --host %HOST% --port %PORT% --log-level %LOG_LEVEL%

endlocal






