@echo off
REM Script de inicio para Web Content Extractor AI (Windows)

echo Iniciando Web Content Extractor AI...

REM Verificar variables de entorno
if "%OPENROUTER_API_KEY%"=="" (
    echo ADVERTENCIA: OPENROUTER_API_KEY no esta configurada
    echo Crea un archivo .env con tu API key
)

REM Crear entorno virtual si no existe
if not exist "venv" (
    echo Creando entorno virtual...
    python -m venv venv
)

call venv\Scripts\activate.bat

echo Instalando dependencias...
pip install -q -r requirements.txt

echo Iniciando servidor...
python main.py








