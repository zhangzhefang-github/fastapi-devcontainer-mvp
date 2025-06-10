"""
FastAPI Enterprise MVP - Unified Self-Contained Application
This application is completely self-contained with no complex dependencies.
It provides all necessary API endpoints for the frontend to work properly.
"""
import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
SERVICE_MODE = os.getenv("SERVICE_MODE", "standalone")
DEBUG = ENVIRONMENT == "development"

# Setup basic logging
logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("fastapi_enterprise")

# Demo users database
DEMO_USERS = {
    "alice": {
        "username": "alice",
        "email": "alice@example.com",
        "password": "SecurePass123!",
        "full_name": "Alice Johnson",
        "role": "user",
        "bio": "Software developer passionate about Python and FastAPI",
        "is_active": True,
        "is_verified": True,
        "created_at": "2024-01-01T10:00:00Z",
        "updated_at": "2024-01-15T10:30:45Z",
        "last_login_at": "2024-01-15T10:30:45Z"
    },
    "bob": {
        "username": "bob",
        "email": "bob@example.com",
        "password": "AdminPass456!",
        "full_name": "Bob Smith",
        "role": "admin",
        "bio": "System administrator and DevOps engineer",
        "is_active": True,
        "is_verified": True,
        "created_at": "2024-01-01T09:00:00Z",
        "updated_at": "2024-01-15T09:15:30Z",
        "last_login_at": "2024-01-15T09:15:30Z"
    },
    "charlie": {
        "username": "charlie",
        "email": "charlie@example.com",
        "password": "TestPass789!",
        "full_name": "Charlie Brown",
        "role": "user",
        "bio": "QA engineer and testing enthusiast",
        "is_active": True,
        "is_verified": True,
        "created_at": "2024-01-02T14:30:00Z",
        "updated_at": "2024-01-15T14:45:15Z",
        "last_login_at": "2024-01-15T14:45:15Z"
    }
}

# Pydantic models
class LoginRequest(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    username: str
    email: str
    full_name: str
    role: str
    bio: str
    is_active: bool
    is_verified: bool
    created_at: str
    updated_at: str
    last_login_at: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# Authentication function
def authenticate_user(username: str, password: str) -> Optional[Dict]:
    """Authenticate user using demo data."""
    logger.info(f"Authentication attempt for user: {username}")
    
    for user_data in DEMO_USERS.values():
        if (user_data["username"] == username or user_data["email"] == username) and user_data["password"] == password:
            logger.info(f"Authentication successful for user: {username}")
            return user_data
    
    logger.warning(f"Authentication failed for user: {username}")
    return None

# Create FastAPI application
app = FastAPI(
    title="FastAPI Enterprise MVP",
    version="1.0.0",
    description="Enterprise-grade FastAPI application - Unified Self-Contained Version",
    docs_url="/docs" if DEBUG else None,
    redoc_url="/redoc" if DEBUG else None,
    debug=DEBUG
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service registry
service_registry = {
    "backend": {
        "name": "backend",
        "status": "healthy",
        "url": "http://localhost:8000",
        "health_endpoint": "/health",
        "last_check": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "environment": ENVIRONMENT
    },
    "frontend": {
        "name": "frontend",
        "status": "unknown",
        "url": "http://localhost:8501",
        "health_endpoint": "/_stcore/health",
        "last_check": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "environment": ENVIRONMENT
    }
}

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with service information."""
    logger.info("Root endpoint accessed")
    return {
        "message": "Welcome to FastAPI Enterprise MVP",
        "version": "1.0.0",
        "environment": ENVIRONMENT,
        "service_mode": SERVICE_MODE,
        "status": "running",
        "docs_url": "/docs" if DEBUG else None,
        "health_url": "/health",
        "api_endpoints": [
            "/api/v1/auth/login",
            "/api/v1/users",
            "/services"
        ],
        "features": {
            "authentication": True,
            "user_management": True,
            "service_discovery": True,
            "health_checks": True
        }
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    logger.debug("Health check accessed")
    return {
        "status": "healthy",
        "service": "fastapi-enterprise-mvp",
        "version": "1.0.0",
        "environment": ENVIRONMENT,
        "timestamp": datetime.utcnow().isoformat(),
        "uptime": "running",
        "dependencies": {
            "database": "demo_mode",
            "cache": "demo_mode",
            "external_services": "demo_mode"
        }
    }

# Readiness check endpoint
@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint."""
    return {
        "status": "ready",
        "service": "fastapi-enterprise-mvp",
        "dependencies": service_registry,
        "timestamp": datetime.utcnow().isoformat()
    }

# Authentication endpoint
@app.post("/api/v1/auth/login", response_model=LoginResponse)
async def login(request: Request):
    """User login endpoint that supports both JSON and form data."""

    # Determine content type and parse accordingly
    content_type = request.headers.get("content-type", "")

    try:
        if "application/json" in content_type:
            # Handle JSON data
            body = await request.json()
            username = body.get("username")
            password = body.get("password")
            logger.info(f"Login attempt (JSON) for username: {username}")
        elif "application/x-www-form-urlencoded" in content_type:
            # Handle form data
            form = await request.form()
            username = form.get("username")
            password = form.get("password")
            logger.info(f"Login attempt (Form) for username: {username}")
        else:
            # Try to parse as JSON by default
            body = await request.json()
            username = body.get("username")
            password = body.get("password")
            logger.info(f"Login attempt (Default JSON) for username: {username}")
    except Exception as e:
        logger.error(f"Failed to parse login request: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail="Invalid request format. Expected JSON or form data with 'username' and 'password' fields."
        )

    if not username or not password:
        logger.warning("Login attempt with missing username or password")
        raise HTTPException(
            status_code=400,
            detail="Username and password are required"
        )

    user = authenticate_user(username, password)
    
    if not user:
        logger.warning(f"Login failed for username: {username}")
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )
    
    if not user["is_active"]:
        logger.warning(f"Login failed - account inactive: {username}")
        raise HTTPException(
            status_code=400,
            detail="Account is deactivated"
        )
    
    # Create mock token
    mock_token = f"mock_token_{user['username']}_{datetime.utcnow().timestamp()}"
    
    user_response = UserResponse(
        username=user["username"],
        email=user["email"],
        full_name=user["full_name"],
        role=user["role"],
        bio=user["bio"],
        is_active=user["is_active"],
        is_verified=user["is_verified"],
        created_at=user["created_at"],
        updated_at=user["updated_at"],
        last_login_at=user["last_login_at"]
    )
    
    logger.info(f"Login successful for username: {username}")
    
    return LoginResponse(
        access_token=mock_token,
        token_type="bearer",
        user=user_response
    )



# Users endpoint
@app.get("/api/v1/users", response_model=list[UserResponse])
async def get_users():
    """Get all users endpoint."""
    logger.info("Users list requested")

    users = []
    for user_data in DEMO_USERS.values():
        users.append(UserResponse(
            username=user_data["username"],
            email=user_data["email"],
            full_name=user_data["full_name"],
            role=user_data["role"],
            bio=user_data["bio"],
            is_active=user_data["is_active"],
            is_verified=user_data["is_verified"],
            created_at=user_data["created_at"],
            updated_at=user_data["updated_at"],
            last_login_at=user_data["last_login_at"]
        ))

    logger.info(f"Returned {len(users)} users")
    return users

# Current user endpoint
@app.get("/api/v1/users/me", response_model=UserResponse)
async def get_current_user(request: Request):
    """Get current user information based on token."""
    # Extract token from Authorization header
    auth_header = request.headers.get("authorization", "")

    if not auth_header.startswith("Bearer "):
        logger.warning("Missing or invalid authorization header")
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid authorization header"
        )

    token = auth_header.replace("Bearer ", "")

    # Extract username from mock token
    if token.startswith("mock_token_"):
        username = token.split("_")[2]  # mock_token_username_timestamp

        # Find user by username
        for user_data in DEMO_USERS.values():
            if user_data["username"] == username:
                logger.info(f"Current user info requested for: {username}")

                return UserResponse(
                    username=user_data["username"],
                    email=user_data["email"],
                    full_name=user_data["full_name"],
                    role=user_data["role"],
                    bio=user_data["bio"],
                    is_active=user_data["is_active"],
                    is_verified=user_data["is_verified"],
                    created_at=user_data["created_at"],
                    updated_at=user_data["updated_at"],
                    last_login_at=user_data["last_login_at"]
                )

    logger.warning(f"Invalid token or user not found: {token[:20]}...")
    raise HTTPException(
        status_code=401,
        detail="Invalid token or user not found"
    )

