"""Workflow orchestration engine for managing step execution and run lifecycle."""

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Run, RunStep, Step, Workflow
from app.executors.ai_generate import AIGenerateExecutor
from app.executors.approval import ApprovalExecutor
from app.executors.conditional import ConditionalExecutor
from app.executors.form import FormExecutor
from app.models.schemas import (
    AIGenerateStepConfig,
    ApprovalStepConfig,
    ConditionalStepConfig,
    FormStepConfig,
)


class WorkflowEngine:
    """Orchestrates workflow execution with step routing and lifecycle management."""

    def __init__(self, session: AsyncSession):
        """Initialize workflow engine with database session.

        Args:
            session: Async SQLAlchemy session for transactional execution
        """
        self.session = session

    async def start_run(
        self, workflow_id: str, inputs: dict[str, Any], idempotency_key: str | None = None
    ) -> Run:
        """Start a new workflow run.

        Args:
            workflow_id: ID of workflow to execute
            inputs: Initial input data for workflow context
            idempotency_key: Optional client-provided deduplication key

        Returns:
            Created Run instance

        Raises:
            ValueError: If workflow not found or idempotency key already exists
        """
        # Check for existing run with same idempotency key
        if idempotency_key:
            result = await self.session.execute(
                select(Run).where(Run.idempotency_key == idempotency_key)
            )
            existing_run = result.scalar_one_or_none()
            if existing_run:
                return existing_run

        # Fetch workflow definition
        result = await self.session.execute(select(Workflow).where(Workflow.id == workflow_id))
        workflow = result.scalar_one_or_none()
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")

        # Initialize run context
        context: dict[str, Any] = {
            "static": {},
            "profile": {},
            "runtime": inputs.copy(),
        }

        # Create run record (workflow guaranteed non-None by check above)
        run = Run(
            id=str(uuid.uuid4()),
            workflow_id=workflow_id,
            workflow_version=workflow.version,  # type: ignore[attr-defined]
            status="running",
            current_step=workflow.start_step,  # type: ignore[attr-defined]
            context=context,
            idempotency_key=idempotency_key,
        )

        self.session.add(run)
        await self.session.commit()
        await self.session.refresh(run)

        # Start executing from start_step
        await self._execute_workflow(run)

        return run

    async def resume_run(self, run_id: str, inputs: dict[str, Any] | None = None) -> Run:
        """Resume a waiting workflow run with new inputs.

        Args:
            run_id: ID of run to resume
            inputs: Form inputs or approval data to continue execution

        Returns:
            Updated Run instance

        Raises:
            ValueError: If run not found or not in waiting state
        """
        # Fetch run
        result = await self.session.execute(select(Run).where(Run.id == run_id))
        run = result.scalar_one_or_none()
        if not run:
            raise ValueError(f"Run {run_id} not found")

        if run.status != "waiting":
            raise ValueError(f"Run {run_id} is not in waiting state (status={run.status})")

        # Merge new inputs into runtime context and validate
        if inputs:
            # For form/approval steps, validate inputs before resuming
            if run.current_step:
                # Fetch workflow to get step definition
                workflow_result = await self.session.execute(
                    select(Workflow).where(Workflow.id == run.workflow_id)
                )
                workflow = workflow_result.scalar_one_or_none()
                if workflow:
                    step_map = {step.step_id: step for step in workflow.steps}
                    current_step = step_map.get(run.current_step)

                    # If current step is a form, validate inputs
                    if current_step and current_step.type == "form":
                        form_config = FormStepConfig(**current_step.config)
                        form_executor = FormExecutor(form_config)
                        validated_inputs = form_executor.validate_fields(inputs)
                        inputs = validated_inputs  # Use validated inputs

                        # Move to next step (form completed)
                        run.current_step = current_step.next

                    # If current step is approval, validate approval decision
                    elif current_step and current_step.type == "approval":
                        # Validate approval structure
                        if "approval" not in inputs:
                            raise ValueError("Missing 'approval' key in resume data")

                        approval_data = inputs["approval"]
                        if not isinstance(approval_data, dict):
                            raise ValueError("Approval data must be a dictionary")

                        if "approved" not in approval_data:
                            raise ValueError("Missing 'approved' field in approval data")

                        # Store approval decision in context
                        approval_key = f"{run.current_step}_approval"
                        if approval_key in run.context["runtime"]:
                            # Update approval metadata
                            run.context["runtime"][approval_key]["status"] = (
                                "approved" if approval_data["approved"] else "rejected"
                            )
                            run.context["runtime"][approval_key]["comments"] = approval_data.get(
                                "comments", ""
                            )

                        # Move to next step (approval completed)
                        run.current_step = current_step.next

            run.context["runtime"].update(inputs)
            # Mark context as modified for SQLAlchemy change detection
            from sqlalchemy.orm.attributes import flag_modified

            flag_modified(run, "context")

        # Update status back to running
        run.status = "running"
        await self.session.commit()

        # Continue execution from next step
        await self._execute_workflow(run)

        # Refresh run to get latest state after execution
        await self.session.refresh(run)

        return run

    async def _execute_workflow(self, run: Run) -> None:
        """Execute workflow steps sequentially until completion, pause, or error.

        Args:
            run: Run instance to execute

        Workflow:
            1. Load current step definition
            2. Create appropriate executor
            3. Execute step with context
            4. If pause signal: mark run waiting, commit, exit
            5. If success: record step completion, move to next step
            6. If error: rollback, mark run failed
            7. If no next step: mark run completed
        """
        # Fetch workflow and steps
        workflow_result = await self.session.execute(
            select(Workflow).where(Workflow.id == run.workflow_id)
        )
        workflow = workflow_result.scalar_one_or_none()
        if not workflow:
            raise ValueError(f"Workflow {run.workflow_id} not found")

        # Build step lookup map
        step_map = {step.step_id: step for step in workflow.steps}

        # Execute steps sequentially
        while run.current_step:
            step = step_map.get(run.current_step)
            if not step:
                # Invalid step reference - fail run
                run.status = "failed"
                await self.session.commit()
                raise ValueError(f"Step {run.current_step} not found in workflow")

            try:
                # Execute step
                result = await self.execute_step(run, step)

                # Mark context as modified (executors update context in-place)
                from sqlalchemy.orm.attributes import flag_modified

                flag_modified(run, "context")

                # Check for pause signal
                if result.get("pause"):
                    # Record waiting step
                    run_step = RunStep(
                        id=str(uuid.uuid4()),
                        run_id=run.id,
                        step_id=step.step_id,
                        type=step.type,
                        status="completed",  # Form/approval steps complete when they pause
                        output=result,
                        error=None,
                    )
                    self.session.add(run_step)

                    # Mark run as waiting
                    run.status = "waiting"
                    await self.session.commit()
                    return

                # Record successful step completion
                run_step = RunStep(
                    id=str(uuid.uuid4()),
                    run_id=run.id,
                    step_id=step.step_id,
                    type=step.type,
                    status="completed",
                    output=result,
                    error=None,
                )
                self.session.add(run_step)

                # Move to next step
                run.current_step = step.next
                await self.session.commit()

                # If no next step, workflow is complete
                if not run.current_step:
                    run.status = "completed"
                    await self.session.commit()
                    return

            except Exception as e:
                # Capture IDs before rollback (to avoid detached instance issues)
                run_id = run.id
                step_id = step.step_id
                step_type = step.type
                error_msg = str(e)

                # Rollback transaction
                await self.session.rollback()

                # Re-fetch run to reattach to session
                run_result = await self.session.execute(select(Run).where(Run.id == run_id))
                run = run_result.scalar_one()

                # Record failed step
                run_step = RunStep(
                    id=str(uuid.uuid4()),
                    run_id=run_id,
                    step_id=step_id,
                    type=step_type,
                    status="failed",
                    output=None,
                    error=error_msg,
                )
                self.session.add(run_step)

                # Mark run as failed
                run.status = "failed"
                await self.session.commit()
                raise

    async def execute_step(self, run: Run, step: Step) -> dict[str, Any]:
        """Execute a single step by routing to appropriate executor.

        Args:
            run: Current run instance
            step: Step definition to execute

        Returns:
            Step execution result

        Raises:
            ValueError: If step type is unsupported
        """
        # Route to appropriate executor based on step type
        if step.type == "form":
            form_config = FormStepConfig(**step.config)
            form_executor = FormExecutor(form_config)
            return await form_executor.execute(run.context, step.step_id)

        elif step.type == "ai_generate":
            ai_config = AIGenerateStepConfig(**step.config)
            ai_executor = AIGenerateExecutor(ai_config)
            return await ai_executor.execute(run.context, step.step_id)

        elif step.type == "conditional":
            cond_config = ConditionalStepConfig(**step.config)
            cond_executor = ConditionalExecutor(cond_config)
            return await cond_executor.execute(run.context, step.step_id)

        elif step.type == "api_call":
            raise NotImplementedError("API call executor not yet implemented (WP-006)")

        elif step.type == "approval":
            approval_config = ApprovalStepConfig(**step.config)
            approval_executor = ApprovalExecutor(approval_config)
            return await approval_executor.execute(run.context, step.step_id)

        else:
            raise ValueError(f"Unsupported step type: {step.type}")
