@echo off
setlocal

REM Install dependencies if needed
where pip >nul 2>nul
if %errorlevel% neq 0 (
  echo pip not found. Ensure Python is installed and added to PATH.
  goto :eof
)

pip install -r requirements-automator.txt >nul 2>nul

REM Forward all args to the script
py -3 cursor_automator.py %*

endlocal


