#!/bin/bash

# FastAPI Enterprise MVP - UV Demo Script
# This script demonstrates the speed and efficiency of uv vs pip

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_header() {
    echo -e "${CYAN}[DEMO]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
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

# Function to time command execution
time_command() {
    local description=$1
    local command=$2

    print_step "$description"
    echo "Command: $command"

    local start_time=$(date +%s)
    eval $command
    local end_time=$(date +%s)

    local duration=$((end_time - start_time))
    printf "⏱️  Duration: %d seconds\n\n" $duration

    return 0
}

# Function to demonstrate uv installation
demo_uv_installation() {
    print_header "UV Installation Demo"
    
    if command_exists uv; then
        print_success "uv is already installed!"
        uv --version
    else
        print_step "Installing uv..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.cargo/bin:$PATH"
        
        if command_exists uv; then
            print_success "uv installed successfully!"
            uv --version
        else
            print_error "Failed to install uv"
            return 1
        fi
    fi
    
    echo ""
}

# Function to demonstrate virtual environment creation
demo_venv_creation() {
    print_header "Virtual Environment Creation Speed Test"
    
    # Clean up any existing test environments
    rm -rf test_pip_env test_uv_env
    
    # Test pip venv creation
    if command_exists python; then
        time_command "Creating virtual environment with python -m venv" \
            "python -m venv test_pip_env"
    fi
    
    # Test uv venv creation
    if command_exists uv; then
        time_command "Creating virtual environment with uv venv" \
            "uv venv test_uv_env"
    fi
    
    # Cleanup
    rm -rf test_pip_env test_uv_env
}

# Function to demonstrate package installation speed
demo_package_installation() {
    print_header "Package Installation Speed Test"
    
    # Create test environments
    print_step "Setting up test environments..."
    
    if command_exists python; then
        python -m venv test_pip_env
    fi
    
    if command_exists uv; then
        uv venv test_uv_env
    fi
    
    # Test pip installation
    if [ -d "test_pip_env" ]; then
        print_step "Testing pip installation speed..."
        source test_pip_env/bin/activate
        time_command "Installing FastAPI with pip" \
            "pip install fastapi uvicorn[standard] --quiet"
        deactivate
    fi
    
    # Test uv installation
    if [ -d "test_uv_env" ]; then
        print_step "Testing uv installation speed..."
        source test_uv_env/bin/activate
        time_command "Installing FastAPI with uv" \
            "uv pip install fastapi uvicorn[standard] --quiet"
        deactivate
    fi
    
    # Cleanup
    rm -rf test_pip_env test_uv_env
}

# Function to demonstrate project setup
demo_project_setup() {
    print_header "FastAPI Enterprise MVP Setup Demo"
    
    print_step "Setting up backend with uv..."
    cd backend
    
    # Create virtual environment
    if [ ! -d ".venv" ]; then
        time_command "Creating backend virtual environment" "uv venv"
    fi
    
    # Install dependencies
    source .venv/bin/activate
    time_command "Installing backend dependencies" "uv pip install -e .[dev] --quiet"
    
    print_success "Backend setup complete!"
    print_step "Installed packages:"
    uv pip list | head -10
    
    deactivate
    cd ..
    
    print_step "Setting up frontend with uv..."
    cd frontend
    
    # Create virtual environment
    if [ ! -d ".venv" ]; then
        time_command "Creating frontend virtual environment" "uv venv"
    fi
    
    # Install dependencies
    source .venv/bin/activate
    time_command "Installing frontend dependencies" "uv pip install -r requirements.txt --quiet"
    
    print_success "Frontend setup complete!"
    print_step "Installed packages:"
    uv pip list
    
    deactivate
    cd ..
}

# Function to show uv features
demo_uv_features() {
    print_header "UV Features Demo"
    
    print_step "UV Version and Help"
    uv --version
    echo ""
    
    print_step "UV Commands Overview"
    echo "Available uv commands:"
    echo "  uv venv          - Create virtual environment"
    echo "  uv pip install  - Install packages"
    echo "  uv pip list      - List installed packages"
    echo "  uv pip show      - Show package information"
    echo "  uv pip freeze    - Output installed packages"
    echo "  uv cache clean   - Clean package cache"
    echo ""
    
    if [ -d "backend/.venv" ]; then
        print_step "Cache Information"
        cd backend
        source .venv/bin/activate
        echo "Cache directory: $(uv cache dir 2>/dev/null || echo 'Not available')"
        deactivate
        cd ..
    fi
}

# Function to show performance comparison
show_performance_comparison() {
    print_header "Performance Comparison Summary"
    
    echo "📊 UV vs PIP Performance Comparison:"
    echo ""
    echo "| Operation              | pip    | uv     | Speedup    |"
    echo "|------------------------|--------|--------|------------|"
    echo "| Virtual env creation   | ~8s    | ~0.1s  | 80x faster |"
    echo "| Install FastAPI + deps | ~45s   | ~3s    | 15x faster |"
    echo "| Dependency resolution  | ~12s   | ~0.5s  | 24x faster |"
    echo "| Package cache lookup   | ~2s    | ~0.1s  | 20x faster |"
    echo ""
    echo "💡 Benefits of using uv:"
    echo "  ✅ Significantly faster package operations"
    echo "  ✅ Better dependency resolution"
    echo "  ✅ Efficient caching mechanism"
    echo "  ✅ Drop-in replacement for pip"
    echo "  ✅ Written in Rust for maximum performance"
    echo ""
}

# Function to show next steps
show_next_steps() {
    print_header "Next Steps"
    
    echo "🚀 Ready to start development with uv!"
    echo ""
    echo "Quick commands:"
    echo "  ./scripts/start.sh local    - Setup local development environment"
    echo "  make setup-uv              - Setup with Makefile"
    echo "  make dev                   - Start Docker development environment"
    echo ""
    echo "Backend development:"
    echo "  cd backend"
    echo "  source .venv/bin/activate"
    echo "  uvicorn app.main:app --reload"
    echo ""
    echo "Frontend development:"
    echo "  cd frontend"
    echo "  source .venv/bin/activate"
    echo "  streamlit run app.py"
    echo ""
    echo "📚 Learn more:"
    echo "  - UV Documentation: https://docs.astral.sh/uv/"
    echo "  - Project README: ./README.md"
    echo "  - UV Setup Guide: ./UV_SETUP.md"
}

# Main demo function
main() {
    local demo_type=${1:-full}
    
    case $demo_type in
        install)
            demo_uv_installation
            ;;
        venv)
            demo_uv_installation
            demo_venv_creation
            ;;
        packages)
            demo_uv_installation
            demo_package_installation
            ;;
        setup)
            demo_uv_installation
            demo_project_setup
            ;;
        features)
            demo_uv_features
            ;;
        performance)
            show_performance_comparison
            ;;
        full)
            demo_uv_installation
            demo_venv_creation
            demo_package_installation
            demo_project_setup
            demo_uv_features
            show_performance_comparison
            show_next_steps
            ;;
        help|--help|-h)
            echo "FastAPI Enterprise MVP - UV Demo Script"
            echo ""
            echo "Usage: $0 [DEMO_TYPE]"
            echo ""
            echo "Demo Types:"
            echo "  install      - UV installation demo"
            echo "  venv         - Virtual environment creation demo"
            echo "  packages     - Package installation speed demo"
            echo "  setup        - Project setup demo"
            echo "  features     - UV features overview"
            echo "  performance  - Performance comparison"
            echo "  full         - Complete demo (default)"
            echo "  help         - Show this help message"
            echo ""
            ;;
        *)
            print_error "Unknown demo type: $demo_type"
            echo "Use '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
