"""Conditional step executor for workflow branching via sandboxed expression evaluation."""

from typing import Any

from asteval import Interpreter

from app.models.schemas import ConditionalStepConfig

# Maximum expression length to prevent DoS
MAX_EXPRESSION_LENGTH = 256

# Timeout for expression evaluation (milliseconds)
EXPRESSION_TIMEOUT_MS = 100

# Whitelisted safe functions for expression evaluation
SAFE_FUNCTIONS = {
    "min": min,
    "max": max,
    "abs": abs,
    "len": len,
    "str": str,
    "int": int,
    "float": float,
    "bool": bool,
}


class ConditionalExecutor:
    """Executes conditional steps using sandboxed expression evaluation."""

    def __init__(self, config: ConditionalStepConfig):
        """Initialize conditional executor with step configuration.

        Args:
            config: Conditional step configuration containing expression
        """
        self.config = config

    def _create_interpreter(self) -> Interpreter:
        """Create a sandboxed asteval interpreter with safety restrictions.

        Returns:
            Configured asteval Interpreter instance
        """
        # Create interpreter with minimal builtins
        interpreter = Interpreter(
            usersyms=SAFE_FUNCTIONS.copy(),
            use_numpy=False,  # Disable numpy to reduce attack surface
            max_time=EXPRESSION_TIMEOUT_MS / 1000.0,  # Convert ms to seconds
        )

        # Disable potentially dangerous operations
        interpreter.no_print = True
        interpreter.no_if = True  # Disable if statements
        interpreter.no_for = True  # Disable for loops
        interpreter.no_while = True  # Disable while loops
        interpreter.no_try = True  # Disable try/except
        interpreter.no_functiondef = True  # Disable function definitions
        interpreter.no_ifexp = False  # Allow ternary expressions (safe)
        interpreter.no_listcomp = False  # Allow list comprehensions (safe)
        interpreter.no_augassign = True  # Disable augmented assignment
        interpreter.no_assert = True  # Disable assertions
        interpreter.no_delete = True  # Disable del statements
        interpreter.no_raise = True  # Disable raise statements
        interpreter.no_import = True  # Disable imports

        return interpreter

    def _validate_expression(self, expression: str) -> None:
        """Validate expression before evaluation.

        Args:
            expression: Boolean expression to validate

        Raises:
            ValueError: If expression is invalid (empty, too long, unsafe patterns)
        """
        # Check for empty expression
        if not expression or not expression.strip():
            raise ValueError("Expression cannot be empty")

        # Check length limit
        if len(expression) > MAX_EXPRESSION_LENGTH:
            raise ValueError(
                f"Expression exceeds maximum length of {MAX_EXPRESSION_LENGTH} characters"
            )

        # Block attribute access attempts (basic security check)
        if "__" in expression or "." in expression:
            # Allow . in numbers (e.g., 3.14) but block attribute access
            import re

            # Check if all dots are part of numeric literals
            if re.search(r"[a-zA-Z_]\.", expression):
                raise ValueError("Attribute access not allowed in expressions")

    def _merge_context_namespaces(self, context: dict[str, Any]) -> dict[str, Any]:
        """Merge context layers into flat namespace for expression evaluation.

        Priority order: runtime > profile > static (later overrides earlier).

        Args:
            context: Workflow execution context with static/profile/runtime layers

        Returns:
            Flattened namespace dictionary
        """
        namespace = {}

        # Merge in priority order (static first, runtime last to override)
        for layer in ["static", "profile", "runtime"]:
            if layer in context and isinstance(context[layer], dict):
                namespace.update(context[layer])

        return namespace

    async def execute(self, context: dict[str, Any], step_id: str) -> dict[str, Any]:
        """Execute conditional step by evaluating sandboxed boolean expression.

        Args:
            context: Current workflow execution context
            step_id: ID of the current step

        Returns:
            Execution result with boolean evaluation result

        Raises:
            ValueError: If expression is invalid or unsafe
            NameError: If expression references undefined variables
            SyntaxError: If expression has syntax errors
        """
        expression = self.config.when

        # Validate expression before evaluation
        self._validate_expression(expression)

        # Create sandboxed interpreter
        interpreter = self._create_interpreter()

        # Merge context namespaces into flat namespace
        namespace = self._merge_context_namespaces(context)

        # Load variables into interpreter
        for key, value in namespace.items():
            interpreter.symtable[key] = value

        # Evaluate expression
        try:
            result = interpreter(expression)

            # Check for errors during evaluation
            if interpreter.error:
                error_msg = str(interpreter.error[0])

                # Check for specific error types
                if "not defined" in error_msg:
                    raise NameError(error_msg)
                elif "invalid syntax" in error_msg or "SyntaxError" in error_msg:
                    raise ValueError("Invalid expression syntax")
                elif "import" in error_msg.lower():
                    raise ValueError("Import not allowed in expressions")
                else:
                    raise ValueError(f"Expression evaluation failed: {error_msg}")

        except (SyntaxError, TypeError) as e:
            raise ValueError(f"Invalid expression syntax: {e}") from e

        # Return result
        return {
            "result": bool(result),
            "expression": expression,
        }
