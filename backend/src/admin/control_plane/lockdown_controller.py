from fastapi import APIRouter, Depends, Request
from src.security.admin_middleware import require_admin, enable_lockdown, disable_lockdown, lockdown_status
from src.admin.admin_activity_feed import publish_admin_event

router = APIRouter(prefix="/lockdown", tags=["admin-lockdown"])

@router.post("/enable")
def lockdown_enable(request: Request, user = Depends(require_admin)):
    publish_admin_event("lockdown_enabled", user["sub"], request.url.path)
    return enable_lockdown()

@router.post("/disable")
def lockdown_disable(request: Request, user = Depends(require_admin)):
    publish_admin_event("lockdown_disabled", user["sub"], request.url.path)
    return disable_lockdown()

@router.get("/status")
def lockdown_get_status(request: Request, user = Depends(require_admin)):
    publish_admin_event("lockdown_status", user["sub"], request.url.path)
    return lockdown_status()
