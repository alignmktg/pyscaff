PyScaff Test Infrastructure
============================

Structure:
----------
tests/
├── __init__.py              # Test suite marker
├── conftest.py              # Shared pytest fixtures
├── unit/                    # Unit tests
│   ├── __init__.py
│   └── test_fixtures.py     # Fixture smoke tests
├── integration/             # Integration tests
│   └── __init__.py
├── perf/                    # Performance tests (Locust)
│   └── __init__.py
└── features/                # BDD tests (Gherkin)
    └── __init__.py

Fixtures Available (conftest.py):
----------------------------------

Database Fixtures:
- test_db_url           : Returns "sqlite+aiosqlite:///:memory:"
- db_engine             : Async SQLAlchemy engine (in-memory SQLite)
- db_session            : Async database session (auto-rollback)
- sync_db_engine        : Sync SQLAlchemy engine (for migrations)
- sync_db_session       : Sync database session (auto-rollback)

App Fixtures:
- app                   : FastAPI app instance (placeholder until app.main created)
- async_client          : FastAPI TestClient for API testing

AI/Mock Fixtures:
- mock_ai_provider      : Mock AI provider with generate() method
- mock_openai_client    : Mock OpenAI client (chat.completions.create)

Sample Data Fixtures:
- sample_workflow_yaml        : Sample workflow as YAML string
- sample_workflow_definition  : Sample workflow as Python dict

Observability Fixtures:
- mock_otel_tracer      : Mock OpenTelemetry tracer
- reset_env_vars        : Auto-cleanup env vars (autouse=True)

Environment Overrides:
----------------------
DATABASE_URL    = "sqlite+aiosqlite:///:memory:"
AI_PROVIDER     = "mock"
MOCK_AI_MODE    = "success"
MOCK_AI_SEED    = "42"

Running Tests:
--------------
# All tests
pytest tests/

# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# With coverage
pytest --cov=app --cov-report=term-missing

# Single test
pytest tests/unit/test_fixtures.py::test_async_client_fixture

# Verbose with stdout
pytest -vv -s tests/

Configuration:
--------------
Test config in pyproject.toml [tool.pytest.ini_options]:
- asyncio_mode = "auto"
- Auto-coverage enabled (--cov=app)
- Test discovery: test_*.py files

Next Steps:
-----------
1. Install dependencies: pip install -e ".[dev]"
2. Create app/main.py with FastAPI app
3. Create database models in app/db/
4. Uncomment Base.metadata.create_all in conftest.py
5. Add actual unit tests in tests/unit/
6. Add integration tests in tests/integration/
7. Add performance tests (Locust) in tests/perf/
8. Run: make test
