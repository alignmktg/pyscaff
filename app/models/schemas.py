"""Pydantic schemas for API request/response contracts.

This module defines the data validation and serialization models used
by the FastAPI endpoints for workflows, steps, runs, and execution history.
"""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


# Step Schemas
class StepConfigField(BaseModel):
    """Form field configuration."""

    key: str = Field(..., description="Field identifier")
    type: str = Field(..., description="Field type (string, number, boolean, etc.)")
    required: bool = Field(default=True, description="Whether field is required")
    pattern: str | None = Field(default=None, description="Validation regex pattern")

    model_config = ConfigDict(extra="forbid")


class StepConfig(BaseModel):
    """Base step configuration (type-specific configs extend this)."""

    model_config = ConfigDict(extra="allow")


class FormStepConfig(StepConfig):
    """Form step configuration."""

    fields: list[StepConfigField] = Field(..., description="Form fields to collect")


class AIGenerateStepConfig(StepConfig):
    """AI generate step configuration."""

    template_id: str = Field(..., description="AI template identifier")
    variables: list[str] = Field(..., description="Template variables from context")
    json_schema: dict[str, Any] = Field(..., description="Expected output JSON Schema")


class ConditionalStepConfig(StepConfig):
    """Conditional step configuration."""

    when: str = Field(..., description="Boolean expression to evaluate")


class APICallStepConfig(StepConfig):
    """API call step configuration."""

    url: str = Field(..., description="API endpoint URL (supports templating)")
    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"] = Field(..., description="HTTP method")
    headers: dict[str, str] | None = Field(default=None, description="Request headers")
    body: dict[str, Any] | None = Field(default=None, description="Request body")
    timeout_s: int | None = Field(default=30, description="Request timeout in seconds")


class ApprovalStepConfig(StepConfig):
    """Approval step configuration."""

    approvers: list[str] = Field(..., description="List of approver emails")


# Step Definition
class StepBase(BaseModel):
    """Base step definition."""

    id: str = Field(..., description="Step identifier")
    type: Literal["form", "ai_generate", "conditional", "api_call", "approval"] = Field(
        ..., description="Step type"
    )
    name: str = Field(..., description="Human-readable step name")
    next: str | None = Field(default=None, description="Next step ID (null = terminal)")
    config: dict[str, Any] = Field(..., description="Type-specific configuration")

    model_config = ConfigDict(extra="forbid")


class StepCreate(StepBase):
    """Schema for creating a step (used internally)."""

    pass


class StepResponse(StepBase):
    """Schema for step in API responses."""

    pass


# Workflow Schemas
class WorkflowBase(BaseModel):
    """Base workflow data."""

    name: str = Field(..., description="Workflow name", min_length=1, max_length=255)
    version: str = Field(..., description="Semver version (e.g., '0.1.0')")
    start_step: str = Field(..., description="ID of the first step to execute")
    steps: list[StepBase] = Field(..., description="Workflow step definitions", min_length=1)

    model_config = ConfigDict(extra="forbid")


class WorkflowCreate(WorkflowBase):
    """Schema for creating a workflow."""

    pass


class WorkflowUpdate(BaseModel):
    """Schema for updating a workflow (creates new version)."""

    name: str | None = Field(default=None, description="Updated workflow name")
    start_step: str | None = Field(default=None, description="Updated start step")
    steps: list[StepBase] | None = Field(default=None, description="Updated step definitions")

    model_config = ConfigDict(extra="forbid")


class WorkflowResponse(BaseModel):
    """Schema for workflow in API responses."""

    id: str = Field(..., description="Workflow unique identifier")
    version: int = Field(..., description="Version number (integer)")
    name: str = Field(..., description="Workflow name")
    definition: dict[str, Any] = Field(..., description="Full workflow definition as JSON")
    start_step: str = Field(..., description="Starting step ID")
    created_at: datetime = Field(..., description="Creation timestamp")

    model_config = ConfigDict(from_attributes=True, extra="forbid")


# Run Schemas
class RunContext(BaseModel):
    """Runtime execution context."""

    static: dict[str, Any] = Field(default_factory=dict, description="Static configuration")
    profile: dict[str, Any] = Field(default_factory=dict, description="User profile data")
    runtime: dict[str, Any] = Field(default_factory=dict, description="Runtime-computed values")

    model_config = ConfigDict(extra="forbid")


class RunCreate(BaseModel):
    """Schema for starting a workflow run."""

    workflow_id: str = Field(..., description="Workflow to execute")
    inputs: dict[str, Any] = Field(default_factory=dict, description="Initial input data")
    idempotency_key: str | None = Field(
        default=None, description="Client-provided deduplication key"
    )

    model_config = ConfigDict(extra="forbid")


class RunResume(BaseModel):
    """Schema for resuming a waiting run."""

    inputs: dict[str, Any] | None = Field(
        default=None, description="Form inputs or approval decision"
    )
    approval: Literal["approved", "rejected"] | None = Field(
        default=None, description="Approval decision"
    )
    comments: str | None = Field(default=None, description="Approval comments")

    model_config = ConfigDict(extra="forbid")


class RunResponse(BaseModel):
    """Schema for run in API responses."""

    id: str = Field(..., description="Run unique identifier")
    workflow_id: str = Field(..., description="Workflow being executed")
    workflow_version: int = Field(..., description="Workflow version")
    status: Literal["queued", "running", "waiting", "completed", "failed", "canceled"] = Field(
        ..., description="Current execution status"
    )
    current_step: str | None = Field(default=None, description="Currently executing step")
    context: dict[str, Any] = Field(..., description="Execution context")
    started_at: datetime = Field(..., description="Run start timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True, extra="forbid")


# RunStep Schemas
class RunStepResponse(BaseModel):
    """Schema for run step execution record."""

    id: str = Field(..., description="Run step unique identifier")
    run_id: str = Field(..., description="Parent run ID")
    step_id: str = Field(..., description="Step definition ID")
    type: str = Field(..., description="Step type")
    status: Literal["pending", "running", "completed", "failed"] = Field(
        ..., description="Step execution status"
    )
    output: dict[str, Any] | None = Field(default=None, description="Step output data")
    error: str | None = Field(default=None, description="Error message if failed")
    started_at: datetime = Field(..., description="Step start timestamp")
    ended_at: datetime = Field(..., description="Step end timestamp")

    model_config = ConfigDict(from_attributes=True, extra="forbid")


# Execution History
class RunHistoryResponse(BaseModel):
    """Schema for run execution history."""

    run_id: str = Field(..., description="Run identifier")
    workflow_name: str = Field(..., description="Workflow name")
    status: str = Field(..., description="Current run status")
    steps: list[RunStepResponse] = Field(..., description="Execution history")

    model_config = ConfigDict(extra="forbid")


# Context Snapshot
class RunContextResponse(BaseModel):
    """Schema for current run context."""

    run_id: str = Field(..., description="Run identifier")
    context: RunContext = Field(..., description="Current context snapshot")

    model_config = ConfigDict(extra="forbid")


# Error Responses
class ErrorResponse(BaseModel):
    """Standard error response."""

    detail: str = Field(..., description="Error message")
    type: str | None = Field(default=None, description="Error type/code")

    model_config = ConfigDict(extra="forbid")


# Validation Response
class ValidationResponse(BaseModel):
    """Workflow validation response."""

    valid: bool = Field(..., description="Whether workflow is valid")
    errors: list[str] = Field(default_factory=list, description="Validation error messages")

    model_config = ConfigDict(extra="forbid")
