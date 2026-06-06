#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "==> Updating .env with API + JWT settings"
touch .env
grep -q "^JWT_SECRET=" .env || echo "JWT_SECRET=$(openssl rand -hex 32)" >> .env
grep -q "^RATE_LIMIT_PER_MINUTE=" .env || echo "RATE_LIMIT_PER_MINUTE=60" >> .env
grep -q "^API_BASE_URL=" .env || echo "API_BASE_URL=https://api.predictoraai.com" >> .env

echo "==> Ensuring backend requirements"
REQ_FILE="backend/requirements.txt"
grep -q "pyjwt" "$REQ_FILE" || echo "pyjwt" >> "$REQ_FILE"
grep -q "passlib[bcrypt]" "$REQ_FILE" || echo "passlib[bcrypt]" >> "$REQ_FILE"
grep -q "slowapi" "$REQ_FILE" || echo "slowapi" >> "$REQ_FILE"
grep -q "prometheus-fastapi-instrumentator" "$REQ_FILE" || echo "prometheus-fastapi-instrumentator" >> "$REQ_FILE"

echo "==> Writing backend auth/rate_limit/monitoring modules"

cat > backend/auth.py << 'EOF'
import os
import datetime
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret")
JWT_ALG = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

security = HTTPBearer()

def create_access_token(sub: str) -> str:
    now = datetime.datetime.utcnow()
    payload = {
        "sub": sub,
        "iat": now,
        "exp": now + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    token = creds.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
EOF

cat > backend/rate_limit.py << 'EOF'
import os
from slowapi import Limiter
from slowapi.util import get_remote_address

RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{RATE_LIMIT_PER_MINUTE}/minute"],
)
EOF

cat > backend/monitoring.py << 'EOF'
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi import FastAPI

def setup_metrics(app: FastAPI) -> None:
    Instrumentator().instrument(app).expose(app, endpoint="/metrics")
EOF

echo "==> Rewriting backend main.py with JWT + rate limiting + metrics"

cat > backend/main.py << 'EOF'
import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from slowapi.middleware import SlowAPIMiddleware

from auth import create_access_token, get_current_user
from rate_limit import limiter
from monitoring import setup_metrics

PG_USER = os.getenv("PG_USER", "postgres")
PG_PASSWORD = os.getenv("PG_PASSWORD", "postgres")
PG_HOST = os.getenv("PG_HOST", "predictoraai-db")
PG_PORT = os.getenv("PG_PORT", "5432")
PG_DB = os.getenv("PG_DB", "predictoraai")

app = FastAPI(title="PredictoraAI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later if θες
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

setup_metrics(app)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/auth/login")
def login(username: str, password: str):
    if username != "admin" or password != os.getenv("ADMIN_PASSWORD", "admin"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    token = create_access_token(sub=username)
    return {"access_token": token, "token_type": "bearer"}

@app.get("/me")
def me(user: str = Depends(get_current_user)):
    return {"user": user}

@app.get("/secure/ping")
def secure_ping(user: str = Depends(get_current_user)):
    return {"status": "ok", "user": user}
EOF

echo "==> Disabling Traefik on legacy api-green"
sed -i 's/traefik.enable: "true"/traefik.enable: "false"/' docker-compose.yml

echo "==> Rebuild backend image"
docker compose build backend

echo "==> Bring up backend + traefik"
docker compose up -d backend traefik

echo "==> Stop legacy blue/green API containers"
docker compose stop api-blue api-green || true

echo "==> Done."
echo "Test:"
echo "  curl https://api.predictoraai.com/health"
echo "  curl -X POST https://api.predictoraai.com/auth/login -d \"username=admin&password=\$ADMIN_PASSWORD\""
EOF
