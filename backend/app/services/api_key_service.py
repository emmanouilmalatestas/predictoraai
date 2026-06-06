from sqlalchemy.orm import Session
from app.models.api_key import APIKey

def validate_api_key(db: Session, key: str) -> bool:
    api_key = db.query(APIKey).filter(APIKey.key == key, APIKey.active == True).first()
    return api_key is not None
