@echo off
echo ========================================
echo    BLATAM ACADEMY MIGRATION TOOL
echo ========================================
echo.

echo Choose migration option:
echo 1. Dry Run (simulation only)
echo 2. Full Migration with Backup
echo 3. Full Migration without Backup
echo 4. Exit
echo.

set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    echo.
    echo Running DRY RUN simulation...
    powershell -ExecutionPolicy Bypass -File "migrate_to_e_drive.ps1" -DryRun
) else if "%choice%"=="2" (
    echo.
    echo Running FULL MIGRATION with backup...
    powershell -ExecutionPolicy Bypass -File "migrate_to_e_drive.ps1"
) else if "%choice%"=="3" (
    echo.
    echo Running FULL MIGRATION without backup...
    powershell -ExecutionPolicy Bypass -File "migrate_to_e_drive.ps1" -SkipBackup
) else if "%choice%"=="4" (
    echo Exiting...
    exit /b 0
) else (
    echo Invalid choice. Please run the script again.
    pause
    exit /b 1
)

echo.
echo Migration process completed.
pause 