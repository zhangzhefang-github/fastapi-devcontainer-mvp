"""
Streamlit frontend with real API integration.
"""
import streamlit as st
import requests
import json
from datetime import datetime
from typing import Dict, Optional

# Configuration
BACKEND_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="FastAPI Enterprise MVP - API Integration",
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
    .demo-user {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_data" not in st.session_state:
    st.session_state.user_data = None
if "access_token" not in st.session_state:
    st.session_state.access_token = None

def show_success(message: str):
    """Show success message."""
    st.markdown(f'<div class="success-box">✅ {message}</div>', unsafe_allow_html=True)

def show_error(message: str):
    """Show error message."""
    st.markdown(f'<div class="error-box">❌ {message}</div>', unsafe_allow_html=True)

def show_info(message: str):
    """Show info message."""
    st.markdown(f'<div class="info-box">ℹ️ {message}</div>', unsafe_allow_html=True)

def check_backend_status():
    """Check if backend is running."""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def api_login(username: str, password: str) -> Optional[Dict]:
    """Login via API."""
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/auth/login",
            json={"username": username, "password": password},
            timeout=5
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            error_detail = response.json().get("detail", "Login failed")
            show_error(f"Login failed: {error_detail}")
            return None
            
    except requests.exceptions.RequestException as e:
        show_error(f"Connection error: {str(e)}")
        return None

def api_register(user_data: Dict) -> bool:
    """Register via API."""
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/auth/register",
            json=user_data,
            timeout=5
        )
        
        if response.status_code == 200:
            show_success("Registration successful! You can now login.")
            return True
        else:
            error_detail = response.json().get("detail", "Registration failed")
            show_error(f"Registration failed: {error_detail}")
            return False
            
    except requests.exceptions.RequestException as e:
        show_error(f"Connection error: {str(e)}")
        return False

def api_get_users() -> Optional[list]:
    """Get users via API."""
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/users", timeout=5)
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
            
    except requests.exceptions.RequestException:
        return None

