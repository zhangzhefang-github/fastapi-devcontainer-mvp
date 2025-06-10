#!/bin/bash

# FastAPI Enterprise MVP - Complete Testing Script
# This script tests both backend API and provides demo data for frontend testing

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_header() {
    echo -e "${CYAN}🧪 $1${NC}"
}

print_step() {
    echo -e "${BLUE}▶️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}💡 $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

API_BASE="http://localhost:8000"
FRONTEND_URL="http://localhost:8501"

# Function to test API endpoint
test_api() {
    local method=$1
    local endpoint=$2
    local data=$3
    local description=$4
    
    print_step "Testing: $description"
    
    if [ -z "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" -X $method "$API_BASE$endpoint")
    else
        response=$(curl -s -w "\n%{http_code}" -X $method \
            -H "Content-Type: application/json" \
            -d "$data" \
            "$API_BASE$endpoint")
    fi
    
    # Extract status code (last line)
    status_code=$(echo "$response" | tail -n1)
    # Extract body (all but last line)
    body=$(echo "$response" | head -n -1)
    
    if [[ $status_code -ge 200 && $status_code -lt 300 ]]; then
        print_success "$method $endpoint - Status: $status_code"
        if [ ! -z "$body" ]; then
            echo "Response: $body" | head -c 200
            if [ ${#body} -gt 200 ]; then
                echo "..."
            fi
            echo ""
        fi
        return 0
    else
        print_error "$method $endpoint - Status: $status_code"
        echo "Response: $body"
        return 1
    fi
}

# Function to test backend API
test_backend() {
    print_header "Backend API Testing"
    echo ""
    
    # Test basic endpoints
    test_api "GET" "/" "" "Root endpoint"
    test_api "GET" "/health" "" "Health check"
    
    echo ""
    print_info "Backend API is working! ✨"
    echo ""
}

# Function to show demo data for frontend testing
show_demo_data() {
    print_header "Frontend Testing - Demo User Data"
    echo ""
    
    print_info "Use these demo accounts to test the frontend:"
    echo ""
    
    echo "👤 Demo User 1 (Regular User):"
    echo "   Email: alice@example.com"
    echo "   Username: alice"
    echo "   Password: SecurePass123!"
    echo "   Full Name: Alice Johnson"
    echo "   Role: user"
    echo ""
    
    echo "👤 Demo User 2 (Admin User):"
    echo "   Email: bob@example.com"
    echo "   Username: bob"
    echo "   Password: AdminPass456!"
    echo "   Full Name: Bob Smith"
    echo "   Role: admin"
    echo ""
    
    echo "👤 Demo User 3 (Test User):"
    echo "   Email: charlie@example.com"
    echo "   Username: charlie"
    echo "   Password: TestPass789!"
    echo "   Full Name: Charlie Brown"
    echo "   Role: user"
    echo ""
}

# Function to show frontend testing steps
show_frontend_testing() {
    print_header "Frontend Testing Steps"
    echo ""
    
    print_step "1. Open Frontend Application"
    echo "   🌐 URL: $FRONTEND_URL"
    echo "   📱 The Streamlit app should load with a login page"
    echo ""
    
    print_step "2. Test User Registration"
    echo "   ✏️  Click 'Register' button"
    echo "   📝 Fill in the registration form:"
    echo "      - Email: your-email@example.com"
    echo "      - Username: your-username"
    echo "      - Password: YourSecurePass123!"
    echo "      - Full Name: Your Full Name"
    echo "      - Bio: (optional)"
    echo "      - ✅ Accept terms and conditions"
    echo "   🚀 Click 'Register' to create account"
    echo ""
    
    print_step "3. Test User Login"
    echo "   🔑 Use one of the demo accounts above"
    echo "   📧 Enter username/email and password"
    echo "   🚀 Click 'Login' button"
    echo "   ✅ Should redirect to dashboard"
    echo ""
    
    print_step "4. Test Dashboard Features"
    echo "   👤 Profile Tab: View and edit user information"
    echo "   👥 Users Tab: Browse other users (if logged in)"
    echo "   🔧 System Tab: Check system status and health"
    echo ""
    
    print_step "5. Test Logout"
    echo "   🚪 Click 'Logout' button in sidebar"
    echo "   🔄 Should return to login page"
    echo ""
}

# Function to show API testing examples
show_api_testing() {
    print_header "API Testing Examples"
    echo ""
    
    print_step "1. Test API Documentation"
    echo "   📚 Interactive Docs: $API_BASE/docs"
    echo "   📖 ReDoc: $API_BASE/redoc"
    echo ""
    
    print_step "2. Test Health Endpoints"
    echo "   ❤️  Health Check:"
    echo "      curl $API_BASE/health"
    echo ""
    echo "   🔧 Ready Check:"
    echo "      curl $API_BASE/ready"
    echo ""
    
    print_step "3. Test Authentication (when implemented)"
    echo "   🔑 Login:"
    echo '      curl -X POST "$API_BASE/api/v1/auth/login" \'
    echo '        -H "Content-Type: application/x-www-form-urlencoded" \'
    echo '        -d "username=alice&password=SecurePass123!"'
    echo ""
    
    print_step "4. Test User Registration (when implemented)"
    echo "   📝 Register:"
    echo '      curl -X POST "$API_BASE/api/v1/auth/register" \'
    echo '        -H "Content-Type: application/json" \'
    echo '        -d "{"'
    echo '          "email": "test@example.com",'
    echo '          "username": "testuser",'
    echo '          "password": "SecurePass123!",'
    echo '          "full_name": "Test User",'
    echo '          "terms_accepted": true'
    echo '        }"'
    echo ""
}

# Function to check service status
check_services() {
    print_header "Service Status Check"
    echo ""
    
    # Check backend
    if curl -s "$API_BASE/health" >/dev/null 2>&1; then
        print_success "Backend API: Running at $API_BASE"
    else
        print_error "Backend API: Not running or not responding"
        echo "   💡 Start with: cd backend && source .venv/bin/activate && uvicorn app.main_simple:app --reload"
        return 1
    fi
    
    # Check frontend
    if curl -s "$FRONTEND_URL/_stcore/health" >/dev/null 2>&1; then
        print_success "Frontend App: Running at $FRONTEND_URL"
    else
        print_error "Frontend App: Not running or not responding"
        echo "   💡 Start with: cd frontend && source .venv/bin/activate && streamlit run app.py"
        return 1
    fi
    
    echo ""
    return 0
}

# Function to show troubleshooting tips
show_troubleshooting() {
    print_header "Troubleshooting Tips"
    echo ""
    
    print_step "If Backend API is not working:"
    echo "   1. Check if virtual environment is activated"
    echo "   2. Ensure all dependencies are installed: uv pip install -e .[dev]"
    echo "   3. Check Python path: export PYTHONPATH=/path/to/backend"
    echo "   4. Check logs: tail -f logs/backend.log"
    echo ""
    
    print_step "If Frontend is not working:"
    echo "   1. Check if Streamlit is installed: pip list | grep streamlit"
    echo "   2. Check if backend is running and accessible"
    echo "   3. Check frontend logs: tail -f logs/frontend.log"
    echo "   4. Try restarting: pkill -f streamlit && streamlit run app.py"
    echo ""
    
    print_step "If Registration/Login is not working:"
    echo "   1. Check if backend authentication endpoints are implemented"
    echo "   2. Check browser console for JavaScript errors"
    echo "   3. Verify API endpoints in backend/app/api/v1/endpoints/"
    echo "   4. Check database connection (if using database)"
    echo ""
}

# Main function
main() {
    local command=${1:-all}
    
    case $command in
        backend)
            check_services && test_backend
            ;;
        frontend)
            show_demo_data
            show_frontend_testing
            ;;
        api)
            show_api_testing
            ;;
        demo)
            show_demo_data
            ;;
        status)
            check_services
            ;;
        troubleshoot)
            show_troubleshooting
            ;;
        all)
            check_services
            echo ""
            test_backend
            show_demo_data
            show_frontend_testing
            show_api_testing
            ;;
        help|--help|-h)
            echo "FastAPI Enterprise MVP - Complete Testing Script"
            echo ""
            echo "Usage: $0 [COMMAND]"
            echo ""
            echo "Commands:"
            echo "  all           Run all tests and show all info (default)"
            echo "  backend       Test backend API only"
            echo "  frontend      Show frontend testing guide"
            echo "  api           Show API testing examples"
            echo "  demo          Show demo user data"
            echo "  status        Check service status"
            echo "  troubleshoot  Show troubleshooting tips"
            echo "  help          Show this help message"
            echo ""
            ;;
        *)
            print_error "Unknown command: $command"
            echo "Use '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
