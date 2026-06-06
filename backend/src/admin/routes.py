from fastapi import APIRouter, HTTPException, Form, Depends, Request
from src.security.jwt_config import create_access_token, revoke_token
from src.admin.admin_sessions import create_session, touch_session, delete_session
from src.admin.admin_activity_feed import publish_admin_event
from src.security.admin_middleware import require_admin

router = APIRouter(prefix="", tags=["admin"])

def log_admin_action(request: Request, user, action: str):
    publish_admin_event(action, user["sub"], request.url.path)
    print(f"[ADMIN AUDIT] user={user['sub']} role={user['role']} action={action} path={request.url.path}")

@router.post("/login")
def admin_login(
    username: str = Form(...),
    password: str = Form(...),
):
    if username != "admin@predictora.ai" or password != "PredictoraAdmin123!":
        raise HTTPException(status_code=401, detail="Invalid admin credentials")

    # 1. Create admin session
    session_id = create_session(user=username)

    # 2. Issue JWT with jti = session_id
    token = create_access_token({
        "sub": username,
        "role": "admin",
        "jti": session_id
    })

    publish_admin_event("admin_login", username, "/admin/login")

    return {
        "access_token": token,
        "token_type": "bearer",
        "session_id": session_id
    }

@router.get("/panel")
def admin_panel(
    request: Request,
    user = Depends(require_admin),
):
    # Touch session
    touch_session(user["jti"])

    log_admin_action(request, user, "view_panel")
    return {"admin": "panel ok", "user": user["sub"], "session": user["jti"]}

@router.get("/users")
def admin_users(
    request: Request,
    user = Depends(require_admin),
):
    touch_session(user["jti"])

    log_admin_action(request, user, "view_users")
    return {"admin": "users ok", "user": user["sub"], "session": user["jti"]}

@router.post("/logout")
def admin_logout(
    request: Request,
    user = Depends(require_admin),
):
    # Revoke JWT
    revoke_token(user["jti"])

    # Delete session
    delete_session(user["jti"])

    log_admin_action(request, user, "logout")
    return {"detail": "Token revoked and session terminated"}
