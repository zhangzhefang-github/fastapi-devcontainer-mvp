#!/bin/bash

# FastAPI Enterprise MVP - Start Demo
# This script starts both backend and demo frontend for testing

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
    print_header "FastAPI Enterprise MVP - Demo Startup"
    echo ""
    
    # Create logs directory
    mkdir -p logs
    
    # Start backend
    print_step "Starting FastAPI backend..."
    if check_port 8000; then
        print_info "Port 8000 is already in use. Backend may already be running."
    else
        cd backend
        export PYTHONPATH=/home/zzf/fastapi-devcontainer-mvp/backend
        nohup .venv/bin/python -m uvicorn app.main_simple:app --host 0.0.0.0 --port 8000 --reload > ../logs/backend.log 2>&1 &
        echo $! > ../logs/backend.pid
        print_success "Backend started (PID: $(cat ../logs/backend.pid))"
        cd ..
    fi
    
    # Wait for backend
    wait_for_service "http://localhost:8000/health" "Backend API"
    
    # Start demo frontend
    print_step "Starting Demo Frontend..."
    if check_port 8501; then
        print_info "Port 8501 is already in use. Frontend may already be running."
    else
        cd frontend
        export PYTHONPATH=/home/zzf/fastapi-devcontainer-mvp/frontend/.venv/lib/python3.13/site-packages:$PYTHONPATH
        nohup .venv/bin/python -m streamlit run app_demo.py --server.port 8501 --server.address 0.0.0.0 > ../logs/frontend.log 2>&1 &
        echo $! > ../logs/frontend.pid
        print_success "Demo Frontend started (PID: $(cat ../logs/frontend.pid))"
        cd ..
    fi
    
    # Wait for frontend
    wait_for_service "http://localhost:8501/_stcore/health" "Demo Frontend"
    
    echo ""
    print_header "🎉 Demo Environment Ready!"
    echo ""
    
    # Show demo information
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
    echo "🌐 Demo Frontend: http://localhost:8501"
    echo "🔧 Backend API: http://localhost:8000"
    echo "📚 API Docs: http://localhost:8000/docs"
    echo "❤️  Health Check: http://localhost:8000/health"
    echo ""
    
    print_step "Testing Instructions:"
    echo ""
    echo "1. 🌐 Open http://localhost:8501 in your browser"
    echo "2. 🔑 Try logging in with one of the demo accounts above"
    echo "3. 📝 Or register a new account using the registration form"
    echo "4. 🎯 Explore the dashboard tabs: Profile, Users, System, API Test"
    echo "5. 🚪 Test logout functionality"
    echo ""
    
    print_step "Management Commands:"
    echo ""
    echo "📋 View logs: tail -f logs/backend.log logs/frontend.log"
    echo "🛑 Stop services: ./scripts/stop-all.sh"
    echo "🧪 Run tests: ./scripts/test-complete.sh"
    echo ""
    
    print_success "Happy testing! 🎉"
}

main "$@"
