"""Unit tests for FormExecutor."""

import pytest

from app.executors.form import FormExecutor
from app.models.schemas import FormStepConfig, StepConfigField


class TestFormExecutorValidateFields:
    """Tests for FormExecutor.validate_fields()"""

    def test_validate_fields_success_all_required(self):
        """Given all required fields, When validate_fields called, Then passes."""
        config = FormStepConfig(
            fields=[
                StepConfigField(key="name", type="text", required=True),
                StepConfigField(key="email", type="text", required=True),
            ]
        )
        executor = FormExecutor(config)

        inputs = {"name": "John Doe", "email": "john@example.com"}
        validated = executor.validate_fields(inputs)

        assert validated == inputs

    def test_validate_fields_success_with_optional(self):
        """Given optional field omitted, When validate_fields called, Then passes
        without optional field."""
        config = FormStepConfig(
            fields=[
                StepConfigField(key="name", type="text", required=True),
                StepConfigField(key="notes", type="textarea", required=False),
            ]
        )
        executor = FormExecutor(config)

        inputs = {"name": "John Doe"}
        validated = executor.validate_fields(inputs)

        assert validated == {"name": "John Doe"}
        assert "notes" not in validated

    def test_validate_fields_success_optional_provided(self):
        """Given optional field provided, When validate_fields called,
        Then includes optional field."""
        config = FormStepConfig(
            fields=[
                StepConfigField(key="name", type="text", required=True),
                StepConfigField(key="notes", type="textarea", required=False),
            ]
        )
        executor = FormExecutor(config)

        inputs = {"name": "John Doe", "notes": "Some notes"}
        validated = executor.validate_fields(inputs)

        assert validated == inputs

    def test_validate_fields_missing_required_raises_error(self):
        """Given required field missing, When validate_fields called, Then ValueError raised."""
        config = FormStepConfig(
            fields=[
                StepConfigField(key="name", type="text", required=True),
                StepConfigField(key="email", type="text", required=True),
            ]
        )
        executor = FormExecutor(config)

        inputs = {"name": "John Doe"}  # missing email

        with pytest.raises(ValueError, match="Required field 'email' is missing"):
            executor.validate_fields(inputs)

    def test_validate_fields_unsupported_type_raises_error(self):
        """Given unsupported field type, When validate_fields called, Then ValueError raised."""
        config = FormStepConfig(
            fields=[
                StepConfigField(key="age", type="number", required=True),  # unsupported in MVID
            ]
        )
        executor = FormExecutor(config)

        inputs = {"age": "25"}

        with pytest.raises(
            ValueError,
            match="Field type 'number' not supported. Only 'text' and 'textarea' are allowed.",
        ):
            executor.validate_fields(inputs)

    def test_validate_fields_non_string_value_raises_error(self):
        """Given non-string value, When validate_fields called, Then ValueError raised."""
        config = FormStepConfig(
            fields=[
                StepConfigField(key="name", type="text", required=True),
            ]
        )
        executor = FormExecutor(config)

        inputs = {"name": 12345}  # number instead of string

        with pytest.raises(ValueError, match="Field 'name' must be a string"):
            executor.validate_fields(inputs)

    def test_validate_fields_empty_string_allowed(self):
        """Given empty string for required field, When validate_fields called,
        Then passes."""
        config = FormStepConfig(
            fields=[
                StepConfigField(key="name", type="text", required=True),
            ]
        )
        executor = FormExecutor(config)

        inputs = {"name": ""}
        validated = executor.validate_fields(inputs)

        assert validated == {"name": ""}

    def test_validate_fields_textarea_type_allowed(self):
        """Given textarea field type, When validate_fields called, Then validation passes."""
        config = FormStepConfig(
            fields=[
                StepConfigField(key="description", type="textarea", required=True),
            ]
        )
        executor = FormExecutor(config)

        inputs = {"description": "Long text content\nwith multiple lines"}
        validated = executor.validate_fields(inputs)

        assert validated == inputs

    def test_validate_fields_extra_fields_ignored(self):
        """Given extra fields not in schema, When validate_fields called,
        Then extra fields ignored."""
        config = FormStepConfig(
            fields=[
                StepConfigField(key="name", type="text", required=True),
            ]
        )
        executor = FormExecutor(config)

        inputs = {"name": "John Doe", "extra_field": "ignored"}
        validated = executor.validate_fields(inputs)

        assert validated == {"name": "John Doe"}
        assert "extra_field" not in validated


class TestFormExecutorExecute:
    """Tests for FormExecutor.execute()"""

    @pytest.mark.asyncio
    async def test_execute_returns_pause_signal(self):
        """Given form config, When execute called, Then pause signal returned."""
        config = FormStepConfig(
            fields=[
                StepConfigField(key="name", type="text", required=True),
            ]
        )
        executor = FormExecutor(config)

        context = {"static": {}, "profile": {}, "runtime": {}}
        result = await executor.execute(context, step_id="step_1")

        assert result["pause"] is True
        assert result["waiting_for"] == "form"
        assert "fields_schema" in result

    @pytest.mark.asyncio
    async def test_execute_stores_schema_in_context(self):
        """Given form config, When execute called, Then field schema stored in context."""
        config = FormStepConfig(
            fields=[
                StepConfigField(key="name", type="text", required=True),
                StepConfigField(key="email", type="text", required=True),
            ]
        )
        executor = FormExecutor(config)

        context = {"static": {}, "profile": {}, "runtime": {}}
        await executor.execute(context, step_id="step_1")

        assert "step_1_schema" in context["runtime"]
        schema = context["runtime"]["step_1_schema"]
        assert len(schema) == 2
        assert schema[0]["key"] == "name"
        assert schema[1]["key"] == "email"

    @pytest.mark.asyncio
    async def test_execute_returns_correct_fields_schema(self):
        """Given form config, When execute called, Then fields_schema matches config."""
        config = FormStepConfig(
            fields=[
                StepConfigField(key="username", type="text", required=True),
                StepConfigField(key="bio", type="textarea", required=False),
            ]
        )
        executor = FormExecutor(config)

        context = {"static": {}, "profile": {}, "runtime": {}}
        result = await executor.execute(context, step_id="step_2")

        fields_schema = result["fields_schema"]
        assert len(fields_schema) == 2
        assert fields_schema[0]["key"] == "username"
        assert fields_schema[0]["type"] == "text"
        assert fields_schema[0]["required"] is True
        assert fields_schema[1]["key"] == "bio"
        assert fields_schema[1]["type"] == "textarea"
        assert fields_schema[1]["required"] is False

    @pytest.mark.asyncio
    async def test_execute_preserves_existing_runtime_context(self):
        """Given existing runtime context, When execute called, Then existing context preserved."""
        config = FormStepConfig(
            fields=[
                StepConfigField(key="name", type="text", required=True),
            ]
        )
        executor = FormExecutor(config)

        context = {
            "static": {},
            "profile": {},
            "runtime": {"previous_step_data": "preserved"},
        }
        await executor.execute(context, step_id="step_3")

        assert context["runtime"]["previous_step_data"] == "preserved"
        assert "step_3_schema" in context["runtime"]
