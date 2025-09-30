"""Unit tests for database models and Pydantic schemas."""

import uuid
from datetime import datetime

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Run, RunStep, Step, Workflow


class TestWorkflowModel:
    """Test Workflow SQLAlchemy model."""

    @pytest.mark.asyncio
    async def test_create_workflow(self, db_session: AsyncSession) -> None:
        """Test creating a workflow with all fields."""
        workflow_id = str(uuid.uuid4())
        definition = {
            "name": "test_workflow",
            "version": "0.1.0",
            "start_step": "step1",
            "steps": [
                {
                    "id": "step1",
                    "type": "form",
                    "name": "Test Form",
                    "next": None,
                    "config": {"fields": []},
                }
            ],
        }

        workflow = Workflow(
            id=workflow_id,
            version=1,
            name="test_workflow",
            definition=definition,
            start_step="step1",
        )

        db_session.add(workflow)
        await db_session.commit()
        await db_session.refresh(workflow)

        # Verify fields persist correctly
        assert workflow.id == workflow_id
        assert workflow.version == 1
        assert workflow.name == "test_workflow"
        assert workflow.definition == definition
        assert workflow.start_step == "step1"
        assert isinstance(workflow.created_at, datetime)

    @pytest.mark.asyncio
    async def test_workflow_steps_relationship(self, db_session: AsyncSession) -> None:
        """Test Workflow has relationship to Steps."""
        workflow = Workflow(
            id=str(uuid.uuid4()),
            version=1,
            name="test_workflow",
            definition={},
            start_step="step1",
        )
        db_session.add(workflow)
        await db_session.flush()

        step = Step(
            id=str(uuid.uuid4()),
            workflow_id=workflow.id,
            step_id="step1",
            type="form",
            name="Test Step",
            next=None,
            config={"fields": []},
        )
        db_session.add(step)
        await db_session.commit()

        # Refresh to load relationships
        await db_session.refresh(workflow)

        assert len(workflow.steps) == 1
        assert workflow.steps[0].step_id == "step1"


class TestStepModel:
    """Test Step SQLAlchemy model."""

    @pytest.mark.asyncio
    async def test_create_step(self, db_session: AsyncSession) -> None:
        """Test creating a step with all fields."""
        workflow = Workflow(
            id=str(uuid.uuid4()),
            version=1,
            name="test_workflow",
            definition={},
            start_step="step1",
        )
        db_session.add(workflow)
        await db_session.flush()

        step_id = str(uuid.uuid4())
        config = {
            "fields": [
                {"key": "name", "type": "string", "required": True},
            ]
        }

        step = Step(
            id=step_id,
            workflow_id=workflow.id,
            step_id="step1",
            type="form",
            name="Collect Name",
            next="step2",
            config=config,
        )

        db_session.add(step)
        await db_session.commit()
        await db_session.refresh(step)

        # Verify fields persist correctly
        assert step.id == step_id
        assert step.workflow_id == workflow.id
        assert step.step_id == "step1"
        assert step.type == "form"
        assert step.name == "Collect Name"
        assert step.next == "step2"
        assert step.config == config

    @pytest.mark.asyncio
    async def test_step_types(self, db_session: AsyncSession) -> None:
        """Test all valid step types can be created."""
        workflow = Workflow(
            id=str(uuid.uuid4()),
            version=1,
            name="test_workflow",
            definition={},
            start_step="step1",
        )
        db_session.add(workflow)
        await db_session.flush()

        step_types = ["form", "ai_generate", "conditional", "api_call", "approval"]

        for idx, step_type in enumerate(step_types):
            step = Step(
                id=str(uuid.uuid4()),
                workflow_id=workflow.id,
                step_id=f"step{idx + 1}",
                type=step_type,
                name=f"Test {step_type}",
                next=None,
                config={},
            )
            db_session.add(step)

        await db_session.commit()

        # Query all steps
        result = await db_session.execute(select(Step).where(Step.workflow_id == workflow.id))
        steps = result.scalars().all()

        assert len(steps) == 5
        created_types = {step.type for step in steps}
        assert created_types == set(step_types)


