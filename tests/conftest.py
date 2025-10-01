"""Pytest configuration and shared fixtures for PyScaff tests."""

import os
from collections.abc import AsyncGenerator, Generator
from typing import Any
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# Override DATABASE_URL for tests to use in-memory SQLite
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["AI_PROVIDER"] = "mock"
os.environ["MOCK_AI_MODE"] = "success"
os.environ["MOCK_AI_SEED"] = "42"


@pytest.fixture(scope="session")
def test_db_url() -> str:
    """Return test database URL (in-memory SQLite)."""
    return "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def db_engine() -> AsyncGenerator[Any, None]:
    """Create async SQLAlchemy engine for testing with in-memory SQLite."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )

    # Import Base and create all tables
    from app.db.base import Base
    from app.db.models import Run, RunStep, Step, Workflow  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Cleanup
    await engine.dispose()


@pytest.fixture
async def db_session(db_engine: Any) -> AsyncGenerator[AsyncSession, None]:
    """Create async database session for testing."""
    async_session_maker = sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest.fixture
def sync_db_engine() -> Generator[Any, None, None]:
    """Create sync SQLAlchemy engine for testing (for migrations and sync operations)."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )

    # Import Base and create all tables
    from app.db.base import Base
    from app.db.models import Run, RunStep, Step, Workflow  # noqa: F401

    Base.metadata.create_all(bind=engine)

    yield engine

    engine.dispose()


@pytest.fixture
def sync_db_session(sync_db_engine: Any) -> Generator[Session, None, None]:
    """Create sync database session for testing."""
    SessionLocal = sessionmaker(bind=sync_db_engine)
    session = SessionLocal()

    yield session

    session.rollback()
    session.close()


@pytest.fixture
def mock_ai_provider() -> Mock:
    """Create mock AI provider for testing.

    Returns a mock that simulates the AI provider interface with:
    - generate() method returning valid JSON matching schemas
    - Configurable responses for different test scenarios
    """
    mock = Mock()
    mock.generate = AsyncMock()

    # Default successful response
    mock.generate.return_value = {
        "success": True,
        "data": {"result": "mock_ai_output"},
        "metadata": {
            "provider": "mock",
            "template_id": "test_template",
            "template_version": "1.0",
            "tokens_prompt": 100,
            "tokens_output": 50,
            "latency_ms": 150,
            "retry_count": 0,
        },
    }

    return mock


@pytest.fixture
def app() -> Any:
    """Create FastAPI app instance for testing.

    This fixture will be updated once app.main:app is created.
    """
    # This will be uncommented once the FastAPI app is created
    # from app.main import app
    # return app

    # Placeholder for now
    from fastapi import FastAPI

    test_app = FastAPI()

    @test_app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return test_app


@pytest.fixture
def async_client(app: Any) -> Generator[TestClient, None, None]:
    """Create FastAPI TestClient for async testing.

    Usage:
        def test_endpoint(async_client):
            response = async_client.get("/v1/workflows")
            assert response.status_code == 200
    """
    with TestClient(app) as client:
        yield client


@pytest.fixture
def mock_openai_client() -> Mock:
    """Create mock OpenAI client for testing AI integrations."""
    mock = Mock()
    mock.chat = Mock()
    mock.chat.completions = Mock()
    mock.chat.completions.create = AsyncMock()

    # Default response structure matching OpenAI API
    mock.chat.completions.create.return_value = Mock(
        id="chatcmpl-test123",
        choices=[
            Mock(
                message=Mock(
                    content='{"result": "test_output"}',
                    role="assistant",
                ),
                finish_reason="stop",
            )
        ],
        usage=Mock(
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
        ),
        model="gpt-4",
    )

    return mock


@pytest.fixture
def sample_workflow_yaml() -> str:
    """Return sample workflow YAML for testing."""
    return """
name: test_workflow
version: 0.1.0
start_step: step1

steps:
  - id: step1
    type: form
    name: Collect Input
    next: step2
    config:
      fields:
        - key: user_name
          type: string
          required: true

  - id: step2
    type: ai_generate
    name: Generate Response
    next: null
    config:
      template_id: test_template
      variables:
        - user_name
      json_schema:
        type: object
        properties:
          greeting:
            type: string
        required:
          - greeting
"""


@pytest.fixture
def sample_workflow_definition() -> dict[str, Any]:
    """Return sample workflow definition as dict for testing."""
    return {
        "name": "test_workflow",
        "version": "0.1.0",
        "start_step": "step1",
        "steps": [
            {
                "id": "step1",
                "type": "form",
                "name": "Collect Input",
                "next": "step2",
                "config": {
                    "fields": [
                        {
                            "key": "user_name",
                            "type": "string",
                            "required": True,
                        }
                    ]
                },
            },
            {
                "id": "step2",
                "type": "ai_generate",
                "name": "Generate Response",
                "next": None,
                "config": {
                    "template_id": "test_template",
                    "variables": ["user_name"],
                    "json_schema": {
                        "type": "object",
                        "properties": {"greeting": {"type": "string"}},
                        "required": ["greeting"],
                    },
                },
            },
        ],
    }


@pytest.fixture(autouse=True)
def reset_env_vars() -> Generator[None, None, None]:
    """Reset environment variables after each test."""
    original_env = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def mock_otel_tracer() -> Mock:
    """Create mock OpenTelemetry tracer for testing observability."""
    mock = Mock()
    mock.start_as_current_span = Mock()
    mock.start_as_current_span.return_value.__enter__ = Mock()
    mock.start_as_current_span.return_value.__exit__ = Mock()
    return mock
