# 🚀 **MAKEFILE PARA SISTEMA DE GESTIÓN DE RECURSOS INTELIGENTE**
# Automatización de tareas comunes de desarrollo

.PHONY: help install install-dev install-gpu install-docker test test-cov lint format clean run demo docker-build docker-run docker-stop docs

# ============================================================================
# 🎯 **VARIABLES**
# ============================================================================
PYTHON := python
PIP := pip
PYTEST := pytest
BLACK := black
ISORT := isort
FLAKE8 := flake8
MYPY := mypy
DOCKER := docker
DOCKER_COMPOSE := docker-compose

# Directorios
SRC_DIR := .
TEST_DIR := tests
DOCS_DIR := docs
BUILD_DIR := build
DIST_DIR := dist

# Archivos principales
MAIN_FILE := intelligent_resource_manager.py
DEMO_FILE := resource_manager_demo.py
TEST_FILE := test_intelligent_resource_manager.py
CONFIG_FILE := resource_config.yaml

# ============================================================================
# 📋 **AYUDA**
# ============================================================================
help: ## Mostrar ayuda
	@echo "🚀 Sistema de Gestión de Recursos Inteligente - Makefile"
	@echo "=================================================="
	@echo ""
	@echo "Comandos disponibles:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Ejemplos:"
	@echo "  make install     # Instalación completa"
	@echo "  make test        # Ejecutar tests"
	@echo "  make run         # Ejecutar sistema"
	@echo "  make demo        # Ejecutar demo con interfaz"

# ============================================================================
# 📦 **INSTALACIÓN**
# ============================================================================
install: ## Instalación completa del sistema
	@echo "📦 Instalando dependencias..."
	$(PIP) install -r requirements_optimized.txt
	@echo "✅ Instalación completada"

install-dev: ## Instalación para desarrollo
	@echo "🔧 Instalando dependencias de desarrollo..."
	$(PIP) install -e ".[dev]"
	@echo "✅ Dependencias de desarrollo instaladas"

install-gpu: ## Instalación con soporte GPU
	@echo "🎮 Instalando dependencias GPU..."
	$(PIP) install -e ".[gpu]"
	@echo "✅ Dependencias GPU instaladas"

install-docker: ## Instalación con Docker
	@echo "🐳 Instalando dependencias Docker..."
	$(PIP) install -e ".[distributed]"
	@echo "✅ Dependencias Docker instaladas"

install-all: ## Instalación completa con todas las opciones
	@echo "🚀 Instalación completa con todas las opciones..."
	$(PIP) install -e ".[all]"
	@echo "✅ Instalación completa finalizada"

# ============================================================================
# 🧪 **TESTING**
# ============================================================================
test: ## Ejecutar tests
	@echo "🧪 Ejecutando tests..."
	$(PYTEST) $(TEST_FILE) -v

test-cov: ## Ejecutar tests con cobertura
	@echo "📊 Ejecutando tests con cobertura..."
	$(PYTEST) $(TEST_FILE) --cov=. --cov-report=html --cov-report=term

test-fast: ## Ejecutar tests rápidos
	@echo "⚡ Ejecutando tests rápidos..."
	$(PYTEST) $(TEST_FILE) -v -m "not slow"

test-gpu: ## Ejecutar tests que requieren GPU
	@echo "🎮 Ejecutando tests GPU..."
	$(PYTEST) $(TEST_FILE) -v -m "gpu"

test-integration: ## Ejecutar tests de integración
	@echo "🔗 Ejecutando tests de integración..."
	$(PYTEST) $(TEST_FILE) -v -m "integration"

# ============================================================================
# 🔧 **LINTING Y FORMATEO**
# ============================================================================
lint: ## Ejecutar linting
	@echo "🔍 Ejecutando linting..."
	$(FLAKE8) $(SRC_DIR)
	$(MYPY) $(SRC_DIR)

format: ## Formatear código
	@echo "🎨 Formateando código..."
	$(BLACK) $(SRC_DIR)
	$(ISORT) $(SRC_DIR)