class TestRunModel:
    """Test Run SQLAlchemy model."""

    @pytest.mark.asyncio
    async def test_create_run(self, db_session: AsyncSession) -> None:
        """Test creating a run with all required fields."""
        workflow = Workflow(
            id=str(uuid.uuid4()),
            version=1,
            name="test_workflow",
            definition={},
            start_step="step1",
        )
        db_session.add(workflow)
        await db_session.flush()

        run_id = str(uuid.uuid4())
        context = {
            "static": {"app_name": "test"},
            "profile": {"user_id": "123"},
            "runtime": {},
        }

        run = Run(
            id=run_id,
            workflow_id=workflow.id,
            workflow_version=1,
            status="queued",
            current_step=None,
            context=context,
            idempotency_key="test-key-123",
        )

        db_session.add(run)
        await db_session.commit()
        await db_session.refresh(run)

        # Verify fields persist correctly
        assert run.id == run_id
        assert run.workflow_id == workflow.id
        assert run.workflow_version == 1
        assert run.status == "queued"
        assert run.current_step is None
        assert run.context == context
        assert run.idempotency_key == "test-key-123"
        assert isinstance(run.started_at, datetime)
        assert isinstance(run.updated_at, datetime)

    @pytest.mark.asyncio
    async def test_run_statuses(self, db_session: AsyncSession) -> None:
        """Test all valid run statuses."""
        workflow = Workflow(
            id=str(uuid.uuid4()),
            version=1,
            name="test_workflow",
            definition={},
            start_step="step1",
        )
        db_session.add(workflow)
        await db_session.flush()

        statuses = ["queued", "running", "waiting", "completed", "failed", "canceled"]

        for status in statuses:
            run = Run(
                id=str(uuid.uuid4()),
                workflow_id=workflow.id,
                workflow_version=1,
                status=status,
                current_step=None,
                context={},
            )
            db_session.add(run)

        await db_session.commit()

        # Query all runs
        result = await db_session.execute(select(Run).where(Run.workflow_id == workflow.id))
        runs = result.scalars().all()

        assert len(runs) == 6
        created_statuses = {run.status for run in runs}
        assert created_statuses == set(statuses)

    @pytest.mark.asyncio
    async def test_run_idempotency_key_unique(self, db_session: AsyncSession) -> None:
        """Test idempotency key uniqueness constraint."""
        workflow = Workflow(
            id=str(uuid.uuid4()),
            version=1,
            name="test_workflow",
            definition={},
            start_step="step1",
        )
        db_session.add(workflow)
        await db_session.flush()

        # Create first run with idempotency key
        run1 = Run(
            id=str(uuid.uuid4()),
            workflow_id=workflow.id,
            workflow_version=1,
            status="queued",
            current_step=None,
            context={},
            idempotency_key="unique-key",
        )
        db_session.add(run1)
        await db_session.commit()

        # Attempt to create second run with same idempotency key
        run2 = Run(
            id=str(uuid.uuid4()),
            workflow_id=workflow.id,
            workflow_version=1,
            status="queued",
            current_step=None,
            context={},
            idempotency_key="unique-key",
        )
        db_session.add(run2)

        # Should raise integrity error
        from sqlalchemy.exc import IntegrityError

        with pytest.raises(IntegrityError):
            await db_session.commit()


class TestRunStepModel:
    """Test RunStep SQLAlchemy model."""

    @pytest.mark.asyncio
    async def test_create_run_step(self, db_session: AsyncSession) -> None:
        """Test creating run step execution record."""
        workflow = Workflow(
            id=str(uuid.uuid4()),
            version=1,
            name="test_workflow",
            definition={},
            start_step="step1",
        )
        db_session.add(workflow)
        await db_session.flush()

        run = Run(
            id=str(uuid.uuid4()),
            workflow_id=workflow.id,
            workflow_version=1,
            status="running",
            current_step="step1",
            context={},
        )
        db_session.add(run)
        await db_session.flush()

        run_step_id = str(uuid.uuid4())
        output = {"result": "success", "data": {"key": "value"}}

        run_step = RunStep(
            id=run_step_id,
            run_id=run.id,
            step_id="step1",
            type="form",
            status="completed",
            output=output,
            error=None,
        )

        db_session.add(run_step)
        await db_session.commit()
        await db_session.refresh(run_step)

        # Verify fields persist correctly
        assert run_step.id == run_step_id
        assert run_step.run_id == run.id
        assert run_step.step_id == "step1"
        assert run_step.type == "form"
        assert run_step.status == "completed"
        assert run_step.output == output
        assert run_step.error is None
        assert isinstance(run_step.started_at, datetime)
        assert isinstance(run_step.ended_at, datetime)

    @pytest.mark.asyncio
    async def test_run_step_with_error(self, db_session: AsyncSession) -> None:
        """Test run step with error message."""
        workflow = Workflow(
            id=str(uuid.uuid4()),
            version=1,
            name="test_workflow",
            definition={},
            start_step="step1",
        )
        db_session.add(workflow)
        await db_session.flush()

        run = Run(
            id=str(uuid.uuid4()),
            workflow_id=workflow.id,
            workflow_version=1,
            status="failed",
            current_step="step1",
            context={},
        )
        db_session.add(run)
        await db_session.flush()

        run_step = RunStep(
            id=str(uuid.uuid4()),
            run_id=run.id,
            step_id="step1",
            type="ai_generate",
            status="failed",
            output=None,
            error="Schema validation failed: missing required field 'greeting'",
        )

        db_session.add(run_step)
        await db_session.commit()
        await db_session.refresh(run_step)

        assert run_step.status == "failed"
        assert run_step.output is None
        assert "Schema validation failed" in run_step.error

    @pytest.mark.asyncio
    async def test_run_steps_relationship(self, db_session: AsyncSession) -> None:
        """Test Run has relationship to RunSteps for execution history."""
        workflow = Workflow(
            id=str(uuid.uuid4()),
            version=1,
            name="test_workflow",
            definition={},
            start_step="step1",
        )
        db_session.add(workflow)
        await db_session.flush()

        run = Run(
            id=str(uuid.uuid4()),
            workflow_id=workflow.id,
            workflow_version=1,
            status="completed",
            current_step=None,
            context={},
        )
        db_session.add(run)
        await db_session.flush()

        # Create execution history
        for idx in range(3):
            run_step = RunStep(
                id=str(uuid.uuid4()),
                run_id=run.id,
                step_id=f"step{idx + 1}",
                type="form",
                status="completed",
                output={"step": idx + 1},
                error=None,
            )
            db_session.add(run_step)

        await db_session.commit()
        await db_session.refresh(run)

        # Verify relationship loads execution history
        assert len(run.run_steps) == 3
        assert [step.step_id for step in run.run_steps] == ["step1", "step2", "step3"]
