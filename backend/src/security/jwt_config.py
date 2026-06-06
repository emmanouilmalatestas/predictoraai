import os
import time
import uuid
from typing import Any, Dict

import jwt
from fastapi import HTTPException, status
from pydantic import BaseModel

SECRET_KEY = os.getenv("JWT_SECRET", "CHANGE_ME_IN_PRODUCTION")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = 60 * 60  # 1 hour

REVOKED_JTIS: set[str] = set()


class TokenData(BaseModel):
    sub: str
    role: str
    jti: str
    exp: int


def create_access_token(data: Dict[str, Any], expires_in: int = ACCESS_TOKEN_EXPIRE_SECONDS) -> str:
    to_encode = data.copy()
    now = int(time.time())
    to_encode.update(
        {
            "iat": now,
            "exp": now + expires_in,
            "iss": "predictora-backend",
            "aud": "predictora-admin",
            # USE THE SESSION ID PASSED IN
            "jti": data["jti"],
        }
    )
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            audience="predictora-admin",
            options={"require": ["exp", "iat", "jti", "sub", "role"]},
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    jti = payload.get("jti")
    if jti in REVOKED_JTIS:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token revoked")

    return TokenData(
        sub=payload["sub"],
        role=payload["role"],
        jti=payload["jti"],
        exp=payload["exp"],
    )


def revoke_token(jti: str) -> None:
    REVOKED_JTIS.add(jti)
