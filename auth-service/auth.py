from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from models import User
from database import get_db
from config import get_settings
import uuid

#Load settings to get secrets and configurations
settings = get_settings()
#Tool for hashing passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
#Used to extract bearer token from requests
security = HTTPBearer()

#Password utilities

def hash_pwd(pwd: str) -> str:
    """Hash password using bcrypt"""
    return pwd_context.hash(pwd)

def verify_password(plain_pwd: str, hashed_pwd: str) -> bool:
    """verify password against a hash"""
    return pwd_context.verify(plain_pwd, hashed_pwd)

#JWT token creation

def create_access_token(user_id: uuid.UUID) -> str:
    """Create JWT access token"""
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {
        "sub": str(user_id),
        "exp": expire,
        "type": "access"

    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm= settings.JWT_ALGORITHM
    )

    return encoded_jwt

def create_refresh_token(user_id: uuid.UUID) -> tuple[str, datetime]:
    """Create refresh token"""

    expire = datetime.now(timezone.utc) + timedelta(days=settings.REDFRESH_TOKEN_EXPIRE_DAYS)

    to_encode = {
        "sub": str(user_id),
        "exp": expire,
        "type": "refresh",
        "jti": str(uuid.uuid4())
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm= settings.JWT_ALGORITHM
    )

    return encoded_jwt, expire

#Verify token

def verify_token(token: str, expected_type: str = "access") -> Optional[uuid.UUID]:
    """Verify and return user id if verified or else return None"""

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms= settings.JWT_ALGORITHM
        )

        user_id= payload.get("sub")
        token_type = payload.get("type")

        if user_id is None or token_type != expected_type:
            return None
        
        return uuid.UUID(user_id)
    except JWTError:
        return None


#Dependency for protected routes
async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
) -> User:
    """Dependency to get current user. If token is not valid or user is not found 401 is raised"""

    token = credentials.credentials

    user_id = verify_token(token, expected_type="access")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"}

        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
    
    return user