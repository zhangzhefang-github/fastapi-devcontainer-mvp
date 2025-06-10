"""
FastAPI application with mock authentication endpoints and comprehensive logging.
"""
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Optional
import hashlib

# Import logging configuration
from app.core.logging_config import setup_logging, get_logger
from app.middleware.logging_middleware import (
    LoggingMiddleware,
    CorrelationIdMiddleware,
    SecurityLoggingMiddleware,
    ErrorLoggingMiddleware
)
from app.utils.logging_decorators import log_function_call, log_performance, log_errors

# Setup logging before anything else
setup_logging()
logger = get_logger("main")

# Create application instance
app = FastAPI(
    title="FastAPI Enterprise MVP",
    version="1.0.0",
    description="Enterprise-grade FastAPI application with mock authentication and comprehensive logging",
)

# Log application startup
logger.info("Starting FastAPI Enterprise MVP application")

# Add logging middleware (order matters!)
app.add_middleware(ErrorLoggingMiddleware)
app.add_middleware(SecurityLoggingMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(CorrelationIdMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("Middleware configured successfully")

# Mock user database
DEMO_USERS = {
    "alice": {
        "username": "alice",
        "email": "alice@example.com",
        "password_hash": hashlib.sha256("SecurePass123!".encode()).hexdigest(),
        "full_name": "Alice Johnson",
        "role": "user",
        "bio": "Software developer passionate about Python and FastAPI",
        "is_active": True,
        "is_verified": True
    },
    "bob": {
        "username": "bob",
        "email": "bob@example.com", 
        "password_hash": hashlib.sha256("AdminPass456!".encode()).hexdigest(),
        "full_name": "Bob Smith",
        "role": "admin",
        "bio": "System administrator and DevOps engineer",
        "is_active": True,
        "is_verified": True
    },
    "charlie": {
        "username": "charlie",
        "email": "charlie@example.com",
        "password_hash": hashlib.sha256("TestPass789!".encode()).hexdigest(),
        "full_name": "Charlie Brown",
        "role": "user", 
        "bio": "QA engineer and testing enthusiast",
        "is_active": True,
        "is_verified": True
    }
}

# Pydantic models
class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    username: str
    password: str
    full_name: str
    bio: Optional[str] = ""
    terms_accepted: bool

class UserResponse(BaseModel):
    username: str
    email: str
    full_name: str
    role: str
    bio: str
    is_active: bool
    is_verified: bool

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# Helper functions
def hash_password(password: str) -> str:
    """Hash password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()

@log_function_call(logger_name="auth", log_args=False)  # Don't log password
@log_performance(threshold_ms=500.0)
def authenticate_user(username: str, password: str) -> Optional[Dict]:
    """Authenticate user with username/email and password."""
    logger.info(f"Authentication attempt for user: {username}")

    password_hash = hash_password(password)

    for user_data in DEMO_USERS.values():
        if (user_data["username"] == username or user_data["email"] == username) and user_data["password_hash"] == password_hash:
            logger.info(f"Authentication successful for user: {username}")
            return user_data

    logger.warning(f"Authentication failed for user: {username}")
    return None

# Root endpoints
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to FastAPI Enterprise MVP",
        "version": "1.0.0",
        "status": "running",
        "features": ["authentication", "user_management", "health_checks"]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "fastapi-enterprise-mvp",
        "version": "1.0.0"
    }

@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint."""
    return {
        "status": "ready",
        "service": "fastapi-enterprise-mvp",
        "dependencies": {
            "database": "mock",
            "cache": "mock"
        }
    }

# Authentication endpoints
@app.post("/api/v1/auth/login", response_model=LoginResponse)
@log_function_call(logger_name="api.auth")
@log_errors(logger_name="api.auth")
async def login(login_data: LoginRequest):
    """User login endpoint."""
    logger.info(f"Login attempt for username: {login_data.username}")

    user = authenticate_user(login_data.username, login_data.password)

    if not user:
        logger.warning(f"Login failed for username: {login_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is deactivated"
        )
    
    # Create mock token
    mock_token = f"mock_token_{user['username']}"
    
    user_response = UserResponse(
        username=user["username"],
        email=user["email"],
        full_name=user["full_name"],
        role=user["role"],
        bio=user["bio"],
        is_active=user["is_active"],
        is_verified=user["is_verified"]
    )
    
    return LoginResponse(
        access_token=mock_token,
        token_type="bearer",
        user=user_response
    )

@app.post("/api/v1/auth/register", response_model=UserResponse)
async def register(register_data: RegisterRequest):
    """User registration endpoint."""
    if not register_data.terms_accepted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Terms and conditions must be accepted"
        )
    
    # Check if username already exists
    if register_data.username in DEMO_USERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Check if email already exists
    for user in DEMO_USERS.values():
        if user["email"] == register_data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Validate password strength
    if len(register_data.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long"
        )
    
    # Create new user
    new_user = {
        "username": register_data.username,
        "email": register_data.email,
        "password_hash": hash_password(register_data.password),
        "full_name": register_data.full_name,
        "role": "user",
        "bio": register_data.bio,
        "is_active": True,
        "is_verified": False
    }
    
    # Add to mock database
    DEMO_USERS[register_data.username] = new_user
    
    return UserResponse(
        username=new_user["username"],
        email=new_user["email"],
        full_name=new_user["full_name"],
        role=new_user["role"],
        bio=new_user["bio"],
        is_active=new_user["is_active"],
        is_verified=new_user["is_verified"]
    )

@app.get("/api/v1/users", response_model=list[UserResponse])
async def get_users():
    """Get all users endpoint."""
    users = []
    for user_data in DEMO_USERS.values():
        users.append(UserResponse(
            username=user_data["username"],
            email=user_data["email"],
            full_name=user_data["full_name"],
            role=user_data["role"],
            bio=user_data["bio"],
            is_active=user_data["is_active"],
            is_verified=user_data["is_verified"]
        ))
    return users

@app.get("/api/v1/users/me", response_model=UserResponse)
async def get_current_user():
    """Get current user endpoint (mock)."""
    # In a real implementation, this would extract user from JWT token
    # For demo, return Alice's data
    user_data = DEMO_USERS["alice"]
    return UserResponse(
        username=user_data["username"],
        email=user_data["email"],
        full_name=user_data["full_name"],
        role=user_data["role"],
        bio=user_data["bio"],
        is_active=user_data["is_active"],
        is_verified=user_data["is_verified"]
    )

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main_with_auth:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
