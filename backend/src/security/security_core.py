import os
import time
import uuid
from typing import Dict, Any

import jwt
from fastapi import HTTPException, status
from pydantic import BaseModel

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------
SECRET_KEY = os.getenv("JWT_SECRET", "CHANGE_ME_IN_PRODUCTION")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = 60 * 60  # 1 hour
REFRESH_TOKEN_EXPIRE_SECONDS = 60 * 60 * 24 * 30  # 30 days

# Token revocation store (in-memory for now)
REVOKED_JTIS: set[str] = set()

# Service accounts (machine-to-machine)
SERVICE_ACCOUNTS = {
    "internal-task-runner": "task-runner-secret",
    "analytics-engine": "analytics-secret",
}


# ---------------------------------------------------------
# MODELS
# ---------------------------------------------------------
class TokenData(BaseModel):
    sub: str
    role: str
    jti: str
    exp: int
    iss: str
    aud: str


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------
def generate_id() -> str:
    """Generic UUID for audit, request, session IDs."""
    return str(uuid.uuid4())


def now() -> int:
    return int(time.time())


# ---------------------------------------------------------
# ACCESS TOKEN
# ---------------------------------------------------------
def create_access_token(data: Dict[str, Any], expires_in: int = ACCESS_TOKEN_EXPIRE_SECONDS) -> str:
    payload = data.copy()
    jti = generate_id()
    current = now()

    payload.update(
        {
            "jti": jti,
            "iat": current,
            "exp": current + expires_in,
            "iss": "predictora-backend",
            "aud": "predictora-admin",
        }
    )

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# ---------------------------------------------------------
# REFRESH TOKEN (Skeleton)
# ---------------------------------------------------------
def create_refresh_token(sub: str) -> str:
    payload = {
        "sub": sub,
        "type": "refresh",
        "jti": generate_id(),
        "iat": now(),
        "exp": now() + REFRESH_TOKEN_EXPIRE_SECONDS,
        "iss": "predictora-backend",
        "aud": "predictora-admin",
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# ---------------------------------------------------------
# SERVICE ACCOUNT TOKENS
# ---------------------------------------------------------
def create_service_token(service_name: str) -> str:
    if service_name not in SERVICE_ACCOUNTS:
        raise HTTPException(status_code=403, detail="Unknown service account")

    payload = {
        "sub": service_name,
        "role": "service",
        "jti": generate_id(),
        "iat": now(),
        "exp": now() + 3600,
        "iss": "predictora-backend",
        "aud": "predictora-internal",
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# ---------------------------------------------------------
# DECODE + VALIDATION
# ---------------------------------------------------------
def decode_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            audience=["predictora-admin", "predictora-internal"],
            options={"require": ["exp", "iat", "jti", "sub"]},
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    if payload["jti"] in REVOKED_JTIS:
        raise HTTPException(status_code=401, detail="Token revoked")

    return TokenData(**payload)


# ---------------------------------------------------------
# REVOKE
# ---------------------------------------------------------
def revoke_token(jti: str):
    REVOKED_JTIS.add(jti)
