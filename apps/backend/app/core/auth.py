from typing import Optional
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .config import settings
from .jwt_utils import verify_token as verify_jwt_token
from .database import db_manager
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=False)

async def verify_token(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> str:
    """
    Verify the API token from the Authorization header
    Support both JWT tokens and legacy API tokens
    """
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Authorization header required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    # First try JWT token verification
    token_data = verify_jwt_token(token)
    if token_data:
        username = token_data.get("sub")
        if username:
            # Verify user still exists and is active
            user = db_manager.get_user_by_username(username)
            if user and user.get("is_active", True):
                return token
    
    # Fallback to legacy token verification for backward compatibility
    if token == settings.SECRET_KEY or token == "your-secret-key-here":
        return token
    
    logger.warning(f"Invalid token attempt: {token[:10]}...")
    raise HTTPException(
        status_code=401,
        detail="Invalid token",
        headers={"WWW-Authenticate": "Bearer"},
    )

async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """
    Get current user from JWT token
    """
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Authorization header required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    token_data = verify_jwt_token(token)
    
    if not token_data:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username = token_data.get("sub")
    if not username:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db_manager.get_user_by_username(username)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=401,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user 