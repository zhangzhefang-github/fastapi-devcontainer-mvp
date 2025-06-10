#!/bin/bash

# FastAPI Enterprise MVP - Stop All Services
# This script stops both backend and frontend services

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_header() {
    echo -e "${CYAN}🛑 $1${NC}"
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

# Function to stop service by PID file
stop_service() {
    local service_name=$1
    local pid_file=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p $pid > /dev/null 2>&1; then
            print_step "Stopping $service_name (PID: $pid)..."
            kill $pid
            
            # Wait for process to stop
            local attempts=0
            while ps -p $pid > /dev/null 2>&1 && [ $attempts -lt 10 ]; do
                sleep 1
                attempts=$((attempts + 1))
            done
            
            if ps -p $pid > /dev/null 2>&1; then
                print_warning "Force killing $service_name..."
                kill -9 $pid
            fi
            
            print_success "$service_name stopped"
        else
            print_warning "$service_name was not running"
        fi
        
        rm -f "$pid_file"
    else
        print_warning "No PID file found for $service_name"
    fi
}

# Function to stop services by port
stop_by_port() {
    local port=$1
    local service_name=$2
    
    local pids=$(lsof -ti:$port 2>/dev/null || true)
    
    if [ ! -z "$pids" ]; then
        print_step "Stopping $service_name on port $port..."
        echo "$pids" | xargs kill -TERM 2>/dev/null || true
        
        # Wait a moment
        sleep 2
        
        # Force kill if still running
        local remaining_pids=$(lsof -ti:$port 2>/dev/null || true)
        if [ ! -z "$remaining_pids" ]; then
            print_warning "Force killing $service_name..."
            echo "$remaining_pids" | xargs kill -9 2>/dev/null || true
        fi
        
        print_success "$service_name stopped"
    else
        print_warning "$service_name was not running on port $port"
    fi
}

# Function to clean up log files
cleanup_logs() {
    if [ -d "logs" ]; then
        print_step "Cleaning up log files..."
        rm -f logs/*.pid
        # Keep log files for debugging, just remove PID files
        print_success "Cleanup completed"
    fi
}

# Main function
main() {
    local command=${1:-stop}
    
    case $command in
        stop)
            print_header "FastAPI Enterprise MVP - Stopping All Services"
            echo ""
            
            # Stop by PID files first
            stop_service "Backend API" "logs/backend.pid"
            stop_service "Frontend App" "logs/frontend.pid"
            
            # Stop by ports as backup
            stop_by_port 8000 "Backend API"
            stop_by_port 8501 "Frontend App"
            
            # Clean up
            cleanup_logs
            
            echo ""
            print_success "All services stopped"
            ;;
        kill)
            print_header "Force Killing All Services"
            echo ""
            
            # Force kill by ports
            stop_by_port 8000 "Backend API"
            stop_by_port 8501 "Frontend App"
            
            # Also kill any uvicorn or streamlit processes
            pkill -f "uvicorn.*app.main" 2>/dev/null || true
            pkill -f "streamlit.*app.py" 2>/dev/null || true
            
            cleanup_logs
            
            print_success "All services force killed"
            ;;
        status)
            print_header "Service Status"
            echo ""
            
            # Check backend
            if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
                print_success "Backend API: Running on port 8000"
            else
                print_error "Backend API: Not running"
            fi
            
            # Check frontend
            if lsof -Pi :8501 -sTCP:LISTEN -t >/dev/null 2>&1; then
                print_success "Frontend App: Running on port 8501"
            else
                print_error "Frontend App: Not running"
            fi
            ;;
        help|--help|-h)
            echo "FastAPI Enterprise MVP - Stop All Services"
            echo ""
            echo "Usage: $0 [COMMAND]"
            echo ""
            echo "Commands:"
            echo "  stop      Stop all services gracefully (default)"
            echo "  kill      Force kill all services"
            echo "  status    Show services status"
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
