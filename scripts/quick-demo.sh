#!/bin/bash

# FastAPI Enterprise MVP - Quick UV Demo
# A simplified demo showing uv vs pip performance

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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Main demo
main() {
    print_header "FastAPI Enterprise MVP - UV Quick Demo"
    echo ""
    
    # Check if uv is installed
    if ! command_exists uv; then
        print_step "Installing uv..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.cargo/bin:$PATH"
        
        if command_exists uv; then
            print_success "uv installed successfully!"
        else
            echo "❌ Failed to install uv. Please install manually."
            exit 1
        fi
    else
        print_success "uv is already installed!"
    fi
    
    echo ""
    print_step "UV Version:"
    uv --version
    echo ""
    
    # Performance comparison
    print_header "Performance Comparison"
    echo ""
    echo "📊 UV vs PIP Speed Comparison:"
    echo ""
    echo "| Operation              | pip    | uv     | Speedup    |"
    echo "|------------------------|--------|--------|------------|"
    echo "| Virtual env creation   | ~8s    | ~0.1s  | 80x faster |"
    echo "| Install FastAPI + deps | ~45s   | ~3s    | 15x faster |"
    echo "| Dependency resolution  | ~12s   | ~0.5s  | 24x faster |"
    echo "| Package cache lookup   | ~2s    | ~0.1s  | 20x faster |"
    echo ""
    
    # Quick venv demo
    print_header "Virtual Environment Speed Test"
    echo ""
    
    # Clean up any existing test environments
    rm -rf test_demo_env
    
    print_step "Creating virtual environment with uv..."
    time uv venv test_demo_env
    print_success "Virtual environment created!"
    echo ""
    
    print_step "Activating and installing a package..."
    source test_demo_env/bin/activate
    time uv pip install requests --quiet
    print_success "Package installed!"
    
    print_step "Installed packages:"
    uv pip list
    
    deactivate
    rm -rf test_demo_env
    echo ""
    
    # Project setup demo
    print_header "FastAPI Enterprise MVP Setup"
    echo ""
    
    print_info "To setup this project with uv, run:"
    echo ""
    echo "  ./scripts/start.sh local    # Quick setup"
    echo "  make setup-uv              # Using Makefile"
    echo ""
    echo "Manual setup:"
    echo "  cd backend"
    echo "  uv venv"
    echo "  source .venv/bin/activate"
    echo "  uv pip install -e .[dev]"
    echo "  uvicorn app.main:app --reload"
    echo ""
    
    print_header "Why Choose UV?"
    echo ""
    echo "✅ 10-100x faster than pip"
    echo "✅ Better dependency resolution"
    echo "✅ Efficient caching"
    echo "✅ Drop-in replacement for pip"
    echo "✅ Written in Rust for performance"
    echo "✅ Active development by Astral"
    echo ""
    
    print_header "Next Steps"
    echo ""
    echo "🚀 Ready to start? Try these commands:"
    echo ""
    echo "  ./scripts/start.sh local     # Setup local development"
    echo "  ./scripts/demo-uv.sh full    # Complete demo"
    echo "  make setup-uv               # Alternative setup"
    echo ""
    echo "📚 Learn more:"
    echo "  - UV Setup Guide: ./UV_SETUP.md"
    echo "  - Project README: ./README.md"
    echo "  - UV Documentation: https://docs.astral.sh/uv/"
    echo ""
    
    print_success "Demo complete! Happy coding with uv! 🎉"
}

main "$@"
