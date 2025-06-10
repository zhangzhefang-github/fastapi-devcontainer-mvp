"""
API v1 router configuration.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, admin

api_router = APIRouter()

# Authentication routes
api_router.include_router(
    auth.router, 
    prefix="/auth", 
    tags=["Authentication"]
)

# User management routes
api_router.include_router(
    users.router, 
    prefix="/users", 
    tags=["Users"]
)

# Admin routes
api_router.include_router(
    admin.router, 
    prefix="/admin", 
    tags=["Admin"]
)
