"""API router for tldraw sync service."""
from fastapi import APIRouter

from src.api.sync import router as sync_router

router = APIRouter()

router.include_router(sync_router)
