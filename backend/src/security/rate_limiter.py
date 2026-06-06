import time
from typing import Dict, Tuple

from fastapi import Request
from fastapi.responses import JSONResponse

# -----------------------------
# CONFIG
# -----------------------------
GLOBAL_WINDOW_SECONDS = 60
GLOBAL_MAX_REQUESTS = 100

LOGIN_WINDOW_SECONDS = 600  # 10 minutes
LOGIN_MAX_FAILURES = 5

# -----------------------------
# IN-MEMORY STORES
# -----------------------------
# key: (ip, path) -> [timestamps...]
REQUEST_LOG: Dict[Tuple[str, str], list] = {}

# key: ip -> [failure_timestamps...]
LOGIN_FAILURES: Dict[str, list] = {}


def _cleanup_old(entries: list, window: int) -> list:
    now = time.time()
    return [t for t in entries if now - t <= window]


async def global_rate_limiter(request: Request, call_next):
    ip = request.client.host
    path = request.url.path

    key = (ip, path)
    now = time.time()

    entries = REQUEST_LOG.get(key, [])
    entries = _cleanup_old(entries, GLOBAL_WINDOW_SECONDS)
    entries.append(now)
    REQUEST_LOG[key] = entries

    if len(entries) > GLOBAL_MAX_REQUESTS:
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests. Please slow down."},
        )

    response = await call_next(request)
    return response


def register_login_failure(ip: str):
    now = time.time()
    failures = LOGIN_FAILURES.get(ip, [])
    failures = _cleanup_old(failures, LOGIN_WINDOW_SECONDS)
    failures.append(now)
    LOGIN_FAILURES[ip] = failures


def is_ip_blocked_for_login(ip: str) -> bool:
    failures = LOGIN_FAILURES.get(ip, [])
    failures = _cleanup_old(failures, LOGIN_WINDOW_SECONDS)
    LOGIN_FAILURES[ip] = failures
    return len(failures) >= LOGIN_MAX_FAILURES
