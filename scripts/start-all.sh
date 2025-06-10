#!/bin/bash

# FastAPI Enterprise MVP - Start All Services
# This script starts both backend and frontend in the background

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
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

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to wait for service to be ready
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    print_step "Waiting for $service_name to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" >/dev/null 2>&1; then
            print_success "$service_name is ready!"
            return 0
        fi
        
        echo -n "."
        sleep 1
        attempt=$((attempt + 1))
    done
    
    print_error "$service_name failed to start within $max_attempts seconds"
    return 1
}

# Function to start backend
start_backend() {
    print_step "Starting FastAPI backend..."
    
    if check_port 8000; then
        print_warning "Port 8000 is already in use. Skipping backend startup."
        return 0
    fi
    
    cd backend
    
    # Check if virtual environment exists
    if [ ! -d ".venv" ]; then
        print_step "Creating backend virtual environment..."
        uv venv
        source .venv/bin/activate
        uv pip install -e .[dev]
    fi
    
    # Start backend in background
    export PYTHONPATH=/home/zzf/fastapi-devcontainer-mvp/backend
    nohup python -m uvicorn app.main_simple:app --host 0.0.0.0 --port 8000 --reload > ../logs/backend.log 2>&1 &
    echo $! > ../logs/backend.pid
    
    cd ..
    
    # Wait for backend to be ready
    wait_for_service "http://localhost:8000/health" "Backend API"
}

# Function to start frontend
start_frontend() {
    print_step "Starting Streamlit frontend..."
    
    if check_port 8501; then
        print_warning "Port 8501 is already in use. Skipping frontend startup."
        return 0
    fi
    
    cd frontend
    
    # Check if virtual environment exists
    if [ ! -d ".venv" ]; then
        print_step "Creating frontend virtual environment..."
        uv venv
        source .venv/bin/activate
        uv pip install -r requirements.txt
    fi
    
    # Start frontend in background
    export PYTHONPATH=/home/zzf/fastapi-devcontainer-mvp/frontend/.venv/lib/python3.13/site-packages:$PYTHONPATH
    nohup python -m streamlit run app.py --server.port 8501 --server.address 0.0.0.0 > ../logs/frontend.log 2>&1 &
    echo $! > ../logs/frontend.pid
    
    cd ..
    
    # Wait for frontend to be ready
    wait_for_service "http://localhost:8501/_stcore/health" "Frontend App"
}

# Function to show running services
show_services() {
    print_header "🌐 Services Status"
    echo ""
    
    # Check backend
    if curl -s http://localhost:8000/health >/dev/null 2>&1; then
        print_success "Backend API: http://localhost:8000"
        echo "  📚 API Docs: http://localhost:8000/docs"
        echo "  ❤️  Health: http://localhost:8000/health"
    else
        print_error "Backend API: Not responding"
    fi
    
    echo ""
    
    # Check frontend
    if curl -s http://localhost:8501/_stcore/health >/dev/null 2>&1; then
        print_success "Frontend App: http://localhost:8501"
    else
        print_error "Frontend App: Not responding"
    fi
    
    echo ""
}

# Function to show logs
show_logs() {
    print_header "📋 Service Logs"
    echo ""
    echo "Backend logs: tail -f logs/backend.log"
    echo "Frontend logs: tail -f logs/frontend.log"
    echo ""
    echo "To stop services: ./scripts/stop-all.sh"
    echo ""
}

# Main function
main() {
    local command=${1:-start}
    
    case $command in
        start)
            print_header "FastAPI Enterprise MVP - Starting All Services"
            echo ""
            
            # Create logs directory
            mkdir -p logs
            
            # Start services
            start_backend
            start_frontend
            
            echo ""
            show_services
            show_logs
            ;;
        status)
            show_services
            ;;
        logs)
            if [ -f "logs/backend.log" ] && [ -f "logs/frontend.log" ]; then
                print_header "📋 Live Logs (Ctrl+C to exit)"
                tail -f logs/backend.log logs/frontend.log
            else
                print_error "Log files not found. Are the services running?"
            fi
            ;;
        help|--help|-h)
            echo "FastAPI Enterprise MVP - Start All Services"
            echo ""
            echo "Usage: $0 [COMMAND]"
            echo ""
            echo "Commands:"
            echo "  start     Start both backend and frontend (default)"
            echo "  status    Show services status"
            echo "  logs      Show live logs"
            echo "  help      Show this help message"
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
