from datetime import datetime, timedelta
import uuid

def create_refresh_token(user_id: str):
    return {
        "token": str(uuid.uuid4()),
        "user_id": user_id,
        "expires_at": datetime.utcnow() + timedelta(days=30)
    }
