from fastapi import APIRouter

from .ask import router as ask_router

router = APIRouter(tags=["v0"])

router.include_router(ask_router, prefix="/ask")
