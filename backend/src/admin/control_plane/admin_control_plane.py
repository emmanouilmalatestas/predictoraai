from fastapi import APIRouter

from .lockdown_controller import router as lockdown_router
from .sessions_controller import router as sessions_router
from .activity_controller import router as activity_router

router = APIRouter(prefix="/admin/control", tags=["admin-control"])

router.include_router(lockdown_router)
router.include_router(sessions_router)
router.include_router(activity_router)
