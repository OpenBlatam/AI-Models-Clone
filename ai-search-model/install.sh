#!/bin/bash

echo "========================================"
echo "AI Search Model - Instalacion"
echo "========================================"
echo

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes con color
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar Python
print_status "Verificando Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    print_success "Python encontrado: $PYTHON_VERSION"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version 2>&1 | cut -d' ' -f2)
    print_success "Python encontrado: $PYTHON_VERSION"
    PYTHON_CMD="python"
else
    print_error "Python no esta instalado o no esta en el PATH"
    echo "Por favor instala Python 3.8 o superior desde https://python.org"
    exit 1
fi

# Verificar Node.js
print_status "Verificando Node.js..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    print_success "Node.js encontrado: $NODE_VERSION"
else
    print_error "Node.js no esta instalado o no esta en el PATH"
    echo "Por favor instala Node.js 16 o superior desde https://nodejs.org"
    exit 1
fi

# Verificar npm
print_status "Verificando npm..."
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    print_success "npm encontrado: $NPM_VERSION"
else
    print_error "npm no esta instalado"
    exit 1
fi

echo

# Crear entorno virtual
print_status "Creando entorno virtual de Python..."
if [ ! -d "venv" ]; then
    $PYTHON_CMD -m venv venv
    if [ $? -eq 0 ]; then
        print_success "Entorno virtual creado"
    else
        print_error "No se pudo crear el entorno virtual"
        exit 1
    fi
else
    print_warning "Entorno virtual ya existe"
fi

# Activar entorno virtual
print_status "Activando entorno virtual..."
source venv/bin/activate
if [ $? -eq 0 ]; then
    print_success "Entorno virtual activado"
else
    print_error "No se pudo activar el entorno virtual"
    exit 1
fi

# Actualizar pip
print_status "Actualizando pip..."
pip install --upgrade pip
if [ $? -eq 0 ]; then
    print_success "pip actualizado"
else
    print_warning "No se pudo actualizar pip"
fi

# Instalar dependencias de Python
print_status "Instalando dependencias de Python..."
pip install -r requirements.txt
if [ $? -eq 0 ]; then
    print_success "Dependencias de Python instaladas"
else
    print_error "No se pudieron instalar las dependencias de Python"
    exit 1
fi

# Instalar dependencias del frontend
print_status "Instalando dependencias del frontend..."
cd frontend
npm install
if [ $? -eq 0 ]; then
    print_success "Dependencias del frontend instaladas"
else
    print_error "No se pudieron instalar las dependencias del frontend"
    exit 1
fi
cd ..

# Crear archivo .env si no existe
if [ ! -f ".env" ]; then
    print_status "Creando archivo de configuracion..."
    cp env.example .env
    print_success "Archivo .env creado"
else
    print_warning "Archivo .env ya existe"
fi

# Crear directorios necesarios
print_status "Creando directorios necesarios..."
mkdir -p backups
mkdir -p logs
print_success "Directorios creados"

# Ejecutar pruebas del sistema
print_status "Ejecutando pruebas del sistema..."
$PYTHON_CMD test_system.py
if [ $? -eq 0 ]; then
    print_success "Pruebas del sistema exitosas"
else
    print_warning "Algunas pruebas fallaron, pero la instalacion continua"
fi

echo
echo "========================================"
echo "Instalacion completada exitosamente!"
echo "========================================"
echo
echo "Para iniciar el sistema:"
echo "1. Ejecuta: $PYTHON_CMD start.py"
echo "2. Abre: http://localhost:3000"
echo "3. API: http://localhost:8000/docs"
echo
echo "Para ejecutar la demostracion:"
echo "$PYTHON_CMD demo.py"
echo
echo "Para ejecutar las pruebas:"
echo "$PYTHON_CMD test_system.py"
echo
echo "Documentacion completa en README.md"
echo



























