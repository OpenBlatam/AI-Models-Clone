# Makefile for Key Messages Feature
# Usage: make <target>

.PHONY: help install install-dev install-test install-cyber install-ml install-all clean test test-unit test-integration lint format check-security check-deps update-deps run run-dev run-prod build docs

# Default target
help:
	@echo "Available targets:"
	@echo "  install        - Install production dependencies"
	@echo "  install-dev    - Install development dependencies"
	@echo "  install-test   - Install testing dependencies"
	@echo "  install-cyber  - Install cybersecurity dependencies"
	@echo "  install-ml     - Install machine learning dependencies"
	@echo "  install-all    - Install all dependencies"
	@echo "  clean          - Clean build artifacts"
	@echo "  test           - Run all tests"
	@echo "  test-unit      - Run unit tests"
	@echo "  test-integration - Run integration tests"
	@echo "  lint           - Run linting"
	@echo "  format         - Format code"
	@echo "  check-security - Run security checks"
	@echo "  check-deps     - Check dependency vulnerabilities"
	@echo "  update-deps    - Update dependencies"
	@echo "  run            - Run the application"
	@echo "  run-dev        - Run in development mode"
	@echo "  run-prod       - Run in production mode"
	@echo "  build          - Build the package"
	@echo "  docs           - Build documentation"

# Installation targets
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

install-test:
	pip install -r requirements-test.txt

install-cyber:
	pip install -r requirements-cyber.txt

install-ml:
	pip install -r requirements.txt
	pip install diffusers matplotlib seaborn plotly scipy tensorboard wandb mlflow tqdm rich click gradio

install-all:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pip install -r requirements-test.txt
	pip install -r requirements-cyber.txt

# Clean targets
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -delete
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".black_cache" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .eggs/

# Testing targets
test:
	pytest tests/ -v --cov=key_messages --cov-report=html --cov-report=term

test-unit:
	pytest tests/unit/ -v --cov=key_messages --cov-report=html --cov-report=term

test-integration:
	pytest tests/integration/ -v --cov=key_messages --cov-report=html --cov-report=term

test-cyber:
	pytest tests/ -m cyber -v

test-ml:
	pytest tests/ -m ml -v

test-api:
	pytest tests/ -m api -v

test-performance:
	pytest tests/ -m performance -v

# Code quality targets
lint:
	flake8 key_messages/ tests/ --max-line-length=88 --extend-ignore=E203,W503
	mypy key_messages/ --ignore-missing-imports
	bandit -r key_messages/ -f json -o bandit-report.json

format:
	black key_messages/ tests/ --line-length=88
	isort key_messages/ tests/ --profile=black

format-check:
	black key_messages/ tests/ --line-length=88 --check
	isort key_messages/ tests/ --profile=black --check

# Security targets
check-security:
	bandit -r key_messages/ -f json -o bandit-report.json
	safety check
	semgrep scan --config=auto

check-deps:
	pip-audit
	safety check

update-deps:
	pip install --upgrade pip
	pip install --upgrade -r requirements.txt
	pip install --upgrade -r requirements-dev.txt

# Run targets
run:
	uvicorn key_messages.api:app --host 0.0.0.0 --port 8000

run-dev:
	uvicorn key_messages.api:app --host 0.0.0.0 --port 8000 --reload --log-level debug

run-prod:
	uvicorn key_messages.api:app --host 0.0.0.0 --port 8000 --workers 4

# Build targets
build:
	python setup.py sdist bdist_wheel

build-clean:
	rm -rf build/ dist/ *.egg-info/
	python setup.py sdist bdist_wheel

# Documentation targets
docs:
	cd docs && make html

docs-clean:
	cd docs && make clean

# Docker targets
docker-build:
	docker build -t key-messages:latest .

docker-run:
	docker run -p 8000:8000 key-messages:latest

docker-dev:
	docker-compose -f docker-compose.dev.yml up --build

docker-prod:
	docker-compose -f docker-compose.prod.yml up --build

# Database targets
db-migrate:
	alembic upgrade head

db-rollback:
	alembic downgrade -1

db-revision:
	alembic revision --autogenerate -m "$(message)"

# Monitoring targets
monitor:
	prometheus --config.file=prometheus.yml

logs:
	tail -f logs/app.log

# Development utilities
shell:
	python -m ipython

profile:
	python -m cProfile -o profile.stats key_messages/api.py

profile-view:
	python -c "import pstats; pstats.Stats('profile.stats').sort_stats('cumulative').print_stats(20)"

# Git hooks
install-hooks:
	pre-commit install

run-hooks:
	pre-commit run --all-files

# Environment setup
setup-env:
	python -m venv venv
	. venv/bin/activate && pip install --upgrade pip
	. venv/bin/activate && make install-all

setup-dev:
	make setup-env
	make install-hooks
	make format

# Quick development cycle
dev-cycle:
	make format
	make lint
	make test
	make run-dev

# Production deployment
deploy:
	make clean
	make build
	make test
	make check-security
	make run-prod 