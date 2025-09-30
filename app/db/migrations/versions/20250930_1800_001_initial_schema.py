"""initial_schema_workflows_steps_runs

Revision ID: 001
Revises:
Create Date: 2025-09-30 18:00:00.000000

Creates the initial database schema for PyScaff workflow orchestrator:
- workflows: Workflow definitions with versioning
- steps: Step configurations (belongs to workflow)
- runs: Workflow execution instances
- run_steps: Step execution history

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create initial schema."""
    # Create workflows table
    op.create_table(
        "workflows",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("definition", sa.JSON(), nullable=False),
        sa.Column("start_step", sa.String(255), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_workflows")),
    )
    op.create_index(op.f("ix_name"), "workflows", ["name"])

    # Create steps table
    op.create_table(
        "steps",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column("workflow_id", sa.String(36), nullable=False),
        sa.Column("step_id", sa.String(255), nullable=False),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("next", sa.String(255), nullable=True),
        sa.Column("config", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(
            ["workflow_id"],
            ["workflows.id"],
            name=op.f("fk_steps_workflow_id_workflows"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_steps")),
    )
    op.create_index(op.f("ix_workflow_id"), "steps", ["workflow_id"])
    op.create_index(op.f("ix_step_id"), "steps", ["step_id"])
    op.create_index(op.f("ix_type"), "steps", ["type"])

    # Create runs table
    op.create_table(
        "runs",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column("workflow_id", sa.String(36), nullable=False),
        sa.Column("workflow_version", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("current_step", sa.String(255), nullable=True),
        sa.Column("context", sa.JSON(), nullable=False),
        sa.Column("idempotency_key", sa.String(255), nullable=True),
        sa.Column(
            "started_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
            onupdate=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(
            ["workflow_id"],
            ["workflows.id"],
            name=op.f("fk_runs_workflow_id_workflows"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_runs")),
        sa.UniqueConstraint("idempotency_key", name=op.f("uq_runs_idempotency_key")),
    )
    op.create_index(op.f("ix_runs_workflow_id"), "runs", ["workflow_id"])
    op.create_index(op.f("ix_runs_status"), "runs", ["status"])
    op.create_index(op.f("ix_runs_idempotency_key"), "runs", ["idempotency_key"])

    # Create run_steps table
    op.create_table(
        "run_steps",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column("run_id", sa.String(36), nullable=False),
        sa.Column("step_id", sa.String(255), nullable=False),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("output", sa.JSON(), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column(
            "started_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.Column(
            "ended_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.ForeignKeyConstraint(
            ["run_id"],
            ["runs.id"],
            name=op.f("fk_run_steps_run_id_runs"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_run_steps")),
    )
    op.create_index(op.f("ix_run_steps_run_id"), "run_steps", ["run_id"])
    op.create_index(op.f("ix_run_steps_step_id"), "run_steps", ["step_id"])
    op.create_index(op.f("ix_run_steps_status"), "run_steps", ["status"])


def downgrade() -> None:
    """Drop all tables."""
    op.drop_table("run_steps")
    op.drop_table("runs")
    op.drop_table("steps")
    op.drop_table("workflows")
