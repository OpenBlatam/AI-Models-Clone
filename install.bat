@echo off
REM 🚀 **SCRIPT DE INSTALACIÓN AUTOMATIZADA PARA WINDOWS**
REM Sistema de Gestión de Recursos Inteligente
REM Instalación completa y configuración automática

setlocal enabledelayedexpansion

REM ============================================================================
REM 🎨 **CONFIGURACIÓN DE COLORES**
REM ============================================================================
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "PURPLE=[95m"
set "CYAN=[96m"
set "WHITE=[97m"
set "NC=[0m"

REM ============================================================================
REM 📋 **FUNCIONES DE UTILIDAD**
REM ============================================================================

:print_header
echo %CYAN%
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                🚀 SISTEMA DE GESTIÓN DE RECURSOS             ║
echo ║                    INTELIGENTE - INSTALADOR                 ║
echo ╚══════════════════════════════════════════════════════════════╝
echo %NC%
goto :eof

:print_step
echo %BLUE%[INFO]%NC% %~1
goto :eof

:print_success
echo %GREEN%[SUCCESS]%NC% %~1
goto :eof

:print_warning
echo %YELLOW%[WARNING]%NC% %~1
goto :eof

:print_error
echo %RED%[ERROR]%NC% %~1
goto :eof

:print_info
echo %PURPLE%[INFO]%NC% %~1
goto :eof

REM ============================================================================
REM 🔍 **VERIFICACIÓN DE REQUISITOS**
REM ============================================================================

:check_requirements
call :print_header
call :print_step "Verificando requisitos del sistema..."

REM Verificar Python
python --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    call :print_success "Python encontrado: %PYTHON_VERSION%"
    
    REM Verificar versión mínima
    python -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)" >nul 2>&1
    if %errorlevel% equ 0 (
        call :print_success "Versión de Python compatible (>= 3.9)"
    ) else (
        call :print_error "Se requiere Python 3.9 o superior"
        exit /b 1
    )
) else (
    call :print_error "Python no encontrado. Por favor instala Python 3.9+"
    exit /b 1
)

REM Verificar pip
pip --version >nul 2>&1
if %errorlevel% equ 0 (
    call :print_success "pip encontrado"
) else (
    call :print_error "pip no encontrado. Por favor instala pip"
    exit /b 1
)

REM Verificar git
git --version >nul 2>&1
if %errorlevel% equ 0 (
    call :print_success "Git encontrado"
) else (
    call :print_warning "Git no encontrado. Algunas funcionalidades pueden no estar disponibles"
)

REM Verificar Docker (opcional)
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    call :print_success "Docker encontrado"
    set DOCKER_AVAILABLE=true
) else (
    call :print_warning "Docker no encontrado. La instalación será local"
    set DOCKER_AVAILABLE=false
)

REM Verificar CUDA (opcional)
nvidia-smi >nul 2>&1
if %errorlevel% equ 0 (
    call :print_success "NVIDIA GPU detectada"
    set CUDA_AVAILABLE=true
) else (
    call :print_info "NVIDIA GPU no detectada. El sistema funcionará sin GPU"
    set CUDA_AVAILABLE=false
)
goto :eof

REM ============================================================================
REM 🐍 **CONFIGURACIÓN DE ENTORNO VIRTUAL**
REM ============================================================================

:setup_virtual_environment
call :print_step "Configurando entorno virtual..."

REM Crear entorno virtual
if not exist "venv" (
    call :print_info "Creando entorno virtual..."
    python -m venv venv
    call :print_success "Entorno virtual creado"
) else (
    call :print_info "Entorno virtual ya existe"
)

REM Activar entorno virtual
call :print_info "Activando entorno virtual..."
call venv\Scripts\activate.bat

REM Actualizar pip
call :print_info "Actualizando pip..."
python -m pip install --upgrade pip setuptools wheel

call :print_success "Entorno virtual configurado"
goto :eof

REM ============================================================================
REM 📦 **INSTALACIÓN DE DEPENDENCIAS**
REM ============================================================================

:install_dependencies
call :print_step "Instalando dependencias..."

REM Verificar que el entorno virtual esté activado
if not defined VIRTUAL_ENV (
    call :print_error "Entorno virtual no activado"
    exit /b 1
)

REM Instalar dependencias base
call :print_info "Instalando dependencias base..."
pip install -r requirements_optimized.txt

REM Instalar dependencias opcionales según disponibilidad
if "%CUDA_AVAILABLE%"=="true" (
    call :print_info "Instalando dependencias GPU..."
    pip install -e ".[gpu]"
)

if "%DOCKER_AVAILABLE%"=="true" (
    call :print_info "Instalando dependencias Docker..."
    pip install -e ".[distributed]"
)

