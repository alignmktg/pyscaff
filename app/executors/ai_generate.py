"""AI generate step executor with schema enforcement."""

import os
from typing import Any

from jsonschema import ValidationError, validate

from app.agent.base import AIProvider
from app.agent.litellm_provider import LiteLLMProvider
from app.agent.mock import MockAIProvider
from app.models.schemas import AIGenerateStepConfig


class AIGenerateExecutor:
    """Executes AI generation steps with JSON schema validation and retry logic."""

    MAX_RETRIES = 2

    def __init__(self, config: AIGenerateStepConfig, provider: AIProvider | None = None):
        """Initialize AI generate executor.

        Args:
            config: AI generate step configuration
            provider: AI provider instance (defaults based on AI_PROVIDER env var)
        """
        self.config = config
        self.provider: AIProvider

        # Use provided provider or create based on env
        if provider is None:
            ai_provider = os.getenv("AI_PROVIDER", "mock").lower()

            if ai_provider == "mock":
                # Use mock provider with configurable mode
                ai_mode = os.getenv("MOCK_AI_MODE", "success")
                ai_seed = int(os.getenv("MOCK_AI_SEED", "42"))
                self.provider = MockAIProvider(mode=ai_mode, seed=ai_seed)
            else:
                # Use LiteLLM for real AI providers (openai, anthropic, etc.)
                ai_model = os.getenv("AI_MODEL")
                self.provider = LiteLLMProvider(model=ai_model)
        else:
            self.provider = provider

    def _extract_variables(self, context: dict[str, Any]) -> dict[str, Any]:
        """Extract template variables from context.

        Args:
            context: Workflow execution context

        Returns:
            Dictionary of variable name → value

        Raises:
            ValueError: If required variable not found in context
        """
        variables = {}

        for var_name in self.config.variables:
            # Search in static, profile, then runtime
            value = None
            for section in ["static", "profile", "runtime"]:
                if section in context and var_name in context[section]:
                    value = context[section][var_name]
                    break

            if value is None:
                raise ValueError(
                    f"Variable '{var_name}' not found in context. Checked: static, profile, runtime"
                )

            variables[var_name] = value

        return variables

    async def execute(self, context: dict[str, Any], step_id: str) -> dict[str, Any]:
        """Execute AI generation step with schema validation and retry logic.

        Args:
            context: Current workflow execution context
            step_id: ID of the current step

        Returns:
            Execution result with output or pause signal

        Workflow:
            1. Extract variables from context
            2. Call AI provider with template + variables + schema
            3. Validate response against JSON schema
            4. On validation failure:
                - If retries < MAX_RETRIES: retry
                - If retries exhausted: pause for manual fix
            5. Store output in context runtime
        """
        # Extract template variables from context
        variables = self._extract_variables(context)

        retry_count = 0
        last_error = None

        while retry_count <= self.MAX_RETRIES:
            try:
                # Generate AI response
                output = await self.provider.generate(
                    template_id=self.config.template_id,
                    variables=variables,
                    json_schema=self.config.json_schema,
                )

                # Validate against JSON schema
                validate(instance=output, schema=self.config.json_schema)

                # Success! Store output in context and return
                context["runtime"][f"{step_id}_output"] = output

                return {
                    "pause": False,
                    "output": output,
                    "retry_count": retry_count,
                }

            except ValidationError as e:
                last_error = f"Schema validation failed: {e.message}"
                retry_count += 1

                if retry_count <= self.MAX_RETRIES:
                    # Retry
                    continue
                else:
                    # Exhausted retries, pause for manual intervention
                    return {
                        "pause": True,
                        "waiting_for": "manual_fix",
                        "error": last_error,
                        "retry_count": retry_count,
                    }

            except (TimeoutError, Exception) as e:
                # Non-retryable error or timeout
                last_error = str(e)
                retry_count += 1

                if retry_count <= self.MAX_RETRIES:
                    continue
                else:
                    return {
                        "pause": True,
                        "waiting_for": "manual_fix",
                        "error": last_error,
                        "retry_count": retry_count,
                    }

        # Should never reach here, but safety fallback
        return {
            "pause": True,
            "waiting_for": "manual_fix",
            "error": last_error or "Unknown error",
            "retry_count": retry_count,
        }
