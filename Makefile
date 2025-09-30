# PyScaff Makefile
# Development and testing commands for the workflow orchestrator

.PHONY: help dev lint format type test migrate seed audit spec-check perf clean

# Default target - show help
help:
	@echo "PyScaff Development Commands"
	@echo "============================"
	@echo "dev         - Run development server with hot reload (port 8000)"
	@echo "lint        - Run ruff linting and format checks"
	@echo "format      - Auto-format code with ruff"
	@echo "type        - Run mypy type checking on app directory"
	@echo "test        - Run pytest with coverage report"
	@echo "migrate     - Run database migrations (alembic upgrade head)"
	@echo "seed        - Seed database with test workflows"
	@echo "audit       - Run security audit with pip-audit"
	@echo "spec-check  - Validate OpenAPI spec with spectral"
	@echo "perf        - Run performance/load tests with locust"
	@echo "clean       - Remove cache directories and temporary files"

# Run development server with hot reload
dev:
	uvicorn app.main:app --reload --port 8000

# Lint code (check only, no modifications)
lint:
	ruff check .
	ruff format --check .

# Auto-format code
format:
	ruff format .

# Type checking
type:
	mypy app

# Run tests with coverage
test:
	pytest --cov=app --cov-report=term-missing --cov-report=html

# Run database migrations
migrate:
	alembic upgrade head

# Seed test workflows into database
seed:
	python scripts/seed_workflows.py

# Security audit
audit:
	pip-audit

# Validate OpenAPI specification
spec-check:
	@if [ -f openapi.yaml ]; then \
		spectral lint openapi.yaml; \
	else \
		echo "Warning: openapi.yaml not found, skipping spec-check"; \
	fi

# Run performance/load tests
perf:
	locust -f tests/perf/locustfile.py

# Clean cache directories
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	@echo "Cache directories cleaned"