REM Instalar dependencias de desarrollo
call :print_info "Instalando dependencias de desarrollo..."
pip install -e ".[dev]"

call :print_success "Dependencias instaladas correctamente"
goto :eof

REM ============================================================================
REM 🔧 **CONFIGURACIÓN DEL SISTEMA**
REM ============================================================================

:setup_configuration
call :print_step "Configurando sistema..."

REM Crear directorios necesarios
call :print_info "Creando directorios..."
if not exist "logs" mkdir logs
if not exist "data" mkdir data
if not exist "models" mkdir models
if not exist "config" mkdir config
if not exist "tests" mkdir tests
if not exist "docs" mkdir docs

REM Crear archivo de configuración por defecto si no existe
if not exist "resource_config.yaml" (
    call :print_info "Creando archivo de configuración por defecto..."
    (
        echo # Configuración del Sistema de Gestión de Recursos Inteligente
        echo system:
        echo   name: "Intelligent Resource Management System"
        echo   version: "1.0.0"
        echo   auto_start: true
        echo   monitoring_interval: 30
        echo   optimization_interval: 5
        echo.
        echo resources:
        echo   cpu_memory:
        echo     resource_type: "memory"
        echo     max_usage: 0.85
        echo     optimal_usage: 0.65
        echo     critical_threshold: 0.92
        echo     auto_optimize: true
        echo     prediction_horizon: 300
        echo.
        echo   gpu:
        echo     resource_type: "gpu"
        echo     max_usage: 0.80
        echo     optimal_usage: 0.60
        echo     critical_threshold: 0.90
        echo     auto_optimize: true
        echo     prediction_horizon: 180
        echo.
        echo optimization:
        echo   priority_levels:
        echo     0: "emergency"
        echo     1: "critical"
        echo     2: "high"
        echo     3: "low"
        echo.
        echo monitoring:
        echo   metrics_history_size: 100
        echo   alert_thresholds:
        echo     warning: 0.75
        echo     critical: 0.90
        echo     emergency: 0.95
    ) > resource_config.yaml
    call :print_success "Archivo de configuración creado"
) else (
    call :print_info "Archivo de configuración ya existe"
)

REM Crear archivo .env por defecto
if not exist ".env" (
    call :print_info "Creando archivo .env..."
    (
        echo # Variables de entorno para el Sistema de Gestión de Recursos Inteligente
        echo GRADIO_SERVER_NAME=0.0.0.0
        echo GRADIO_SERVER_PORT=7860
        echo GRADIO_SHARE=False
        echo MONITORING_ENABLED=true
        echo GPU_ENABLED=true
        echo LOG_LEVEL=INFO
        echo REDIS_URL=redis://localhost:6379
    ) > .env
    call :print_success "Archivo .env creado"
) else (
    call :print_info "Archivo .env ya existe"
)

call :print_success "Configuración del sistema completada"
goto :eof

REM ============================================================================
REM 🧪 **EJECUCIÓN DE TESTS**
REM ============================================================================

:run_tests
call :print_step "Ejecutando tests del sistema..."

REM Verificar que el entorno virtual esté activado
if not defined VIRTUAL_ENV (
    call :print_error "Entorno virtual no activado"
    exit /b 1
)

REM Ejecutar tests
python -m pytest test_intelligent_resource_manager.py -v
if %errorlevel% equ 0 (
    call :print_success "Tests ejecutados correctamente"
) else (
    call :print_warning "Algunos tests fallaron. Revisa los logs para más detalles"
)
goto :eof

REM ============================================================================
REM 🐳 **CONFIGURACIÓN DE DOCKER (OPCIONAL)**
REM ============================================================================

:setup_docker
if "%DOCKER_AVAILABLE%"=="true" (
    call :print_step "Configurando Docker..."
    
    REM Construir imagen Docker
    call :print_info "Construyendo imagen Docker..."
    docker build -t intelligent-resource-manager .
    
    if %errorlevel% equ 0 (
        call :print_success "Imagen Docker construida correctamente"
    ) else (
        call :print_warning "Error al construir imagen Docker"
    )
    
    REM Crear red Docker si no existe
    docker network ls | findstr "resource-network" >nul
    if %errorlevel% neq 0 (
        call :print_info "Creando red Docker..."
        docker network create resource-network
        call :print_success "Red Docker creada"
    )
) else (
    call :print_info "Docker no disponible, saltando configuración de Docker"
)
goto :eof

REM ============================================================================
REM 📊 **VERIFICACIÓN DE INSTALACIÓN**
REM ============================================================================

:verify_installation
call :print_step "Verificando instalación..."

