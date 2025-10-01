"""Unit tests for WorkflowEngine orchestrator."""

import uuid
from typing import Any

import pytest
from sqlalchemy import select

from app.db.models import Run, RunStep, Step, Workflow
from app.engine.orchestrator import WorkflowEngine


@pytest.fixture
async def sample_workflow(db_session: Any) -> Workflow:
    """Create a sample workflow with form → ai_generate → conditional steps."""
    workflow_id = str(uuid.uuid4())

    workflow = Workflow(
        id=workflow_id,
        version=1,
        name="test_workflow",
        definition={
            "name": "test_workflow",
            "version": "0.1.0",
            "start_step": "collect_name",
        },
        start_step="collect_name",
    )

    # Step 1: Form to collect user name
    form_step = Step(
        id=str(uuid.uuid4()),
        workflow_id=workflow_id,
        step_id="collect_name",
        type="form",
        name="Collect Name",
        next="generate_greeting",
        config={
            "fields": [
                {
                    "key": "user_name",
                    "type": "text",
                    "required": True,
                }
            ]
        },
    )

    # Step 2: AI generate greeting
    ai_step = Step(
        id=str(uuid.uuid4()),
        workflow_id=workflow_id,
        step_id="generate_greeting",
        type="ai_generate",
        name="Generate Greeting",
        next="check_result",
        config={
            "template_id": "greeting_template",
            "variables": ["user_name"],
            "json_schema": {
                "type": "object",
                "properties": {
                    "greeting": {"type": "string"},
                    "success": {"type": "boolean"},
                },
                "required": ["greeting", "success"],
            },
        },
    )

    # Step 3: Conditional check
    conditional_step = Step(
        id=str(uuid.uuid4()),
        workflow_id=workflow_id,
        step_id="check_result",
        type="conditional",
        name="Check Result",
        next=None,  # Terminal step
        config={
            "when": "generate_greeting_output['success'] == True",
        },
    )

    workflow.steps = [form_step, ai_step, conditional_step]

    db_session.add(workflow)
    await db_session.commit()
    await db_session.refresh(workflow)

    return workflow


@pytest.fixture
async def simple_workflow(db_session: Any) -> Workflow:
    """Create a simple workflow with single conditional step (no wait-state)."""
    workflow_id = str(uuid.uuid4())

    workflow = Workflow(
        id=workflow_id,
        version=1,
        name="simple_workflow",
        definition={
            "name": "simple_workflow",
            "version": "0.1.0",
            "start_step": "check_input",
        },
        start_step="check_input",
    )

    # Single conditional step
    conditional_step = Step(
        id=str(uuid.uuid4()),
        workflow_id=workflow_id,
        step_id="check_input",
        type="conditional",
        name="Check Input",
        next=None,  # Terminal step
        config={
            "when": "value > 10",
        },
    )

    workflow.steps = [conditional_step]

    db_session.add(workflow)
    await db_session.commit()
    await db_session.refresh(workflow)

    return workflow


