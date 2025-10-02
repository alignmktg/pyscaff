"""Integration tests for approval workflow execution."""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Step, Workflow
from app.engine.orchestrator import WorkflowEngine


class TestApprovalFlow:
    """Test approval step integration with workflow engine."""

    @pytest.mark.asyncio
    async def test_workflow_pauses_at_approval_step(self, db_session: AsyncSession):
        """Given workflow with approval step, When run starts, Then pauses at approval."""
        # Create workflow with approval step
        workflow_id = str(uuid.uuid4())
        workflow = Workflow(
            id=workflow_id,
            version=1,
            name="approval_test_workflow",
            definition={
                "name": "approval_test_workflow",
                "version": "0.1.0",
                "start_step": "approval_step",
                "steps": [
                    {
                        "id": "approval_step",
                        "type": "approval",
                        "name": "Manager Approval",
                        "next": None,
                        "config": {"approvers": ["manager@example.com"]},
                    }
                ],
            },
            start_step="approval_step",
        )
        db_session.add(workflow)
        await db_session.flush()

        # Create approval step
        step = Step(
            id=str(uuid.uuid4()),
            workflow_id=workflow_id,
            step_id="approval_step",
            type="approval",
            name="Manager Approval",
            next=None,
            config={"approvers": ["manager@example.com"]},
        )
        db_session.add(step)
        await db_session.commit()

        # Start workflow run
        engine = WorkflowEngine(db_session)
        run = await engine.start_run(workflow_id=workflow_id, inputs={})

        # Run should pause at approval step
        assert run.status == "waiting"
        assert run.current_step == "approval_step"

        # Context should have approval metadata
        assert "approval_step_approval" in run.context["runtime"]
        approval_data = run.context["runtime"]["approval_step_approval"]
        assert approval_data["status"] == "pending"
        assert "token" in approval_data
        assert approval_data["approvers"] == ["manager@example.com"]

    @pytest.mark.asyncio
    async def test_resume_approval_with_approved(self, db_session: AsyncSession):
        """Given waiting approval, When resumed with approved=true, Then continues workflow."""
        # Create workflow with approval → next step
        workflow_id = str(uuid.uuid4())
        workflow = Workflow(
            id=workflow_id,
            version=1,
            name="approval_continuation_workflow",
            definition={
                "name": "approval_continuation_workflow",
                "version": "0.1.0",
                "start_step": "approval_step",
                "steps": [
                    {
                        "id": "approval_step",
                        "type": "approval",
                        "name": "Approval",
                        "next": "next_step",
                        "config": {"approvers": ["approver@example.com"]},
                    },
                    {
                        "id": "next_step",
                        "type": "form",
                        "name": "Next Step",
                        "next": None,
                        "config": {"fields": [{"key": "data", "type": "text", "required": True}]},
                    },
                ],
            },
            start_step="approval_step",
        )
        db_session.add(workflow)
        await db_session.flush()

        # Create steps
        approval_step = Step(
            id=str(uuid.uuid4()),
            workflow_id=workflow_id,
            step_id="approval_step",
            type="approval",
            name="Approval",
            next="next_step",
            config={"approvers": ["approver@example.com"]},
        )
        next_step = Step(
            id=str(uuid.uuid4()),
            workflow_id=workflow_id,
            step_id="next_step",
            type="form",
            name="Next Step",
            next=None,
            config={"fields": [{"key": "data", "type": "text", "required": True}]},
        )
        db_session.add(approval_step)
        db_session.add(next_step)
        await db_session.commit()

        # Start workflow
        engine = WorkflowEngine(db_session)
        run = await engine.start_run(workflow_id=workflow_id, inputs={})

        assert run.status == "waiting"
        assert run.current_step == "approval_step"

        # Resume with approval
        approval_inputs = {
            "approval": {
                "approved": True,
                "comments": "Approved by manager",
            }
        }
        resumed_run = await engine.resume_run(run_id=run.id, inputs=approval_inputs)

        # Should move to next step
        assert resumed_run.status == "waiting"  # Next step is also a form
        assert resumed_run.current_step == "next_step"

        # Approval metadata should be updated
        approval_data = resumed_run.context["runtime"]["approval_step_approval"]
        assert approval_data["status"] == "approved"
        assert approval_data["comments"] == "Approved by manager"

    @pytest.mark.asyncio
    async def test_resume_approval_with_rejected(self, db_session: AsyncSession):
        """Given waiting approval, When resumed with approved=false, Then marks as rejected."""
        # Create workflow with approval step
        workflow_id = str(uuid.uuid4())
        workflow = Workflow(
            id=workflow_id,
            version=1,
            name="rejection_test_workflow",
            definition={
                "name": "rejection_test_workflow",
                "version": "0.1.0",
                "start_step": "approval_step",
                "steps": [
                    {
                        "id": "approval_step",
                        "type": "approval",
                        "name": "Approval",
                        "next": "next_step",
                        "config": {"approvers": ["approver@example.com"]},
                    },
                    {
                        "id": "next_step",
                        "type": "form",
                        "name": "Next",
                        "next": None,
                        "config": {"fields": []},
                    },
                ],
            },
            start_step="approval_step",
        )
        db_session.add(workflow)
        await db_session.flush()

        approval_step = Step(
            id=str(uuid.uuid4()),
            workflow_id=workflow_id,
            step_id="approval_step",
            type="approval",
            name="Approval",
            next="next_step",
            config={"approvers": ["approver@example.com"]},
        )
        next_step = Step(
            id=str(uuid.uuid4()),
            workflow_id=workflow_id,
            step_id="next_step",
            type="form",
            name="Next",
            next=None,
            config={"fields": []},
        )
        db_session.add(approval_step)
        db_session.add(next_step)
        await db_session.commit()

        # Start workflow
        engine = WorkflowEngine(db_session)
        run = await engine.start_run(workflow_id=workflow_id, inputs={})

        # Resume with rejection
        rejection_inputs = {
            "approval": {
                "approved": False,
                "comments": "Rejected due to policy violation",
            }
        }
        resumed_run = await engine.resume_run(run_id=run.id, inputs=rejection_inputs)

        # Should still move to next step (workflow doesn't block on rejection in MVID)
        assert resumed_run.current_step == "next_step"

        # Approval should be marked as rejected
        approval_data = resumed_run.context["runtime"]["approval_step_approval"]
        assert approval_data["status"] == "rejected"
        assert approval_data["comments"] == "Rejected due to policy violation"

    @pytest.mark.asyncio
    async def test_resume_approval_missing_approval_key(self, db_session: AsyncSession):
        """Given waiting approval, When resumed without approval key, Then raises error."""
        # Create workflow
        workflow_id = str(uuid.uuid4())
        workflow = Workflow(
            id=workflow_id,
            version=1,
            name="validation_test_workflow",
            definition={},
            start_step="approval_step",
        )
        db_session.add(workflow)
        await db_session.flush()

        step = Step(
            id=str(uuid.uuid4()),
            workflow_id=workflow_id,
            step_id="approval_step",
            type="approval",
            name="Approval",
            next=None,
            config={"approvers": ["approver@example.com"]},
        )
        db_session.add(step)
        await db_session.commit()

        # Start workflow
        engine = WorkflowEngine(db_session)
        run = await engine.start_run(workflow_id=workflow_id, inputs={})

        # Try to resume with invalid inputs
        with pytest.raises(ValueError, match="Missing 'approval' key"):
            await engine.resume_run(run_id=run.id, inputs={"invalid": "data"})

    @pytest.mark.asyncio
    async def test_resume_approval_missing_approved_field(self, db_session: AsyncSession):
        """Given waiting approval, When approved field missing, Then raises error."""
        # Create workflow
        workflow_id = str(uuid.uuid4())
        workflow = Workflow(
            id=workflow_id,
            version=1,
            name="validation_test_workflow",
            definition={},
            start_step="approval_step",
        )
        db_session.add(workflow)
        await db_session.flush()

        step = Step(
            id=str(uuid.uuid4()),
            workflow_id=workflow_id,
            step_id="approval_step",
            type="approval",
            name="Approval",
            next=None,
            config={"approvers": ["approver@example.com"]},
        )
        db_session.add(step)
        await db_session.commit()

        # Start workflow
        engine = WorkflowEngine(db_session)
        run = await engine.start_run(workflow_id=workflow_id, inputs={})

        # Try to resume with missing approved field
        with pytest.raises(ValueError, match="Missing 'approved' field"):
            await engine.resume_run(
                run_id=run.id,
                inputs={"approval": {"comments": "test"}},
            )

    @pytest.mark.asyncio
    async def test_approval_with_multiple_approvers(self, db_session: AsyncSession):
        """Given approval with multiple approvers, When executed, Then all stored correctly."""
        approvers = [
            "manager@example.com",
            "director@example.com",
            "ceo@example.com",
        ]

        # Create workflow
        workflow_id = str(uuid.uuid4())
        workflow = Workflow(
            id=workflow_id,
            version=1,
            name="multi_approval_workflow",
            definition={},
            start_step="approval_step",
        )
        db_session.add(workflow)
        await db_session.flush()

        step = Step(
            id=str(uuid.uuid4()),
            workflow_id=workflow_id,
            step_id="approval_step",
            type="approval",
            name="Multi-level Approval",
            next=None,
            config={"approvers": approvers},
        )
        db_session.add(step)
        await db_session.commit()

        # Start workflow
        engine = WorkflowEngine(db_session)
        run = await engine.start_run(workflow_id=workflow_id, inputs={})

        # Check all approvers stored
        approval_data = run.context["runtime"]["approval_step_approval"]
        assert approval_data["approvers"] == approvers
