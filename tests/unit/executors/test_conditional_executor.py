"""Unit tests for ConditionalExecutor."""

import pytest

from app.executors.conditional import ConditionalExecutor
from app.models.schemas import ConditionalStepConfig


class TestConditionalExecutor:
    """Test suite for ConditionalExecutor."""

    @pytest.mark.asyncio
    async def test_simple_boolean_true(self):
        """Given simple boolean expression, When true, Then returns True."""
        config = ConditionalStepConfig(when="age >= 18")
        executor = ConditionalExecutor(config)

        context = {"runtime": {"age": 25}}
        result = await executor.execute(context=context, step_id="cond_1")

        assert result["result"] is True
        assert result["expression"] == "age >= 18"

    @pytest.mark.asyncio
    async def test_simple_boolean_false(self):
        """Given simple boolean expression, When false, Then returns False."""
        config = ConditionalStepConfig(when="age >= 18")
        executor = ConditionalExecutor(config)

        context = {"runtime": {"age": 15}}
        result = await executor.execute(context=context, step_id="cond_1")

        assert result["result"] is False
        assert result["expression"] == "age >= 18"

    @pytest.mark.asyncio
    async def test_comparison_operators(self):
        """Given comparison operators, When evaluated, Then returns correct result."""
        test_cases = [
            ("score > 80", {"score": 85}, True),
            ("score < 80", {"score": 75}, True),
            ("score == 100", {"score": 100}, True),
            ("score != 50", {"score": 75}, True),
            ("score <= 90", {"score": 90}, True),
            ("score >= 60", {"score": 60}, True),
        ]

        for expression, runtime_data, expected in test_cases:
            config = ConditionalStepConfig(when=expression)
            executor = ConditionalExecutor(config)
            context = {"runtime": runtime_data}

            result = await executor.execute(context=context, step_id="cond_1")

            assert result["result"] is expected

    @pytest.mark.asyncio
    async def test_compound_expression(self):
        """Given compound expression, When evaluated, Then returns correct result."""
        config = ConditionalStepConfig(when="score > 80 and attempts < 3")
        executor = ConditionalExecutor(config)

        context = {"runtime": {"score": 85, "attempts": 2}}
        result = await executor.execute(context=context, step_id="cond_1")

        assert result["result"] is True

    @pytest.mark.asyncio
    async def test_compound_expression_false(self):
        """Given compound expression, When one condition false, Then returns False."""
        config = ConditionalStepConfig(when="score > 80 and attempts < 3")
        executor = ConditionalExecutor(config)

        context = {"runtime": {"score": 85, "attempts": 5}}
        result = await executor.execute(context=context, step_id="cond_1")

        assert result["result"] is False

    @pytest.mark.asyncio
    async def test_nested_context_access(self):
        """Given nested context access, When evaluated, Then merges namespaces correctly."""
        config = ConditionalStepConfig(when="value > threshold")
        executor = ConditionalExecutor(config)

        context = {"static": {"threshold": 100}, "runtime": {"value": 150}}
        result = await executor.execute(context=context, step_id="cond_1")

        assert result["result"] is True

    @pytest.mark.asyncio
    async def test_context_priority_runtime_over_static(self):
        """Given same key in multiple contexts, When evaluated, Then runtime takes priority."""
        config = ConditionalStepConfig(when="threshold > 50")
        executor = ConditionalExecutor(config)

        context = {
            "static": {"threshold": 25},
            "runtime": {"threshold": 100},  # This should win
        }
        result = await executor.execute(context=context, step_id="cond_1")

        assert result["result"] is True

    @pytest.mark.asyncio
    async def test_missing_variable_error(self):
        """Given missing variable, When evaluated, Then raises NameError."""
        config = ConditionalStepConfig(when="nonexistent_var > 0")
        executor = ConditionalExecutor(config)

        context = {"runtime": {}}

        with pytest.raises(NameError, match="name 'nonexistent_var' is not defined"):
            await executor.execute(context=context, step_id="cond_1")

    @pytest.mark.asyncio
    async def test_invalid_syntax_error(self):
        """Given invalid syntax, When evaluated, Then raises ValueError."""
        config = ConditionalStepConfig(when="age >= >= 18")
        executor = ConditionalExecutor(config)

        context = {"runtime": {"age": 25}}

        with pytest.raises(ValueError, match="Invalid expression syntax"):
            await executor.execute(context=context, step_id="cond_1")

    @pytest.mark.asyncio
    async def test_blocked_attribute_access(self):
        """Given attribute access attempt, When evaluated, Then raises SecurityError."""
        config = ConditionalStepConfig(when="user.__class__")
        executor = ConditionalExecutor(config)

        context = {"runtime": {"user": "test"}}

        with pytest.raises(ValueError, match="Attribute access not allowed"):
            await executor.execute(context=context, step_id="cond_1")

    @pytest.mark.asyncio
    async def test_blocked_import(self):
        """Given import attempt, When evaluated, Then raises SecurityError."""
        config = ConditionalStepConfig(when="import os")
        executor = ConditionalExecutor(config)

        context = {"runtime": {}}

        with pytest.raises(ValueError, match="Invalid expression syntax|Import not allowed"):
            await executor.execute(context=context, step_id="cond_1")

    @pytest.mark.asyncio
    async def test_whitelist_functions(self):
        """Given whitelisted functions, When evaluated, Then executes successfully."""
        test_cases = [
            ("max(a, b) > 50", {"a": 30, "b": 60}, True),
            ("min(a, b) < 50", {"a": 30, "b": 60}, True),
            ("abs(x) == 10", {"x": -10}, True),
            ("len(items) > 0", {"items": [1, 2, 3]}, True),
            ("str(age) == '25'", {"age": 25}, True),
            ("int(score) > 80", {"score": 85.5}, True),
            ("float(value) < 100.0", {"value": 99}, True),
            ("bool(flag)", {"flag": 1}, True),
        ]

        for expression, runtime_data, expected in test_cases:
            config = ConditionalStepConfig(when=expression)
            executor = ConditionalExecutor(config)
            context = {"runtime": runtime_data}

            result = await executor.execute(context=context, step_id="cond_1")

            assert result["result"] is expected

    @pytest.mark.asyncio
    async def test_logical_operators(self):
        """Given logical operators (and/or/not), When evaluated, Then returns correct result."""
        test_cases = [
            ("a and b", {"a": True, "b": True}, True),
            ("a or b", {"a": False, "b": True}, True),
            ("not a", {"a": False}, True),
            ("a and b or c", {"a": True, "b": False, "c": True}, True),
        ]

        for expression, runtime_data, expected in test_cases:
            config = ConditionalStepConfig(when=expression)
            executor = ConditionalExecutor(config)
            context = {"runtime": runtime_data}

            result = await executor.execute(context=context, step_id="cond_1")

            assert result["result"] is expected

    @pytest.mark.asyncio
    async def test_numeric_operations(self):
        """Given numeric operations, When evaluated, Then returns correct result."""
        test_cases = [
            ("a + b > 100", {"a": 60, "b": 50}, True),
            ("a - b < 10", {"a": 25, "b": 20}, True),
            ("a * b == 100", {"a": 10, "b": 10}, True),
            ("a / b == 2", {"a": 10, "b": 5}, True),
            ("a % b == 1", {"a": 11, "b": 5}, True),
        ]

        for expression, runtime_data, expected in test_cases:
            config = ConditionalStepConfig(when=expression)
            executor = ConditionalExecutor(config)
            context = {"runtime": runtime_data}

            result = await executor.execute(context=context, step_id="cond_1")

            assert result["result"] is expected

    @pytest.mark.asyncio
    async def test_expression_length_limit(self):
        """Given expression exceeding length limit, When evaluated, Then raises ValueError."""
        # Create expression longer than 256 characters
        long_expression = "a > 0 " + "and b > 0 " * 30
        config = ConditionalStepConfig(when=long_expression)
        executor = ConditionalExecutor(config)

        context = {"runtime": {"a": 1, "b": 1}}

        with pytest.raises(ValueError, match="Expression exceeds maximum length"):
            await executor.execute(context=context, step_id="cond_1")

    @pytest.mark.asyncio
    async def test_empty_expression(self):
        """Given empty expression, When evaluated, Then raises ValueError."""
        config = ConditionalStepConfig(when="")
        executor = ConditionalExecutor(config)

        context = {"runtime": {}}

        with pytest.raises(ValueError, match="Expression cannot be empty"):
            await executor.execute(context=context, step_id="cond_1")
