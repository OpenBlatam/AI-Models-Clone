@echo off
REM Test Runner for TruthGPT
REM Finds Python and runs tests

echo ================================================
echo   TruthGPT Test Runner
echo ================================================
echo.

REM Try to find Python
set PYTHON_CMD=

REM Check if python works
python --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD=python
    goto :found_python
)

REM Check common locations
if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    set PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python311\python.exe
    goto :found_python
)

if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python312\python.exe
    goto :found_python
)

if exist "C:\Python311\python.exe" (
    set PYTHON_CMD=C:\Python311\python.exe
    goto :found_python
)

if exist "C:\Python312\python.exe" (
    set PYTHON_CMD=C:\Python312\python.exe
    goto :found_python
)

echo [ERROR] Python not found!
echo.
echo Please install Python from: https://www.python.org/downloads/
echo Make sure to check "Add Python to PATH" during installation
pause
exit /b 1

:found_python
echo [OK] Using Python: %PYTHON_CMD%
%PYTHON_CMD% --version
echo.

REM Check if we're in the right directory
if not exist "core" (
    echo [ERROR] core/ directory not found
    echo Current directory: %CD%
    echo Please run from TruthGPT-main directory
    pause
    exit /b 1
)

if not exist "tests" (
    echo [ERROR] tests/ directory not found
    echo Current directory: %CD%
    echo Please run from TruthGPT-main directory
    pause
    exit /b 1
)

echo ================================================
echo   Running Tests
echo ================================================
echo.

REM Check for command line arguments
if "%1"=="" (
    %PYTHON_CMD% run_unified_tests.py
) else (
    %PYTHON_CMD% run_unified_tests.py %*
)

set TEST_EXIT_CODE=%ERRORLEVEL%

if %TEST_EXIT_CODE% EQU 0 (
    echo.
    echo ================================================
    echo   All tests passed!
    echo ================================================
) else (
    echo.
    echo ================================================
    echo   Some tests failed (exit code: %TEST_EXIT_CODE%)
    echo ================================================
)

echo.
echo Usage examples:
echo   run_tests.bat                    - Run all tests
echo   run_tests.bat core                - Run core tests only
echo   run_tests.bat --failfast          - Stop on first failure
echo   run_tests.bat --verbose           - Verbose output
echo   run_tests.bat --list              - List all categories
echo   run_tests.bat --json report.json  - Export to JSON
echo.

pause
exit /b %TEST_EXIT_CODE%
