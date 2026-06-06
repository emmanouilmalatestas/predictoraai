from fastapi import Request, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer

from src.security.jwt_config import decode_token, REVOKED_JTIS
from src.admin.admin_sessions import touch_session, session_exists
from src.admin.admin_activity_feed import publish_admin_event

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/admin/login")

LOCKDOWN_MODE = False


def require_admin(request: Request, token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)

    sub = payload.sub
    role = payload.role
    jti = payload.jti

    if jti in REVOKED_JTIS:
        raise HTTPException(status_code=401, detail="Token revoked")

    if role != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")

    global LOCKDOWN_MODE
    if LOCKDOWN_MODE and request.url.path != "/admin/control/lockdown/disable":
        raise HTTPException(status_code=503, detail="System in lockdown mode")

    if not session_exists(jti):
        raise HTTPException(status_code=401, detail="Session expired or invalid")

    touch_session(jti)

    publish_admin_event("admin_access", sub, request.url.path)

    return {
        "sub": sub,
        "role": role,
        "jti": jti
    }


def enable_lockdown():
    global LOCKDOWN_MODE
    LOCKDOWN_MODE = True
    return {"status": "lockdown enabled"}


def disable_lockdown():
    global LOCKDOWN_MODE
    LOCKDOWN_MODE = False
    return {"status": "lockdown disabled"}


def lockdown_status():
    return {"lockdown": LOCKDOWN_MODE}
