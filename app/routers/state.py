"""State and context endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import Run, Workflow  # noqa: F401 - Workflow used via Run.workflow relationship
from app.db.session import get_db
from app.models.schemas import (
    ErrorResponse,
    RunContext,
    RunContextResponse,
    RunHistoryResponse,
    RunStepResponse,
)

router = APIRouter(prefix="/v1", tags=["state"])


@router.get(
    "/executions/{run_id}/history",
    response_model=RunHistoryResponse,
    responses={404: {"model": ErrorResponse, "description": "Run not found"}},
)
async def get_run_history(run_id: str, db: AsyncSession = Depends(get_db)) -> RunHistoryResponse:
    """Get step execution history for a workflow run.

    Args:
        run_id: Run identifier
        db: Database session

    Returns:
        Execution history timeline ordered by start time

    Raises:
        HTTPException: If run not found
    """
    # Get run with workflow and steps
    result = await db.execute(
        select(Run)
        .where(Run.id == run_id)
        .options(selectinload(Run.workflow), selectinload(Run.run_steps))
    )
    run = result.scalar_one_or_none()

    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Run '{run_id}' not found"
        )

    # Convert run steps to response format
    steps = []
    for step in run.run_steps:
        steps.append(
            RunStepResponse(
                id=step.id,
                run_id=step.run_id,
                step_id=step.step_id,
                type=step.type,
                status=step.status,
                output=step.output,
                error=step.error,
                started_at=step.started_at,
                ended_at=step.ended_at,
            )
        )

    # Sort by started_at (should already be sorted from query)
    steps.sort(key=lambda x: x.started_at)

    return RunHistoryResponse(
        run_id=run.id,
        workflow_name=run.workflow.name if run.workflow else "Unknown",
        status=run.status,
        steps=steps,
    )


@router.get(
    "/executions/{run_id}/context",
    response_model=RunContextResponse,
    responses={404: {"model": ErrorResponse, "description": "Run not found"}},
)
async def get_run_context(run_id: str, db: AsyncSession = Depends(get_db)) -> RunContextResponse:
    """Get current context snapshot for a workflow run.

    Args:
        run_id: Run identifier
        db: Database session

    Returns:
        Current composite context (static, profile, runtime)

    Raises:
        HTTPException: If run not found
    """
    # Get run
    result = await db.execute(select(Run).where(Run.id == run_id))
    run = result.scalar_one_or_none()

    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Run '{run_id}' not found"
        )

    # Extract context components (context stored as composite dict)
    context_data = run.context or {}

    # Create RunContext from stored data
    context = RunContext(
        static=context_data.get("static", {}),
        profile=context_data.get("profile", {}),
        runtime=context_data.get("runtime", {}),
    )

    return RunContextResponse(run_id=run.id, context=context)
