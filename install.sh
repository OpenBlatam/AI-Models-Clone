#!/bin/bash

# 🚀 **SCRIPT DE INSTALACIÓN AUTOMATIZADA**
# Sistema de Gestión de Recursos Inteligente
# Instalación completa y configuración automática

set -e  # Exit on any error

# ============================================================================
# 🎨 **CONFIGURACIÓN DE COLORES**
# ============================================================================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# ============================================================================
# 📋 **FUNCIONES DE UTILIDAD**
# ============================================================================

print_header() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                🚀 SISTEMA DE GESTIÓN DE RECURSOS             ║"
    echo "║                    INTELIGENTE - INSTALADOR                 ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_step() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_info() {
    echo -e "${PURPLE}[INFO]${NC} $1"
}

# ============================================================================
# 🔍 **VERIFICACIÓN DE REQUISITOS**
# ============================================================================

check_requirements() {
    print_header
    print_step "Verificando requisitos del sistema..."
    
    # Verificar Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python encontrado: $PYTHON_VERSION"
        
        # Verificar versión mínima
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)"; then
            print_success "Versión de Python compatible (>= 3.9)"
        else
            print_error "Se requiere Python 3.9 o superior"
            exit 1
        fi
    else
        print_error "Python 3 no encontrado. Por favor instala Python 3.9+"
        exit 1
    fi
    
    # Verificar pip
    if command -v pip3 &> /dev/null; then
        print_success "pip3 encontrado"
    else
        print_error "pip3 no encontrado. Por favor instala pip"
        exit 1
    fi
    
    # Verificar git
    if command -v git &> /dev/null; then
        print_success "Git encontrado"
    else
        print_warning "Git no encontrado. Algunas funcionalidades pueden no estar disponibles"
    fi
    
    # Verificar Docker (opcional)
    if command -v docker &> /dev/null; then
        print_success "Docker encontrado"
        DOCKER_AVAILABLE=true
    else
        print_warning "Docker no encontrado. La instalación será local"
        DOCKER_AVAILABLE=false
    fi
    
    # Verificar CUDA (opcional)
    if command -v nvidia-smi &> /dev/null; then
        print_success "NVIDIA GPU detectada"
        CUDA_AVAILABLE=true
    else
        print_info "NVIDIA GPU no detectada. El sistema funcionará sin GPU"
        CUDA_AVAILABLE=false
    fi
}

# ============================================================================
# 🐍 **CONFIGURACIÓN DE ENTORNO VIRTUAL**
# ============================================================================

setup_virtual_environment() {
    print_step "Configurando entorno virtual..."
    
    # Crear entorno virtual
    if [ ! -d "venv" ]; then
        print_info "Creando entorno virtual..."
        python3 -m venv venv
        print_success "Entorno virtual creado"
    else
        print_info "Entorno virtual ya existe"
    fi
    
    # Activar entorno virtual
    print_info "Activando entorno virtual..."
    source venv/bin/activate
    
    # Actualizar pip
    print_info "Actualizando pip..."
    pip install --upgrade pip setuptools wheel
    
    print_success "Entorno virtual configurado"
}

# ============================================================================
# 📦 **INSTALACIÓN DE DEPENDENCIAS**
# ============================================================================

install_dependencies() {
    print_step "Instalando dependencias..."
    
    # Verificar que el entorno virtual esté activado
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        print_error "Entorno virtual no activado"
        exit 1
    fi
    
    # Instalar dependencias base
    print_info "Instalando dependencias base..."
    pip install -r requirements_optimized.txt
    
    # Instalar dependencias opcionales según disponibilidad
    if [ "$CUDA_AVAILABLE" = true ]; then
        print_info "Instalando dependencias GPU..."
        pip install -e ".[gpu]"
    fi
    
    if [ "$DOCKER_AVAILABLE" = true ]; then
        print_info "Instalando dependencias Docker..."
        pip install -e ".[distributed]"
    fi
    
    # Instalar dependencias de desarrollo
    print_info "Instalando dependencias de desarrollo..."
    pip install -e ".[dev]"
    
    print_success "Dependencias instaladas correctamente"
}

