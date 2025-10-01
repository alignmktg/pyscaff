"""Base AI provider abstraction."""

from abc import ABC, abstractmethod
from typing import Any


class AIProvider(ABC):
    """Abstract base class for AI providers (OpenAI, Mock, etc)."""

    @abstractmethod
    async def generate(
        self,
        template_id: str,
        variables: dict[str, Any],
        json_schema: dict[str, Any],
    ) -> dict[str, Any]:
        """Generate AI response matching JSON schema.

        Args:
            template_id: Template identifier for AI prompt
            variables: Variables to interpolate into template
            json_schema: Expected output JSON Schema

        Returns:
            AI-generated response as dict matching schema

        Raises:
            ValueError: If schema validation fails after retries
            TimeoutError: If generation takes too long
        """
        pass
