@echo off
echo ========================================
echo AI Search Model - Instalacion
echo ========================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado o no esta en el PATH
    echo Por favor instala Python 3.8 o superior desde https://python.org
    pause
    exit /b 1
)

echo Python encontrado:
python --version

REM Verificar Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js no esta instalado o no esta en el PATH
    echo Por favor instala Node.js 16 o superior desde https://nodejs.org
    pause
    exit /b 1
)

echo Node.js encontrado:
node --version
echo.

REM Crear entorno virtual
echo Creando entorno virtual de Python...
python -m venv venv
if errorlevel 1 (
    echo ERROR: No se pudo crear el entorno virtual
    pause
    exit /b 1
)

REM Activar entorno virtual
echo Activando entorno virtual...
call venv\Scripts\activate.bat

REM Instalar dependencias de Python
echo Instalando dependencias de Python...
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: No se pudieron instalar las dependencias de Python
    pause
    exit /b 1
)

REM Instalar dependencias del frontend
echo Instalando dependencias del frontend...
cd frontend
npm install
if errorlevel 1 (
    echo ERROR: No se pudieron instalar las dependencias del frontend
    pause
    exit /b 1
)
cd ..

REM Crear archivo .env si no existe
if not exist .env (
    echo Creando archivo de configuracion...
    copy env.example .env
)

echo.
echo ========================================
echo Instalacion completada exitosamente!
echo ========================================
echo.
echo Para iniciar el sistema:
echo 1. Ejecuta: python start.py
echo 2. Abre: http://localhost:3000
echo 3. API: http://localhost:8000/docs
echo.
echo Para ejecutar la demostracion:
echo python demo.py
echo.
pause



