format-check: ## Verificar formato sin cambiar
	@echo "✅ Verificando formato..."
	$(BLACK) --check $(SRC_DIR)
	$(ISORT) --check-only $(SRC_DIR)

# ============================================================================
# 🚀 **EJECUCIÓN**
# ============================================================================
run: ## Ejecutar sistema principal
	@echo "🚀 Ejecutando sistema de gestión de recursos..."
	$(PYTHON) $(MAIN_FILE)

demo: ## Ejecutar demo con interfaz Gradio
	@echo "🎮 Ejecutando demo con interfaz Gradio..."
	$(PYTHON) $(DEMO_FILE)

run-monitoring: ## Ejecutar solo monitoreo
	@echo "📊 Ejecutando monitoreo..."
	$(PYTHON) -c "from intelligent_resource_manager import IntelligentResourceOrchestrator; import asyncio; asyncio.run(IntelligentResourceOrchestrator().start())"

# ============================================================================
# 🐳 **DOCKER**
# ============================================================================
docker-build: ## Construir imagen Docker
	@echo "🐳 Construyendo imagen Docker..."
	$(DOCKER) build -t intelligent-resource-manager .

docker-run: ## Ejecutar contenedor Docker
	@echo "🚀 Ejecutando contenedor Docker..."
	$(DOCKER) run -p 7860:7860 --gpus all intelligent-resource-manager

docker-run-dev: ## Ejecutar contenedor Docker en modo desarrollo
	@echo "🔧 Ejecutando contenedor Docker en modo desarrollo..."
	$(DOCKER) run -it -p 7860:7860 -v $(PWD):/app intelligent-resource-manager:dev

docker-compose-up: ## Iniciar servicios con Docker Compose
	@echo "🐳 Iniciando servicios con Docker Compose..."
	$(DOCKER_COMPOSE) up -d

docker-compose-down: ## Detener servicios de Docker Compose
	@echo "🛑 Deteniendo servicios de Docker Compose..."
	$(DOCKER_COMPOSE) down

docker-compose-logs: ## Ver logs de Docker Compose
	@echo "📋 Mostrando logs de Docker Compose..."
	$(DOCKER_COMPOSE) logs -f

docker-stop: ## Detener todos los contenedores
	@echo "🛑 Deteniendo contenedores..."
	$(DOCKER) stop $$($(DOCKER) ps -q)

# ============================================================================
# 📚 **DOCUMENTACIÓN**
# ============================================================================
docs: ## Generar documentación
	@echo "📚 Generando documentación..."
	$(PYTHON) -m sphinx.cmd.build $(DOCS_DIR) $(BUILD_DIR)/docs

docs-serve: ## Servir documentación localmente
	@echo "🌐 Sirviendo documentación en http://localhost:8000..."
	$(PYTHON) -m http.server 8000 --directory $(BUILD_DIR)/docs

# ============================================================================
# 🧹 **LIMPIEZA**
# ============================================================================
clean: ## Limpiar archivos temporales
	@echo "🧹 Limpiando archivos temporales..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf $(BUILD_DIR) $(DIST_DIR)
	rm -rf .pytest_cache .coverage htmlcov
	rm -rf .mypy_cache .ruff_cache

clean-docker: ## Limpiar imágenes y contenedores Docker
	@echo "🐳 Limpiando Docker..."
	$(DOCKER) system prune -f
	$(DOCKER) image prune -f

clean-all: clean clean-docker ## Limpieza completa
	@echo "✨ Limpieza completa realizada"

# ============================================================================
# 📊 **MONITOREO Y PROFILING**
# ============================================================================
profile: ## Ejecutar profiling del sistema
	@echo "🔍 Ejecutando profiling..."
	$(PYTHON) -m pyinstrument $(MAIN_FILE)

profile-memory: ## Profiling de memoria
	@echo "💾 Profiling de memoria..."
	$(PYTHON) -m memory_profiler $(MAIN_FILE)

