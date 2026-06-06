from fastapi import APIRouter, Depends, HTTPException, Request
from src.security.admin_middleware import require_admin
from src.admin.admin_sessions import (
    ADMIN_SESSIONS,
    session_exists,
    delete_session,
)
from src.admin.admin_activity_feed import publish_admin_event

router = APIRouter(prefix="/admin/sessions", tags=["admin-sessions"])


@router.get("/active")
def list_active_sessions(
    request: Request,
    user = Depends(require_admin),
):
    """
    Return all active admin sessions.
    """
    publish_admin_event("list_sessions", user["sub"], request.url.path)
    return list(ADMIN_SESSIONS.values())


@router.delete("/force/{session_id}")
def force_logout(
    session_id: str,
    request: Request,
    user = Depends(require_admin),
):
    """
    Force logout a specific admin session.
    """
    if not session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found")

    delete_session(session_id)
    publish_admin_event("force_logout", user["sub"], request.url.path)

    return {"detail": "Session terminated", "session_id": session_id}


@router.delete("/purge")
def purge_all_sessions(
    request: Request,
    user = Depends(require_admin),
):
    """
    Delete ALL admin sessions (nuclear option).
    """
    ADMIN_SESSIONS.clear()
    publish_admin_event("purge_sessions", user["sub"], request.url.path)

    return {"detail": "All sessions purged"}


@router.get("/stats")
def session_stats(
    request: Request,
    user = Depends(require_admin),
):
    """
    Return session statistics.
    """
    count = len(ADMIN_SESSIONS)
    publish_admin_event("session_stats", user["sub"], request.url.path)

    return {
        "active_sessions": count,
        "sessions": list(ADMIN_SESSIONS.values())
    }
