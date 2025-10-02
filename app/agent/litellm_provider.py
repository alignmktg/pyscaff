"""LiteLLM-based AI provider supporting OpenAI, Anthropic, and other providers."""

import json
import os
from typing import Any

from litellm import acompletion

from app.agent.base import AIProvider


class LiteLLMProvider(AIProvider):
    """AI provider using LiteLLM for unified multi-provider support.

    Supports:
    - OpenAI (gpt-4, gpt-3.5-turbo, etc.) via OPENAI_API_KEY
    - Anthropic (claude-3, etc.) via ANTHROPIC_API_KEY
    - Other providers supported by LiteLLM

    Uses structured outputs with JSON schema enforcement.
    """

    def __init__(
        self,
        model: str | None = None,
        api_key: str | None = None,
        timeout: float = 30.0,
    ):
        """Initialize LiteLLM provider.

        Args:
            model: Model identifier (e.g., "gpt-4", "claude-3-opus-20240229").
                   Defaults to GPT-4 if not specified.
            api_key: API key for the provider. If not provided, will use
                    environment variables (OPENAI_API_KEY, ANTHROPIC_API_KEY, etc.)
            timeout: Request timeout in seconds
        """
        self.model = model or os.getenv("AI_MODEL", "gpt-4")
        self.api_key = api_key
        self.timeout = timeout

    async def generate(
        self,
        template_id: str,
        variables: dict[str, Any],
        json_schema: dict[str, Any],
    ) -> dict[str, Any]:
        """Generate AI response matching JSON schema using LiteLLM.

        Args:
            template_id: Template identifier for AI prompt
            variables: Variables to interpolate into template
            json_schema: Expected output JSON Schema

        Returns:
            AI-generated response as dict matching schema

        Raises:
            ValueError: If schema validation fails or response parsing fails
            TimeoutError: If generation takes too long
        """
        # Build system prompt with schema requirements
        system_prompt = self._build_system_prompt(json_schema)

        # Build user prompt with template variables
        user_prompt = self._build_user_prompt(template_id, variables)

        try:
            # Call LiteLLM with structured output support
            response = await acompletion(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
                timeout=self.timeout,
                api_key=self.api_key,
            )

            # Extract content from response
            content = response.choices[0].message.content

            if not content:
                raise ValueError("Empty response from AI provider")

            # Parse JSON response
            try:
                result: dict[str, Any] = json.loads(content)
            except json.JSONDecodeError as e:
                raise ValueError(f"Failed to parse AI response as JSON: {e}") from e

            # Validate result is a dict
            if not isinstance(result, dict):
                raise ValueError(f"AI response must be a JSON object, got {type(result).__name__}")

            return result

        except TimeoutError as e:
            raise TimeoutError(f"LiteLLM request timed out after {self.timeout}s") from e
        except Exception as e:
            # Re-raise as ValueError for consistency with base interface
            if isinstance(e, (ValueError, TimeoutError)):
                raise
            raise ValueError(f"LiteLLM generation failed: {e}") from e

    def _build_system_prompt(self, json_schema: dict[str, Any]) -> str:
        """Build system prompt with schema requirements.

        Args:
            json_schema: JSON Schema for expected output

        Returns:
            System prompt instructing AI to follow schema
        """
        schema_str = json.dumps(json_schema, indent=2)

        return f"""You are a helpful assistant that generates structured JSON responses.
You must respond with valid JSON that exactly matches the following JSON Schema:

{schema_str}

Requirements:
- Your response must be valid JSON
- All required fields must be present
- Field types must match the schema
- Do not include any text outside the JSON object
"""

    def _build_user_prompt(self, template_id: str, variables: dict[str, Any]) -> str:
        """Build user prompt with template variables.

        Args:
            template_id: Template identifier
            variables: Variables to include in prompt

        Returns:
            User prompt with variables
        """
        # For now, use a simple template format
        # In production, this would load actual templates from a template store
        var_str = "\n".join(f"- {k}: {v}" for k, v in variables.items())

        return f"""Template: {template_id}

Variables:
{var_str}

Generate a response matching the required JSON schema."""
