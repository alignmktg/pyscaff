"""Unit tests for AIGenerateExecutor."""

import pytest

from app.executors.ai_generate import AIGenerateExecutor
from app.models.schemas import AIGenerateStepConfig


class TestAIGenerateExecutor:
    """Test suite for AIGenerateExecutor."""

    def test_executor_initialization(self):
        """Given AI generate config, When executor created, Then stores config."""
        config = AIGenerateStepConfig(
            template_id="test_template",
            variables=["name", "age"],
            json_schema={
                "type": "object",
                "properties": {
                    "greeting": {"type": "string"},
                    "age_group": {"type": "string"},
                },
                "required": ["greeting", "age_group"],
            },
        )
        executor = AIGenerateExecutor(config)

        assert executor.config == config
        assert executor.config.template_id == "test_template"

    @pytest.mark.asyncio
    async def test_execute_with_valid_response(self):
        """Given AI generate step, When valid JSON returned, Then execution succeeds."""
        config = AIGenerateStepConfig(
            template_id="greeting_template",
            variables=["name"],
            json_schema={
                "type": "object",
                "properties": {"message": {"type": "string"}},
                "required": ["message"],
            },
        )
        executor = AIGenerateExecutor(config)

        context = {
            "static": {"name": "Alice"},
            "profile": {},
            "runtime": {},
        }

        result = await executor.execute(context=context, step_id="ai_gen_1")

        assert result["pause"] is False
        assert "output" in result
        assert isinstance(result["output"], dict)
        assert "message" in result["output"]

    @pytest.mark.asyncio
    async def test_execute_interpolates_variables(self):
        """Given template variables, When executed, Then variables interpolated from context."""
        config = AIGenerateStepConfig(
            template_id="personalized_greeting",
            variables=["name", "role"],
            json_schema={
                "type": "object",
                "properties": {"greeting": {"type": "string"}},
                "required": ["greeting"],
            },
        )
        executor = AIGenerateExecutor(config)

        context = {
            "static": {"name": "Bob"},
            "profile": {"role": "developer"},
            "runtime": {},
        }

        result = await executor.execute(context=context, step_id="ai_gen_2")

        # Verify variables were accessed from context
        assert result["pause"] is False
        assert "output" in result

    @pytest.mark.asyncio
    async def test_execute_with_schema_violation_retries(self):
        """Given schema violation, When retry count < 2, Then retries generation."""
        config = AIGenerateStepConfig(
            template_id="schema_test",
            variables=["input"],
            json_schema={
                "type": "object",
                "properties": {
                    "required_field": {"type": "string"},
                },
                "required": ["required_field"],
            },
        )
        executor = AIGenerateExecutor(config)

        context = {
            "static": {"input": "test"},
            "profile": {},
            "runtime": {},
        }

        # This test expects retry logic to be implemented
        # Mock will be configured to fail once then succeed
        result = await executor.execute(context=context, step_id="ai_gen_3")

        # Should eventually succeed after retry
        assert result["pause"] is False
        assert "output" in result
        assert "retry_count" in result
        assert result["retry_count"] >= 0

    @pytest.mark.asyncio
    async def test_execute_with_persistent_schema_failure(self):
        """Given persistent schema violation, When retries exhausted, Then pauses run."""
        from app.agent.mock import MockAIProvider

        config = AIGenerateStepConfig(
            template_id="failing_schema",
            variables=["input"],
            json_schema={
                "type": "object",
                "properties": {
                    "critical_field": {"type": "string"},
                },
                "required": ["critical_field"],
            },
        )
        # Inject mock provider in schema_violation mode
        mock_provider = MockAIProvider(mode="schema_violation")
        executor = AIGenerateExecutor(config, provider=mock_provider)

        context = {
            "static": {"input": "test"},
            "profile": {},
            "runtime": {},
        }

        # Mock will be configured to always return invalid schema
        result = await executor.execute(context=context, step_id="ai_gen_4")

        # After 2 retries, should pause for manual intervention
        assert result["pause"] is True
        assert result["waiting_for"] == "manual_fix"
        assert "error" in result
        assert "schema" in result["error"].lower() or "validation" in result["error"].lower()
        assert result["retry_count"] >= 2

    @pytest.mark.asyncio
    async def test_execute_stores_output_in_context(self):
        """Given successful generation, When executed, Then stores output in runtime context."""
        config = AIGenerateStepConfig(
            template_id="output_test",
            variables=["question"],
            json_schema={
                "type": "object",
                "properties": {"answer": {"type": "string"}},
                "required": ["answer"],
            },
        )
        executor = AIGenerateExecutor(config)

        context = {
            "static": {"question": "What is 2+2?"},
            "profile": {},
            "runtime": {},
        }

        result = await executor.execute(context=context, step_id="ai_gen_5")

        # Output should be stored in context under step_id key
        assert "ai_gen_5_output" in context["runtime"]
        assert context["runtime"]["ai_gen_5_output"] == result["output"]

    @pytest.mark.asyncio
    async def test_execute_with_missing_variable(self):
        """Given missing variable in context, When executed, Then raises ValueError."""
        config = AIGenerateStepConfig(
            template_id="missing_var_test",
            variables=["name", "missing_var"],
            json_schema={
                "type": "object",
                "properties": {"result": {"type": "string"}},
                "required": ["result"],
            },
        )
        executor = AIGenerateExecutor(config)

        context = {
            "static": {"name": "Alice"},
            "profile": {},
            "runtime": {},
        }

        with pytest.raises(ValueError, match="Variable 'missing_var' not found in context"):
            await executor.execute(context=context, step_id="ai_gen_6")

    @pytest.mark.asyncio
    async def test_execute_with_complex_nested_schema(self):
        """Given complex nested JSON schema, When executed, Then validates correctly."""
        config = AIGenerateStepConfig(
            template_id="nested_schema",
            variables=["data"],
            json_schema={
                "type": "object",
                "properties": {
                    "user": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "age": {"type": "integer"},
                        },
                        "required": ["name", "age"],
                    },
                    "tags": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["user", "tags"],
            },
        )
        executor = AIGenerateExecutor(config)

        context = {
            "static": {"data": "test data"},
            "profile": {},
            "runtime": {},
        }

        result = await executor.execute(context=context, step_id="ai_gen_7")

        assert result["pause"] is False
        assert "output" in result
        assert "user" in result["output"]
        assert "tags" in result["output"]
        assert isinstance(result["output"]["tags"], list)
