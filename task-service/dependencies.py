"""
Shared dependencies for FastAPI endpoints
Handles JWT token verification
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from config import get_settings
import uuid

settings = get_settings()
security = HTTPBearer()


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> uuid.UUID:
    """
    Verify JWT token and return user_id
    Does NOT query auth database - just verifies token signature
    
    Raises:
        HTTPException: 401 if token invalid or expired
    """
    token = credentials.credentials
    
    try:
        # Decode and verify token
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        # Extract user_id and token type
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        # Validate
        if user_id is None or token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return uuid.UUID(user_id)
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )