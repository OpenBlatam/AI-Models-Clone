# Onyx Features - Production Makefile
# Automated tasks for development, testing, and deployment

.PHONY: help install dev test lint format build deploy clean logs status health

# Default target
.DEFAULT_GOAL := help

# Variables
PROJECT_NAME := onyx-features
PYTHON_VERSION := 3.11
VENV_NAME := .venv
DOCKER_IMAGE := $(PROJECT_NAME):latest
COMPOSE_FILE := docker-compose.yml

# Colors for output
CYAN := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(CYAN)Onyx Features - Production Makefile$(NC)"
	@echo "$(YELLOW)Available commands:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

# =============================================================================
# DEVELOPMENT ENVIRONMENT
# =============================================================================

install: ## Install dependencies and setup development environment
	@echo "$(CYAN)Setting up development environment...$(NC)"
	python$(PYTHON_VERSION) -m venv $(VENV_NAME)
	$(VENV_NAME)/bin/pip install --upgrade pip setuptools wheel
	$(VENV_NAME)/bin/pip install -r requirements.txt
	$(VENV_NAME)/bin/pip install -r requirements-dev.txt
	@echo "$(GREEN)Development environment ready!$(NC)"

dev: ## Start development server
	@echo "$(CYAN)Starting development server...$(NC)"
	$(VENV_NAME)/bin/python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000

dev-watch: ## Start development server with file watching
	@echo "$(CYAN)Starting development server with hot reload...$(NC)"
	$(VENV_NAME)/bin/watchfiles 'python -m uvicorn app:app --reload' .

# =============================================================================
# CODE QUALITY
# =============================================================================

lint: ## Run linting checks
	@echo "$(CYAN)Running linting checks...$(NC)"
	$(VENV_NAME)/bin/flake8 . --max-line-length=100 --exclude=.venv
	$(VENV_NAME)/bin/mypy . --ignore-missing-imports
	$(VENV_NAME)/bin/isort . --check-only --diff
	$(VENV_NAME)/bin/black . --check --diff
	@echo "$(GREEN)Linting passed!$(NC)"

format: ## Format code with black and isort
	@echo "$(CYAN)Formatting code...$(NC)"
	$(VENV_NAME)/bin/isort .
	$(VENV_NAME)/bin/black .
	@echo "$(GREEN)Code formatted!$(NC)"

type-check: ## Run type checking
	@echo "$(CYAN)Running type checks...$(NC)"
	$(VENV_NAME)/bin/mypy . --ignore-missing-imports

security: ## Run security checks
	@echo "$(CYAN)Running security checks...$(NC)"
	$(VENV_NAME)/bin/bandit -r . -x .venv
	$(VENV_NAME)/bin/safety check

# =============================================================================
# TESTING
# =============================================================================

test: ## Run all tests
	@echo "$(CYAN)Running tests...$(NC)"
	$(VENV_NAME)/bin/pytest tests/ -v --cov=. --cov-report=html --cov-report=term

test-fast: ## Run tests without coverage
	@echo "$(CYAN)Running fast tests...$(NC)"
	$(VENV_NAME)/bin/pytest tests/ -v -x

test-integration: ## Run integration tests
	@echo "$(CYAN)Running integration tests...$(NC)"
	$(VENV_NAME)/bin/pytest tests/integration/ -v

test-unit: ## Run unit tests only
	@echo "$(CYAN)Running unit tests...$(NC)"
	$(VENV_NAME)/bin/pytest tests/unit/ -v

# =============================================================================
# DOCKER OPERATIONS
# =============================================================================

build: ## Build Docker image
	@echo "$(CYAN)Building Docker image...$(NC)"
	docker build -t $(DOCKER_IMAGE) .
	@echo "$(GREEN)Docker image built successfully!$(NC)"

build-no-cache: ## Build Docker image without cache
	@echo "$(CYAN)Building Docker image without cache...$(NC)"
	docker build --no-cache -t $(DOCKER_IMAGE) .

run: ## Run Docker container
	@echo "$(CYAN)Running Docker container...$(NC)"
	docker run -p 8000:8000 --env-file env.example $(DOCKER_IMAGE)

# =============================================================================
# DOCKER COMPOSE OPERATIONS
# =============================================================================

up: ## Start all services with docker-compose
	@echo "$(CYAN)Starting all services...$(NC)"
	docker-compose -f $(COMPOSE_FILE) up -d
	@echo "$(GREEN)All services started!$(NC)"

down: ## Stop all services
	@echo "$(CYAN)Stopping all services...$(NC)"
	docker-compose -f $(COMPOSE_FILE) down
	@echo "$(GREEN)All services stopped!$(NC)"

restart: ## Restart all services
	@echo "$(CYAN)Restarting all services...$(NC)"
	docker-compose -f $(COMPOSE_FILE) restart
	@echo "$(GREEN)All services restarted!$(NC)"

logs: ## Show logs from all services
	docker-compose -f $(COMPOSE_FILE) logs -f

logs-app: ## Show logs from main application
	docker-compose -f $(COMPOSE_FILE) logs -f onyx-features

status: ## Show status of all services
	@echo "$(CYAN)Service Status:$(NC)"
	docker-compose -f $(COMPOSE_FILE) ps

# =============================================================================
# DATABASE OPERATIONS
# =============================================================================

db-up: ## Start only database services
	@echo "$(CYAN)Starting database services...$(NC)"
	docker-compose -f $(COMPOSE_FILE) up -d postgres redis

db-migrate: ## Run database migrations
	@echo "$(CYAN)Running database migrations...$(NC)"
	$(VENV_NAME)/bin/alembic upgrade head

