#!/bin/bash

# FastAPI Enterprise MVP - Unified Environment Setup
# This script creates a single virtual environment for both frontend and backend

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

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Main setup function
main() {
    print_header "FastAPI Enterprise MVP - Unified Environment Setup"
    echo ""
    
    # Check if uv is installed
    if ! command_exists uv; then
        print_step "Installing uv..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.cargo/bin:$PATH"
    fi
    
    # Create unified virtual environment in project root
    print_step "Creating unified virtual environment..."
    if [ -d ".venv" ]; then
        print_warning "Virtual environment already exists. Removing..."
        rm -rf .venv
    fi
    
    uv venv .venv
    source .venv/bin/activate
    
    # Install backend dependencies
    print_step "Installing backend dependencies..."
    cd backend
    uv pip install -e .[dev]
    cd ..
    
    # Install frontend dependencies
    print_step "Installing frontend dependencies..."
    cd frontend
    uv pip install -r requirements.txt
    cd ..
    
    # Create activation script
    print_step "Creating activation script..."
    cat > activate.sh << 'EOF'
#!/bin/bash
# FastAPI Enterprise MVP - Environment Activation Script

# Activate virtual environment
source .venv/bin/activate

# Set Python paths
export PYTHONPATH="$PWD/backend:$PWD/frontend:$PYTHONPATH"

echo "🚀 FastAPI Enterprise MVP environment activated!"
echo ""
echo "Available commands:"
echo "  start-backend    - Start FastAPI backend"
echo "  start-frontend   - Start Streamlit frontend"
echo "  start-both       - Start both services"
echo ""

# Define helper functions
start-backend() {
    echo "🔧 Starting FastAPI backend..."
    cd backend
    uvicorn app.main_simple:app --host 0.0.0.0 --port 8000 --reload
}

start-frontend() {
    echo "📱 Starting Streamlit frontend..."
    cd frontend
    streamlit run app.py --server.port 8501 --server.address 0.0.0.0
}

start-both() {
    echo "🚀 Starting both services..."
    echo "Backend will start in background, frontend in foreground"
    echo "Press Ctrl+C to stop both services"
    
    # Start backend in background
    cd backend
    uvicorn app.main_simple:app --host 0.0.0.0 --port 8000 --reload &
    BACKEND_PID=$!
    cd ..
    
    # Wait a moment for backend to start
    sleep 3
    
    # Start frontend in foreground
    cd frontend
    streamlit run app.py --server.port 8501 --server.address 0.0.0.0 &
    FRONTEND_PID=$!
    cd ..
    
    # Function to cleanup on exit
    cleanup() {
        echo ""
        echo "🛑 Stopping services..."
        kill $BACKEND_PID 2>/dev/null || true
        kill $FRONTEND_PID 2>/dev/null || true
        echo "✅ Services stopped"
        exit 0
    }
    
    # Set trap for cleanup
    trap cleanup SIGINT SIGTERM
    
    echo ""
    echo "🌐 Services starting..."
    echo "Backend: http://localhost:8000"
    echo "Frontend: http://localhost:8501"
    echo ""
    echo "Press Ctrl+C to stop both services"
    
    # Wait for both processes
    wait $BACKEND_PID $FRONTEND_PID
}

# Export functions
export -f start-backend
export -f start-frontend
export -f start-both
EOF
    
    chmod +x activate.sh
    
    # Create requirements.txt for unified environment
    print_step "Creating unified requirements.txt..."
    cat > requirements-unified.txt << 'EOF'
# Backend dependencies
fastapi>=0.104.1
uvicorn[standard]>=0.24.0
pydantic>=2.5.0
pydantic-settings>=2.1.0
python-jose[cryptography]>=3.3.0
python-multipart>=0.0.6
passlib[bcrypt]>=1.7.4
structlog>=23.2.0
prometheus-client>=0.19.0
email-validator>=2.1.0

# Frontend dependencies
streamlit>=1.28.0
requests>=2.31.0
pandas>=2.1.0
plotly>=5.17.0
python-dotenv>=1.0.0

# Development dependencies
pytest>=7.4.3
pytest-asyncio>=0.21.1
pytest-cov>=4.1.0
black>=23.11.0
isort>=5.12.0
ruff>=0.1.6
mypy>=1.7.1
EOF
    
    print_success "Unified environment setup complete!"
    echo ""
    echo "🎯 Usage:"
    echo "  source activate.sh           # Activate environment"
    echo "  start-backend               # Start backend only"
    echo "  start-frontend              # Start frontend only"
    echo "  start-both                  # Start both services"
    echo ""
    echo "🔧 Manual usage:"
    echo "  source .venv/bin/activate   # Activate virtual environment"
    echo "  cd backend && uvicorn app.main_simple:app --reload"
    echo "  cd frontend && streamlit run app.py"
    echo ""
}

main "$@"
