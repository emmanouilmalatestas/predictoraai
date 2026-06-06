from fastapi import Request, HTTPException, Depends
from src.security.jwt_config import decode_token, TokenData

def get_current_user(request: Request) -> TokenData:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = auth_header.split(" ", 1)[1]
    token_data = decode_token(token)
    return token_data

def require_role(required_role: str):
    def dependency(user: TokenData = Depends(get_current_user)) -> TokenData:
        if user.role != required_role:
            raise HTTPException(status_code=403, detail="Insufficient role")
        return user
    return dependency
