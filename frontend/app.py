"""
Enterprise Streamlit frontend for FastAPI application.
"""
import os
import requests
import streamlit as st
from datetime import datetime
from typing import Dict, Optional

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
API_BASE = f"{BACKEND_URL}/api/v1"

# Page configuration
st.set_page_config(
    page_title="FastAPI Enterprise MVP",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


class APIClient:
    """Client for interacting with the FastAPI backend."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
    
    def set_auth_token(self, token: str):
        """Set authentication token for requests."""
        self.session.headers.update({"Authorization": f"Bearer {token}"})
    
    def clear_auth_token(self):
        """Clear authentication token."""
        self.session.headers.pop("Authorization", None)
    
    def login(self, username: str, password: str) -> Dict:
        """Login user and return token data."""
        response = self.session.post(
            f"{self.base_url}/auth/login",
            data={"username": username, "password": password}
        )
        response.raise_for_status()
        return response.json()
    
    def register(self, user_data: Dict) -> Dict:
        """Register new user."""
        response = self.session.post(
            f"{self.base_url}/auth/register",
            json=user_data
        )
        response.raise_for_status()
        return response.json()
    
    def get_current_user(self) -> Dict:
        """Get current user information."""
        response = self.session.get(f"{self.base_url}/users/me")
        response.raise_for_status()
        return response.json()
    
    def get_users(self, skip: int = 0, limit: int = 100) -> Dict:
        """Get list of users."""
        response = self.session.get(
            f"{self.base_url}/users/",
            params={"skip": skip, "limit": limit}
        )
        response.raise_for_status()
        return response.json()
    
    def health_check(self) -> Dict:
        """Check API health."""
        response = self.session.get(f"{BACKEND_URL}/health")
        response.raise_for_status()
        return response.json()


# Initialize API client
api_client = APIClient(API_BASE)

# Session state initialization
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_data" not in st.session_state:
    st.session_state.user_data = None
if "token" not in st.session_state:
    st.session_state.token = None


def show_success(message: str):
    """Show success message."""
    st.markdown(f'<div class="success-box">✅ {message}</div>', unsafe_allow_html=True)


def show_error(message: str):
    """Show error message."""
    st.markdown(f'<div class="error-box">❌ {message}</div>', unsafe_allow_html=True)


def show_info(message: str):
    """Show info message."""
    st.markdown(f'<div class="info-box">ℹ️ {message}</div>', unsafe_allow_html=True)


def login_page():
    """Display login page."""
    st.markdown('<h1 class="main-header">🔐 Login</h1>', unsafe_allow_html=True)
    
    with st.form("login_form"):
        st.subheader("Sign In")
        username = st.text_input("Username or Email", placeholder="Enter your username or email")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        col1, col2 = st.columns(2)
        with col1:
            login_button = st.form_submit_button("Login", use_container_width=True)
        with col2:
            register_button = st.form_submit_button("Register", use_container_width=True)
        
        if login_button:
            if username and password:
                try:
                    token_data = api_client.login(username, password)
                    st.session_state.token = token_data["access_token"]
                    api_client.set_auth_token(st.session_state.token)
                    
                    # Get user data
                    user_data = api_client.get_current_user()
                    st.session_state.user_data = user_data
                    st.session_state.authenticated = True
                    
                    show_success("Login successful!")
                    st.rerun()
                    
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 401:
                        show_error("Invalid username or password")
                    else:
                        show_error(f"Login failed: {e.response.text}")
                except Exception as e:
                    show_error(f"Connection error: {str(e)}")
            else:
                show_error("Please enter both username and password")
        
        if register_button:
            st.session_state.show_register = True
            st.rerun()


def register_page():
    """Display registration page."""
    st.markdown('<h1 class="main-header">📝 Register</h1>', unsafe_allow_html=True)
    
    with st.form("register_form"):
        st.subheader("Create Account")
        
        col1, col2 = st.columns(2)
        with col1:
            email = st.text_input("Email", placeholder="your.email@example.com")
            username = st.text_input("Username", placeholder="Choose a username")
        with col2:
            full_name = st.text_input("Full Name", placeholder="Your full name")
            password = st.text_input("Password", type="password", placeholder="Choose a strong password")
        
        bio = st.text_area("Bio (Optional)", placeholder="Tell us about yourself...")
        terms = st.checkbox("I accept the terms and conditions")
        
        col1, col2 = st.columns(2)
        with col1:
            register_button = st.form_submit_button("Register", use_container_width=True)
        with col2:
            back_button = st.form_submit_button("Back to Login", use_container_width=True)
        
        if register_button:
            if not terms:
                show_error("You must accept the terms and conditions")
            elif not all([email, username, password, full_name]):
                show_error("Please fill in all required fields")
            else:
                try:
                    user_data = {
                        "email": email,
                        "username": username,
                        "password": password,
                        "full_name": full_name,
                        "bio": bio if bio else None,
                        "terms_accepted": terms
                    }
                    
                    api_client.register(user_data)
                    show_success("Registration successful! Please login with your credentials.")
                    st.session_state.show_register = False
                    st.rerun()
                    
                except requests.exceptions.HTTPError as e:
                    error_detail = e.response.json().get("detail", "Registration failed")
                    show_error(f"Registration failed: {error_detail}")
                except Exception as e:
                    show_error(f"Connection error: {str(e)}")
        
        if back_button:
            st.session_state.show_register = False
            st.rerun()


def dashboard_page():
    """Display main dashboard."""
    st.markdown('<h1 class="main-header">🚀 Dashboard</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.subheader(f"Welcome, {st.session_state.user_data['username']}!")
        st.write(f"**Role:** {st.session_state.user_data['role']}")
        st.write(f"**Email:** {st.session_state.user_data['email']}")
        
        if st.button("Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user_data = None
            st.session_state.token = None
            api_client.clear_auth_token()
            st.rerun()
    
    # Main content
    tab1, tab2, tab3 = st.tabs(["Profile", "Users", "System"])
    
    with tab1:
        st.subheader("👤 Profile Information")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Username:**", st.session_state.user_data['username'])
            st.write("**Email:**", st.session_state.user_data['email'])
            st.write("**Role:**", st.session_state.user_data['role'])
        with col2:
            st.write("**Active:**", "✅ Yes" if st.session_state.user_data['is_active'] else "❌ No")
            st.write("**Verified:**", "✅ Yes" if st.session_state.user_data['is_verified'] else "❌ No")
            created_at = datetime.fromisoformat(st.session_state.user_data['created_at'].replace('Z', '+00:00'))
            st.write("**Member since:**", created_at.strftime("%B %d, %Y"))
    
    with tab2:
        st.subheader("👥 Users")
        
        try:
            users = api_client.get_users()
            
            if users:
                for user in users:
                    with st.expander(f"{user['username']} ({user['email']})"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write("**Full Name:**", user.get('full_name', 'N/A'))
                            st.write("**Username:**", user['username'])
                        with col2:
                            created = datetime.fromisoformat(user['created_at'].replace('Z', '+00:00'))
                            st.write("**Joined:**", created.strftime("%Y-%m-%d"))
                            if user.get('bio'):
                                st.write("**Bio:**", user['bio'])
            else:
                show_info("No users found")
                
        except requests.exceptions.HTTPError as e:
            show_error(f"Failed to load users: {e.response.text}")
        except Exception as e:
            show_error(f"Connection error: {str(e)}")
    
    with tab3:
        st.subheader("🔧 System Status")
        
        try:
            health = api_client.health_check()
            show_success(f"API Status: {health['status']}")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("API Version", health.get('version', 'Unknown'))
            with col2:
                # Parse ISO format timestamp
                timestamp_str = health['timestamp']
                if 'T' in timestamp_str:
                    # ISO format: 2025-06-10T16:04:41.395586
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                else:
                    # Fallback to current time if parsing fails
                    timestamp = datetime.now()
                st.metric("Last Check", timestamp.strftime("%H:%M:%S"))
                
        except Exception as e:
            show_error(f"API health check failed: {str(e)}")


def main():
    """Main application logic."""
    # Check if we should show register page
    if getattr(st.session_state, 'show_register', False):
        register_page()
    elif not st.session_state.authenticated:
        login_page()
    else:
        # Set auth token if we have one
        if st.session_state.token:
            api_client.set_auth_token(st.session_state.token)
        dashboard_page()


if __name__ == "__main__":
    main()
