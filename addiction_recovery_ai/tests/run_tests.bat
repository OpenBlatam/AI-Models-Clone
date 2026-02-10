@echo off
REM Test runner script for addiction_recovery_ai (Windows)

echo ==========================================
echo Running Addiction Recovery AI Tests
echo ==========================================

REM Check if pytest is installed
where pytest >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: pytest is not installed
    echo Install it with: pip install -r requirements-dev.txt
    exit /b 1
)

REM Parse command line arguments
set TEST_TYPE=%1
if "%TEST_TYPE%"=="" set TEST_TYPE=all

set COVERAGE=%2
if "%COVERAGE%"=="" set COVERAGE=true

echo Test Type: %TEST_TYPE%
echo Coverage: %COVERAGE%
echo.

REM Change to tests directory
cd /d "%~dp0"

REM Base pytest command
set PYTEST_CMD=pytest

REM Add coverage if requested
if "%COVERAGE%"=="true" (
    set PYTEST_CMD=%PYTEST_CMD% --cov=.. --cov-report=html --cov-report=term-missing
)

REM Run tests based on type
if "%TEST_TYPE%"=="unit" (
    echo Running unit tests...
    %PYTEST_CMD% -m "not integration and not slow" test_*.py
) else if "%TEST_TYPE%"=="integration" (
    echo Running integration tests...
    %PYTEST_CMD% -m integration test_integration*.py
) else if "%TEST_TYPE%"=="api" (
    echo Running API tests...
    %PYTEST_CMD% test_api_endpoints.py
) else if "%TEST_TYPE%"=="services" (
    echo Running service tests...
    %PYTEST_CMD% test_services.py
) else if "%TEST_TYPE%"=="middleware" (
    echo Running middleware tests...
    %PYTEST_CMD% test_middleware.py
) else if "%TEST_TYPE%"=="fast" (
    echo Running fast tests...
    %PYTEST_CMD% -m "not slow" test_*.py
) else if "%TEST_TYPE%"=="all" (
    echo Running all tests...
    %PYTEST_CMD% test_*.py
) else (
    echo Unknown test type: %TEST_TYPE%
    echo Usage: %0 [unit^|integration^|api^|services^|middleware^|fast^|all] [coverage:true^|false]
    exit /b 1
)

REM Check exit code
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ==========================================
    echo All tests passed!
    echo ==========================================
    if "%COVERAGE%"=="true" (
        echo.
        echo Coverage report generated in htmlcov\index.html
    )
) else (
    echo.
    echo ==========================================
    echo Some tests failed!
    echo ==========================================
    exit /b 1
)



