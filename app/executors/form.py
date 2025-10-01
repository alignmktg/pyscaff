"""Form step executor for collecting user inputs."""

from typing import Any

from app.models.schemas import FormStepConfig


class FormExecutor:
    """Executes form steps to collect user input with field validation."""

    def __init__(self, config: FormStepConfig):
        """Initialize form executor with step configuration.

        Args:
            config: Form step configuration containing field definitions
        """
        self.config = config

    def validate_fields(self, inputs: dict[str, Any]) -> dict[str, Any]:
        """Validate form inputs against field schema.

        Args:
            inputs: User-provided input values

        Returns:
            Validated inputs

        Raises:
            ValueError: If validation fails (missing required field, invalid type,
                unsupported field type)
        """
        validated = {}

        for field in self.config.fields:
            # Check if required field is missing
            if field.required and field.key not in inputs:
                raise ValueError(f"Required field '{field.key}' is missing")

            # Skip optional missing fields
            if field.key not in inputs:
                continue

            # Validate field type (text/textarea only for MVID)
            if field.type not in ("text", "textarea"):
                raise ValueError(
                    f"Field type '{field.type}' not supported. "
                    "Only 'text' and 'textarea' are allowed."
                )

            # Validate value is string
            value = inputs[field.key]
            if not isinstance(value, str):
                raise ValueError(f"Field '{field.key}' must be a string")

            validated[field.key] = value

        return validated

    async def execute(self, context: dict[str, Any], step_id: str) -> dict[str, Any]:
        """Execute form step by pausing workflow and storing field schema.

        Args:
            context: Current workflow execution context
            step_id: ID of the current step

        Returns:
            Execution result with pause signal and field schema
        """
        # Store field schema in context for resume validation
        context["runtime"][f"{step_id}_schema"] = self.config.model_dump()["fields"]

        # Return pause signal to engine
        return {
            "pause": True,
            "waiting_for": "form",
            "fields_schema": self.config.model_dump()["fields"],
        }
