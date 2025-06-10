"""
FastAPI dependencies for authentication, authorization, and database access.
"""
from typing import Generator, Optional

import structlog
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import verify_token
from app.models.user import User
from app.schemas.user import TokenPayload
from app.services.user_service import UserService

logger = structlog.get_logger()

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

# Mock database session for now - replace with actual database
class MockAsyncSession:
    """Mock async session for demonstration."""
    async def execute(self, query):
        pass
    
    async def commit(self):
        pass
    
    async def rollback(self):
        pass
    
    async def refresh(self, obj):
        pass
    
    def add(self, obj):
        pass


async def get_db() -> Generator[AsyncSession, None, None]:
    """
    Dependency to get database session.
    Replace with actual database session factory.
    """
    # In a real implementation:
    # async with async_session_maker() as session:
    #     yield session
    
    # Mock for now
    yield MockAsyncSession()


async def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    """Dependency to get user service instance."""
    return UserService(db)


async def get_current_user_token(token: str = Depends(oauth2_scheme)) -> TokenPayload:
    """
    Dependency to get current user from JWT token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = verify_token(token)
        if payload is None:
            raise credentials_exception
        
        token_data = TokenPayload(**payload)
        if token_data.sub is None:
            raise credentials_exception
            
        return token_data
        
    except JWTError:
        raise credentials_exception


async def get_current_user(
    token_data: TokenPayload = Depends(get_current_user_token),
    user_service: UserService = Depends(get_user_service)
) -> User:
    """
    Dependency to get current authenticated user.
    """
    # For now, return a mock user since we don't have database setup
    # In real implementation:
    # user = await user_service.get_by_id(token_data.sub)
    # if user is None:
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         detail="User not found"
    #     )
    # return user
    
    # Mock user for demonstration
    from uuid import uuid4
    from datetime import datetime
    
    mock_user = User()
    mock_user.id = uuid4()
    mock_user.username = "demo_user"
    mock_user.email = "demo@example.com"
    mock_user.role = token_data.role or "user"
    mock_user.is_active = True
    mock_user.is_verified = True
    mock_user.created_at = datetime.utcnow()
    mock_user.updated_at = datetime.utcnow()
    
    return mock_user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to get current active user.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_current_verified_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Dependency to get current verified user.
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not verified"
        )
    return current_user


def require_role(required_role: str):
    """
    Dependency factory to require specific role.
    """
    async def role_checker(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        if not current_user.has_role(required_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    
    return role_checker


def require_permission(required_permission: str):
    """
    Dependency factory to require specific permission.
    """
    async def permission_checker(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        if not current_user.has_permission(required_permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    
    return permission_checker


# Common role dependencies
require_admin = require_role("admin")
require_moderator = require_role("moderator")

# Common permission dependencies
require_read_permission = require_permission("read")
require_write_permission = require_permission("write")
require_delete_permission = require_permission("delete")
require_manage_users_permission = require_permission("manage_users")


class RateLimiter:
    """
    Simple rate limiter dependency.
    In production, use Redis-based rate limiting.
    """
    
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests = {}
    
    async def __call__(self, request) -> None:
        # Simple in-memory rate limiting
        # In production, use Redis with sliding window
        client_ip = request.client.host if request.client else "unknown"
        
        # For now, just log the request
        logger.debug("Rate limit check", client_ip=client_ip)
        
        # In real implementation:
        # current_time = time.time()
        # window_start = current_time - 60  # 1 minute window
        # 
        # if client_ip not in self.requests:
        #     self.requests[client_ip] = []
        # 
        # # Remove old requests
        # self.requests[client_ip] = [
        #     req_time for req_time in self.requests[client_ip]
        #     if req_time > window_start
        # ]
        # 
        # if len(self.requests[client_ip]) >= self.requests_per_minute:
        #     raise HTTPException(
        #         status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        #         detail="Rate limit exceeded"
        #     )
        # 
        # self.requests[client_ip].append(current_time)


# Rate limiter instances
standard_rate_limit = RateLimiter(requests_per_minute=60)
strict_rate_limit = RateLimiter(requests_per_minute=10)
