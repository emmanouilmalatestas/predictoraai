from fastapi import APIRouter

router = APIRouter(
    prefix="/secure",
    tags=["secure"]
)

@router.get("/ping")
def secure_ping():
    return {"secure": "ok"}