REM Verificar que el entorno virtual esté activado
if not defined VIRTUAL_ENV (
    call :print_error "Entorno virtual no activado"
    exit /b 1
)

REM Verificar imports principales
call :print_info "Verificando imports..."

python -c "import torch; print(f'PyTorch: {torch.__version__}')" >nul 2>&1
if %errorlevel% equ 0 (
    call :print_success "PyTorch instalado correctamente"
) else (
    call :print_error "Error al importar PyTorch"
    exit /b 1
)

python -c "import gradio; print(f'Gradio: {gradio.__version__}')" >nul 2>&1
if %errorlevel% equ 0 (
    call :print_success "Gradio instalado correctamente"
) else (
    call :print_error "Error al importar Gradio"
    exit /b 1
)

python -c "import psutil; print('psutil: OK')" >nul 2>&1
if %errorlevel% equ 0 (
    call :print_success "psutil instalado correctamente"
) else (
    call :print_error "Error al importar psutil"
    exit /b 1
)

python -c "import numpy; print(f'NumPy: {numpy.__version__}')" >nul 2>&1
if %errorlevel% equ 0 (
    call :print_success "NumPy instalado correctamente"
) else (
    call :print_error "Error al importar NumPy"
    exit /b 1
)

call :print_success "Verificación de instalación completada"
goto :eof

REM ============================================================================
REM 🎮 **DEMOSTRACIÓN RÁPIDA**
REM ============================================================================

:run_demo
call :print_step "Ejecutando demostración rápida..."

REM Verificar que el entorno virtual esté activado
if not defined VIRTUAL_ENV (
    call :print_error "Entorno virtual no activado"
    exit /b 1
)

call :print_info "Iniciando sistema de gestión de recursos..."
call :print_info "Presiona Ctrl+C para detener"

REM Ejecutar demo
start /B python intelligent_resource_manager.py
set DEMO_PID=%errorlevel%

REM Esperar un momento para que inicie
timeout /t 5 /nobreak >nul

REM Verificar si está ejecutándose
tasklist /FI "PID eq %DEMO_PID%" 2>nul | find /I "%DEMO_PID%" >nul
if %errorlevel% equ 0 (
    call :print_success "Sistema iniciado correctamente"
    call :print_info "El sistema está ejecutándose en segundo plano"
    call :print_info "Para detener: taskkill /PID %DEMO_PID%"
) else (
    call :print_error "Error al iniciar el sistema"
    exit /b 1
)
goto :eof

REM ============================================================================
REM 📚 **DOCUMENTACIÓN Y AYUDA**
REM ============================================================================

:show_help
call :print_header
echo %WHITE%Uso:%NC%
echo   %~nx0 [OPCIÓN]
echo.
echo %WHITE%Opciones:%NC%
echo   --help, -h          Mostrar esta ayuda
echo   --full              Instalación completa (recomendado)
echo   --minimal           Instalación mínima
echo   --docker            Instalación con Docker
echo   --test              Solo ejecutar tests
echo   --demo              Solo ejecutar demo
echo.
echo %WHITE%Ejemplos:%NC%
echo   %~nx0 --full           # Instalación completa
echo   %~nx0 --minimal        # Instalación básica
echo   %~nx0 --test           # Solo tests
echo.
goto :eof

REM ============================================================================
REM 🚀 **FUNCIÓN PRINCIPAL**
REM ============================================================================

:main
if "%~1"=="" set "1=--full"

if "%~1"=="--help" goto :show_help
if "%~1"=="-h" goto :show_help
if "%~1"=="--full" goto :install_full
if "%~1"=="--minimal" goto :install_minimal
if "%~1"=="--docker" goto :install_docker
if "%~1"=="--test" goto :install_test
if "%~1"=="--demo" goto :install_demo

call :print_error "Opción desconocida: %~1"
call :show_help
exit /b 1

:install_full
call :check_requirements
call :setup_virtual_environment
call :install_dependencies
call :setup_configuration
call :setup_docker
call :run_tests
call :verify_installation
call :print_success "¡Instalación completa finalizada!"
call :print_info "Para activar el entorno virtual: venv\Scripts\activate.bat"
call :print_info "Para ejecutar el sistema: python resource_manager_demo.py"
goto :end

:install_minimal
call :check_requirements
call :setup_virtual_environment
call :install_dependencies
call :setup_configuration
call :verify_installation
call :print_success "¡Instalación mínima finalizada!"
goto :end

:install_docker
call :check_requirements
call :setup_docker
call :print_success "¡Configuración de Docker finalizada!"
goto :end

:install_test
call :check_requirements
call :setup_virtual_environment
call :run_tests
goto :end

:install_demo
call :check_requirements
call :setup_virtual_environment
call :run_demo
goto :end

:end
pause
exit /b 0