db-migration: ## Create new database migration
	@echo "$(CYAN)Creating new migration...$(NC)"
	@read -p "Migration name: " name; \
	$(VENV_NAME)/bin/alembic revision --autogenerate -m "$$name"

db-reset: ## Reset database (DANGER: destroys data)
	@echo "$(RED)WARNING: This will destroy all data!$(NC)"
	@read -p "Are you sure? (y/N): " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		docker-compose -f $(COMPOSE_FILE) down -v; \
		docker-compose -f $(COMPOSE_FILE) up -d postgres redis; \
		sleep 5; \
		$(VENV_NAME)/bin/alembic upgrade head; \
	fi

# =============================================================================
# MONITORING & HEALTH CHECKS
# =============================================================================

health: ## Check health of all services
	@echo "$(CYAN)Checking service health...$(NC)"
	@curl -s http://localhost:8000/health | python -m json.tool || echo "$(RED)Main app not responding$(NC)"
	@curl -s http://localhost:9090/-/healthy > /dev/null && echo "$(GREEN)Prometheus: Healthy$(NC)" || echo "$(RED)Prometheus: Unhealthy$(NC)"
	@curl -s http://localhost:3000/api/health > /dev/null && echo "$(GREEN)Grafana: Healthy$(NC)" || echo "$(RED)Grafana: Unhealthy$(NC)"

metrics: ## Show prometheus metrics
	@curl -s http://localhost:8000/metrics

dashboard: ## Open monitoring dashboard
	@echo "$(CYAN)Opening monitoring dashboard...$(NC)"
	@echo "Grafana: http://localhost:3000"
	@echo "Prometheus: http://localhost:9090"
	@echo "Application: http://localhost:8000"

# =============================================================================
# DEPLOYMENT
# =============================================================================

deploy-staging: ## Deploy to staging environment
	@echo "$(CYAN)Deploying to staging...$(NC)"
	docker-compose -f docker-compose.staging.yml up -d
	@echo "$(GREEN)Staging deployment complete!$(NC)"

deploy-prod: ## Deploy to production environment
	@echo "$(CYAN)Deploying to production...$(NC)"
	@echo "$(RED)WARNING: Production deployment!$(NC)"
	@read -p "Are you sure? (y/N): " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		docker-compose -f docker-compose.prod.yml up -d; \
		echo "$(GREEN)Production deployment complete!$(NC)"; \
	fi

# =============================================================================
# MAINTENANCE
# =============================================================================

clean: ## Clean up Docker resources
	@echo "$(CYAN)Cleaning up Docker resources...$(NC)"
	docker system prune -f
	docker volume prune -f
	@echo "$(GREEN)Cleanup complete!$(NC)"

clean-all: ## Clean up everything including images
	@echo "$(CYAN)Cleaning up all Docker resources...$(NC)"
	docker-compose -f $(COMPOSE_FILE) down -v --rmi all
	docker system prune -a -f
	@echo "$(GREEN)Complete cleanup done!$(NC)"

backup: ## Create database backup
	@echo "$(CYAN)Creating database backup...$(NC)"
	mkdir -p backups
	docker-compose -f $(COMPOSE_FILE) exec postgres pg_dump -U onyx_user onyx_db > backups/backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)Backup created!$(NC)"

restore: ## Restore database from backup
	@echo "$(CYAN)Available backups:$(NC)"
	@ls -la backups/
	@read -p "Backup file name: " file; \
	docker-compose -f $(COMPOSE_FILE) exec -T postgres psql -U onyx_user onyx_db < backups/$$file

# =============================================================================
# UTILITIES
# =============================================================================

shell: ## Open shell in main application container
	docker-compose -f $(COMPOSE_FILE) exec onyx-features /bin/bash

db-shell: ## Open database shell
	docker-compose -f $(COMPOSE_FILE) exec postgres psql -U onyx_user onyx_db

redis-shell: ## Open Redis shell
	docker-compose -f $(COMPOSE_FILE) exec redis redis-cli

install-hooks: ## Install git pre-commit hooks
	@echo "$(CYAN)Installing pre-commit hooks...$(NC)"
	$(VENV_NAME)/bin/pre-commit install
	@echo "$(GREEN)Pre-commit hooks installed!$(NC)"

update-deps: ## Update all dependencies
	@echo "$(CYAN)Updating dependencies...$(NC)"
	$(VENV_NAME)/bin/pip-review --auto
	$(VENV_NAME)/bin/pip freeze > requirements.txt
	@echo "$(GREEN)Dependencies updated!$(NC)"

# =============================================================================
# DOCUMENTATION
# =============================================================================

docs: ## Generate documentation
	@echo "$(CYAN)Generating documentation...$(NC)"
	$(VENV_NAME)/bin/sphinx-build -b html docs/ docs/_build/
	@echo "$(GREEN)Documentation generated!$(NC)"

docs-serve: ## Serve documentation locally
	@echo "$(CYAN)Serving documentation at http://localhost:8080$(NC)"
	cd docs/_build && python -m http.server 8080

# =============================================================================
# CI/CD HELPERS
# =============================================================================

ci-test: ## Run CI test suite
	@echo "$(CYAN)Running CI test suite...$(NC)"
	$(VENV_NAME)/bin/pytest tests/ --cov=. --cov-report=xml --junitxml=test-results.xml

ci-build: ## Build for CI/CD
	@echo "$(CYAN)Building for CI/CD...$(NC)"
	docker build -t $(PROJECT_NAME):$(shell git rev-parse --short HEAD) .
	docker tag $(PROJECT_NAME):$(shell git rev-parse --short HEAD) $(PROJECT_NAME):latest

version: ## Show current version
	@echo "$(CYAN)Current version:$(NC)"
	@grep "APP_VERSION" env.example | cut -d'=' -f2 