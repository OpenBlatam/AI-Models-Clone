@echo off
REM Bulk Chat - Windows Start Script
REM ===================================

echo.
echo ========================================
echo    Bulk Chat - Sistema de Chat Continuo
echo ========================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no encontrado. Por favor instala Python 3.8+
    pause
    exit /b 1
)

REM Cambiar al directorio del script
cd /d "%~dp0"

REM Verificar si estamos en el directorio correcto
if not exist "main.py" (
    echo [ERROR] No se encuentra main.py. Asegurate de estar en el directorio correcto.
    pause
    exit /b 1
)

REM Verificar dependencias básicas
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo [ADVERTENCIA] FastAPI no encontrado. Instalando dependencias...
    python install.py
    if errorlevel 1 (
        echo [ERROR] Error al instalar dependencias.
        pause
        exit /b 1
    )
)

REM Leer argumentos
set LLM_PROVIDER=mock
set PORT=8006
set HOST=0.0.0.0

if "%1"=="--help" goto :help
if "%1"=="-h" goto :help
if not "%1"=="" set LLM_PROVIDER=%1
if not "%2"=="" set PORT=%2

:start
echo.
echo Iniciando servidor...
echo Proveedor LLM: %LLM_PROVIDER%
echo Puerto: %PORT%
echo.
echo Para detener el servidor, presiona Ctrl+C
echo.

python -m bulk_chat.main --llm-provider %LLM_PROVIDER% --port %PORT% --host %HOST%

if errorlevel 1 (
    echo.
    echo [ERROR] Error al iniciar el servidor.
    pause
    exit /b 1
)

goto :end

:help
echo.
echo Uso: start.bat [provider] [port]
echo.
echo Opciones:
echo   provider  - Proveedor LLM (openai, anthropic, mock) [default: mock]
echo   port      - Puerto del servidor [default: 8006]
echo.
echo Ejemplos:
echo   start.bat                    - Inicia con modo mock en puerto 8006
echo   start.bat openai 8006        - Inicia con OpenAI en puerto 8006
echo   start.bat mock 9000          - Inicia con mock en puerto 9000
echo.
pause
exit /b 0

:end
pause
















