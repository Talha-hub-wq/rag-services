.PHONY: help build up down logs restart clean test lint format

# Variables
COMPOSE_FILE := docker-compose.yml
COMPOSE_PROD_FILE := docker-compose.prod.yml

help:
	@echo "RAG Service - Make Commands"
	@echo "==========================="
	@echo ""
	@echo "Development:"
	@echo "  make build              - Build Docker images"
	@echo "  make up                 - Start services"
	@echo "  make down               - Stop services"
	@echo "  make logs               - View all logs"
	@echo "  make logs-backend       - View backend logs"
	@echo "  make logs-frontend      - View frontend logs"
	@echo "  make restart            - Restart services"
	@echo ""
	@echo "Testing & Quality:"
	@echo "  make test               - Run pytest"
	@echo "  make test-coverage      - Run tests with coverage"
	@echo "  make lint               - Run pylint"
	@echo "  make format             - Format code with black"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build       - Build Docker images"
	@echo "  make docker-up          - Start Docker services"
	@echo "  make docker-down        - Stop Docker services"
	@echo "  make docker-clean       - Remove all Docker artifacts"
	@echo "  make docker-prod-build  - Build production images"
	@echo "  make docker-prod-up     - Start production services"
	@echo ""
	@echo "Utils:"
	@echo "  make shell-backend      - Open backend container shell"
	@echo "  make shell-frontend     - Open frontend container shell"
	@echo "  make clean              - Clean all generated files"
	@echo "  make env-setup          - Setup .env file"

# Development Commands
build:
	docker-compose build

up:
	docker-compose up -d
	@echo "✅ Services started"
	@echo "API: http://localhost:8000"
	@echo "Docs: http://localhost:8000/docs"
	@echo "Frontend: http://localhost:8501"

down:
	docker-compose down

logs:
	docker-compose logs -f

logs-backend:
	docker-compose logs -f backend

logs-frontend:
	docker-compose logs -f frontend

restart:
	docker-compose restart

status:
	docker-compose ps

# Testing & Quality
test:
	docker-compose exec backend pytest

test-coverage:
	docker-compose exec backend pytest --cov=. --cov-report=html --cov-report=term-missing
	@echo "✅ Coverage report generated in htmlcov/"

lint:
	docker-compose exec backend pylint services/ models/ config/

format:
	docker-compose exec backend black .

# Docker Management
docker-build:
	docker-compose -f $(COMPOSE_FILE) build --no-cache

docker-up:
	docker-compose -f $(COMPOSE_FILE) up -d
	@echo "✅ Development services started"

docker-down:
	docker-compose -f $(COMPOSE_FILE) down

docker-clean:
	docker-compose down -v
	docker image prune -f
	@echo "✅ Docker cleaned"

docker-prod-build:
	docker-compose -f $(COMPOSE_PROD_FILE) build --no-cache

docker-prod-up:
	docker-compose -f $(COMPOSE_PROD_FILE) up -d
	@echo "✅ Production services started"

docker-prod-down:
	docker-compose -f $(COMPOSE_PROD_FILE) down

# Container Shell Access
shell-backend:
	docker-compose exec backend bash

shell-frontend:
	docker-compose exec frontend bash

# Database & Utils
db-migrate:
	docker-compose exec backend alembic upgrade head

db-rollback:
	docker-compose exec backend alembic downgrade -1

health-check:
	@echo "Checking health..."
	@curl -s http://localhost:8000/health | jq . || echo "Backend not responding"
	@echo ""

# Setup
env-setup:
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✅ .env file created from .env.example"; \
		echo "⚠️  Please update .env with your configuration"; \
	else \
		echo "⚠️  .env file already exists"; \
	fi
	@mkdir -p documents logs
	@echo "✅ Directories created"

# Cleanup
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".coverage" -delete
	rm -rf htmlcov/ build/ dist/ *.egg-info
	@echo "✅ Cleaned up Python cache files"

# Full workflow
setup: env-setup build
	@echo "✅ Setup complete!"
	@echo "Run 'make up' to start services"

start: up
	@sleep 2
	@echo ""
	@echo "✅ All services started!"
	@echo ""
	@echo "API Documentation: http://localhost:8000/docs"
	@echo "Frontend: http://localhost:8501"
	@echo ""

full-test: build test lint
	@echo "✅ All tests passed!"

# Default
.DEFAULT_GOAL := help
