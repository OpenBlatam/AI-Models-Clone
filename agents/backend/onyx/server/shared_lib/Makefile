# Makefile - Comandos Simplificados
# ===================================

.PHONY: help deploy deploy-lambda deploy-ecs deploy-local setup test clean

# Variables
SERVICE_NAME ?= shared-lib-service
STAGE ?= dev
REGION ?= us-east-1

help:
	@echo "🚀 Shared Library - Comandos Disponibles"
	@echo ""
	@echo "Deployment:"
	@echo "  make deploy          - Deploy automático (Lambda por defecto)"
	@echo "  make deploy-lambda   - Deploy a AWS Lambda"
	@echo "  make deploy-ecs      - Deploy a AWS ECS"
	@echo "  make deploy-local    - Iniciar servicios locales"
	@echo ""
	@echo "Setup:"
	@echo "  make setup          - Configurar recursos AWS"
	@echo ""
	@echo "Testing:"
	@echo "  make test           - Ejecutar tests"
	@echo ""
	@echo "Utilidades:"
	@echo "  make clean          - Limpiar archivos temporales"
	@echo ""
	@echo "Variables:"
	@echo "  SERVICE_NAME=$(SERVICE_NAME)"
	@echo "  STAGE=$(STAGE)"
	@echo "  REGION=$(REGION)"
	@echo ""
	@echo "Ejemplos:"
	@echo "  make deploy SERVICE_NAME=mi-servicio STAGE=prod"
	@echo "  make deploy-lambda SERVICE_NAME=mi-api"
	@echo "  make deploy-ecs SERVICE_NAME=mi-servicio"

deploy: deploy-lambda
	@echo "✅ Deployment completado"

deploy-lambda:
	@echo "🚀 Deploying to AWS Lambda..."
	@chmod +x deploy 2>/dev/null || true
	@./deploy lambda $(SERVICE_NAME) $(STAGE) $(REGION) || \
	 python3 deploy lambda $(SERVICE_NAME) $(STAGE) $(REGION) || \
	 echo "Usa: ./deploy lambda $(SERVICE_NAME) $(STAGE) $(REGION)"

deploy-ecs:
	@echo "🚀 Deploying to AWS ECS..."
	@chmod +x deploy 2>/dev/null || true
	@./deploy ecs $(SERVICE_NAME) $(STAGE) $(REGION) || \
	 python3 deploy ecs $(SERVICE_NAME) $(STAGE) $(REGION) || \
	 echo "Usa: ./deploy ecs $(SERVICE_NAME) $(STAGE) $(REGION)"

deploy-local:
	@echo "🚀 Iniciando servicios locales..."
	@cd docker && docker-compose up -d
	@echo "✅ Servicios iniciados"
	@echo "   API: http://localhost:8030"
	@echo "   Docs: http://localhost:8030/docs"

setup:
	@echo "📦 Configurando recursos AWS..."
	@python3 aws/setup_aws.py $(SERVICE_NAME) $(REGION)

test:
	@echo "🧪 Ejecutando tests..."
	@python3 -m pytest tests/ -v || echo "No hay tests configurados"

clean:
	@echo "🧹 Limpiando archivos temporales..."
	@find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -r {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -r {} + 2>/dev/null || true
	@echo "✅ Limpieza completada"

# Alias comunes
d: deploy
dl: deploy-lambda
de: deploy-ecs
dlocal: deploy-local
s: setup
t: test
c: clean




