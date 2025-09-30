"""AI inference endpoints."""

from fastapi import APIRouter

router = APIRouter(prefix="/v1/ai", tags=["ai"])
