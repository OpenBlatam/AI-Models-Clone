@echo off
REM Script para ejecutar tests de Playwright en Windows

echo 🧪 Ejecutando Tests de Playwright
echo ==================================
echo.

REM Verificar que el servidor Next.js esté corriendo
echo ⚠️  Asegúrate de que el servidor Next.js esté corriendo:
echo    npm run dev
echo.
pause

REM Ejecutar tests
echo.
echo 🚀 Ejecutando tests...
call npm run test:e2e

echo.
echo ✅ Tests completados!
pause











