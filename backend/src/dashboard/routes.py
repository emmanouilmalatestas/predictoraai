from fastapi import APIRouter

router = APIRouter(
    prefix="/dashboard",
    tags=["dashboard"]
)

@router.get("/ping")
def dashboard_ping():
    return {"dashboard": "ok"}
