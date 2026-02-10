@echo off
echo ========================================
echo Abriendo Safe Tensors Viewer
echo ========================================
echo.

cd /d "%~dp0"
python list_safe_tensors.py --html --open

pause


