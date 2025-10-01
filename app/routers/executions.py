"""Workflow execution endpoints."""

import hashlib
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Run, Workflow
from app.db.session import get_db
from app.engine.orchestrator import WorkflowEngine
from app.models.schemas import (
    ErrorResponse,
    RunCreate,
    RunResponse,
    RunResume,
)

router = APIRouter(prefix="/v1/executions", tags=["executions"])


def generate_idempotency_key(workflow_id: str, inputs: dict[str, Any]) -> str:
    """Generate SHA256 idempotency key from workflow ID and inputs.

    Args:
        workflow_id: Workflow identifier
        inputs: Input data for the run

    Returns:
        SHA256 hash as hex string
    """
    # Create stable string representation
    key_data = f"{workflow_id}:{sorted(inputs.items())}"
    return hashlib.sha256(key_data.encode()).hexdigest()


async def execute_workflow_async(
    run_id: str, workflow_id: str, inputs: dict[str, Any], db_url: str
) -> None:
    """Execute workflow in background (for async processing).

    Args:
        run_id: Run identifier
        workflow_id: Workflow to execute
        inputs: Initial inputs
        db_url: Database URL for new session
    """
    # This would be implemented with proper async task queue (Celery, etc.)
    # For now, synchronous execution in the request handler
    pass


@router.post(
    "",
    response_model=RunResponse,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        404: {"model": ErrorResponse, "description": "Workflow not found"},
        409: {"model": ErrorResponse, "description": "Idempotency conflict"},
    },
)
async def start_execution(
    run_data: RunCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> RunResponse:
    """Start a new workflow run.

    Args:
        run_data: Workflow ID and initial inputs
        background_tasks: FastAPI background task manager
        db: Database session

    Returns:
        202 Accepted with run details

    Raises:
        HTTPException: If workflow not found or idempotency conflict
    """
    # Check workflow exists
    result = await db.execute(select(Workflow).where(Workflow.id == run_data.workflow_id))
    workflow = result.scalar_one_or_none()

    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow '{run_data.workflow_id}' not found",
        )

    # Generate or use provided idempotency key
    idempotency_key = run_data.idempotency_key
    if not idempotency_key:
        idempotency_key = generate_idempotency_key(run_data.workflow_id, run_data.inputs)

    # Create workflow engine and start run
    engine = WorkflowEngine(db)

    try:
        run = await engine.start_run(
            workflow_id=run_data.workflow_id,
            inputs=run_data.inputs,
            idempotency_key=idempotency_key,
        )

        # Execute first step (might transition to waiting immediately)
        await engine.execute_step(run.id)

    except ValueError as e:
        # Check if it's an idempotency conflict
        if "already exists" in str(e).lower():
            # Return existing run
            existing_result = await db.execute(
                select(Run).where(Run.idempotency_key == idempotency_key)
            )
            existing_run = existing_result.scalar_one_or_none()
            if existing_run:
                return RunResponse(
                    id=existing_run.id,
                    workflow_id=existing_run.workflow_id,
                    workflow_version=existing_run.workflow_version,
                    status=existing_run.status,
                    current_step=existing_run.current_step,
                    context=existing_run.context,
                    started_at=existing_run.started_at,
                    updated_at=existing_run.updated_at,
                )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    # Return run details with 202 Accepted
    return RunResponse(
        id=run.id,
        workflow_id=run.workflow_id,
        workflow_version=run.workflow_version,
        status=run.status,
        current_step=run.current_step,
        context=run.context,
        started_at=run.started_at,
        updated_at=run.updated_at,
    )


@router.get(
    "/{run_id}",
    response_model=RunResponse,
    responses={404: {"model": ErrorResponse, "description": "Run not found"}},
)
async def get_run_status(run_id: str, db: AsyncSession = Depends(get_db)) -> RunResponse:
    """Get current status of a workflow run.

    Args:
        run_id: Run identifier
        db: Database session

    Returns:
        Current run status and metadata

    Raises:
        HTTPException: If run not found
    """
    result = await db.execute(select(Run).where(Run.id == run_id))
    run = result.scalar_one_or_none()

    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Run '{run_id}' not found"
        )

    return RunResponse(
        id=run.id,
        workflow_id=run.workflow_id,
        workflow_version=run.workflow_version,
        status=run.status,
        current_step=run.current_step,
        context=run.context,
        started_at=run.started_at,
        updated_at=run.updated_at,
    )


@router.post(
    "/{run_id}/resume",
    response_model=RunResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Run not found"},
        409: {"model": ErrorResponse, "description": "Run not in waiting state"},
        400: {"model": ErrorResponse, "description": "Invalid resume data"},
    },
)
async def resume_execution(
    run_id: str, resume_data: RunResume, db: AsyncSession = Depends(get_db)
) -> RunResponse:
    """Resume a waiting workflow run with inputs or approval.

    Args:
        run_id: Run to resume
        resume_data: Form inputs or approval decision
        db: Database session

    Returns:
        Updated run status

    Raises:
        HTTPException: If run not found, not waiting, or invalid data
    """
    # Get run
    result = await db.execute(select(Run).where(Run.id == run_id))
    run = result.scalar_one_or_none()

    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Run '{run_id}' not found"
        )

    if run.status != "waiting":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Run '{run_id}' is not in waiting state (current: {run.status})",
        )

    # Validate resume data
    if resume_data.inputs and resume_data.approval:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot provide both inputs and approval in same request",
        )

    if not resume_data.inputs and not resume_data.approval:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide either inputs or approval decision",
        )

    # Prepare resume inputs
    inputs: dict[str, Any] = {}
    if resume_data.inputs:
        inputs = resume_data.inputs
    else:
        # Handle approval
        inputs = {
            "approval": {
                "approved": resume_data.approval == "approved",
                "comments": resume_data.comments or "",
            }
        }

    # Create engine and resume
    engine = WorkflowEngine(db)

    try:
        await engine.resume_run(run_id=run_id, inputs=inputs)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    # Refresh run data
    await db.refresh(run)

    return RunResponse(
        id=run.id,
        workflow_id=run.workflow_id,
        workflow_version=run.workflow_version,
        status=run.status,
        current_step=run.current_step,
        context=run.context,
        started_at=run.started_at,
        updated_at=run.updated_at,
    )


@router.post(
    "/{run_id}/cancel",
    response_model=RunResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Run not found"},
        409: {"model": ErrorResponse, "description": "Run cannot be canceled"},
    },
)
async def cancel_execution(run_id: str, db: AsyncSession = Depends(get_db)) -> RunResponse:
    """Cancel a running or waiting workflow run.

    Args:
        run_id: Run to cancel
        db: Database session

    Returns:
        Updated run with canceled status

    Raises:
        HTTPException: If run not found or already completed/failed
    """
    # Get run
    result = await db.execute(select(Run).where(Run.id == run_id))
    run = result.scalar_one_or_none()

    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Run '{run_id}' not found"
        )

    # Check if run can be canceled
    if run.status in ["completed", "failed", "canceled"]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Run '{run_id}' cannot be canceled (status: {run.status})",
        )

    # Update status to canceled
    run.status = "canceled"
    await db.commit()
    await db.refresh(run)

    return RunResponse(
        id=run.id,
        workflow_id=run.workflow_id,
        workflow_version=run.workflow_version,
        status=run.status,
        current_step=run.current_step,
        context=run.context,
        started_at=run.started_at,
        updated_at=run.updated_at,
    )
