# AI Document Generator Makefile

.PHONY: help install dev test lint format clean build run docker-build docker-run docker-compose-up docker-compose-down k8s-deploy k8s-delete

# Default target
help: ## Show this help message
	@echo "AI Document Generator - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Development setup
install: ## Install dependencies
	pip install -r requirements.txt

dev: ## Run development server
	uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Testing
test: ## Run all tests
	pytest

test-unit: ## Run unit tests only
	pytest -m "not integration"

test-integration: ## Run integration tests only
	pytest -m integration

test-coverage: ## Run tests with coverage
	pytest --cov=app --cov-report=html --cov-report=term-missing

test-watch: ## Run tests in watch mode
	pytest-watch

# Code quality
lint: ## Run linting
	flake8 app tests
	mypy app
	black --check app tests
	isort --check-only app tests

format: ## Format code
	black app tests
	isort app tests

# Database
db-migrate: ## Run database migrations
	alembic upgrade head

db-migrate-create: ## Create new migration
	alembic revision --autogenerate -m "$(MESSAGE)"

db-reset: ## Reset database
	alembic downgrade base
	alembic upgrade head

# Docker
docker-build: ## Build Docker image
	docker build -t ai-document-generator:latest .

docker-run: ## Run Docker container
	docker run -p 8000:8000 --env-file .env ai-document-generator:latest

docker-compose-up: ## Start all services with Docker Compose
	docker-compose up -d

docker-compose-down: ## Stop all services with Docker Compose
	docker-compose down

docker-compose-logs: ## View Docker Compose logs
	docker-compose logs -f

docker-compose-build: ## Build and start services
	docker-compose up --build -d

# Kubernetes
k8s-deploy: ## Deploy to Kubernetes
	kubectl apply -f k8s/

k8s-delete: ## Delete from Kubernetes
	kubectl delete -f k8s/

k8s-monitoring: ## Deploy monitoring stack
	kubectl apply -f k8s/monitoring.yaml

k8s-logs: ## View application logs
	kubectl logs -f deployment/ai-document-generator

k8s-status: ## Check deployment status
	kubectl get pods -l app=ai-document-generator
	kubectl get services
	kubectl get ingress

# Production
build: ## Build production image
	docker build -t ai-document-generator:$(VERSION) .
	docker tag ai-document-generator:$(VERSION) ai-document-generator:latest

run: ## Run production server
	uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# Utilities
clean: ## Clean up temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf dist
	rm -rf build

setup-env: ## Setup environment file
	cp .env.example .env
	@echo "Please edit .env file with your configuration"

# Security
security-scan: ## Run security scan
	bandit -r app/
	safety check

# Performance
benchmark: ## Run performance benchmarks
	pytest tests/benchmarks/ -v

load-test: ## Run load tests
	k6 run tests/load/load-test.js

# Documentation
docs: ## Generate API documentation
	@echo "API documentation available at http://localhost:8000/docs"

docs-build: ## Build documentation
	sphinx-build -b html docs/ docs/_build/html

# CI/CD
ci-test: ## Run CI test suite
	pytest --cov=app --cov-report=xml --junitxml=test-results.xml

ci-lint: ## Run CI linting
	flake8 app tests
	mypy app
	black --check app tests
	isort --check-only app tests

# Environment variables
VERSION ?= latest
MESSAGE ?= "Auto-generated migration"




