"""Workflow execution endpoints."""

from fastapi import APIRouter

router = APIRouter(prefix="/v1/executions", tags=["executions"])
