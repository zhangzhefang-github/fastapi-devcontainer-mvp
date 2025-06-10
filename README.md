# 🚀 FastAPI Enterprise MVP

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.12-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg?style=flat&logo=python&logoColor=white)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg?style=flat&logo=docker&logoColor=white)](https://docker.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.45.1-FF4B4B.svg?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

[English](#english) | [中文](#中文)

---

## 🏗️ Enterprise-Grade Architecture

A production-ready FastAPI microservice with enterprise security, monitoring, and modern web interface. Features unified backend architecture with Streamlit frontend for rapid development and deployment.

### 🎯 Key Features

- 🔐 **JWT Authentication & RBAC**: Role-based access control with secure token management
- 📊 **Modern Web Interface**: Streamlit-powered frontend with real-time dashboard
- 🏗️ **Unified Backend**: Single FastAPI application serving both API and web interface
- 📈 **Observability**: Structured logging, health checks, and system monitoring
- 🧪 **Testing Ready**: Comprehensive test suite with demo users and scenarios
- 🐳 **Docker Support**: Full containerization with simple and advanced deployment options
- 🔒 **Enterprise Security**: Input validation, CORS, security headers
- 📚 **Auto Documentation**: Interactive OpenAPI docs and user guides
- ⚡ **High Performance**: Async/await architecture with optimized response times
- 🎨 **User Experience**: Intuitive interface with login, dashboard, and user management

## 🚀 Quick Start

### Prerequisites
- **Docker & Docker Compose** (for containerized development)
- **Python 3.11+** (for local development)
- **Git** (for cloning the repository)

### 🐳 Docker Quick Start (Recommended)

The fastest way to get started is using Docker:

```bash
# Clone the repository
git clone https://github.com/your-username/fastapi-devcontainer-mvp.git
cd fastapi-devcontainer-mvp

# Start with Docker (simple version)
./scripts/docker-start-simple.sh

# Or manually
docker-compose -f docker-compose.simple.yml up -d
```

**Access the application:**
- 🎨 **Frontend**: http://localhost:8501
- 🔧 **Backend API**: http://localhost:8000
- 📚 **API Docs**: http://localhost:8000/docs

**Demo Login Credentials:**
- Username: `alice` | Password: `SecurePass123!`
- Username: `bob` | Password: `AdminPass456!`

### 🛠️ Development Setup

#### Option 1: Docker Development (Recommended)
```bash
# Clone repository
git clone https://github.com/your-username/fastapi-devcontainer-mvp.git
cd fastapi-devcontainer-mvp

# Start development environment
docker-compose -f docker-compose.simple.yml up -d

# View logs
docker-compose -f docker-compose.simple.yml logs -f

# Stop services
docker-compose -f docker-compose.simple.yml down
```

#### Option 2: Local Development
```bash
# Backend setup
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .[dev]
uvicorn app.main_unified:app --reload --host 0.0.0.0 --port 8000

# Frontend setup (new terminal)
cd frontend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py --server.port 8501
```

#### Option 3: DevContainer (VS Code)
```bash
# Clone and open in DevContainer
git clone https://github.com/your-username/fastapi-devcontainer-mvp.git
cd fastapi-devcontainer-mvp
code .
# VS Code will prompt to reopen in container
```

#### Option 4: Local Development with uv (Alternative)
```bash
# Install uv (if not already installed)
make install-uv
# or: pip install uv

# Backend setup with uv
cd backend
uv venv                           # Create virtual environment
source .venv/bin/activate         # Activate (macOS/Linux)
# .venv\Scripts\activate          # Activate (Windows)
uv pip install -e .[dev]         # Install dependencies
uvicorn app.main:app --reload     # Start backend

# Frontend setup (new terminal)
cd frontend
uv venv                           # Create virtual environment
source .venv/bin/activate         # Activate (macOS/Linux)
uv pip install -r requirements.txt
streamlit run app.py
```

#### Option 5: Traditional pip/venv
```bash
# Backend setup
cd backend
python -m venv .venv
source .venv/bin/activate         # macOS/Linux
# .venv\Scripts\activate          # Windows
pip install -e .[dev]
uvicorn app.main:app --reload

# Frontend setup (new terminal)
cd frontend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

### ⚡ Why uv?

**uv** is an extremely fast Python package installer and resolver, written in Rust:

- **🚀 10-100x faster** than pip for most operations
- **🔒 Better dependency resolution** with conflict detection
- **💾 Efficient caching** reduces redundant downloads
- **🔄 Drop-in replacement** for pip in most cases

| Operation | pip | uv | Speedup |
|-----------|-----|----|---------|
| Install FastAPI + deps | 45s | 3s | **15x faster** |
| Create virtual env | 8s | 0.1s | **80x faster** |
| Resolve dependencies | 12s | 0.5s | **24x faster** |

## 🧪 完整测试指南

### 快速演示启动

```bash
# 一键启动演示环境（包含前后端）
./scripts/start-demo.sh

# 访问演示应用
# 前端: http://localhost:8501
# 后端: http://localhost:8000
```

### 演示用户账户

| 用户名 | 密码 | 角色 |
|--------|------|------|
| `alice` | `SecurePass123!` | 普通用户 |
| `bob` | `AdminPass456!` | 管理员 |
| `charlie` | `TestPass789!` | 测试用户 |

### 测试功能

- **🔑 用户登录/注册**: 完整的用户认证流程
- **📊 仪表板**: 个人资料、用户管理、系统状态
- **🔧 API测试**: 直接在前端测试后端API
- **👥 用户管理**: 查看和管理注册用户

📚 **详细测试指南**: [TESTING_GUIDE.md](TESTING_GUIDE.md)

## 🔐 API测试示例

```bash
# 健康检查
curl http://localhost:8000/health

# API文档
open http://localhost:8000/docs

# 测试脚本
./scripts/test-complete.sh
```

### 🧪 Testing

```bash
# Run tests with coverage
pytest --cov=app --cov-report=html

# Load testing
locust -f tests/load_test.py --host=http://localhost:8000
```

## 📁 Project Structure

```
fastapi-devcontainer-mvp/
├── .devcontainer/          # DevContainer configuration
├── backend/                # FastAPI application
│   ├── app/
│   │   ├── api/           # API routes
│   │   ├── core/          # Core functionality
│   │   ├── models/        # Data models
│   │   ├── services/      # Business logic
│   │   └── utils/         # Utilities
│   ├── tests/             # Test suite
│   └── pyproject.toml     # Python dependencies
├── frontend/              # Streamlit frontend
├── nginx/                 # Reverse proxy
├── monitoring/            # Observability stack
└── docker-compose.yml     # Multi-service orchestration
```

## 🔧 Configuration

Environment variables in `.env`:

```env
# Security
JWT_SECRET=your-super-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30

# Database
DATABASE_URL=postgresql://user:pass@db:5432/app

# Monitoring
LOG_LEVEL=INFO
ENABLE_METRICS=true
```

## 📊 Monitoring & Observability

- **Health Checks**: `/health`, `/ready`
- **Metrics**: Prometheus metrics at `/metrics`
- **Logging**: Structured JSON logging
- **Tracing**: OpenTelemetry integration

## 🛡️ Security Features

- JWT token authentication
- Role-based access control (RBAC)
- Input validation with Pydantic
- Rate limiting
- CORS configuration
- Security headers

## 🚀 Deployment

### Local Development
```bash
docker-compose up -d
```

### Production
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 📈 Performance

- Async/await throughout
- Connection pooling
- Response caching
- Load balancing ready

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit pull request

## 📄 License

MIT License - see LICENSE file for details.
