from fastapi import APIRouter

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"]
)

@router.get("/ping")
def tasks_ping():
    return {"tasks": "ok"}
