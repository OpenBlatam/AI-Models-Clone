#!/bin/bash

echo "========================================"
echo "TikTok Scheduler - Iniciando Servidor"
echo "========================================"
echo ""

# Verificar si Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 no está instalado"
    exit 1
fi

# Verificar si las dependencias están instaladas
echo "Verificando dependencias..."
if ! python3 -c "import flask" 2>/dev/null; then
    echo "Instalando dependencias..."
    pip3 install -r requirements_tiktok_scheduler.txt
    if [ $? -ne 0 ]; then
        echo "ERROR: No se pudieron instalar las dependencias"
        exit 1
    fi
fi

# Cambiar al directorio del script
cd "$(dirname "$0")"

# Iniciar el servidor
echo ""
echo "Iniciando servidor en http://localhost:8000"
echo "Presiona Ctrl+C para detener el servidor"
echo ""
python3 tiktok_scheduler_backend.py