monitor: ## Monitorear recursos del sistema
	@echo "📊 Monitoreando recursos..."
	$(PYTHON) -c "import psutil; print(f'CPU: {psutil.cpu_percent()}%'); print(f'Memory: {psutil.virtual_memory().percent}%')"

# ============================================================================
# 🔄 **DESARROLLO**
# ============================================================================
dev-setup: install-dev format lint ## Configuración completa para desarrollo
	@echo "🔧 Configuración de desarrollo completada"

dev-test: test-cov lint ## Tests completos con linting
	@echo "✅ Tests y linting completados"

dev-run: dev-test run ## Ejecutar con tests previos
	@echo "🚀 Sistema ejecutándose"

dev-demo: dev-test demo ## Ejecutar demo con tests previos
	@echo "🎮 Demo ejecutándose"

# ============================================================================
# 🚀 **PRODUCCIÓN**
# ============================================================================
prod-build: ## Construir para producción
	@echo "🏭 Construyendo para producción..."
	$(PYTHON) setup.py sdist bdist_wheel

prod-install: ## Instalar en modo producción
	@echo "📦 Instalando en modo producción..."
	$(PIP) install --no-dev -r requirements_optimized.txt

prod-run: ## Ejecutar en modo producción
	@echo "🚀 Ejecutando en modo producción..."
	$(PYTHON) $(MAIN_FILE) --production

# ============================================================================
# 🔧 **UTILIDADES**
# ============================================================================
check-deps: ## Verificar dependencias
	@echo "🔍 Verificando dependencias..."
	$(PIP) check

update-deps: ## Actualizar dependencias
	@echo "🔄 Actualizando dependencias..."
	$(PIP) install --upgrade -r requirements_optimized.txt

freeze: ## Generar requirements.txt con versiones exactas
	@echo "📋 Generando requirements.txt..."
	$(PIP) freeze > requirements_frozen.txt

security-check: ## Verificar vulnerabilidades de seguridad
	@echo "🔒 Verificando vulnerabilidades..."
	$(PIP) install safety
	safety check

# ============================================================================
# 🎯 **TAREAS COMPUESTAS**
# ============================================================================
full-setup: install-all dev-setup test-cov ## Configuración completa del proyecto
	@echo "🎉 Configuración completa finalizada!"

ci: test-cov lint security-check ## Pipeline de CI
	@echo "✅ Pipeline de CI completado"

release: clean prod-build test-cov ## Preparar release
	@echo "🎉 Release preparado!"

# ============================================================================
# 📋 **INFORMACIÓN**
# ============================================================================
info: ## Mostrar información del sistema
	@echo "📊 Información del sistema:"
	@echo "  Python: $$($(PYTHON) --version)"
	@echo "  PyTorch: $$($(PYTHON) -c 'import torch; print(torch.__version__)' 2>/dev/null || echo 'No instalado')"
	@echo "  CUDA: $$($(PYTHON) -c 'import torch; print(torch.version.cuda)' 2>/dev/null || echo 'No disponible')"
	@echo "  GPU: $$($(PYTHON) -c 'import torch; print(torch.cuda.is_available())' 2>/dev/null || echo 'No disponible')"

version: ## Mostrar versión del sistema
	@echo "📋 Versión del sistema:"
	@$(PYTHON) -c "from intelligent_resource_manager import __version__; print(__version__)" 2>/dev/null || echo "Versión no disponible"

# ============================================================================
# 🚨 **EMERGENCIA**
# ============================================================================
emergency-stop: ## Detener todos los procesos del sistema
	@echo "🚨 Deteniendo todos los procesos..."
	pkill -f $(MAIN_FILE) || true
	pkill -f $(DEMO_FILE) || true
	$(DOCKER_COMPOSE) down || true
	@echo "✅ Todos los procesos detenidos"

emergency-clean: emergency-stop clean-all ## Limpieza de emergencia
	@echo "🧹 Limpieza de emergencia completada"

# ============================================================================
# 🎯 **DEFAULT**
# ============================================================================
.DEFAULT_GOAL := help
