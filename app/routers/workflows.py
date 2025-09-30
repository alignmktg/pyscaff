"""Workflow management endpoints."""

from fastapi import APIRouter

router = APIRouter(prefix="/v1/workflows", tags=["workflows"])
