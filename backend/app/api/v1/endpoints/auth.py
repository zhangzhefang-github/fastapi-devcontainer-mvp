"""
Authentication endpoints with enterprise security features.
"""
from datetime import timedelta
from typing import Any

import structlog
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.config import settings
from app.core.logging import log_security_event
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_token,
)
from app.schemas.user import Token, UserLogin, UserRegister, User as UserSchema
from app.services.user_service import UserService

router = APIRouter()
logger = structlog.get_logger()


@router.post("/login", response_model=Token)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    client_ip = request.client.host if request.client else "unknown"
    
    try:
        # Authenticate user
        user = await user_service.authenticate(
            username=form_data.username,
            password=form_data.password
        )
        
        if not user:
            log_security_event(
                event_type="login_failed",
                ip_address=client_ip,
                details={"username": form_data.username, "reason": "invalid_credentials"}
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            log_security_event(
                event_type="login_failed",
                user_id=str(user.id),
                ip_address=client_ip,
                details={"reason": "account_disabled"}
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        
        if user.is_account_locked():
            log_security_event(
                event_type="login_failed",
                user_id=str(user.id),
                ip_address=client_ip,
                details={"reason": "account_locked"}
            )
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail="Account is temporarily locked due to failed login attempts"
            )
        
        # Create tokens
        access_token_expires = timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
        access_token = create_access_token(
            subject=str(user.id),
            expires_delta=access_token_expires,
            additional_claims={"role": user.role, "username": user.username}
        )
        
        refresh_token = create_refresh_token(subject=str(user.id))
        
        # Update user login info
        await user_service.update_last_login(user.id, client_ip)
        
        log_security_event(
            event_type="login_success",
            user_id=str(user.id),
            ip_address=client_ip
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.JWT_EXPIRE_MINUTES * 60,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Login error", error=str(e), username=form_data.username)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/register", response_model=UserSchema)
async def register(
    request: Request,
    user_data: UserRegister,
    user_service: UserService = Depends()
) -> Any:
    """
    Register a new user.
    """
    client_ip = request.client.host if request.client else "unknown"
    
    try:
        # Check if user already exists
        existing_user = await user_service.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        existing_user = await user_service.get_by_username(user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Create new user
        user = await user_service.create_user(user_data)
        
        log_security_event(
            event_type="user_registered",
            user_id=str(user.id),
            ip_address=client_ip,
            details={"email": user.email, "username": user.username}
        )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Registration error", error=str(e), email=user_data.email)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    request: Request,
    refresh_token: str,
    user_service: UserService = Depends()
) -> Any:
    """
    Refresh access token using refresh token.
    """
    client_ip = request.client.host if request.client else "unknown"
    
    try:
        # Verify refresh token
        payload = verify_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Get user
        user = await user_service.get_by_id(user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new access token
        access_token_expires = timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
        access_token = create_access_token(
            subject=str(user.id),
            expires_delta=access_token_expires,
            additional_claims={"role": user.role, "username": user.username}
        )
        
        log_security_event(
            event_type="token_refreshed",
            user_id=str(user.id),
            ip_address=client_ip
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.JWT_EXPIRE_MINUTES * 60,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Token refresh error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/logout")
async def logout(
    request: Request,
    # current_user: UserSchema = Depends(get_current_user)  # Will implement dependencies later
) -> Any:
    """
    Logout user and invalidate token.
    """
    client_ip = request.client.host if request.client else "unknown"

    # In a real implementation, you would:
    # 1. Add the token to a blacklist
    # 2. Remove the session from the database
    # 3. Clear any cached user data

    log_security_event(
        event_type="user_logout",
        # user_id=str(current_user.id),
        ip_address=client_ip
    )

    return {"message": "Successfully logged out"}
