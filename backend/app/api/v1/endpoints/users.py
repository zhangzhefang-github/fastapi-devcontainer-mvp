"""
User management endpoints.
"""
from typing import Any, List
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import (
    get_current_active_user,
    get_current_verified_user,
    get_user_service,
    require_admin,
    standard_rate_limit,
)
from app.models.user import User
from app.schemas.user import (
    User as UserSchema,
    UserPublic,
    UserUpdate,
    UserPasswordUpdate,
)
from app.services.user_service import UserService

router = APIRouter()
logger = structlog.get_logger()


@router.get("/me", response_model=UserSchema)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get current user information.
    """
    return current_user


@router.put("/me", response_model=UserSchema)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
    _: None = Depends(standard_rate_limit)
) -> Any:
    """
    Update current user information.
    """
    try:
        updated_user = await user_service.update_user(
            user_id=current_user.id,
            user_data=user_update
        )
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        logger.info("User profile updated", user_id=str(current_user.id))
        return updated_user
        
    except Exception as e:
        logger.error("Error updating user profile", user_id=str(current_user.id), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.put("/me/password")
async def update_current_user_password(
    password_update: UserPasswordUpdate,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
    _: None = Depends(standard_rate_limit)
) -> Any:
    """
    Update current user password.
    """
    try:
        success = await user_service.update_password(
            user_id=current_user.id,
            current_password=password_update.current_password,
            new_password=password_update.new_password
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        logger.info("User password updated", user_id=str(current_user.id))
        return {"message": "Password updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error updating password", user_id=str(current_user.id), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/", response_model=List[UserPublic])
async def get_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of users to return"),
    search: str = Query(None, description="Search query for username, email, or full name"),
    current_user: User = Depends(get_current_verified_user),
    user_service: UserService = Depends(get_user_service)
) -> Any:
    """
    Get list of users (public information only).
    """
    try:
        if search:
            users = await user_service.search_users(
                query=search,
                skip=skip,
                limit=limit
            )
        else:
            users = await user_service.get_users(skip=skip, limit=limit)
        
        return users
        
    except Exception as e:
        logger.error("Error getting users", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/{user_id}", response_model=UserPublic)
async def get_user_by_id(
    user_id: UUID,
    current_user: User = Depends(get_current_verified_user),
    user_service: UserService = Depends(get_user_service)
) -> Any:
    """
    Get user by ID (public information only).
    """
    try:
        user = await user_service.get_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting user", user_id=str(user_id), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete("/me")
async def deactivate_current_user(
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service)
) -> Any:
    """
    Deactivate current user account.
    """
    try:
        success = await user_service.deactivate_user(current_user.id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to deactivate account"
            )
        
        logger.info("User account deactivated", user_id=str(current_user.id))
        return {"message": "Account deactivated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error deactivating account", user_id=str(current_user.id), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
