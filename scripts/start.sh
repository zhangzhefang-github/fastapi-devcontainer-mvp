#!/bin/bash

# FastAPI Enterprise MVP - Quick Start Script
# This script helps you get the application running quickly

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install uv if not present
install_uv() {
    if ! command_exists uv; then
        print_status "Installing uv package manager..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.cargo/bin:$PATH"

        if command_exists uv; then
            print_success "uv installed successfully!"
        else
            print_warning "uv installation may require terminal restart"
        fi
    else
        print_status "uv is already installed"
    fi
}

# Function to setup local Python environment with uv
setup_local_env() {
    print_status "Setting up local development environment with uv..."

    # Install uv if needed
    install_uv

    # Setup backend
    print_status "Setting up backend environment..."
    cd backend
    if [ ! -d ".venv" ]; then
        uv venv
    fi

    # Check if activation works
    if [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
        uv pip install -e .[dev]
        print_success "Backend environment ready!"
    else
        print_error "Failed to create backend virtual environment"
        return 1
    fi

    cd ..

    # Setup frontend
    print_status "Setting up frontend environment..."
    cd frontend
    if [ ! -d ".venv" ]; then
        uv venv
    fi

    if [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
        uv pip install -r requirements.txt
        print_success "Frontend environment ready!"
    else
        print_error "Failed to create frontend virtual environment"
        return 1
    fi

    cd ..

    print_success "Local development environment setup complete!"
    echo ""
    echo "To start development:"
    echo "1. Backend: cd backend && source .venv/bin/activate && uvicorn app.main:app --reload"
    echo "2. Frontend: cd frontend && source .venv/bin/activate && streamlit run app.py"
}

# Function to check if Docker is running
check_docker() {
    if ! command_exists docker; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi

    if ! command_exists docker-compose; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
}

# Function to create .env file if it doesn't exist
setup_env() {
    if [ ! -f .env ]; then
        print_status "Creating .env file..."
        cp .env.example .env 2>/dev/null || {
            print_warning ".env.example not found, creating basic .env file"
            cat > .env << EOF
# Security Configuration
JWT_SECRET=$(openssl rand -base64 32)
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30

# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@db:5432/fastapi_app
REDIS_URL=redis://redis:6379/0

# Application Configuration
APP_NAME=FastAPI Enterprise MVP
APP_VERSION=1.0.0
DEBUG=true
LOG_LEVEL=INFO
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8501"]

# Monitoring Configuration
ENABLE_METRICS=true
ENABLE_TRACING=true

# Container Configuration
BACKEND_PORT=8000
FRONTEND_PORT=8501
NGINX_PORT=80
EOF
        }
        print_success ".env file created"
    else
        print_status ".env file already exists"
    fi
}

# Function to start development environment
start_dev() {
    print_status "Starting development environment..."
    
    # Build and start services
    docker-compose -f docker-compose.dev.yml up -d --build
    
    # Wait for services to be healthy
    print_status "Waiting for services to be ready..."
    sleep 10
    
    # Check service health
    check_services
}

# Function to start production environment
start_prod() {
    print_status "Starting production environment..."
    
    # Build and start services
    docker-compose up -d --build
    
    # Wait for services to be healthy
    print_status "Waiting for services to be ready..."
    sleep 15
    
    # Check service health
    check_services
}

# Function to check service health
check_services() {
    print_status "Checking service health..."
    
    # Check backend
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        print_success "Backend is healthy"
    else
        print_warning "Backend health check failed"
    fi
    
    # Check frontend
    if curl -f http://localhost:8501/_stcore/health >/dev/null 2>&1; then
        print_success "Frontend is healthy"
    else
        print_warning "Frontend health check failed"
    fi
}

# Function to show service URLs
show_urls() {
    echo ""
    print_success "🚀 Application is running!"
    echo ""
    echo "📱 Frontend (Streamlit):  http://localhost:8501"
    echo "🔧 Backend API:          http://localhost:8000"
    echo "📚 API Documentation:    http://localhost:8000/docs"
    echo "📊 Alternative Docs:     http://localhost:8000/redoc"
    echo "❤️  Health Check:        http://localhost:8000/health"
    echo "📈 Metrics:              http://localhost:8000/metrics"
    echo ""
    echo "🔐 Demo Credentials:"
    echo "   Username: alice"
    echo "   Password: 123456"
    echo "   Role: admin"
    echo ""
    echo "   Username: bob"
    echo "   Password: 123456"
    echo "   Role: user"
    echo ""
}

# Function to show logs
show_logs() {
    print_status "Showing application logs (Ctrl+C to exit)..."
    docker-compose -f docker-compose.dev.yml logs -f
}

# Function to stop services
stop_services() {
    print_status "Stopping services..."
    docker-compose -f docker-compose.dev.yml down
    docker-compose down
    print_success "Services stopped"
}

# Function to clean up
cleanup() {
    print_status "Cleaning up containers and volumes..."
    docker-compose -f docker-compose.dev.yml down -v --remove-orphans
    docker-compose down -v --remove-orphans
    docker system prune -f
    print_success "Cleanup completed"
}

# Function to run tests
run_tests() {
    print_status "Running tests..."
    docker-compose -f docker-compose.dev.yml exec backend pytest --cov=app --cov-report=term
}

# Function to show help
show_help() {
    echo "FastAPI Enterprise MVP - Quick Start Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  dev       Start development environment with Docker (default)"
    echo "  local     Setup local development environment with uv"
    echo "  prod      Start production environment"
    echo "  logs      Show application logs"
    echo "  test      Run tests"
    echo "  stop      Stop all services"
    echo "  clean     Clean up containers and volumes"
    echo "  health    Check service health"
    echo "  install-uv Install uv package manager"
    echo "  help      Show this help message"
    echo ""
}

# Main script logic
main() {
    local command=${1:-dev}
    
    case $command in
        dev)
            check_docker
            setup_env
            start_dev
            show_urls
            ;;
        local)
            setup_local_env
            ;;
        prod)
            check_docker
            setup_env
            start_prod
            show_urls
            ;;
        logs)
            show_logs
            ;;
        test)
            run_tests
            ;;
        stop)
            stop_services
            ;;
        clean)
            cleanup
            ;;
        health)
            check_services
            ;;
        install-uv)
            install_uv
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
