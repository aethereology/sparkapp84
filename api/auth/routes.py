import logging
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from .auth import (
    authenticate_user, create_access_token, create_refresh_token,
    verify_token, get_user, Token, User, get_current_active_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()

class LoginRequest(BaseModel):
    username: str
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str

@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest):
    """Authenticate user and return JWT tokens"""
    user = authenticate_user(login_data.username, login_data.password)
    if not user:
        logger.warning(f"Failed login attempt for username: {login_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token_data = {
        "sub": user.username,
        "scopes": user.roles,
        "email": user.email,
        "full_name": user.full_name
    }
    
    access_token = create_access_token(
        data=token_data, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data={"sub": user.username})
    
    logger.info(f"User {user.username} logged in successfully")
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_data: RefreshRequest):
    """Refresh access token using refresh token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = verify_token(refresh_data.refresh_token, "refresh")
    if payload is None:
        raise credentials_exception
    
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    user = get_user(username)
    if user is None:
        raise credentials_exception
    
    # Create new tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token_data = {
        "sub": user.username,
        "scopes": user.roles,
        "email": user.email,
        "full_name": user.full_name
    }
    
    access_token = create_access_token(
        data=token_data, expires_delta=access_token_expires
    )
    new_refresh_token = create_refresh_token(data={"sub": user.username})
    
    logger.info(f"Tokens refreshed for user {user.username}")
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_active_user)):
    """Logout user (client should discard tokens)"""
    logger.info(f"User {current_user.username} logged out")
    return {"message": "Successfully logged out"}

@router.get("/status")
async def auth_status():
    """Get authentication system status (public endpoint)"""
    return {
        "status": "active",
        "token_expire_minutes": ACCESS_TOKEN_EXPIRE_MINUTES,
        "supported_roles": ["admin", "reviewer", "user"]
    }