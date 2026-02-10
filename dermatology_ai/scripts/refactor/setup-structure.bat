@echo off
REM ============================================================================
REM Setup Refactored Structure
REM Creates directory structure for refactoring
REM ============================================================================

setlocal

set PROJECT_ROOT=%~dp0..\..
cd /d "%PROJECT_ROOT%"

echo ==========================================
echo Setting up Refactored Structure
echo ==========================================
echo.

REM Create docs structure
if not exist "docs" mkdir "docs"
if not exist "docs\architecture" mkdir "docs\architecture"
if not exist "docs\dependencies" mkdir "docs\dependencies"
if not exist "docs\features" mkdir "docs\features"
if not exist "docs\guides" mkdir "docs\guides"
if not exist "docs\api" mkdir "docs\api"
echo [OK] Created docs structure

REM Create config structure
if not exist "config\environments" mkdir "config\environments"
if not exist "config\schemas" mkdir "config\schemas"
if not exist "config\models" mkdir "config\models"
echo [OK] Created config structure

REM Create scripts/refactor if needed
if not exist "scripts\refactor" mkdir "scripts\refactor"
echo [OK] Created scripts\refactor directory

echo.
echo ==========================================
echo Structure setup completed
echo ==========================================

endlocal



