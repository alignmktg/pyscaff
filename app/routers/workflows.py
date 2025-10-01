"""Workflow management endpoints."""

import uuid
from typing import Any

import yaml
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Run, Step, Workflow
from app.db.session import get_db
from app.models.schemas import (
    ErrorResponse,
    ValidationResponse,
    WorkflowCreate,
    WorkflowResponse,
    WorkflowUpdate,
)

router = APIRouter(prefix="/v1/workflows", tags=["workflows"])


@router.post(
    "",
    response_model=WorkflowResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid workflow definition"},
        422: {"model": ErrorResponse, "description": "Validation error"},
    },
)
async def create_workflow(
    workflow_data: WorkflowCreate, db: AsyncSession = Depends(get_db)
) -> WorkflowResponse:
    """Create a new workflow from YAML/JSON definition.

    Args:
        workflow_data: Workflow creation data with steps and configuration
        db: Database session

    Returns:
        Created workflow with ID and version

    Raises:
        HTTPException: If workflow validation fails or creation errors occur
    """
    # Validate workflow structure
    if not workflow_data.steps:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Workflow must have at least one step"
        )

    # Validate start_step exists in steps
    step_ids = {step.id for step in workflow_data.steps}
    if workflow_data.start_step not in step_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Start step '{workflow_data.start_step}' not found in workflow steps",
        )

    # Validate all next step references exist
    for step in workflow_data.steps:
        if step.next and step.next not in step_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Step '{step.id}' references non-existent next step '{step.next}'",
            )

    # Create workflow with initial version
    workflow_id = str(uuid.uuid4())
    workflow = Workflow(
        id=workflow_id,
        version=1,
        name=workflow_data.name,
        start_step=workflow_data.start_step,
        definition={
            "name": workflow_data.name,
            "version": workflow_data.version,
            "start_step": workflow_data.start_step,
            "steps": [step.model_dump() for step in workflow_data.steps],
        },
    )

    # Create step records
    for step_def in workflow_data.steps:
        step = Step(
            workflow_id=workflow_id,
            step_id=step_def.id,
            type=step_def.type,
            name=step_def.name,
            next=step_def.next,
            config=step_def.config,
        )
        db.add(step)

    db.add(workflow)
    await db.commit()
    await db.refresh(workflow)

    return WorkflowResponse(
        id=workflow.id,
        version=workflow.version,
        name=workflow.name,
        definition=workflow.definition,
        start_step=workflow.start_step,
        created_at=workflow.created_at,
    )


@router.get(
    "/{workflow_id}",
    response_model=WorkflowResponse,
    responses={404: {"model": ErrorResponse, "description": "Workflow not found"}},
)
async def get_workflow(workflow_id: str, db: AsyncSession = Depends(get_db)) -> WorkflowResponse:
    """Retrieve workflow definition by ID.

    Args:
        workflow_id: Unique workflow identifier
        db: Database session

    Returns:
        Workflow definition with metadata

    Raises:
        HTTPException: If workflow not found
    """
    result = await db.execute(select(Workflow).where(Workflow.id == workflow_id))
    workflow = result.scalar_one_or_none()

    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Workflow '{workflow_id}' not found"
        )

    return WorkflowResponse(
        id=workflow.id,
        version=workflow.version,
        name=workflow.name,
        definition=workflow.definition,
        start_step=workflow.start_step,
        created_at=workflow.created_at,
    )


@router.put(
    "/{workflow_id}",
    response_model=WorkflowResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Workflow not found"},
        400: {"model": ErrorResponse, "description": "Invalid update data"},
    },
)
async def update_workflow(
    workflow_id: str, workflow_update: WorkflowUpdate, db: AsyncSession = Depends(get_db)
) -> WorkflowResponse:
    """Update workflow (creates new version).

    Args:
        workflow_id: Workflow to update
        workflow_update: Fields to update (partial update supported)
        db: Database session

    Returns:
        Updated workflow with incremented version

    Raises:
        HTTPException: If workflow not found or validation fails
    """
    # Get existing workflow
    result = await db.execute(select(Workflow).where(Workflow.id == workflow_id))
    existing = result.scalar_one_or_none()

    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Workflow '{workflow_id}' not found"
        )

    # Prepare update data
    update_data = workflow_update.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update"
        )

    # Update workflow fields and increment version
    new_definition = existing.definition.copy()

    if workflow_update.name is not None:
        existing.name = workflow_update.name
        new_definition["name"] = workflow_update.name

    if workflow_update.start_step is not None:
        # Validate start_step exists in current steps
        if workflow_update.steps:
            step_ids = {step.id for step in workflow_update.steps}
        else:
            # Get existing step IDs
            step_result = await db.execute(
                select(Step.step_id).where(Step.workflow_id == workflow_id)
            )
            step_ids = {row[0] for row in step_result}

        if workflow_update.start_step not in step_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Start step '{workflow_update.start_step}' not found in workflow steps",
            )
        existing.start_step = workflow_update.start_step
        new_definition["start_step"] = workflow_update.start_step

    if workflow_update.steps is not None:
        # Validate step references
        step_ids = {step.id for step in workflow_update.steps}
        for step in workflow_update.steps:
            if step.next and step.next not in step_ids:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Step '{step.id}' references non-existent next step '{step.next}'",
                )

        # Delete existing steps and create new ones
        await db.execute(delete(Step).where(Step.workflow_id == workflow_id))

        for step_def in workflow_update.steps:
            step = Step(
                workflow_id=workflow_id,
                step_id=step_def.id,
                type=step_def.type,
                name=step_def.name,
                next=step_def.next,
                config=step_def.config,
            )
            db.add(step)

        new_definition["steps"] = [step.model_dump() for step in workflow_update.steps]

    # Increment version and update definition
    existing.version += 1
    new_definition["version"] = f"{existing.version}.0.0"
    existing.definition = new_definition

    await db.commit()
    await db.refresh(existing)

    return WorkflowResponse(
        id=existing.id,
        version=existing.version,
        name=existing.name,
        definition=existing.definition,
        start_step=existing.start_step,
        created_at=existing.created_at,
    )