def show_demo_users():
    """Show demo user accounts."""
    st.markdown("### 🎭 Demo User Accounts")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="demo-user">
            <h4>👤 Alice (User)</h4>
            <p><strong>Username:</strong> alice</p>
            <p><strong>Email:</strong> alice@example.com</p>
            <p><strong>Password:</strong> SecurePass123!</p>
            <p><strong>Role:</strong> Regular User</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="demo-user">
            <h4>👨‍💼 Bob (Admin)</h4>
            <p><strong>Username:</strong> bob</p>
            <p><strong>Email:</strong> bob@example.com</p>
            <p><strong>Password:</strong> AdminPass456!</p>
            <p><strong>Role:</strong> Administrator</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="demo-user">
            <h4>🧪 Charlie (Tester)</h4>
            <p><strong>Username:</strong> charlie</p>
            <p><strong>Email:</strong> charlie@example.com</p>
            <p><strong>Password:</strong> TestPass789!</p>
            <p><strong>Role:</strong> QA Tester</p>
        </div>
        """, unsafe_allow_html=True)

def login_page():
    """Display login page."""
    st.markdown('<h1 class="main-header">🔐 FastAPI Enterprise MVP</h1>', unsafe_allow_html=True)
    
    # Backend status
    backend_status = check_backend_status()
    if backend_status:
        show_success(f"Backend API is running at {BACKEND_URL}")
    else:
        show_error(f"Backend API is not responding at {BACKEND_URL}")
        show_info("Please start the backend with: cd backend && .venv/bin/python -m uvicorn app.main_with_auth:app --reload")
    
    # Show demo users
    show_demo_users()
    
    # Login form
    st.markdown("### 🚪 Login")
    with st.form("login_form"):
        username = st.text_input("Username or Email", placeholder="Enter username or email")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        
        col1, col2 = st.columns(2)
        with col1:
            login_button = st.form_submit_button("🔑 Login", use_container_width=True)
        with col2:
            register_button = st.form_submit_button("📝 Register", use_container_width=True)
        
        if login_button:
            if username and password:
                if backend_status:
                    login_response = api_login(username, password)
                    if login_response:
                        st.session_state.access_token = login_response["access_token"]
                        st.session_state.user_data = login_response["user"]
                        st.session_state.authenticated = True
                        show_success("Login successful!")
                        st.rerun()
                else:
                    show_error("Backend API is not available")
            else:
                show_error("Please enter both username and password")
        
        if register_button:
            st.session_state.show_register = True
            st.rerun()

def register_page():
    """Display registration page."""
    st.markdown('<h1 class="main-header">📝 Register New Account</h1>', unsafe_allow_html=True)
    
    backend_status = check_backend_status()
    if not backend_status:
        show_error("Backend API is not available. Registration requires API connection.")
        if st.button("🔙 Back to Login"):
            st.session_state.show_register = False
            st.rerun()
        return
    
    with st.form("register_form"):
        col1, col2 = st.columns(2)
        with col1:
            email = st.text_input("Email *", placeholder="your.email@example.com")
            username = st.text_input("Username *", placeholder="Choose a username")
        with col2:
            full_name = st.text_input("Full Name *", placeholder="Your full name")
            password = st.text_input("Password *", type="password", placeholder="Choose a strong password")
        
        bio = st.text_area("Bio (Optional)", placeholder="Tell us about yourself...")
        terms = st.checkbox("I accept the terms and conditions *")
        
        col1, col2 = st.columns(2)
        with col1:
            register_button = st.form_submit_button("✅ Register", use_container_width=True)
        with col2:
            back_button = st.form_submit_button("🔙 Back to Login", use_container_width=True)
        
        if register_button:
            if not terms:
                show_error("You must accept the terms and conditions")
            elif not all([email, username, password, full_name]):
                show_error("Please fill in all required fields")
            else:
                user_data = {
                    "email": email,
                    "username": username,
                    "password": password,
                    "full_name": full_name,
                    "bio": bio if bio else "",
                    "terms_accepted": terms
                }
                
                if api_register(user_data):
                    st.session_state.show_register = False
                    st.rerun()
        
        if back_button:
            st.session_state.show_register = False
            st.rerun()

def dashboard_page():
    """Display main dashboard."""
    st.markdown('<h1 class="main-header">🚀 Dashboard</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.subheader(f"Welcome, {st.session_state.user_data['full_name']}!")
        st.write(f"**Username:** {st.session_state.user_data['username']}")
        st.write(f"**Email:** {st.session_state.user_data['email']}")
        st.write(f"**Role:** {st.session_state.user_data['role']}")
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user_data = None
            st.session_state.access_token = None
            st.rerun()
    
    # Main content
    tab1, tab2, tab3, tab4 = st.tabs(["👤 Profile", "👥 Users", "🔧 System", "🧪 API Test"])
    
    with tab1:
        st.subheader("👤 Profile Information")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Username:**", st.session_state.user_data['username'])
            st.write("**Email:**", st.session_state.user_data['email'])
            st.write("**Full Name:**", st.session_state.user_data['full_name'])
        with col2:
            st.write("**Role:**", st.session_state.user_data['role'])
            st.write("**Active:**", "✅ Yes" if st.session_state.user_data['is_active'] else "❌ No")
            st.write("**Verified:**", "✅ Yes" if st.session_state.user_data['is_verified'] else "❌ No")
        
        if st.session_state.user_data.get('bio'):
            st.write("**Bio:**", st.session_state.user_data['bio'])
    
    with tab2:
        st.subheader("👥 All Users (via API)")
        
        users = api_get_users()
        if users:
            for user in users:
                with st.expander(f"{user['full_name']} (@{user['username']})"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Email:**", user['email'])
                        st.write("**Role:**", user['role'])
                    with col2:
                        st.write("**Active:**", "✅ Yes" if user['is_active'] else "❌ No")
                        st.write("**Verified:**", "✅ Yes" if user['is_verified'] else "❌ No")
                    if user.get('bio'):
                        st.write("**Bio:**", user['bio'])
        else:
            show_error("Failed to load users from API")
    
    with tab3:
        st.subheader("🔧 System Status")
        
        # Backend status
        backend_status = check_backend_status()
        if backend_status:
            show_success(f"Backend API: Running at {BACKEND_URL}")
        else:
            show_error(f"Backend API: Not responding at {BACKEND_URL}")
        
        # System info
        if users:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Users", len(users))
            with col2:
                active_users = sum(1 for u in users if u['is_active'])
                st.metric("Active Users", active_users)
            with col3:
                verified_users = sum(1 for u in users if u['is_verified'])
                st.metric("Verified Users", verified_users)
    
    with tab4:
        st.subheader("🧪 API Testing")
        
        if check_backend_status():
            st.write("**Available API Endpoints:**")
            st.code(f"""
# Health Check
curl {BACKEND_URL}/health

# Login
curl -X POST {BACKEND_URL}/api/v1/auth/login \\
  -H "Content-Type: application/json" \\
  -d '{{"username": "alice", "password": "SecurePass123!"}}'

# Get Users
curl {BACKEND_URL}/api/v1/users

# API Documentation
{BACKEND_URL}/docs
            """)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔍 Test Health Endpoint"):
                    try:
                        response = requests.get(f"{BACKEND_URL}/health")
                        st.json(response.json())
                    except Exception as e:
                        show_error(f"Error: {str(e)}")
            
            with col2:
                if st.button("👥 Test Users Endpoint"):
                    try:
                        response = requests.get(f"{BACKEND_URL}/api/v1/users")
                        st.json(response.json())
                    except Exception as e:
                        show_error(f"Error: {str(e)}")
        else:
            show_error("Backend API is not running. Please start the backend service first.")

def main():
    """Main application logic."""
    # Check if we should show register page
    if getattr(st.session_state, 'show_register', False):
        register_page()
    elif not st.session_state.authenticated:
        login_page()
    else:
        dashboard_page()

if __name__ == "__main__":
    main()