class TestWorkflowEngine:
    """Test suite for WorkflowEngine."""

    async def test_start_run_creates_run_record(self, db_session: Any, sample_workflow: Workflow):
        """Given workflow ID, When start_run(), Then creates run with status='running'."""
        engine = WorkflowEngine(db_session)

        run = await engine.start_run(
            workflow_id=sample_workflow.id,
            inputs={"initial": "data"},
        )

        assert run.id is not None
        assert run.workflow_id == sample_workflow.id
        assert run.workflow_version == sample_workflow.version
        assert run.status == "waiting"  # Form step pauses immediately
        assert run.current_step == "collect_name"
        assert run.context["runtime"]["initial"] == "data"

    async def test_start_run_with_idempotency_key(self, db_session: Any, sample_workflow: Workflow):
        """Given idempotency key, When start_run() twice, Then returns same run."""
        engine = WorkflowEngine(db_session)
        idempotency_key = "test-key-123"

        # First call creates run
        run1 = await engine.start_run(
            workflow_id=sample_workflow.id,
            inputs={"initial": "data"},
            idempotency_key=idempotency_key,
        )

        # Second call returns same run
        run2 = await engine.start_run(
            workflow_id=sample_workflow.id,
            inputs={"different": "data"},
            idempotency_key=idempotency_key,
        )

        assert run1.id == run2.id
        assert run2.context["runtime"]["initial"] == "data"  # Original inputs preserved

    async def test_start_run_invalid_workflow(self, db_session: Any):
        """Given invalid workflow ID, When start_run(), Then raises ValueError."""
        engine = WorkflowEngine(db_session)

        with pytest.raises(ValueError, match="Workflow .* not found"):
            await engine.start_run(
                workflow_id="nonexistent-workflow-id",
                inputs={},
            )

    async def test_resume_run_continues_execution(self, db_session: Any, sample_workflow: Workflow):
        """Given waiting run, When resume_run() with inputs, Then continues to next step."""
        engine = WorkflowEngine(db_session)

        # Start run (pauses at form step)
        run = await engine.start_run(
            workflow_id=sample_workflow.id,
            inputs={},
        )
        assert run.status == "waiting"

        # Resume with form inputs
        resumed_run = await engine.resume_run(
            run_id=run.id,
            inputs={"user_name": "Alice"},
        )

        # Should have moved to ai_generate step or completed
        assert resumed_run.id == run.id
        assert resumed_run.context["runtime"]["user_name"] == "Alice"
        # AI step should complete and move to conditional, which should also complete
        assert resumed_run.status == "completed"

    async def test_resume_run_invalid_run_id(self, db_session: Any):
        """Given invalid run ID, When resume_run(), Then raises ValueError."""
        engine = WorkflowEngine(db_session)

        with pytest.raises(ValueError, match="Run .* not found"):
            await engine.resume_run(
                run_id="nonexistent-run-id",
                inputs={},
            )

    async def test_resume_run_not_waiting(self, db_session: Any, simple_workflow: Workflow):
        """Given run not in waiting state, When resume_run(), Then raises ValueError."""
        engine = WorkflowEngine(db_session)

        # Start run that completes immediately (no wait-state)
        run = await engine.start_run(
            workflow_id=simple_workflow.id,
            inputs={"value": 15},
        )
        assert run.status == "completed"

        # Attempt to resume completed run
        with pytest.raises(ValueError, match="not in waiting state"):
            await engine.resume_run(
                run_id=run.id,
                inputs={},
            )

    async def test_workflow_completes_when_last_step_finishes(
        self, db_session: Any, simple_workflow: Workflow
    ):
        """Given workflow, When last step finishes, Then run status='completed'."""
        engine = WorkflowEngine(db_session)

        run = await engine.start_run(
            workflow_id=simple_workflow.id,
            inputs={"value": 15},
        )

        assert run.status == "completed"
        assert run.current_step is None

    async def test_execute_step_form_pauses_run(self, db_session: Any, sample_workflow: Workflow):
        """Given form step, When executed, Then pauses run with waiting status."""
        engine = WorkflowEngine(db_session)

        run = await engine.start_run(
            workflow_id=sample_workflow.id,
            inputs={},
        )

        # Form step should pause
        assert run.status == "waiting"
        assert run.current_step == "collect_name"

        # Check that field schema stored in context
        assert "collect_name_schema" in run.context["runtime"]

    async def test_execute_step_conditional_evaluates(
        self, db_session: Any, simple_workflow: Workflow
    ):
        """Given conditional step, When executed, Then evaluates expression."""
        engine = WorkflowEngine(db_session)

        run = await engine.start_run(
            workflow_id=simple_workflow.id,
            inputs={"value": 15},
        )

        # Conditional should evaluate and complete
        assert run.status == "completed"

    async def test_execute_step_unsupported_type(self, db_session: Any):
        """Given unsupported step type, When executed, Then raises ValueError."""
        workflow_id = str(uuid.uuid4())

        workflow = Workflow(
            id=workflow_id,
            version=1,
            name="invalid_workflow",
            definition={"name": "invalid", "version": "0.1.0", "start_step": "bad_step"},
            start_step="bad_step",
        )

        bad_step = Step(
            id=str(uuid.uuid4()),
            workflow_id=workflow_id,
            step_id="bad_step",
            type="unsupported_type",
            name="Bad Step",
            next=None,
            config={},
        )

        workflow.steps = [bad_step]

        db_session.add(workflow)
        await db_session.commit()

        engine = WorkflowEngine(db_session)

        with pytest.raises(ValueError, match="Unsupported step type"):
            await engine.start_run(workflow_id=workflow_id, inputs={})

    async def test_error_handling_rolls_back_transaction(self, db_session: Any):
        """Given step execution error, When error occurs, Then rolls back and marks run failed."""
        workflow_id = str(uuid.uuid4())

        workflow = Workflow(
            id=workflow_id,
            version=1,
            name="error_workflow",
            definition={"name": "error", "version": "0.1.0", "start_step": "error_step"},
            start_step="error_step",
        )

        # Conditional with invalid expression (references undefined variable)
        error_step = Step(
            id=str(uuid.uuid4()),
            workflow_id=workflow_id,
            step_id="error_step",
            type="conditional",
            name="Error Step",
            next=None,
            config={
                "when": "undefined_variable > 10",
            },
        )

        workflow.steps = [error_step]

        db_session.add(workflow)
        await db_session.commit()

        engine = WorkflowEngine(db_session)

        with pytest.raises(NameError):
            await engine.start_run(workflow_id=workflow_id, inputs={})

        # Verify run marked as failed
        result = await db_session.execute(select(Run).where(Run.workflow_id == workflow_id))
        run = result.scalar_one_or_none()
        assert run is not None
        assert run.status == "failed"

        # Verify failed step recorded
        result = await db_session.execute(select(RunStep).where(RunStep.run_id == run.id))
        run_step = result.scalar_one_or_none()
        assert run_step is not None
        assert run_step.status == "failed"
        assert run_step.error is not None

    async def test_step_execution_history_recorded(
        self, db_session: Any, simple_workflow: Workflow
    ):
        """Given step execution, When completed, Then records step in history."""
        engine = WorkflowEngine(db_session)

        run = await engine.start_run(
            workflow_id=simple_workflow.id,
            inputs={"value": 15},
        )

        # Query execution history
        result = await db_session.execute(
            select(RunStep).where(RunStep.run_id == run.id).order_by(RunStep.started_at)
        )
        run_steps = result.scalars().all()

        assert len(run_steps) == 1
        assert run_steps[0].step_id == "check_input"
        assert run_steps[0].type == "conditional"
        assert run_steps[0].status == "completed"
        assert run_steps[0].output is not None

    async def test_context_merges_across_steps(self, db_session: Any, sample_workflow: Workflow):
        """Given multi-step workflow, When steps execute, Then context accumulates data."""
        engine = WorkflowEngine(db_session)

        # Start run (pauses at form)
        run = await engine.start_run(
            workflow_id=sample_workflow.id,
            inputs={"initial": "data"},
        )

        # Resume with form inputs
        await engine.resume_run(
            run_id=run.id,
            inputs={"user_name": "Bob"},
        )

        # Refresh run to get updated context
        await db_session.refresh(run)

        # Context should contain data from all steps
        assert run.context["runtime"]["initial"] == "data"
        assert run.context["runtime"]["user_name"] == "Bob"
        # AI step should have added output
        assert "generate_greeting_output" in run.context["runtime"]

    async def test_invalid_step_reference_fails_run(self, db_session: Any):
        """Given step with invalid next reference, When executed, Then fails run."""
        workflow_id = str(uuid.uuid4())

        workflow = Workflow(
            id=workflow_id,
            version=1,
            name="invalid_ref_workflow",
            definition={
                "name": "invalid_ref",
                "version": "0.1.0",
                "start_step": "step1",
            },
            start_step="step1",
        )

        # Step references non-existent next step
        step1 = Step(
            id=str(uuid.uuid4()),
            workflow_id=workflow_id,
            step_id="step1",
            type="conditional",
            name="Step 1",
            next="nonexistent_step",  # Invalid reference
            config={"when": "True"},
        )

        workflow.steps = [step1]

        db_session.add(workflow)
        await db_session.commit()

        engine = WorkflowEngine(db_session)

        with pytest.raises(ValueError, match="Step .* not found in workflow"):
            await engine.start_run(workflow_id=workflow_id, inputs={})

    async def test_ai_generate_step_execution(self, db_session: Any, sample_workflow: Workflow):
        """Given ai_generate step, When executed, Then generates output and continues."""
        engine = WorkflowEngine(db_session)

        # Start and pause at form
        run = await engine.start_run(
            workflow_id=sample_workflow.id,
            inputs={},
        )

        # Resume to trigger AI step
        await engine.resume_run(
            run_id=run.id,
            inputs={"user_name": "Charlie"},
        )

        # Refresh to get latest state
        await db_session.refresh(run)

        # AI output should be in context
        assert "generate_greeting_output" in run.context["runtime"]
        ai_output = run.context["runtime"]["generate_greeting_output"]
        assert "greeting" in ai_output
        assert "success" in ai_output

    async def test_full_workflow_lifecycle(self, db_session: Any, sample_workflow: Workflow):
        """Given workflow, When executed end-to-end, Then completes successfully."""
        engine = WorkflowEngine(db_session)

        # 1. Start run
        run = await engine.start_run(
            workflow_id=sample_workflow.id,
            inputs={"initial": "data"},
        )
        assert run.status == "waiting"
        assert run.current_step == "collect_name"

        # 2. Resume with form inputs
        resumed_run = await engine.resume_run(
            run_id=run.id,
            inputs={"user_name": "Diana"},
        )
        assert resumed_run.status == "completed"
        assert resumed_run.current_step is None

        # 3. Verify execution history
        result = await db_session.execute(
            select(RunStep).where(RunStep.run_id == run.id).order_by(RunStep.started_at)
        )
        run_steps = result.scalars().all()

        # Should have 3 completed steps: form → ai_generate → conditional
        assert len(run_steps) == 3
        assert all(step.status == "completed" for step in run_steps)
        assert [step.step_id for step in run_steps] == [
            "collect_name",
            "generate_greeting",
            "check_result",
        ]
