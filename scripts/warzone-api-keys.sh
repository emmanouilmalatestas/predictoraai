#!/bin/bash
set -e

PROJECT_DIR="/home/deploy/predictoraai"
cd "$PROJECT_DIR"

echo "[WARZONE] Creating api_keys table in Postgres..."

docker exec -i predictoraai-db psql -U postgres -d predictoraai << 'EOF'
CREATE TABLE IF NOT EXISTS api_keys (
    id SERIAL PRIMARY KEY,
    key TEXT UNIQUE NOT NULL,
    owner TEXT NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
EOF

echo "[WARZONE] Ensuring API_SECRET in .env..."

if ! grep -q "^API_SECRET=" .env 2>/dev/null; then
  SECRET=$(openssl rand -hex 32)
  echo "API_SECRET=$SECRET" >> .env
  echo "[WARZONE] Added API_SECRET to .env"
else
  echo "[WARZONE] API_SECRET already exists in .env"
fi

echo "[WARZONE] Writing api_keys.py helper..."

cat > backend/api_keys.py << 'PYEOF'
import os
import secrets
from fastapi import HTTPException, status, Depends, Request
import psycopg2

DB_URL = "postgresql://postgres:postgres@predictoraai-db:5432/predictoraai"

def get_db():
    conn = psycopg2.connect(DB_URL)
    try:
        yield conn
    finally:
        conn.close()

def require_api_key(request: Request, db=Depends(get_db)):
    api_key = request.headers.get("x-api-key")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
        )
    cur = db.cursor()
    cur.execute(
        "SELECT active FROM api_keys WHERE key = %s",
        (api_key,)
    )
    row = cur.fetchone()
    if not row or not row[0]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or inactive API key",
        )
PYEOF

echo "[WARZONE] Done. Now you can protect routes with require_api_key."
