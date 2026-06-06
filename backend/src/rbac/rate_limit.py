import time
from fastapi import HTTPException, status, Request
from src.audit.logger import log_event

# CONFIG
MAX_ATTEMPTS = 5
WINDOW_SECONDS = 60
BAN_SECONDS = 600  # 10 minutes

# MEMORY STORAGE
attempts = {}
banned = {}

def rate_limit_login(request: Request):
    ip = request.client.host
    now = time.time()

    # Check if banned
    if ip in banned:
        if now < banned[ip]:
            log_event(f"BLOCKED login attempt from banned IP {ip}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many attempts. Try again later."
            )
        else:
            del banned[ip]

    # Initialize attempts
    if ip not in attempts:
        attempts[ip] = []

    # Remove old attempts
    attempts[ip] = [t for t in attempts[ip] if now - t < WINDOW_SECONDS]

    # Check limit
    if len(attempts[ip]) >= MAX_ATTEMPTS:
        banned[ip] = now + BAN_SECONDS
        attempts[ip] = []
        log_event(f"IP {ip} auto-banned for excessive login attempts")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. You are temporarily banned."
        )

    # Record attempt
    attempts[ip].append(now)
    log_event(f"Failed login attempt from IP {ip}")
