@echo off
REM Script to run all tests on Windows

echo Running bulk_chat tests...
echo ==========================

REM Run all tests
pytest tests\ -v --cov=bulk_chat --cov-report=term-missing

REM Run with coverage report
echo.
echo Generating coverage report...
pytest tests\ --cov=bulk_chat --cov-report=html

echo.
echo Tests completed! Coverage report in htmlcov\


