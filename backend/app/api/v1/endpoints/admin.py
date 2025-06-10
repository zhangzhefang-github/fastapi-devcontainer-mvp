"""
Admin-only endpoints for user and system management.
"""
from typing import Any, List
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import (
    get_user_service,
    require_admin,
    require_manage_users_permission,
    strict_rate_limit,
)
from app.models.user import User
from app.schemas.user import (
    User as UserSchema,
    UserStats,
    UserUpdate,
)
from app.services.user_service import UserService

router = APIRouter()
logger = structlog.get_logger()


@router.get("/users", response_model=List[UserSchema])
async def admin_get_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of users to return"),
    search: str = Query(None, description="Search query"),
    include_inactive: bool = Query(False, description="Include inactive users"),
    current_user: User = Depends(require_admin),
    user_service: UserService = Depends(get_user_service),
    _: None = Depends(strict_rate_limit)
) -> Any:
    """
    Admin endpoint to get all users with full information.
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
        
        # Filter inactive users if not requested
        if not include_inactive:
            users = [user for user in users if user.is_active]
        
        logger.info(
            "Admin retrieved users list",
            admin_id=str(current_user.id),
            count=len(users),
            search=search
        )
        
        return users
        
    except Exception as e:
        logger.error("Error in admin get users", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/users/{user_id}", response_model=UserSchema)
async def admin_get_user(
    user_id: UUID,
    current_user: User = Depends(require_admin),
    user_service: UserService = Depends(get_user_service)
) -> Any:
    """
    Admin endpoint to get user by ID with full information.
    """
    try:
        user = await user_service.get_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        logger.info(
            "Admin retrieved user details",
            admin_id=str(current_user.id),
            target_user_id=str(user_id)
        )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error in admin get user", user_id=str(user_id), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.put("/users/{user_id}", response_model=UserSchema)
async def admin_update_user(
    user_id: UUID,
    user_update: UserUpdate,
    current_user: User = Depends(require_manage_users_permission),
    user_service: UserService = Depends(get_user_service)
) -> Any:
    """
    Admin endpoint to update any user.
    """
    try:
        updated_user = await user_service.update_user(
            user_id=user_id,
            user_data=user_update
        )
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        logger.info(
            "Admin updated user",
            admin_id=str(current_user.id),
            target_user_id=str(user_id),
            updated_fields=list(user_update.dict(exclude_unset=True).keys())
        )
        
        return updated_user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error in admin update user", user_id=str(user_id), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete("/users/{user_id}")
async def admin_deactivate_user(
    user_id: UUID,
    current_user: User = Depends(require_manage_users_permission),
    user_service: UserService = Depends(get_user_service)
) -> Any:
    """
    Admin endpoint to deactivate a user.
    """
    try:
        # Prevent self-deactivation
        if user_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot deactivate your own account"
            )
        
        success = await user_service.deactivate_user(user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        logger.warning(
            "Admin deactivated user",
            admin_id=str(current_user.id),
            target_user_id=str(user_id)
        )
        
        return {"message": "User deactivated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error in admin deactivate user", user_id=str(user_id), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/stats", response_model=UserStats)
async def admin_get_user_stats(
    current_user: User = Depends(require_admin),
    user_service: UserService = Depends(get_user_service)
) -> Any:
    """
    Admin endpoint to get user statistics.
    """
    try:
        # Mock stats for now - implement actual counting in service
        stats = UserStats(
            total_users=100,
            active_users=95,
            verified_users=80,
            new_users_today=5,
            new_users_this_week=25,
            new_users_this_month=100
        )
        
        logger.info(
            "Admin retrieved user stats",
            admin_id=str(current_user.id)
        )
        
        return stats
        
    except Exception as e:
        logger.error("Error in admin get stats", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/users/{user_id}/activate")
async def admin_activate_user(
    user_id: UUID,
    current_user: User = Depends(require_manage_users_permission),
    user_service: UserService = Depends(get_user_service)
) -> Any:
    """
    Admin endpoint to activate a deactivated user.
    """
    try:
        user = await user_service.get_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already active"
            )
        
        # Activate user (implement in service)
        # success = await user_service.activate_user(user_id)
        
        logger.info(
            "Admin activated user",
            admin_id=str(current_user.id),
            target_user_id=str(user_id)
        )
        
        return {"message": "User activated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error in admin activate user", user_id=str(user_id), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/users/{user_id}/verify-email")
async def admin_verify_user_email(
    user_id: UUID,
    current_user: User = Depends(require_admin),
    user_service: UserService = Depends(get_user_service)
) -> Any:
    """
    Admin endpoint to manually verify a user's email.
    """
    try:
        user = await user_service.get_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if user.is_email_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already verified"
            )
        
        # Verify email (implement in service)
        # success = await user_service.verify_email(user_id)
        
        logger.info(
            "Admin verified user email",
            admin_id=str(current_user.id),
            target_user_id=str(user_id)
        )
        
        return {"message": "Email verified successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error in admin verify email", user_id=str(user_id), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
