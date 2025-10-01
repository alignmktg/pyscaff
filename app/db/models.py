"""SQLAlchemy database models for PyScaff workflow orchestrator.

This module defines the core database tables:
- Workflow: Workflow definitions with versioning
- Step: Individual step configurations (belongs to workflow)
- Run: Workflow execution instances
- RunStep: Step execution history records
"""

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def utcnow() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(UTC)


class Workflow(Base):
    """Workflow definition model.

    Stores canonical workflow definitions with versioning support.
    Each workflow contains steps and metadata for orchestration.
    """

    __tablename__ = "workflows"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    definition: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    start_step: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )

    # Relationships
    steps: Mapped[list["Step"]] = relationship(
        "Step",
        back_populates="workflow",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    runs: Mapped[list["Run"]] = relationship(
        "Run",
        back_populates="workflow",
        cascade="all, delete-orphan",
        lazy="select",
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<Workflow(id={self.id}, name={self.name}, version={self.version})>"


class Step(Base):
    """Step definition model.

    Represents individual steps within a workflow.
    Each step has a type (form, ai_generate, conditional, etc.) and type-specific config.
    """

    __tablename__ = "steps"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, index=True
    )
    step_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    next: Mapped[str | None] = mapped_column(String(255), nullable=True)
    config: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)

    # Relationships
    workflow: Mapped["Workflow"] = relationship("Workflow", back_populates="steps")

    def __repr__(self) -> str:
        """String representation."""
        return f"<Step(id={self.id}, step_id={self.step_id}, type={self.type})>"


class Run(Base):
    """Workflow run execution model.

    Tracks the execution state of a workflow instance.
    Contains runtime context, current position, and execution status.
    """

    __tablename__ = "runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, index=True
    )
    workflow_version: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    current_step: Mapped[str | None] = mapped_column(String(255), nullable=True)
    context: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    idempotency_key: Mapped[str | None] = mapped_column(
        String(255), nullable=True, unique=True, index=True
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow
    )

    # Relationships
    workflow: Mapped["Workflow"] = relationship("Workflow", back_populates="runs")
    run_steps: Mapped[list["RunStep"]] = relationship(
        "RunStep",
        back_populates="run",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="RunStep.started_at",
    )

    __table_args__ = (
        # Ensure idempotency keys are unique when not null
        UniqueConstraint("idempotency_key", name="uq_runs_idempotency_key"),
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<Run(id={self.id}, workflow_id={self.workflow_id}, status={self.status})>"


class RunStep(Base):
    """Step execution history model.

    Records the execution details for each step in a workflow run.
    Tracks timing, output, and errors for observability.
    """

    __tablename__ = "run_steps"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("runs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    step_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    output: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )
    ended_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )

    # Relationships
    run: Mapped["Run"] = relationship("Run", back_populates="run_steps")

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<RunStep(id={self.id}, run_id={self.run_id}, "
            f"step_id={self.step_id}, status={self.status})>"
        )
