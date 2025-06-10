#!/bin/bash

# FastAPI Enterprise MVP - Enterprise Startup Script
# This script provides a unified, production-ready startup solution

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_header() {
    echo -e "${CYAN}🏢 $1${NC}"
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

# Configuration
ENVIRONMENT=${1:-development}
SERVICE_MODE=${2:-standalone}

# Function to validate environment
validate_environment() {
    case $ENVIRONMENT in
        development|testing|staging|production)
            print_success "Environment: $ENVIRONMENT"
            ;;
        *)
            print_error "Invalid environment: $ENVIRONMENT"
            echo "Valid environments: development, testing, staging, production"
            exit 1
            ;;
    esac
}

# Function to validate service mode
validate_service_mode() {
    case $SERVICE_MODE in
        standalone|microservice|demo)
            print_success "Service mode: $SERVICE_MODE"
            ;;
        *)
            print_error "Invalid service mode: $SERVICE_MODE"
            echo "Valid modes: standalone, microservice, demo"
            exit 1
            ;;
    esac
}

# Function to setup environment variables
setup_environment() {
    print_step "Setting up environment variables..."
    
    # Export environment variables
    export ENVIRONMENT=$ENVIRONMENT
    export SERVICE_MODE=$SERVICE_MODE
    export PYTHONPATH="$(pwd)/backend:$PYTHONPATH"
    
    print_success "Environment configured"
}

# Function to stop existing services
stop_existing_services() {
    print_step "Stopping existing services..."
    
    # Stop any running processes
    pkill -f "uvicorn.*main" 2>/dev/null || true
    pkill -f "streamlit.*app" 2>/dev/null || true
    
    sleep 2
    print_success "Existing services stopped"
}

# Function to start backend
start_backend() {
    print_step "Starting backend service..."
    
    cd backend
    
    # Install dependencies if needed
    if [ ! -d ".venv" ]; then
        print_step "Creating virtual environment..."
        python -m venv .venv
    fi
    
    # Activate virtual environment and install dependencies
    source .venv/bin/activate 2>/dev/null || true
    pip install -q fastapi uvicorn pydantic pydantic-settings structlog python-json-logger
    
    # Start backend
    export PYTHONPATH="$(pwd):$PYTHONPATH"
    nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > ../logs/backend.log 2>&1 &
    
    cd ..
    print_success "Backend service started"
}

# Function to start frontend
start_frontend() {
    print_step "Starting frontend service..."
    
    cd frontend
    
    # Install dependencies if needed
    pip install -q streamlit requests
    
    # Start frontend
    export BACKEND_URL="http://localhost:8000"
    nohup streamlit run app.py --server.port 8501 --server.address 0.0.0.0 > ../logs/frontend.log 2>&1 &
    
    cd ..
    print_success "Frontend service started"
}

# Function to wait for services
wait_for_services() {
    print_step "Waiting for services to be ready..."
    
    local max_attempts=30
    local attempt=1
    
    # Wait for backend
    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:8000/health >/dev/null 2>&1; then
            print_success "Backend is ready"
            break
        fi
        
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    if [ $attempt -gt $max_attempts ]; then
        print_warning "Backend may still be starting..."
    fi
    
    # Wait for frontend
    attempt=1
    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:8501 >/dev/null 2>&1; then
            print_success "Frontend is ready"
            break
        fi
        
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    if [ $attempt -gt $max_attempts ]; then
        print_warning "Frontend may still be starting..."
    fi
}

# Function to show service status
show_status() {
    print_step "Service Status:"
    echo ""
    
    # Backend status
    if curl -s http://localhost:8000/health >/dev/null 2>&1; then
        print_success "🔧 Backend: Running - http://localhost:8000"
        print_success "📚 API Docs: http://localhost:8000/docs"
    else
        print_error "🔧 Backend: Not responding"
    fi
    
    # Frontend status
    if curl -s http://localhost:8501 >/dev/null 2>&1; then
        print_success "🌐 Frontend: Running - http://localhost:8501"
    else
        print_error "🌐 Frontend: Not responding"
    fi
}

# Function to show management commands
show_management() {
    print_step "Management Commands:"
    echo ""
    echo "📋 View backend logs: tail -f logs/backend.log"
    echo "📋 View frontend logs: tail -f logs/frontend.log"
    echo "🛑 Stop services: pkill -f 'uvicorn.*main'; pkill -f 'streamlit.*app'"
    echo "🔄 Restart: $0 $ENVIRONMENT $SERVICE_MODE"
    echo ""
    echo "🧪 Test API:"
    echo "   curl http://localhost:8000/health"
    echo "   curl http://localhost:8000/services"
    echo ""
}

# Main function
main() {
    print_header "FastAPI Enterprise MVP - Enterprise Startup"
    echo ""
    
    print_step "Configuration:"
    echo "   Environment: $ENVIRONMENT"
    echo "   Service Mode: $SERVICE_MODE"
    echo ""
    
    # Validate inputs
    validate_environment
    validate_service_mode
    
    # Create logs directory
    mkdir -p logs
    
    # Setup environment
    setup_environment
    
    # Stop existing services
    stop_existing_services
    
    # Start services
    start_backend
    start_frontend
    
    # Wait for services
    wait_for_services
    
    echo ""
    print_header "🎉 Enterprise Environment Ready!"
    echo ""
    
    # Show status
    show_status
    echo ""
    
    # Show management commands
    show_management
    
    print_success "Enterprise FastAPI MVP is running!"
    print_step "Access the application at: http://localhost:8501"
    print_step "API documentation at: http://localhost:8000/docs"
}

# Handle command line arguments
case "${1:-}" in
    help|--help|-h)
        echo "FastAPI Enterprise MVP - Enterprise Startup Script"
        echo ""
        echo "Usage: $0 [ENVIRONMENT] [SERVICE_MODE]"
        echo ""
        echo "Environments:"
        echo "  development  Development environment (default)"
        echo "  testing      Testing environment"
        echo "  staging      Staging environment"
        echo "  production   Production environment"
        echo ""
        echo "Service Modes:"
        echo "  standalone   Single service mode (default)"
        echo "  microservice Full microservice mode"
        echo "  demo         Demo/mock mode"
        echo ""
        echo "Examples:"
        echo "  $0                           # Development, standalone"
        echo "  $0 production microservice   # Production, microservice"
        echo "  $0 development demo          # Development, demo mode"
        echo ""
        ;;
    *)
        main
        ;;
esac
