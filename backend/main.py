from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from starlette.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

# =========================
# CONFIG
# =========================

APP_TITLE = "Predictora Backend"
APP_VERSION = "1.0.0"

SECRET_KEY = "CHANGE_THIS_TO_YOUR_REAL_SECRET_KEY"
ALGORITHM = "HS256"

API_KEY_HEADER_NAME = "X-API-Key"
EXPECTED_API_KEY = "PREDICTORA_KEY_123"  # ή από env

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

app = FastAPI(title=APP_TITLE, version=APP_VERSION)


# =========================
# API KEY MIDDLEWARE
# =========================

class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Επιτρέπουμε root και openapi/docs χωρίς API key
        open_paths = {"/", "/openapi.json", "/docs", "/redoc"}
        if request.url.path in open_paths:
            return await call_next(request)

        api_key = request.headers.get(API_KEY_HEADER_NAME)
        if not api_key or api_key != EXPECTED_API_KEY:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid or missing API key"},
            )

        return await call_next(request)


app.add_middleware(APIKeyMiddleware)


# =========================
# AUTH HELPERS
# =========================

def create_access_token(email: str, role: str = "admin"):
    from datetime import datetime, timedelta

    expire = datetime.utcnow() + timedelta(hours=1)
    payload = {
        "sub": email,
        "role": role,
        "exp": expire,
        "iat": datetime.utcnow(),
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        role = payload.get("role")
        if email is None or role is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )
        return {
            "email": email,
            "role": role,
            "exp": payload.get("exp"),
        }
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


def require_role(required_role: str):
    def checker(user: dict):
        if user.get("role") != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return True

    return checker


# =========================
# ROUTES
# =========================

@app.get("/")
async def root():
    return {"status": "ok", "service": "Predictora Backend"}


# 1) Υπάρχον login: POST /auth/login
@app.post("/auth/login")
async def login(username: str = "", password: str = ""):
    # Production: εδώ βάζεις πραγματικό έλεγχο χρήστη από DB
    if username != "admin@predictora.ai" or password != "PredictoraAdmin123!":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    access_token = create_access_token(email=username, role="admin")
    return {"access_token": access_token, "token_type": "bearer"}


# 2) ΝΕΟ: GET /auth/me
@app.get("/auth/me")
async def auth_me(user: dict = Depends(get_current_user)):
    return {
        "email": user["email"],
        "role": user["role"],
        "session_expires": user["exp"],
    }


# 3) ΝΕΟ: protected endpoint με RBAC
@app.get("/secure/data")
async def secure_data(user: dict = Depends(get_current_user)):
    require_role("admin")(user)
    return {
        "message": "Secure data access granted",
        "user": user["email"],
        "role": user["role"],
    }


# 4) Υπάρχον: Stripe webhook (dummy)
@app.post("/stripe/webhook")
async def stripe_webhook():
    # Βάλε εδώ το πραγματικό Stripe handling
    return {"status": "ok"}

