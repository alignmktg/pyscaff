"""Unit tests for FormExecutor."""

import pytest

from app.executors.form import FormExecutor
from app.models.schemas import FormStepConfig, StepConfigField


class TestFormExecutor:
    """Test suite for FormExecutor."""

    def test_validate_fields_text_type(self):
        """Given text field, When validated, Then accepts valid string."""
        config = FormStepConfig(
            fields=[
                StepConfigField(key="name", type="text", required=True),
            ]
        )
        executor = FormExecutor(config)

        inputs = {"name": "John Doe"}
        result = executor.validate_fields(inputs)

        assert result["name"] == "John Doe"

    def test_validate_fields_textarea_type(self):
        """Given textarea field, When validated, Then accepts valid string."""
        config = FormStepConfig(
            fields=[
                StepConfigField(key="description", type="textarea", required=True),
            ]
        )
        executor = FormExecutor(config)

        inputs = {"description": "Multi-line\ntext\nhere"}
        result = executor.validate_fields(inputs)

        assert result["description"] == "Multi-line\ntext\nhere"

    def test_validate_fields_required_missing(self):
        """Given required field, When missing, Then raises ValueError."""
        config = FormStepConfig(
            fields=[
                StepConfigField(key="name", type="text", required=True),
            ]
        )
        executor = FormExecutor(config)

        with pytest.raises(ValueError, match="Required field 'name' is missing"):
            executor.validate_fields({})

    def test_validate_fields_optional_missing(self):
        """Given optional field, When missing, Then validation succeeds."""
        config = FormStepConfig(
            fields=[
                StepConfigField(key="name", type="text", required=False),
            ]
        )
        executor = FormExecutor(config)

        result = executor.validate_fields({})

        assert "name" not in result

    def test_validate_fields_invalid_type(self):
        """Given unsupported field type, When validated, Then raises ValueError."""
        config = FormStepConfig(
            fields=[
                StepConfigField(key="age", type="number", required=True),
            ]
        )
        executor = FormExecutor(config)

        with pytest.raises(ValueError, match="Field type 'number' not supported"):
            executor.validate_fields({"age": 25})

    def test_validate_fields_multiple_fields(self):
        """Given multiple fields, When validated, Then all processed correctly."""
        config = FormStepConfig(
            fields=[
                StepConfigField(key="name", type="text", required=True),
                StepConfigField(key="bio", type="textarea", required=False),
            ]
        )
        executor = FormExecutor(config)

        inputs = {"name": "Jane", "bio": "Software engineer"}
        result = executor.validate_fields(inputs)

        assert result["name"] == "Jane"
        assert result["bio"] == "Software engineer"

    def test_validate_fields_non_string_value(self):
        """Given non-string value for text field, When validated, Then raises ValueError."""
        config = FormStepConfig(
            fields=[
                StepConfigField(key="name", type="text", required=True),
            ]
        )
        executor = FormExecutor(config)

        with pytest.raises(ValueError, match="Field 'name' must be a string"):
            executor.validate_fields({"name": 123})

    @pytest.mark.asyncio
    async def test_execute_pauses_workflow(self):
        """Given form step, When executed, Then run status becomes 'waiting'."""
        config = FormStepConfig(
            fields=[
                StepConfigField(key="email", type="text", required=True),
            ]
        )
        executor = FormExecutor(config)

        context = {"runtime": {}}
        result = await executor.execute(context=context, step_id="form_1")

        assert result["pause"] is True
        assert result["waiting_for"] == "form"
        assert result["fields_schema"] == config.model_dump()["fields"]

    @pytest.mark.asyncio
    async def test_execute_stores_schema_in_context(self):
        """Given form step, When executed, Then field schema stored in context."""
        config = FormStepConfig(
            fields=[
                StepConfigField(key="username", type="text", required=True),
            ]
        )
        executor = FormExecutor(config)

        context = {"runtime": {}}
        await executor.execute(context=context, step_id="form_1")

        assert "form_1_schema" in context["runtime"]
        assert context["runtime"]["form_1_schema"] == config.model_dump()["fields"]
