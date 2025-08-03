from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ...schemas.auth import UserLogin, TokenResponse, UserResponse
from ...core.database import db_manager
from ...core.jwt_utils import verify_password, create_access_token, verify_token
from ...core.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()

@router.post("/login", response_model=TokenResponse)
async def login_for_access_token(user_credentials: UserLogin):
    """Login user and return JWT token"""
    try:
        # Get user from database
        user = db_manager.get_user_by_username(user_credentials.username)
        
        if not user:
            logger.warning(f"Login attempt with invalid username: {user_credentials.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify password
        if not verify_password(user_credentials.password, user["password_hash"]):
            logger.warning(f"Login attempt with invalid password for user: {user_credentials.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if user is active
        if not user.get("is_active", True):
            logger.warning(f"Login attempt for inactive user: {user_credentials.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Update last login
        db_manager.update_user_last_login(user["id"])
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["username"], "user_id": user["id"]},
            expires_delta=access_token_expires
        )
        
        # Prepare user response
        user_response = UserResponse(
            id=str(user["id"]),
            username=user["username"],
            email=user["email"],
            full_name=user.get("full_name"),
            is_active=user.get("is_active", True),
            created_at=user["created_at"],
            last_login=user.get("last_login")
        )
        
        logger.info(f"User {user_credentials.username} logged in successfully")
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/me", response_model=UserResponse)
async def read_users_me(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]):
    """Get current user information"""
    try:
        # Verify token
        token_data = verify_token(credentials.credentials)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get user from database
        username = token_data.get("sub")
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user = db_manager.get_user_by_username(username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return UserResponse(
            id=str(user["id"]),
            username=user["username"],
            email=user["email"],
            full_name=user.get("full_name"),
            is_active=user.get("is_active", True),
            created_at=user["created_at"],
            last_login=user.get("last_login")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/logout")
async def logout(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]):
    """Logout user (client should discard token)"""
    try:
        # Verify token
        token_data = verify_token(credentials.credentials)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        username = token_data.get("sub")
        logger.info(f"User {username} logged out")
        
        return {"message": "Successfully logged out"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )