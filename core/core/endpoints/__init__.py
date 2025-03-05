from fastapi import APIRouter

from .health import router as health_router
from .root import router as root_router
from .v0 import router as v0_router

router = APIRouter()

router.include_router(root_router)
router.include_router(health_router)
router.include_router(v0_router, prefix="/v0")
