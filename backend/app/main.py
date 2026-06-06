import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api.deps.db import SessionLocal
from app.services.api_key_service import validate_api_key

from app.api.routers import auth, admin, secure, tasks, dashboard
from app.monitoring import setup_metrics
from app.audit.logger import log_event


app = FastAPI(
    title="PredictoraAI Backend",
    version="1.0.0",
)


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# API KEY MIDDLEWARE (Postgres-based)
# ---------------------------------------------------------
@app.middleware("http")
async def verify_api_key(request: Request, call_next):
    open_paths = {
        "/health",
        "/openapi.json",
        "/docs",
        "/redoc",
        "/metrics",
        "/auth/login",
        "/auth/register",
        "/webhook",   # Stripe webhook
    }

    if request.url.path in open_paths:
        return await call_next(request)

    api_key = request.headers.get("X-API-Key")
    if not api_key:
        return JSONResponse(status_code=401, content={"detail": "Missing API key"})

    db = SessionLocal()
    try:
        if not validate_api_key(db, api_key):
            log_event(f"Invalid API key attempt: {api_key}")
            return JSONResponse(status_code=403, content={"detail": "Invalid API key"})
    finally:
        db.close()

    return await call_next(request)


# ---------------------------------------------------------
# HEALTH
# ---------------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok"}


# ---------------------------------------------------------
# ROUTERS
# ---------------------------------------------------------
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(secure.router)
app.include_router(tasks.router)
app.include_router(dashboard.router)


# ---------------------------------------------------------
# METRICS
# ---------------------------------------------------------
setup_metrics(app)


# ---------------------------------------------------------
# STRIPE WEBHOOK ROUTER
# ---------------------------------------------------------
# Το stripe_webhook.py είναι στο root backend/
# και το container το τρέχει ως ξεχωριστό service.
# Αν θέλεις να το φορτώσεις και εδώ:
try:
    from stripe_webhook import router as stripe_router
    app.include_router(stripe_router)
except Exception:
    pass