# ============================================================================
# 🔧 **CONFIGURACIÓN DEL SISTEMA**
# ============================================================================

setup_configuration() {
    print_step "Configurando sistema..."
    
    # Crear directorios necesarios
    print_info "Creando directorios..."
    mkdir -p logs
    mkdir -p data
    mkdir -p models
    mkdir -p config
    mkdir -p tests
    mkdir -p docs
    
    # Crear archivo de configuración por defecto si no existe
    if [ ! -f "resource_config.yaml" ]; then
        print_info "Creando archivo de configuración por defecto..."
        cat > resource_config.yaml << 'EOF'
# Configuración del Sistema de Gestión de Recursos Inteligente
system:
  name: "Intelligent Resource Management System"
  version: "1.0.0"
  auto_start: true
  monitoring_interval: 30
  optimization_interval: 5

resources:
  cpu_memory:
    resource_type: "memory"
    max_usage: 0.85
    optimal_usage: 0.65
    critical_threshold: 0.92
    auto_optimize: true
    prediction_horizon: 300
    
  gpu:
    resource_type: "gpu"
    max_usage: 0.80
    optimal_usage: 0.60
    critical_threshold: 0.90
    auto_optimize: true
    prediction_horizon: 180

optimization:
  priority_levels:
    0: "emergency"
    1: "critical"
    2: "high"
    3: "low"

monitoring:
  metrics_history_size: 100
  alert_thresholds:
    warning: 0.75
    critical: 0.90
    emergency: 0.95
EOF
        print_success "Archivo de configuración creado"
    else
        print_info "Archivo de configuración ya existe"
    fi
    
    # Crear archivo .env por defecto
    if [ ! -f ".env" ]; then
        print_info "Creando archivo .env..."
        cat > .env << 'EOF'
# Variables de entorno para el Sistema de Gestión de Recursos Inteligente
GRADIO_SERVER_NAME=0.0.0.0
GRADIO_SERVER_PORT=7860
GRADIO_SHARE=False
MONITORING_ENABLED=true
GPU_ENABLED=true
LOG_LEVEL=INFO
REDIS_URL=redis://localhost:6379
EOF
        print_success "Archivo .env creado"
    else
        print_info "Archivo .env ya existe"
    fi
    
    print_success "Configuración del sistema completada"
}

# ============================================================================
# 🧪 **EJECUCIÓN DE TESTS**
# ============================================================================

run_tests() {
    print_step "Ejecutando tests del sistema..."
    
    # Verificar que el entorno virtual esté activado
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        print_error "Entorno virtual no activado"
        return 1
    fi
    
    # Ejecutar tests
    if python -m pytest test_intelligent_resource_manager.py -v; then
        print_success "Tests ejecutados correctamente"
    else
        print_warning "Algunos tests fallaron. Revisa los logs para más detalles"
    fi
}

# ============================================================================
# 🐳 **CONFIGURACIÓN DE DOCKER (OPCIONAL)**
# ============================================================================

setup_docker() {
    if [ "$DOCKER_AVAILABLE" = true ]; then
        print_step "Configurando Docker..."
        
        # Construir imagen Docker
        print_info "Construyendo imagen Docker..."
        docker build -t intelligent-resource-manager .
        
        if [ $? -eq 0 ]; then
            print_success "Imagen Docker construida correctamente"
        else
            print_warning "Error al construir imagen Docker"
        fi
        
        # Crear red Docker si no existe
        if ! docker network ls | grep -q "resource-network"; then
            print_info "Creando red Docker..."
            docker network create resource-network
            print_success "Red Docker creada"
        fi
    else
        print_info "Docker no disponible, saltando configuración de Docker"
    fi
}

# ============================================================================
# 📊 **VERIFICACIÓN DE INSTALACIÓN**
# ============================================================================

