"""
Pytest configuration and fixtures for the test suite.
"""
import asyncio
from typing import AsyncGenerator, Generator
from uuid import uuid4

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.core.config import settings
from app.main import app


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Create a test client for the FastAPI application."""
    with TestClient(app) as test_client:
        yield test_client


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client for the FastAPI application."""
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        yield async_client


@pytest.fixture
def mock_user_data():
    """Mock user data for testing."""
    return {
        "id": str(uuid4()),
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "role": "user",
        "is_active": True,
        "is_verified": True,
    }


@pytest.fixture
def mock_admin_data():
    """Mock admin user data for testing."""
    return {
        "id": str(uuid4()),
        "email": "admin@example.com",
        "username": "admin",
        "full_name": "Admin User",
        "role": "admin",
        "is_active": True,
        "is_verified": True,
        "is_superuser": True,
    }


@pytest.fixture
def auth_headers(mock_user_data):
    """Create authentication headers for testing."""
    from app.core.security import create_access_token
    
    token = create_access_token(
        subject=mock_user_data["id"],
        additional_claims={
            "role": mock_user_data["role"],
            "username": mock_user_data["username"]
        }
    )
    
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_auth_headers(mock_admin_data):
    """Create admin authentication headers for testing."""
    from app.core.security import create_access_token
    
    token = create_access_token(
        subject=mock_admin_data["id"],
        additional_claims={
            "role": mock_admin_data["role"],
            "username": mock_admin_data["username"]
        }
    )
    
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_user_create_data():
    """Sample data for user creation."""
    return {
        "email": "newuser@example.com",
        "username": "newuser",
        "password": "SecurePass123!",
        "full_name": "New User",
        "terms_accepted": True,
    }


@pytest.fixture
def sample_login_data():
    """Sample data for user login."""
    return {
        "username": "testuser",
        "password": "testpass123",
    }


@pytest.fixture(autouse=True)
def reset_test_state():
    """Reset any global state before each test."""
    # Clear any caches, reset singletons, etc.
    yield
    # Cleanup after test


class MockDatabase:
    """Mock database for testing."""
    
    def __init__(self):
        self.users = {}
        self.sessions = {}
    
    async def get_user_by_id(self, user_id: str):
        return self.users.get(user_id)
    
    async def get_user_by_email(self, email: str):
        for user in self.users.values():
            if user.get("email") == email:
                return user
        return None
    
    async def get_user_by_username(self, username: str):
        for user in self.users.values():
            if user.get("username") == username:
                return user
        return None
    
    async def create_user(self, user_data: dict):
        user_id = str(uuid4())
        user = {**user_data, "id": user_id}
        self.users[user_id] = user
        return user
    
    async def update_user(self, user_id: str, update_data: dict):
        if user_id in self.users:
            self.users[user_id].update(update_data)
            return self.users[user_id]
        return None
    
    async def delete_user(self, user_id: str):
        return self.users.pop(user_id, None)


@pytest.fixture
def mock_db():
    """Mock database fixture."""
    return MockDatabase()


@pytest.fixture
def override_dependencies(mock_db):
    """Override FastAPI dependencies for testing."""
    from app.api.dependencies import get_db, get_user_service
    from app.services.user_service import UserService
    
    async def get_test_db():
        return mock_db
    
    async def get_test_user_service():
        return UserService(mock_db)
    
    app.dependency_overrides[get_db] = get_test_db
    app.dependency_overrides[get_user_service] = get_test_user_service
    
    yield
    
    # Clean up overrides
    app.dependency_overrides.clear()


# Pytest markers
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.slow = pytest.mark.slow
