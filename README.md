# PyScaff

[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**AI Workflow Orchestrator - MVID Release**

PyScaff is an AI workflow orchestrator built with Python + FastAPI. This is the MVID (Minimum Viable Internal Dogfood) release - a canonical, executable specification designed for internal use. It orchestrates multi-step workflows with YAML definitions, async execution, wait-states, and AI integration. Think GitHub Actions + Temporal + LangChain, but optimized for agentic AI coding patterns.

## Tech Stack

- **Runtime**: Python 3.12+
- **Framework**: FastAPI + Uvicorn
- **Validation**: Pydantic 2.8+
- **Database**: PostgreSQL (production), SQLite (dev)
- **ORM**: SQLAlchemy 2.0 + Alembic migrations
- **HTTP Client**: httpx
- **Observability**: OpenTelemetry (traces, structured logs)
- **Testing**: pytest, Locust (perf), schemathesis (contract)
- **Linting**: ruff + mypy
- **AI Provider**: OpenAI (production) / Mock (dev/test)

## Quick Start

```bash
# Install dependencies (editable mode with dev extras)
pip install -e ".[dev]"

# Run database migrations
make migrate

# Start development server with hot reload
make dev
# OR: uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`. Visit `http://localhost:8000/docs` for interactive API documentation.

## Development Commands

```bash
# Linting & formatting
make lint         # ruff check + format check

# Type checking
make type         # mypy app

# Testing
make test         # pytest all tests

# Database migrations
make migrate      # alembic upgrade head

# Seed workflows for testing
make seed         # python scripts/seed_workflows.py

# Security audit
make audit        # pip-audit

# API contract validation
make spec-check   # spectral lint openapi.yaml

# Performance/load testing
make perf         # locust -f tests/perf/locustfile.py
```

See `Makefile` for all available commands.

## Docker Development

```bash
# Start full stack (API + Postgres + OTEL collector)
docker-compose up

# Database only (for local API dev)
docker-compose up db

# Clean restart
docker-compose down -v && docker-compose up
```

## Documentation

- **[CLAUDE.md](CLAUDE.md)** - Development guide and architecture overview
- **[pyscaff-prd.md](pyscaff-prd.md)** - Product Requirements Document (v0.3.0)
- **[docs/adr](docs/adr)** - Architecture Decision Records

## License

MIT