@router.delete(
    "/{workflow_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"model": ErrorResponse, "description": "Workflow not found"},
        409: {"model": ErrorResponse, "description": "Workflow has active runs"},
    },
)
async def delete_workflow(workflow_id: str, db: AsyncSession = Depends(get_db)) -> Response:
    """Delete workflow if no active runs exist.

    Args:
        workflow_id: Workflow to delete
        db: Database session

    Returns:
        204 No Content on success

    Raises:
        HTTPException: If workflow not found or has active runs
    """
    # Check workflow exists
    result = await db.execute(select(Workflow).where(Workflow.id == workflow_id))
    workflow = result.scalar_one_or_none()

    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Workflow '{workflow_id}' not found"
        )

    # Check for active runs
    run_result = await db.execute(
        select(Run).where(
            Run.workflow_id == workflow_id,
            Run.status.in_(["queued", "running", "waiting"]),
        )
    )
    active_runs = run_result.scalar_one_or_none()

    if active_runs:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot delete workflow '{workflow_id}' with active runs",
        )

    # Delete workflow (cascades to steps and runs)
    await db.delete(workflow)
    await db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{workflow_id}/validate",
    response_model=ValidationResponse,
    responses={404: {"model": ErrorResponse, "description": "Workflow not found"}},
)
async def validate_workflow(
    workflow_id: str, yaml_content: dict[str, Any], db: AsyncSession = Depends(get_db)
) -> ValidationResponse:
    """Validate YAML workflow structure.

    Args:
        workflow_id: Workflow ID (for context, can be 'new' for new workflows)
        yaml_content: YAML content to validate as dict with 'yaml' key
        db: Database session

    Returns:
        Validation result with any errors

    Raises:
        HTTPException: If workflow_id provided but not found
    """
    errors = []

    try:
        # Parse YAML if provided as string
        if isinstance(yaml_content.get("yaml"), str):
            workflow_def = yaml.safe_load(yaml_content["yaml"])
        else:
            workflow_def = yaml_content.get("yaml", {})

        # Basic structure validation
        if not isinstance(workflow_def, dict):
            errors.append("Workflow definition must be a YAML object")
            return ValidationResponse(valid=False, errors=errors)

        # Required fields
        required_fields = ["name", "start_step", "steps"]
        for field in required_fields:
            if field not in workflow_def:
                errors.append(f"Missing required field: {field}")

        if errors:
            return ValidationResponse(valid=False, errors=errors)

        # Validate steps structure
        if not isinstance(workflow_def.get("steps"), list):
            errors.append("Steps must be a list")
        elif not workflow_def["steps"]:
            errors.append("Workflow must have at least one step")
        else:
            step_ids = set()
            for idx, step in enumerate(workflow_def["steps"]):
                if not isinstance(step, dict):
                    errors.append(f"Step {idx} must be an object")
                    continue

                # Check required step fields
                step_required = ["id", "type", "name", "config"]
                for field in step_required:
                    if field not in step:
                        errors.append(f"Step {idx} missing required field: {field}")

                if "id" in step:
                    if step["id"] in step_ids:
                        errors.append(f"Duplicate step ID: {step['id']}")
                    step_ids.add(step["id"])

                # Validate step type
                valid_types = ["form", "ai_generate", "conditional", "api_call", "approval"]
                if "type" in step and step["type"] not in valid_types:
                    errors.append(f"Step {step.get('id', idx)} has invalid type: {step['type']}")

            # Validate start_step exists
            if workflow_def["start_step"] not in step_ids:
                errors.append(f"Start step '{workflow_def['start_step']}' not found in steps")

            # Validate next step references
            for step in workflow_def["steps"]:
                if "next" in step and step["next"] and step["next"] not in step_ids:
                    errors.append(
                        f"Step '{step.get('id', '?')}' references "
                        f"non-existent next step '{step['next']}'"
                    )

    except yaml.YAMLError as e:
        errors.append(f"Invalid YAML syntax: {str(e)}")
    except Exception as e:
        errors.append(f"Validation error: {str(e)}")

    return ValidationResponse(valid=len(errors) == 0, errors=errors)
