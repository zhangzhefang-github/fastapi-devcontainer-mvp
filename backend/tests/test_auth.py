"""
Tests for authentication endpoints.
"""
import pytest
from fastapi import status
from fastapi.testclient import TestClient


@pytest.mark.unit
def test_login_success(client: TestClient, sample_login_data):
    """Test successful login."""
    response = client.post(
        "/api/v1/auth/login",
        data=sample_login_data
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"
    assert "expires_in" in data


@pytest.mark.unit
def test_login_invalid_credentials(client: TestClient):
    """Test login with invalid credentials."""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "nonexistent",
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "access_token" not in response.json()


@pytest.mark.unit
def test_login_missing_credentials(client: TestClient):
    """Test login with missing credentials."""
    response = client.post("/api/v1/auth/login", data={})
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.unit
def test_register_success(client: TestClient, sample_user_create_data):
    """Test successful user registration."""
    response = client.post(
        "/api/v1/auth/register",
        json=sample_user_create_data
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == sample_user_create_data["email"]
    assert data["username"] == sample_user_create_data["username"]
    assert "password" not in data  # Password should not be returned
    assert "hashed_password" not in data


@pytest.mark.unit
def test_register_duplicate_email(client: TestClient, sample_user_create_data):
    """Test registration with duplicate email."""
    # First registration
    client.post("/api/v1/auth/register", json=sample_user_create_data)
    
    # Second registration with same email
    response = client.post("/api/v1/auth/register", json=sample_user_create_data)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already registered" in response.json()["detail"].lower()


@pytest.mark.unit
def test_register_duplicate_username(client: TestClient, sample_user_create_data):
    """Test registration with duplicate username."""
    # First registration
    client.post("/api/v1/auth/register", json=sample_user_create_data)
    
    # Second registration with same username but different email
    duplicate_data = sample_user_create_data.copy()
    duplicate_data["email"] = "different@example.com"
    
    response = client.post("/api/v1/auth/register", json=duplicate_data)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already taken" in response.json()["detail"].lower()


@pytest.mark.unit
def test_register_weak_password(client: TestClient, sample_user_create_data):
    """Test registration with weak password."""
    weak_password_data = sample_user_create_data.copy()
    weak_password_data["password"] = "weak"
    
    response = client.post("/api/v1/auth/register", json=weak_password_data)
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.unit
def test_register_terms_not_accepted(client: TestClient, sample_user_create_data):
    """Test registration without accepting terms."""
    no_terms_data = sample_user_create_data.copy()
    no_terms_data["terms_accepted"] = False
    
    response = client.post("/api/v1/auth/register", json=no_terms_data)
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.unit
def test_refresh_token_success(client: TestClient, auth_headers):
    """Test successful token refresh."""
    # First, get a refresh token by logging in
    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "testpass123"}
    )
    
    refresh_token = login_response.json().get("refresh_token")
    if not refresh_token:
        pytest.skip("Refresh token not implemented in mock")
    
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.unit
def test_refresh_token_invalid(client: TestClient):
    """Test token refresh with invalid token."""
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "invalid_token"}
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.unit
def test_logout_success(client: TestClient, auth_headers):
    """Test successful logout."""
    response = client.post(
        "/api/v1/auth/logout",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    assert "successfully logged out" in response.json()["message"].lower()


@pytest.mark.unit
def test_logout_without_auth(client: TestClient):
    """Test logout without authentication."""
    response = client.post("/api/v1/auth/logout")
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.integration
def test_full_auth_flow(client: TestClient, sample_user_create_data):
    """Test complete authentication flow: register -> login -> access protected endpoint -> logout."""
    # 1. Register
    register_response = client.post(
        "/api/v1/auth/register",
        json=sample_user_create_data
    )
    assert register_response.status_code == status.HTTP_200_OK
    
    # 2. Login
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": sample_user_create_data["username"],
            "password": sample_user_create_data["password"]
        }
    )
    assert login_response.status_code == status.HTTP_200_OK
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Access protected endpoint
    me_response = client.get("/api/v1/users/me", headers=headers)
    assert me_response.status_code == status.HTTP_200_OK
    
    # 4. Logout
    logout_response = client.post("/api/v1/auth/logout", headers=headers)
    assert logout_response.status_code == status.HTTP_200_OK


@pytest.mark.unit
def test_password_validation():
    """Test password validation rules."""
    from app.schemas.user import UserCreate
    from pydantic import ValidationError
    
    # Valid password
    valid_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "SecurePass123!",
        "full_name": "Test User",
        "terms_accepted": True
    }
    
    user = UserCreate(**valid_data)
    assert user.password == "SecurePass123!"
    
    # Invalid passwords
    invalid_passwords = [
        "short",  # Too short
        "nouppercase123!",  # No uppercase
        "NOLOWERCASE123!",  # No lowercase
        "NoNumbers!",  # No numbers
    ]
    
    for invalid_password in invalid_passwords:
        invalid_data = valid_data.copy()
        invalid_data["password"] = invalid_password
        
        with pytest.raises(ValidationError):
            UserCreate(**invalid_data)
