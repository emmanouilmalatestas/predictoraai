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
