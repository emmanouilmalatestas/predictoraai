kfrom fastapi import FastAPI
import asyncpg
import os

from src.events.middleware import EventMiddleware


# ---------------------------------------------------------
# Database Pool
# ---------------------------------------------------------
async def init_db():
    return await asyncpg.create_pool(
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        database=os.getenv("PG_DB"),
        host=os.getenv("PG_HOST", "postgres"),
        port=int(os.getenv("PG_PORT", 5432)),
        min_size=1,
        max_size=5,
    )


# ---------------------------------------------------------
# FastAPI App
# ---------------------------------------------------------
app = FastAPI()
pool = None


# ---------------------------------------------------------
# Startup / Shutdown
# ---------------------------------------------------------
@app.on_event("startup")
async def startup():
    global pool
    pool = await init_db()
    app.add_middleware(EventMiddleware, pool=pool)


@app.on_event("shutdown")
async def shutdown():
    await pool.close()


# ---------------------------------------------------------
# Health Endpoint
# ---------------------------------------------------------
@app.get("/health")
async def health():
    return {"status": "ok"}

