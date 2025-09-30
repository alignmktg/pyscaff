"""Smoke tests to validate pytest fixtures work correctly."""

from typing import Any
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient


def test_async_client_fixture(async_client: TestClient) -> None:
    """Verify async_client fixture provides a working TestClient."""
    assert async_client is not None
    assert isinstance(async_client, TestClient)


def test_mock_ai_provider_fixture(mock_ai_provider: Mock) -> None:
    """Verify mock_ai_provider fixture returns expected structure."""
    assert mock_ai_provider is not None
    assert hasattr(mock_ai_provider, "generate")
    assert mock_ai_provider.generate is not None


def test_sample_workflow_yaml_fixture(sample_workflow_yaml: str) -> None:
    """Verify sample_workflow_yaml fixture returns valid YAML string."""
    assert sample_workflow_yaml is not None
    assert isinstance(sample_workflow_yaml, str)
    assert "name: test_workflow" in sample_workflow_yaml
    assert "start_step: step1" in sample_workflow_yaml


def test_sample_workflow_definition_fixture(sample_workflow_definition: dict[str, Any]) -> None:
    """Verify sample_workflow_definition fixture returns valid dict."""
    assert sample_workflow_definition is not None
    assert isinstance(sample_workflow_definition, dict)
    assert sample_workflow_definition["name"] == "test_workflow"
    assert sample_workflow_definition["version"] == "0.1.0"
    assert "steps" in sample_workflow_definition
    assert len(sample_workflow_definition["steps"]) == 2


def test_mock_openai_client_fixture(mock_openai_client: Mock) -> None:
    """Verify mock_openai_client fixture provides OpenAI-compatible interface."""
    assert mock_openai_client is not None
    assert hasattr(mock_openai_client, "chat")
    assert hasattr(mock_openai_client.chat, "completions")
    assert hasattr(mock_openai_client.chat.completions, "create")


def test_test_db_url_fixture(test_db_url: str) -> None:
    """Verify test_db_url fixture returns SQLite in-memory URL."""
    assert test_db_url == "sqlite+aiosqlite:///:memory:"


@pytest.mark.asyncio
async def test_db_session_fixture_async(db_session: Any) -> None:
    """Verify db_session fixture provides async session."""
    assert db_session is not None
    # Session should be usable for async operations
    assert hasattr(db_session, "execute")
    assert hasattr(db_session, "commit")
    assert hasattr(db_session, "rollback")


def test_sync_db_session_fixture(sync_db_session: Any) -> None:
    """Verify sync_db_session fixture provides sync session."""
    assert sync_db_session is not None
    # Session should be usable for sync operations
    assert hasattr(sync_db_session, "execute")
    assert hasattr(sync_db_session, "commit")
    assert hasattr(sync_db_session, "rollback")


def test_mock_otel_tracer_fixture(mock_otel_tracer: Mock) -> None:
    """Verify mock_otel_tracer fixture provides tracer interface."""
    assert mock_otel_tracer is not None
    assert hasattr(mock_otel_tracer, "start_as_current_span")
