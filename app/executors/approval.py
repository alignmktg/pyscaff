"""Approval step executor for human approval wait-states."""

import secrets
from typing import Any

from app.models.schemas import ApprovalStepConfig


class ApprovalExecutor:
    """Executes approval steps to pause workflow for human approval."""

    def __init__(self, config: ApprovalStepConfig):
        """Initialize approval executor with step configuration.

        Args:
            config: Approval step configuration containing approver emails
        """
        self.config = config

    def generate_approval_token(self) -> str:
        """Generate secure random approval token.

        Returns:
            URL-safe random token (32 bytes = 43 chars base64)
        """
        return secrets.token_urlsafe(32)

    async def execute(self, context: dict[str, Any], step_id: str) -> dict[str, Any]:
        """Execute approval step by pausing workflow and generating approval token.

        Args:
            context: Current workflow execution context
            step_id: ID of the current step

        Returns:
            Execution result with pause signal, token, and approvers

        Workflow:
            1. Generate secure random approval token
            2. Store token and approvers in context
            3. Return pause signal to engine
            4. Log approval URL (mock email for MVID)
        """
        # Generate secure approval token
        approval_token = self.generate_approval_token()

        # Store approval metadata in context for resume validation
        context["runtime"][f"{step_id}_approval"] = {
            "token": approval_token,
            "approvers": self.config.approvers,
            "status": "pending",
        }

        # Mock email sending (MVID: just log the approval URL)
        # In production, this would send actual emails with approval links
        for approver in self.config.approvers:
            approval_url = f"http://localhost:3000/approvals/{approval_token}"
            print(f"[MOCK EMAIL] To: {approver}")
            print("[MOCK EMAIL] Subject: Approval Required")
            print(f"[MOCK EMAIL] Approval URL: {approval_url}")

        # Return pause signal to engine
        return {
            "pause": True,
            "waiting_for": "approval",
            "approval_token": approval_token,
            "approvers": self.config.approvers,
        }
