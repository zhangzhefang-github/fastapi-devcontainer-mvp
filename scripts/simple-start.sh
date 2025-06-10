#!/bin/bash

# FastAPI Enterprise MVP - Simple Start Script
# This script starts both backend and frontend services

set -e

echo "🚀 FastAPI Enterprise MVP - Starting Services"
echo "============================================="

# Create logs directory
mkdir -p logs

# Function to check if port is in use
check_port() {
    local port=$1
    if netstat -tuln 2>/dev/null | grep ":$port " >/dev/null; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Start backend
echo "▶️  Starting FastAPI backend..."
if check_port 8000; then
    echo "⚠️  Port 8000 is already in use. Skipping backend startup."
else
    cd backend
    export PYTHONPATH=/home/zzf/fastapi-devcontainer-mvp/backend
    nohup .venv/bin/python -m uvicorn app.main_simple:app --host 0.0.0.0 --port 8000 --reload > ../logs/backend.log 2>&1 &
    echo $! > ../logs/backend.pid
    echo "✅ Backend started (PID: $(cat ../logs/backend.pid))"
    cd ..
fi

# Wait a moment
sleep 3

# Start frontend
echo "▶️  Starting Streamlit frontend..."
if check_port 8501; then
    echo "⚠️  Port 8501 is already in use. Skipping frontend startup."
else
    cd frontend
    export PYTHONPATH=/home/zzf/fastapi-devcontainer-mvp/frontend/.venv/lib/python3.13/site-packages:$PYTHONPATH
    nohup .venv/bin/python -m streamlit run app.py --server.port 8501 --server.address 0.0.0.0 > ../logs/frontend.log 2>&1 &
    echo $! > ../logs/frontend.pid
    echo "✅ Frontend started (PID: $(cat ../logs/frontend.pid))"
    cd ..
fi

# Wait for services to be ready
echo ""
echo "⏳ Waiting for services to be ready..."
sleep 5

# Check services
echo ""
echo "🌐 Service Status:"
echo "=================="

# Check backend
if curl -s http://localhost:8000/health >/dev/null 2>&1; then
    echo "✅ Backend API: http://localhost:8000"
    echo "   📚 API Docs: http://localhost:8000/docs"
else
    echo "❌ Backend API: Not responding"
fi

# Check frontend
if curl -s http://localhost:8501/_stcore/health >/dev/null 2>&1; then
    echo "✅ Frontend App: http://localhost:8501"
else
    echo "❌ Frontend App: Not responding"
fi

echo ""
echo "📋 Management Commands:"
echo "======================"
echo "View logs: tail -f logs/backend.log logs/frontend.log"
echo "Stop services: ./scripts/stop-all.sh"
echo ""
echo "🎉 Services are running! Open http://localhost:8501 in your browser."
