#!/bin/bash

# FastAPI Enterprise MVP - Start with Authentication
# This script starts backend with auth API and frontend with API integration

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_header() {
    echo -e "${CYAN}🚀 $1${NC}"
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

# Function to check if port is in use
check_port() {
    local port=$1
    if netstat -tuln 2>/dev/null | grep ":$port " >/dev/null; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to wait for service
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=15
    local attempt=1
    
    print_step "Waiting for $service_name to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" >/dev/null 2>&1; then
            print_success "$service_name is ready!"
            return 0
        fi
        
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo ""
    echo "⚠️  $service_name may still be starting..."
    return 1
}

main() {
    print_header "FastAPI Enterprise MVP - Authentication Demo"
    echo ""
    
    # Stop any existing services
    print_step "Stopping existing services..."
    ./scripts/stop-all.sh >/dev/null 2>&1 || true
    
    # Create logs directory
    mkdir -p logs
    
    # Start backend with authentication
    print_step "Starting FastAPI backend with authentication..."
    cd backend
    export PYTHONPATH=/home/zzf/fastapi-devcontainer-mvp/backend
    nohup .venv/bin/python -m uvicorn app.main_with_auth:app --host 0.0.0.0 --port 8000 --reload > ../logs/backend.log 2>&1 &
    echo $! > ../logs/backend.pid
    print_success "Backend with auth started (PID: $(cat ../logs/backend.pid))"
    cd ..
    
    # Wait for backend
    wait_for_service "http://localhost:8000/health" "Backend API"
    
    # Start frontend with API integration
    print_step "Starting Frontend with API integration..."
    cd frontend
    export PYTHONPATH=/home/zzf/fastapi-devcontainer-mvp/frontend/.venv/lib/python3.13/site-packages:$PYTHONPATH
    nohup .venv/bin/python -m streamlit run app_with_api.py --server.port 8501 --server.address 0.0.0.0 > ../logs/frontend.log 2>&1 &
    echo $! > ../logs/frontend.pid
    print_success "Frontend with API started (PID: $(cat ../logs/frontend.pid))"
    cd ..
    
    # Wait for frontend
    wait_for_service "http://localhost:8501/_stcore/health" "Frontend App"
    
    echo ""
    print_header "🎉 Authentication Demo Ready!"
    echo ""
    
    # Test API endpoints
    print_step "Testing API endpoints..."
    echo ""
    
    # Test health
    if curl -s http://localhost:8000/health >/dev/null 2>&1; then
        print_success "✅ Health endpoint working"
    else
        echo "❌ Health endpoint failed"
    fi
    
    # Test login endpoint
    login_response=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
        -H "Content-Type: application/json" \
        -d '{"username": "alice", "password": "SecurePass123!"}' \
        -w "%{http_code}")
    
    if echo "$login_response" | tail -c 4 | grep -q "200"; then
        print_success "✅ Login API endpoint working"
    else
        echo "❌ Login API endpoint failed"
    fi
    
    echo ""
    print_step "Demo User Accounts:"
    echo ""
    echo "👤 Alice (Regular User):"
    echo "   Username: alice"
    echo "   Password: SecurePass123!"
    echo ""
    echo "👨‍💼 Bob (Admin User):"
    echo "   Username: bob" 
    echo "   Password: AdminPass456!"
    echo ""
    echo "🧪 Charlie (Test User):"
    echo "   Username: charlie"
    echo "   Password: TestPass789!"
    echo ""
    
    print_step "Access URLs:"
    echo ""
    echo "🌐 Frontend App: http://localhost:8501"
    echo "🔧 Backend API: http://localhost:8000"
    echo "📚 API Docs: http://localhost:8000/docs"
    echo "❤️  Health Check: http://localhost:8000/health"
    echo ""
    
    print_step "API Testing Examples:"
    echo ""
    echo "# Login API"
    echo "curl -X POST http://localhost:8000/api/v1/auth/login \\"
    echo "  -H \"Content-Type: application/json\" \\"
    echo "  -d '{\"username\": \"alice\", \"password\": \"SecurePass123!\"}'"
    echo ""
    echo "# Register API"
    echo "curl -X POST http://localhost:8000/api/v1/auth/register \\"
    echo "  -H \"Content-Type: application/json\" \\"
    echo "  -d '{\"email\": \"test@example.com\", \"username\": \"testuser\", \"password\": \"TestPass123!\", \"full_name\": \"Test User\", \"terms_accepted\": true}'"
    echo ""
    echo "# Get Users API"
    echo "curl http://localhost:8000/api/v1/users"
    echo ""
    
    print_step "Testing Instructions:"
    echo ""
    echo "1. 🌐 Open http://localhost:8501 in your browser"
    echo "2. 🔑 Login with real API integration (alice/SecurePass123!)"
    echo "3. 📝 Register new users via API"
    echo "4. 🎯 Explore dashboard with live API data"
    echo "5. 🧪 Test API endpoints in the API Test tab"
    echo ""
    
    print_step "Management Commands:"
    echo ""
    echo "📋 View logs: tail -f logs/backend.log logs/frontend.log"
    echo "🛑 Stop services: ./scripts/stop-all.sh"
    echo "🧪 Run tests: ./scripts/test-complete.sh"
    echo ""
    
    print_success "Happy testing with real API integration! 🎉"
}

main "$@"
