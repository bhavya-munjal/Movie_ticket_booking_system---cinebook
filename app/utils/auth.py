from passlib.context import CryptContext
from itsdangerous import URLSafeTimedSerializer
from fastapi import Request, HTTPException
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
serializer = URLSafeTimedSerializer(settings.SECRET_KEY)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_session_token(user_id: int) -> str:
    return serializer.dumps({"user_id": user_id})

def decode_session_token(token: str) -> dict | None:
    try:
        return serializer.loads(token, max_age=86400)
    except Exception:
        return None

def get_current_user_id(request: Request) -> int | None:
    token = request.cookies.get("session")
    if not token:
        return None
    data = decode_session_token(token)
    return data.get("user_id") if data else None

def require_user(request: Request):
    uid = get_current_user_id(request)
    if not uid:
        raise HTTPException(status_code=302, headers={"Location": "/auth/login"})
    return uid
