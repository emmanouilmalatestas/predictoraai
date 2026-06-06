from fastapi import APIRouter

from src.admin.control_plane.lockdown_controller import router as lockdown_router
from src.admin.control_plane.sessions_controller import router as sessions_router
from src.admin.control_plane.activity_controller import router as activity_router

router = APIRouter()

router.include_router(lockdown_router)
router.include_router(sessions_router)
router.include_router(activity_router)
