@echo off
echo ============================================================
echo   Configuracion de Token de HuggingFace
echo ============================================================
echo.
echo Este script te ayudara a configurar el token necesario
echo para acceder al modelo Flux2.
echo.
echo IMPORTANTE: Necesitas:
echo   1. Una cuenta en HuggingFace (gratis)
echo   2. Un token de acceso (Read permission)
echo   3. Aceptar los terminos del modelo
echo.
echo ============================================================
echo.

set /p TOKEN="Pega tu token de HuggingFace aqui: "

if "%TOKEN%"=="" (
    echo.
    echo Error: No se proporciono token.
    pause
    exit /b 1
)

echo.
echo Configurando token para esta sesion...
set HUGGINGFACE_TOKEN=%TOKEN%

echo.
echo ============================================================
echo   Token configurado exitosamente!
echo ============================================================
echo.
echo El token esta configurado para esta sesion de terminal.
echo.
echo Para configurarlo permanentemente, ejecuta:
echo   setx HUGGINGFACE_TOKEN "%TOKEN%"
echo.
echo Ahora puedes ejecutar:
echo   python run_server.py
echo.
echo ============================================================
echo.

pause


