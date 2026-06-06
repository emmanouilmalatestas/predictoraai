import time
import uuid
import os
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

from src.security.security_core import (
    decode_token,
    REVOKED_JTIS,
    SERVICE_ACCOUNTS,
)

from src.security.rate_limiter import (
    global_rate_limiter,
    register_login_failure,
    is_ip_blocked_for_login,
)

# ---------------------------------------------------------
# RATE LIMIT MIDDLEWARE (GLOBAL)
# ---------------------------------------------------------
async def rate_limit_middleware(request: Request, call_next):
    return await global_rate_limiter(request, call_next)


# ---------------------------------------------------------
# REQUEST ID INJECTION
# ---------------------------------------------------------
async def request_id_middleware(request: Request, call_next):
    request.state.request_id = str(uuid.uuid4())
    response = await call_next(request)
    response.headers["X-Request-ID"] = request.state.request_id
    return response


# ---------------------------------------------------------
# API KEY MIDDLEWARE (FINAL, PRODUCTION SAFE)
# ---------------------------------------------------------
async def api_key_middleware(request: Request, call_next):
    path = request.url.path

    OPEN_PATHS = {
        "/health",
        "/openapi.json",
        "/docs",
        "/redoc",
        "/metrics",
        "/auth/login",
        "/auth/register",
        "/admin/login",
        "/admin",
    }

    # Allowlist
    for p in OPEN_PATHS:
        if path.startswith(p):
            return await call_next(request)

    incoming_key = request.headers.get("X-API-Key")
    if not incoming_key:
        return JSONResponse(
            status_code=401,
            content={"detail": "Missing API key"},
        )

    expected_key = os.getenv("API_KEY")
    if not expected_key:
        return JSONResponse(
            status_code=500,
            content={"detail": "API key not configured on server"},
        )

    if incoming_key != expected_key:
        return JSONResponse(
            status_code=403,
            content={"detail": "Invalid API key"},
        )

    return await call_next(request)


# ---------------------------------------------------------
# JWT DEPENDENCY
# ---------------------------------------------------------
def get_jwt_user(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = auth_header.split(" ", 1)[1]
    return decode_token(token)


# ---------------------------------------------------------
# SIMPLE BRUTE FORCE GUARD (LEGACY / OPTIONAL)
# ---------------------------------------------------------
FAILED_LOGINS = {}  # ip -> [timestamps]


def brute_force_guard(ip: str):
    now = time.time()

    if ip not in FAILED_LOGINS:
        FAILED_LOGINS[ip] = []

    FAILED_LOGINS[ip] = [t for t in FAILED_LOGINS[ip] if now - t < 600]

    if len(FAILED_LOGINS[ip]) >= 5:
        raise HTTPException(status_code=429, detail="Too many failed attempts. Try later.")


def register_failed_login(ip: str):
    now = time.time()
    if ip not in FAILED_LOGINS:
        FAILED_LOGINS[ip] = []
    FAILED_LOGINS[ip].append(now)


# ---------------------------------------------------------
# SECURITY HEADERS
# ---------------------------------------------------------
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response