verify_installation() {
    print_step "Verificando instalación..."
    
    # Verificar que el entorno virtual esté activado
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        print_error "Entorno virtual no activado"
        return 1
    fi
    
    # Verificar imports principales
    print_info "Verificando imports..."
    
    if python -c "import torch; print(f'PyTorch: {torch.__version__}')"; then
        print_success "PyTorch instalado correctamente"
    else
        print_error "Error al importar PyTorch"
        return 1
    fi
    
    if python -c "import gradio; print(f'Gradio: {gradio.__version__}')"; then
        print_success "Gradio instalado correctamente"
    else
        print_error "Error al importar Gradio"
        return 1
    fi
    
    if python -c "import psutil; print('psutil: OK')"; then
        print_success "psutil instalado correctamente"
    else
        print_error "Error al importar psutil"
        return 1
    fi
    
    if python -c "import numpy; print(f'NumPy: {numpy.__version__}')"; then
        print_success "NumPy instalado correctamente"
    else
        print_error "Error al importar NumPy"
        return 1
    fi
    
    print_success "Verificación de instalación completada"
}

# ============================================================================
# 🎮 **DEMOSTRACIÓN RÁPIDA**
# ============================================================================

run_demo() {
    print_step "Ejecutando demostración rápida..."
    
    # Verificar que el entorno virtual esté activado
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        print_error "Entorno virtual no activado"
        return 1
    fi
    
    print_info "Iniciando sistema de gestión de recursos..."
    print_info "Presiona Ctrl+C para detener"
    
    # Ejecutar demo
    python intelligent_resource_manager.py &
    DEMO_PID=$!
    
    # Esperar un momento para que inicie
    sleep 5
    
    # Verificar si está ejecutándose
    if kill -0 $DEMO_PID 2>/dev/null; then
        print_success "Sistema iniciado correctamente"
        print_info "El sistema está ejecutándose en segundo plano"
        print_info "Para detener: kill $DEMO_PID"
    else
        print_error "Error al iniciar el sistema"
        return 1
    fi
}

# ============================================================================
# 📚 **DOCUMENTACIÓN Y AYUDA**
# ============================================================================

show_help() {
    print_header
    echo -e "${WHITE}Uso:${NC}"
    echo "  $0 [OPCIÓN]"
    echo ""
    echo -e "${WHITE}Opciones:${NC}"
    echo "  --help, -h          Mostrar esta ayuda"
    echo "  --full              Instalación completa (recomendado)"
    echo "  --minimal           Instalación mínima"
    echo "  --docker            Instalación con Docker"
    echo "  --test              Solo ejecutar tests"
    echo "  --demo              Solo ejecutar demo"
    echo ""
    echo -e "${WHITE}Ejemplos:${NC}"
    echo "  $0 --full           # Instalación completa"
    echo "  $0 --minimal        # Instalación básica"
    echo "  $0 --test           # Solo tests"
    echo ""
}

# ============================================================================
# 🚀 **FUNCIÓN PRINCIPAL**
# ============================================================================

main() {
    case "${1:---full}" in
        --help|-h)
            show_help
            exit 0
            ;;
        --full)
            print_header
            check_requirements
            setup_virtual_environment
            install_dependencies
            setup_configuration
            setup_docker
            run_tests
            verify_installation
            print_success "¡Instalación completa finalizada!"
            print_info "Para activar el entorno virtual: source venv/bin/activate"
            print_info "Para ejecutar el sistema: python resource_manager_demo.py"
            ;;
        --minimal)
            print_header
            check_requirements
            setup_virtual_environment
            install_dependencies
            setup_configuration
            verify_installation
            print_success "¡Instalación mínima finalizada!"
            ;;
        --docker)
            print_header
            check_requirements
            setup_docker
            print_success "¡Configuración de Docker finalizada!"
            ;;
        --test)
            print_header
            check_requirements
            setup_virtual_environment
            run_tests
            ;;
        --demo)
            print_header
            check_requirements
            setup_virtual_environment
            run_demo
            ;;
        *)
            print_error "Opción desconocida: $1"
            show_help
            exit 1
            ;;
    esac
}

# ============================================================================
# 🎯 **EJECUCIÓN**
# ============================================================================

# Verificar si se ejecuta directamente
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
