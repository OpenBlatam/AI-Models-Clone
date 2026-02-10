@echo off
REM Setup script for AI Job Replacement Helper (Windows)

echo 🚀 Setting up AI Job Replacement Helper...

REM Crear entorno virtual
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activar entorno virtual
echo 🔌 Activating virtual environment...
call venv\Scripts\activate.bat

REM Instalar dependencias
echo 📥 Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Crear directorios necesarios
echo 📁 Creating directories...
if not exist "logs" mkdir logs
if not exist "data" mkdir data
if not exist "exports" mkdir exports

REM Copiar .env.example si no existe .env
if not exist ".env" (
    echo ⚙️  Creating .env file...
    copy .env.example .env
    echo ⚠️  Please edit .env file with your configuration
)

echo ✅ Setup complete!
echo 📝 Next steps:
echo    1. Edit .env file with your configuration
echo    2. Run: python main.py
echo    3. Visit: http://localhost:8030

pause




