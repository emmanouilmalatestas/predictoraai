from fastapi import APIRouter, Depends, Request
from src.security.admin_middleware import require_admin
from src.admin.admin_activity_feed import ACTIVITY_FEED, publish_admin_event

router = APIRouter(prefix="/activity", tags=["admin-activity"])

@router.get("/recent")
def recent_activity(request: Request, user = Depends(require_admin)):
    publish_admin_event("activity_view", user["sub"], request.url.path)
    return ACTIVITY_FEED[-50:]

@router.get("/all")
def all_activity(request: Request, user = Depends(require_admin)):
    publish_admin_event("activity_view_all", user["sub"], request.url.path)
    return ACTIVITY_FEED