# Service discovery endpoints
@app.get("/services")
async def get_services():
    """Get all registered services and their status."""
    logger.debug("Service discovery requested")
    
    # Update backend service status
    service_registry["backend"]["last_check"] = datetime.utcnow().isoformat()
    service_registry["backend"]["status"] = "healthy"
    
    return {
        "registry_status": "healthy",
        "total_services": len(service_registry),
        "healthy_services": len([s for s in service_registry.values() if s["status"] == "healthy"]),
        "services": service_registry,
        "last_updated": datetime.utcnow().isoformat()
    }

@app.get("/services/{service_name}")
async def get_service(service_name: str):
    """Get specific service information."""
    logger.debug(f"Service info requested for: {service_name}")
    
    if service_name not in service_registry:
        logger.warning(f"Service not found: {service_name}")
        raise HTTPException(
            status_code=404,
            detail=f"Service '{service_name}' not found"
        )
    
    return service_registry[service_name]

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {type(exc).__name__}: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "type": type(exc).__name__,
            "path": str(request.url.path),
            "method": request.method,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup tasks."""
    logger.info("🚀 FastAPI Enterprise MVP starting...")
    logger.info(f"   Environment: {ENVIRONMENT}")
    logger.info(f"   Service Mode: {SERVICE_MODE}")
    logger.info(f"   Debug: {DEBUG}")
    logger.info(f"   Demo Users: {len(DEMO_USERS)}")
    logger.info("✅ Application ready!")
    
    # Log available endpoints
    logger.info("📋 Available API endpoints:")
    logger.info("   GET  / - Root information")
    logger.info("   GET  /health - Health check")
    logger.info("   GET  /ready - Readiness check")
    logger.info("   POST /api/v1/auth/login - User authentication (JSON/Form)")
    logger.info("   GET  /api/v1/users - List all users")
    logger.info("   GET  /api/v1/users/me - Current user info")
    logger.info("   GET  /services - Service discovery")
    logger.info("   GET  /services/{name} - Specific service info")
    if DEBUG:
        logger.info("   GET  /docs - API documentation")

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main_unified:app",
        host="0.0.0.0",
        port=8000,
        reload=DEBUG,
        log_level="debug" if DEBUG else "info"
    )
