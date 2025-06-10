.PHONY: help build up down logs test lint format clean dev prod

# Default target
help:

# Environment setup with uv (recommended)
install-uv:
	@echo "Installing uv package manager..."
	@curl -LsSf https://astral.sh/uv/install.sh | sh
	@echo "uv installed successfully!"
	@echo "You may need to restart your terminal or run: source ~/.bashrc"

setup-uv:
	@echo "Setting up development environment with uv..."
	@echo "Backend setup..."
	cd backend && \
	uv venv && \
	. .venv/bin/activate && \
	uv pip install -e .[dev]
	@echo "Frontend setup..."
	cd frontend && \
	uv venv && \
	. .venv/bin/activate && \
	uv pip install -r requirements.txt
	@echo "Setup complete! Use 'source backend/.venv/bin/activate' to activate backend env"

setup-pip:
	@echo "Setting up development environment with pip..."
	@echo "Backend setup..."
	cd backend && \
	python -m venv .venv && \
	. .venv/bin/activate && \
	pip install -e .[dev]
	@echo "Frontend setup..."
	cd frontend && \
	python -m venv .venv && \
	. .venv/bin/activate && \
	pip install -r requirements.txt
	@echo "Setup complete!"

# Update dependencies with uv
update-deps-uv:
	@echo "Updating dependencies with uv..."
	cd backend && uv lock --upgrade
	cd frontend && uv pip compile requirements.in -o requirements.txt

# Sync dependencies with uv
sync-deps-uv:
	cd backend && . .venv/bin/activate && uv pip sync requirements.lock
	cd frontend && . .venv/bin/activate && uv pip sync requirements.txt

# Setup unified environment (single venv for both frontend and backend)
setup-unified:
	@echo "Setting up unified development environment..."
	./scripts/setup-unified.sh

# Start all services locally
start-all:
	@echo "Starting all services locally..."
	./scripts/start-all.sh

# Start demo environment (frontend only)
start-demo:
	@echo "Starting demo environment..."
	./scripts/start-demo.sh

# Start with authentication (full API integration)
start-auth:
	@echo "Starting with authentication API..."
	./scripts/start-with-auth.sh

# Stop all local services
stop-all:
	@echo "Stopping all local services..."
	./scripts/stop-all.sh

# Show service status
status:
	@echo "Checking service status..."
	./scripts/stop-all.sh status
	@echo "FastAPI Enterprise MVP - Available commands:"
	@echo ""
	@echo "Environment Setup:"
	@echo "  setup-uv     - Setup development environment with uv (separate envs)"
	@echo "  setup-unified - Setup unified environment for both frontend and backend"
	@echo "  setup-pip    - Setup development environment with pip"
	@echo "  install-uv   - Install uv package manager"
	@echo ""
	@echo "Development:"
	@echo "  dev          - Start development environment (Docker)"
	@echo "  start-all    - Start both frontend and backend (local)"
	@echo "  stop-all     - Stop all local services"
	@echo "  build-dev    - Build development images"
	@echo "  logs         - Show logs from all services"
	@echo "  logs-api     - Show API logs only"
	@echo "  logs-frontend - Show frontend logs only"
	@echo ""
	@echo "Production:"
	@echo "  prod         - Start production environment"
	@echo "  build-prod   - Build production images"
	@echo ""
	@echo "Testing:"
	@echo "  test         - Run all tests"
	@echo "  test-unit    - Run unit tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  test-coverage - Run tests with coverage report"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint         - Run linting checks"
	@echo "  format       - Format code with black and isort"
	@echo "  type-check   - Run mypy type checking"
	@echo ""
	@echo "Database:"
	@echo "  db-migrate   - Run database migrations"
	@echo "  db-upgrade   - Upgrade database to latest migration"
	@echo "  db-reset     - Reset database (WARNING: destroys data)"
	@echo ""
	@echo "Utilities:"
	@echo "  clean        - Clean up containers and volumes"
	@echo "  shell        - Open shell in backend container"
	@echo "  psql         - Connect to PostgreSQL database"
	@echo "  redis-cli    - Connect to Redis"

# Development environment
dev:
	docker-compose -f docker-compose.dev.yml up -d
	@echo "Development environment started!"
	@echo "API: http://localhost:8000"
	@echo "Frontend: http://localhost:8501"
	@echo "Docs: http://localhost:8000/docs"

build-dev:
	docker-compose -f docker-compose.dev.yml build

# Production environment
prod:
	docker-compose up -d
	@echo "Production environment started!"

build-prod:
	docker-compose build

# Logs
logs:
	docker-compose -f docker-compose.dev.yml logs -f

logs-api:
	docker-compose -f docker-compose.dev.yml logs -f backend

logs-frontend:
	docker-compose -f docker-compose.dev.yml logs -f frontend

# Testing
test:
	docker-compose -f docker-compose.dev.yml exec backend pytest

test-unit:
	docker-compose -f docker-compose.dev.yml exec backend pytest -m "unit"

test-integration:
	docker-compose -f docker-compose.dev.yml exec backend pytest -m "integration"

test-coverage:
	docker-compose -f docker-compose.dev.yml exec backend pytest --cov=app --cov-report=html --cov-report=term

# Code quality
lint:
	docker-compose -f docker-compose.dev.yml exec backend ruff check app/
	docker-compose -f docker-compose.dev.yml exec backend black --check app/
	docker-compose -f docker-compose.dev.yml exec backend isort --check-only app/

format:
	docker-compose -f docker-compose.dev.yml exec backend black app/
	docker-compose -f docker-compose.dev.yml exec backend isort app/
	docker-compose -f docker-compose.dev.yml exec backend ruff --fix app/

type-check:
	docker-compose -f docker-compose.dev.yml exec backend mypy app/

# Database operations
db-migrate:
	docker-compose -f docker-compose.dev.yml exec backend alembic revision --autogenerate -m "$(msg)"

db-upgrade:
	docker-compose -f docker-compose.dev.yml exec backend alembic upgrade head

db-reset:
	docker-compose -f docker-compose.dev.yml down -v
	docker-compose -f docker-compose.dev.yml up -d db
	sleep 5
	docker-compose -f docker-compose.dev.yml exec backend alembic upgrade head

# Utilities
clean:
	docker-compose -f docker-compose.dev.yml down -v --remove-orphans
	docker-compose down -v --remove-orphans
	docker system prune -f

shell:
	docker-compose -f docker-compose.dev.yml exec backend bash

psql:
	docker-compose -f docker-compose.dev.yml exec db psql -U postgres -d fastapi_app

redis-cli:
	docker-compose -f docker-compose.dev.yml exec redis redis-cli

# Stop services
down:
	docker-compose -f docker-compose.dev.yml down

down-prod:
	docker-compose down

# Build specific services
build-backend:
	docker-compose -f docker-compose.dev.yml build backend

build-frontend:
	docker-compose -f docker-compose.dev.yml build frontend

# Restart services
restart:
	docker-compose -f docker-compose.dev.yml restart

restart-backend:
	docker-compose -f docker-compose.dev.yml restart backend

restart-frontend:
	docker-compose -f docker-compose.dev.yml restart frontend

# Health checks
health:
	@echo "Checking service health..."
	@curl -f http://localhost:8000/health || echo "Backend unhealthy"
	@curl -f http://localhost:8501/_stcore/health || echo "Frontend unhealthy"

# Install pre-commit hooks
install-hooks:
	docker-compose -f docker-compose.dev.yml exec backend pre-commit install

# Run pre-commit on all files
pre-commit:
	docker-compose -f docker-compose.dev.yml exec backend pre-commit run --all-files
