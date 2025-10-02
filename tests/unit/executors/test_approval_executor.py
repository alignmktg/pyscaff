"""Unit tests for ApprovalExecutor."""

import pytest

from app.executors.approval import ApprovalExecutor
from app.models.schemas import ApprovalStepConfig


class TestApprovalExecutor:
    """Test suite for ApprovalExecutor."""

    def test_generate_approval_token(self):
        """Given approval executor, When token generated, Then returns secure random string."""
        config = ApprovalStepConfig(approvers=["user@example.com"])
        executor = ApprovalExecutor(config)

        token = executor.generate_approval_token()

        # Token should be URL-safe string of reasonable length
        assert isinstance(token, str)
        assert len(token) >= 32  # At least 32 chars for security
        assert token.isalnum() or "-" in token or "_" in token  # URL-safe chars

    def test_generate_approval_token_unique(self):
        """Given approval executor, When multiple tokens generated, Then each is unique."""
        config = ApprovalStepConfig(approvers=["user@example.com"])
        executor = ApprovalExecutor(config)

        # Generate multiple tokens
        tokens = [executor.generate_approval_token() for _ in range(10)]

        # All tokens should be unique
        assert len(tokens) == len(set(tokens))

    @pytest.mark.asyncio
    async def test_execute_pauses_workflow(self):
        """Given approval step, When executed, Then run pauses with waiting_for='approval'."""
        config = ApprovalStepConfig(approvers=["approver1@example.com", "approver2@example.com"])
        executor = ApprovalExecutor(config)

        context = {"runtime": {}}
        result = await executor.execute(context=context, step_id="approval_1")

        assert result["pause"] is True
        assert result["waiting_for"] == "approval"
        assert "approval_token" in result
        assert result["approvers"] == ["approver1@example.com", "approver2@example.com"]

    @pytest.mark.asyncio
    async def test_execute_stores_approval_metadata_in_context(self):
        """Given approval step, When executed, Then metadata stored in context."""
        config = ApprovalStepConfig(approvers=["manager@example.com"])
        executor = ApprovalExecutor(config)

        context = {"runtime": {}}
        result = await executor.execute(context=context, step_id="approval_1")

        # Check context has approval metadata
        assert "approval_1_approval" in context["runtime"]
        approval_metadata = context["runtime"]["approval_1_approval"]

        assert approval_metadata["token"] == result["approval_token"]
        assert approval_metadata["approvers"] == ["manager@example.com"]
        assert approval_metadata["status"] == "pending"

    @pytest.mark.asyncio
    async def test_execute_returns_approval_token(self):
        """Given approval step, When executed, Then token returned in result."""
        config = ApprovalStepConfig(approvers=["user@example.com"])
        executor = ApprovalExecutor(config)

        context = {"runtime": {}}
        result = await executor.execute(context=context, step_id="step1")

        assert "approval_token" in result
        assert isinstance(result["approval_token"], str)
        assert len(result["approval_token"]) >= 32

    @pytest.mark.asyncio
    async def test_execute_single_approver(self):
        """Given single approver, When executed, Then approver list has one entry."""
        config = ApprovalStepConfig(approvers=["ceo@example.com"])
        executor = ApprovalExecutor(config)

        context = {"runtime": {}}
        result = await executor.execute(context=context, step_id="approval_ceo")

        assert result["approvers"] == ["ceo@example.com"]
        assert context["runtime"]["approval_ceo_approval"]["approvers"] == ["ceo@example.com"]

    @pytest.mark.asyncio
    async def test_execute_multiple_approvers(self):
        """Given multiple approvers, When executed, Then all approvers stored."""
        approvers = [
            "manager@example.com",
            "director@example.com",
            "vp@example.com",
        ]
        config = ApprovalStepConfig(approvers=approvers)
        executor = ApprovalExecutor(config)

        context = {"runtime": {}}
        result = await executor.execute(context=context, step_id="multi_approval")

        assert result["approvers"] == approvers
        assert context["runtime"]["multi_approval_approval"]["approvers"] == approvers

    @pytest.mark.asyncio
    async def test_execute_with_existing_runtime_context(self):
        """Given context with existing data, When executed, Then preserves data."""
        config = ApprovalStepConfig(approvers=["approver@example.com"])
        executor = ApprovalExecutor(config)

        # Context with existing runtime data
        context = {
            "runtime": {
                "previous_step_output": {"result": "success"},
                "user_input": "test data",
            }
        }
        await executor.execute(context=context, step_id="approval_2")

        # Should preserve existing runtime data
        assert context["runtime"]["previous_step_output"] == {"result": "success"}
        assert context["runtime"]["user_input"] == "test data"

        # And add approval metadata
        assert "approval_2_approval" in context["runtime"]

    @pytest.mark.asyncio
    async def test_execute_prints_mock_emails(self, capsys):
        """Given approval step, When executed, Then prints mock email logs."""
        config = ApprovalStepConfig(approvers=["user1@example.com", "user2@example.com"])
        executor = ApprovalExecutor(config)

        context = {"runtime": {}}
        await executor.execute(context=context, step_id="approval_1")

        # Capture printed output
        captured = capsys.readouterr()

        # Should log mock emails for each approver
        assert "[MOCK EMAIL] To: user1@example.com" in captured.out
        assert "[MOCK EMAIL] To: user2@example.com" in captured.out
        assert "Approval Required" in captured.out
        assert "http://localhost:3000/approvals/" in captured.out
