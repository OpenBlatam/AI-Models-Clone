@echo off
echo.
echo ===============================================
echo 💾 BLATAM-ACADEMY MIGRATION TO E:\ DRIVE
echo ===============================================
echo.
echo This script will migrate the entire project to E:\ drive
echo to free up space on C:\ drive.
echo.
echo Current location: C:\Users\USER\blatam-academy
echo New location:     E:\blatam-academy
echo.
echo Features:
echo ✅ Smart migration (excludes heavy unnecessary files)
echo ✅ Backup of critical files
echo ✅ Integrity verification
echo ✅ Progress tracking
echo.
pause
echo.
echo 🚀 Starting migration...
echo.

python MIGRATE_TO_E_DRIVE.py

echo.
echo ===============================================
echo Migration script completed.
echo Check the output above for results.
echo.
echo If successful, you can now access your project at:
echo E:\blatam-academy
echo.
echo Remember to update your IDE/editor paths!
echo ===============================================
echo.
pause 