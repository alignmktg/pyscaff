"""Mock AI provider for deterministic testing."""

import random
from typing import Any

from app.agent.base import AIProvider


class MockAIProvider(AIProvider):
    """Mock AI provider that returns deterministic responses for testing."""

    def __init__(self, mode: str = "success", seed: int = 42):
        """Initialize mock provider.

        Args:
            mode: Operation mode (success, schema_violation, timeout, transient_error)
            seed: RNG seed for deterministic outputs
        """
        self.mode = mode
        self.seed = seed
        self.call_count = 0
        random.seed(seed)

    async def generate(
        self,
        template_id: str,
        variables: dict[str, Any],
        json_schema: dict[str, Any],
    ) -> dict[str, Any]:
        """Generate mock AI response based on configured mode.

        Args:
            template_id: Template identifier
            variables: Variables for template
            json_schema: Expected output schema

        Returns:
            Mock response matching schema (in success mode)

        Raises:
            ValueError: In schema_violation mode
            TimeoutError: In timeout mode
        """
        self.call_count += 1

        if self.mode == "timeout":
            raise TimeoutError("Mock AI provider timed out")

        if self.mode == "transient_error" and self.call_count == 1:
            raise ValueError("Transient error (will succeed on retry)")

        if self.mode == "schema_violation":
            # Return invalid response missing required fields
            return {"invalid": "response"}

        # Success mode: generate valid response based on schema
        return self._generate_from_schema(json_schema)

    def _generate_from_schema(self, schema: dict[str, Any]) -> dict[str, Any]:
        """Generate valid JSON matching schema.

        Args:
            schema: JSON Schema to match

        Returns:
            Generated JSON object
        """
        if schema.get("type") != "object":
            raise ValueError("Only object schemas supported in mock")

        properties = schema.get("properties", {})
        required = schema.get("required", [])
        result = {}

        for prop_name, prop_schema in properties.items():
            if prop_name in required or random.random() > 0.3:
                result[prop_name] = self._generate_value(prop_schema)

        return result

    def _generate_value(self, schema: dict[str, Any]) -> Any:
        """Generate value matching property schema.

        Args:
            schema: Property schema

        Returns:
            Generated value
        """
        prop_type = schema.get("type")

        if prop_type == "string":
            return f"mock_value_{random.randint(1, 100)}"
        elif prop_type == "integer":
            return random.randint(1, 100)
        elif prop_type == "number":
            return round(random.random() * 100, 2)
        elif prop_type == "boolean":
            return random.choice([True, False])
        elif prop_type == "array":
            items_schema = schema.get("items", {})
            length = random.randint(1, 3)
            return [self._generate_value(items_schema) for _ in range(length)]
        elif prop_type == "object":
            return self._generate_from_schema(schema)
        else:
            return None
