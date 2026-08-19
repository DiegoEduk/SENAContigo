from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenData(BaseModel):
    user_id: int
    correo: str
    rol: str
    regional_id: Optional[int] = None
    centro_id: Optional[int] = None
    aprendiz_id: Optional[int] = None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain text password against its hash."""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        # Fallback for dev/legacy plain password comparison if needed
        return plain_password == hashed_password


def get_password_hash(password: str) -> str:
    """Generate bcrypt hash for password."""
    return pwd_context.hash(password)


def create_access_token(
    subject: Union[str, int],
    payload: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create a JWT access token."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "access",
        **payload
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(
    subject: Union[str, int],
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create a JWT refresh token."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "refresh"
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
