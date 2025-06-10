#!/bin/bash

# Docker启动脚本 - 简化版本
# FastAPI Enterprise MVP - Simple Docker Startup

set -e

echo "🐳 Starting FastAPI Enterprise MVP with Docker (Simple Version)..."

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# 检查docker-compose是否可用
if ! command -v docker-compose > /dev/null 2>&1; then
    echo "❌ docker-compose is not installed. Please install docker-compose first."
    exit 1
fi

# 进入项目根目录
cd "$(dirname "$0")/.."

echo "📁 Current directory: $(pwd)"

# 停止现有容器（如果有）
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.simple.yml down --remove-orphans

# 启动服务
echo "🚀 Starting services..."
docker-compose -f docker-compose.simple.yml up -d

# 等待服务启动
echo "⏳ Waiting for services to start..."
sleep 15

# 检查服务状态
echo "🔍 Checking service status..."
docker-compose -f docker-compose.simple.yml ps

# 健康检查
echo "🏥 Performing health checks..."

# 检查后端
echo "🔧 Checking backend health..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null; then
        echo "✅ Backend is healthy!"
        break
    fi
    echo "⏳ Waiting for backend... ($i/30)"
    sleep 2
done

# 检查前端
echo "🎨 Checking frontend health..."
for i in {1..30}; do
    if curl -s http://localhost:8501/_stcore/health > /dev/null; then
        echo "✅ Frontend is healthy!"
        break
    fi
    echo "⏳ Waiting for frontend... ($i/30)"
    sleep 2
done

echo ""
echo "🎉 FastAPI Enterprise MVP is now running!"
echo ""
echo "📋 Available services:"
echo "   🔧 Backend API:  http://localhost:8000"
echo "   📚 API Docs:     http://localhost:8000/docs"
echo "   🎨 Frontend:     http://localhost:8501"
echo ""
echo "🔍 To view logs:"
echo "   docker-compose -f docker-compose.simple.yml logs -f"
echo ""
echo "🛑 To stop services:"
echo "   docker-compose -f docker-compose.simple.yml down"
echo ""
echo "🎯 Test login credentials:"
echo "   Username: alice | Password: SecurePass123!"
echo "   Username: bob   | Password: AdminPass456!"
echo ""
