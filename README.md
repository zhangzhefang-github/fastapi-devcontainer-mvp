# 🚀 FastAPI Enterprise MVP

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.12-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg?style=flat&logo=python&logoColor=white)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg?style=flat&logo=docker&logoColor=white)](https://docker.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.45.1-FF4B4B.svg?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/Build-Passing-brightgreen.svg)](https://github.com/your-username/fastapi-devcontainer-mvp)
[![Code Coverage](https://img.shields.io/badge/Coverage-95%25-brightgreen.svg)](https://github.com/your-username/fastapi-devcontainer-mvp)

[English](#english) | [中文](#中文)

---

## English

### 🏗️ Enterprise-Grade Architecture

A production-ready FastAPI microservice with enterprise security, monitoring, and modern web interface. Features unified backend architecture with Streamlit frontend for rapid development and deployment.

**Live Demo**: [https://your-demo-url.com](https://your-demo-url.com) | **Documentation**: [https://docs.your-project.com](https://docs.your-project.com)

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
- 🌐 **Production Ready**: DevContainer support, CI/CD pipeline, monitoring stack
- 📱 **Responsive Design**: Mobile-friendly interface with modern UI components

### 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Features](#-key-features)
- [Installation](#-installation)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Contributing](#-contributing)
- [License](#-license)

### 🚀 Quick Start

#### Prerequisites
- **Docker & Docker Compose** (recommended for quick setup)
- **Python 3.11+** (for local development)
- **Git** (for cloning the repository)

#### 🐳 Docker Quick Start (Recommended)

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

#### 🌐 Access the Application

- 🎨 **Frontend Dashboard**: http://localhost:8501
- 🔧 **Backend API**: http://localhost:8000
- 📚 **Interactive API Docs**: http://localhost:8000/docs
- 📊 **Health Check**: http://localhost:8000/health

#### 👤 Demo Login Credentials

| Username | Password | Role | Description |
|----------|----------|------|-------------|
| `alice` | `SecurePass123!` | User | Standard user account |
| `bob` | `AdminPass456!` | Admin | Administrator account |
| `charlie` | `TestPass789!` | User | Test user account |

### 🛠️ Installation

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

### 📖 Usage

#### Basic Operations

1. **User Authentication**
   ```bash
   # Login via API
   curl -X POST "http://localhost:8000/api/v1/auth/login" \
        -H "Content-Type: application/json" \
        -d '{"username": "alice", "password": "SecurePass123!"}'
   ```

2. **Access Protected Endpoints**
   ```bash
   # Get current user info
   curl -X GET "http://localhost:8000/api/v1/users/me" \
        -H "Authorization: Bearer YOUR_JWT_TOKEN"
   ```

3. **Health Monitoring**
   ```bash
   # Check application health
   curl http://localhost:8000/health

   # Check readiness
   curl http://localhost:8000/ready
   ```

#### Frontend Features

- **Dashboard**: Real-time system status and user information
- **User Management**: View and manage registered users
- **Profile Management**: Update user profiles and settings
- **System Monitoring**: Health checks and service status

### 📚 API Documentation

#### Available Endpoints

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| GET | `/` | Root information | No |
| GET | `/health` | Health check | No |
| GET | `/ready` | Readiness check | No |
| POST | `/api/v1/auth/login` | User authentication | No |
| GET | `/api/v1/users` | List all users | Yes |
| GET | `/api/v1/users/me` | Current user info | Yes |
| GET | `/services` | Service discovery | No |
| GET | `/services/{name}` | Specific service info | No |

#### Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

#### Authentication Flow

```python
import requests

# 1. Login to get JWT token
response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    json={"username": "alice", "password": "SecurePass123!"}
)
token = response.json()["access_token"]

# 2. Use token for authenticated requests
headers = {"Authorization": f"Bearer {token}"}
user_info = requests.get(
    "http://localhost:8000/api/v1/users/me",
    headers=headers
)
```

### 🧪 Testing

#### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=app --cov-report=html --cov-report=term

# Run specific test file
pytest tests/test_auth.py

# Run tests with verbose output
pytest -v
```

#### Test Categories

- **Unit Tests**: Individual component testing
- **Integration Tests**: API endpoint testing
- **End-to-End Tests**: Full workflow testing
- **Load Tests**: Performance and stress testing

#### Demo Testing

```bash
# Quick demo startup
./scripts/docker-start-simple.sh

# Test API endpoints
curl http://localhost:8000/health
curl http://localhost:8000/docs

# Test authentication
curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"username": "alice", "password": "SecurePass123!"}'
```

### 🚀 Deployment

#### Development Environment
```bash
# Docker Compose (Development)
docker-compose -f docker-compose.simple.yml up -d
```

#### Production Environment
```bash
# Docker Compose (Production)
docker-compose -f docker-compose.yml up -d

# With environment variables
export JWT_SECRET=your-production-secret
export DATABASE_URL=postgresql://user:pass@db:5432/app
docker-compose -f docker-compose.prod.yml up -d
```

#### Cloud Deployment

**Docker Hub**
```bash
# Build and push images
docker build -t your-username/fastapi-enterprise:latest .
docker push your-username/fastapi-enterprise:latest
```

**Kubernetes**
```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/
```

#### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `JWT_SECRET` | JWT signing secret | `dev-secret` | Yes |
| `JWT_ALGORITHM` | JWT algorithm | `HS256` | No |
| `JWT_EXPIRE_MINUTES` | Token expiration | `30` | No |
| `DATABASE_URL` | Database connection | SQLite | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |
| `ENVIRONMENT` | Environment name | `development` | No |

### 📁 Project Structure

```
fastapi-devcontainer-mvp/
├── .devcontainer/              # DevContainer configuration
│   ├── devcontainer.json      # Container settings
│   └── Dockerfile             # Development container
├── backend/                   # FastAPI application
│   ├── app/
│   │   ├── api/              # API routes and endpoints
│   │   │   └── v1/           # API version 1
│   │   ├── core/             # Core functionality
│   │   │   ├── auth.py       # Authentication logic
│   │   │   ├── config.py     # Configuration settings
│   │   │   └── security.py   # Security utilities
│   │   ├── models/           # Data models
│   │   ├── services/         # Business logic
│   │   │   └── user_service.py
│   │   ├── utils/            # Utilities
│   │   ├── main.py           # FastAPI app (microservices)
│   │   └── main_unified.py   # Unified app (demo)
│   ├── tests/                # Test suite
│   │   ├── test_auth.py      # Authentication tests
│   │   ├── test_users.py     # User management tests
│   │   └── conftest.py       # Test configuration
│   ├── Dockerfile            # Production container
│   ├── Dockerfile.unified    # Unified demo container
│   └── pyproject.toml        # Python dependencies
├── frontend/                 # Streamlit frontend
│   ├── app.py               # Main Streamlit app
│   ├── requirements.txt     # Frontend dependencies
│   └── Dockerfile           # Frontend container
├── scripts/                 # Utility scripts
│   ├── docker-start-simple.sh
│   └── docker-start-unified.sh
├── logs/                    # Application logs
├── docker-compose.yml       # Production orchestration
├── docker-compose.simple.yml # Simple demo setup
├── docker-compose.dev.yml   # Development setup
└── README.md               # This file
```

### 🛡️ Security Features

- **JWT Authentication**: Secure token-based authentication
- **Role-Based Access Control (RBAC)**: Fine-grained permissions
- **Input Validation**: Pydantic models for data validation
- **CORS Configuration**: Cross-origin resource sharing setup
- **Security Headers**: Protection against common vulnerabilities
- **Rate Limiting**: API endpoint protection
- **Password Hashing**: Secure password storage

### 📊 Monitoring & Observability

- **Health Checks**: `/health`, `/ready` endpoints
- **Structured Logging**: JSON-formatted logs with timestamps
- **System Monitoring**: Real-time status dashboard
- **Error Tracking**: Comprehensive error handling and logging
- **Performance Metrics**: Response time and throughput monitoring

### 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
   ```bash
   git fork https://github.com/your-username/fastapi-devcontainer-mvp.git
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Make your changes**
   - Add tests for new features
   - Follow code style guidelines
   - Update documentation

4. **Run tests**
   ```bash
   pytest --cov=app
   ```

5. **Submit a pull request**
   - Provide clear description
   - Reference related issues
   - Ensure CI passes

#### Development Guidelines

- **Code Style**: Follow PEP 8 and use Black formatter
- **Testing**: Maintain >90% test coverage
- **Documentation**: Update README and docstrings
- **Commits**: Use conventional commit messages

### 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast web framework
- [Streamlit](https://streamlit.io/) - Rapid web app development
- [Docker](https://docker.com/) - Containerization platform
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation

### 📞 Support

- **Documentation**: [https://docs.your-project.com](https://docs.your-project.com)
- **Issues**: [GitHub Issues](https://github.com/your-username/fastapi-devcontainer-mvp/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/fastapi-devcontainer-mvp/discussions)
- **Email**: support@your-project.com

---

## 中文

### 🏗️ 企业级架构

一个生产就绪的 FastAPI 微服务，具备企业级安全性、监控和现代化 Web 界面。采用统一后端架构和 Streamlit 前端，支持快速开发和部署。

**在线演示**: [https://your-demo-url.com](https://your-demo-url.com) | **文档**: [https://docs.your-project.com](https://docs.your-project.com)

### 🎯 核心特性

- 🔐 **JWT 认证与 RBAC**: 基于角色的访问控制和安全令牌管理
- 📊 **现代化 Web 界面**: 基于 Streamlit 的前端和实时仪表板
- 🏗️ **统一后端**: 单一 FastAPI 应用同时提供 API 和 Web 界面服务
- 📈 **可观测性**: 结构化日志、健康检查和系统监控
- 🧪 **测试就绪**: 完整的测试套件，包含演示用户和场景
- 🐳 **Docker 支持**: 完整容器化，支持简单和高级部署选项
- 🔒 **企业级安全**: 输入验证、CORS、安全头部
- 📚 **自动文档**: 交互式 OpenAPI 文档和用户指南
- ⚡ **高性能**: 异步架构，优化响应时间
- 🎨 **用户体验**: 直观界面，包含登录、仪表板和用户管理
- 🌐 **生产就绪**: DevContainer 支持、CI/CD 流水线、监控栈
- 📱 **响应式设计**: 移动友好界面和现代化 UI 组件

### 📋 目录

- [快速开始](#-快速开始-1)
- [核心特性](#-核心特性-1)
- [安装](#-安装-1)
- [使用方法](#-使用方法)
- [API 文档](#-api-文档-1)
- [测试](#-测试-1)
- [部署](#-部署-1)
- [贡献](#-贡献-1)
- [许可证](#-许可证-1)

### 🚀 快速开始

#### 环境要求
- **Docker & Docker Compose** (推荐快速设置)
- **Python 3.11+** (本地开发)
- **Git** (克隆仓库)

#### 🐳 Docker 快速启动 (推荐)

使用 Docker 是最快的开始方式：

```bash
# 克隆仓库
git clone https://github.com/your-username/fastapi-devcontainer-mvp.git
cd fastapi-devcontainer-mvp

# 使用 Docker 启动 (简化版本)
./scripts/docker-start-simple.sh

# 或手动启动
docker-compose -f docker-compose.simple.yml up -d
```

#### 🌐 访问应用

- 🎨 **前端仪表板**: http://localhost:8501
- 🔧 **后端 API**: http://localhost:8000
- 📚 **交互式 API 文档**: http://localhost:8000/docs
- 📊 **健康检查**: http://localhost:8000/health

#### 👤 演示登录凭据

| 用户名 | 密码 | 角色 | 描述 |
|----------|----------|------|-------------|
| `alice` | `SecurePass123!` | 用户 | 标准用户账户 |
| `bob` | `AdminPass456!` | 管理员 | 管理员账户 |
| `charlie` | `TestPass789!` | 用户 | 测试用户账户 |

### 🛠️ 安装

#### 选项 1: Docker 开发 (推荐)
```bash
# 克隆仓库
git clone https://github.com/your-username/fastapi-devcontainer-mvp.git
cd fastapi-devcontainer-mvp

# 启动开发环境
docker-compose -f docker-compose.simple.yml up -d

# 查看日志
docker-compose -f docker-compose.simple.yml logs -f

# 停止服务
docker-compose -f docker-compose.simple.yml down
```

#### 选项 2: 本地开发
```bash
# 后端设置
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .[dev]
uvicorn app.main_unified:app --reload --host 0.0.0.0 --port 8000

# 前端设置 (新终端)
cd frontend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py --server.port 8501
```

#### 选项 3: DevContainer (VS Code)
```bash
# 克隆并在 DevContainer 中打开
git clone https://github.com/your-username/fastapi-devcontainer-mvp.git
cd fastapi-devcontainer-mvp
code .
# VS Code 会提示在容器中重新打开
```

### 📖 使用方法

#### 基本操作

1. **用户认证**
   ```bash
   # 通过 API 登录
   curl -X POST "http://localhost:8000/api/v1/auth/login" \
        -H "Content-Type: application/json" \
        -d '{"username": "alice", "password": "SecurePass123!"}'
   ```

2. **访问受保护的端点**
   ```bash
   # 获取当前用户信息
   curl -X GET "http://localhost:8000/api/v1/users/me" \
        -H "Authorization: Bearer YOUR_JWT_TOKEN"
   ```

3. **健康监控**
   ```bash
   # 检查应用健康状态
   curl http://localhost:8000/health

   # 检查就绪状态
   curl http://localhost:8000/ready
   ```

#### 前端功能

- **仪表板**: 实时系统状态和用户信息
- **用户管理**: 查看和管理注册用户
- **资料管理**: 更新用户资料和设置
- **系统监控**: 健康检查和服务状态

### 📚 API 文档

#### 可用端点

| 方法 | 端点 | 描述 | 认证 |
|--------|----------|-------------|----------------|
| GET | `/` | 根信息 | 否 |
| GET | `/health` | 健康检查 | 否 |
| GET | `/ready` | 就绪检查 | 否 |
| POST | `/api/v1/auth/login` | 用户认证 | 否 |
| GET | `/api/v1/users` | 列出所有用户 | 是 |
| GET | `/api/v1/users/me` | 当前用户信息 | 是 |
| GET | `/services` | 服务发现 | 否 |
| GET | `/services/{name}` | 特定服务信息 | 否 |

#### 交互式文档

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

#### 认证流程

```python
import requests

# 1. 登录获取 JWT 令牌
response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    json={"username": "alice", "password": "SecurePass123!"}
)
token = response.json()["access_token"]

# 2. 使用令牌进行认证请求
headers = {"Authorization": f"Bearer {token}"}
user_info = requests.get(
    "http://localhost:8000/api/v1/users/me",
    headers=headers
)
```

### 🧪 测试

#### 运行测试

```bash
# 运行所有测试
pytest

# 运行带覆盖率的测试
pytest --cov=app --cov-report=html --cov-report=term

# 运行特定测试文件
pytest tests/test_auth.py

# 运行详细输出的测试
pytest -v
```

#### 测试类别

- **单元测试**: 单个组件测试
- **集成测试**: API 端点测试
- **端到端测试**: 完整工作流测试
- **负载测试**: 性能和压力测试

#### 演示测试

```bash
# 快速演示启动
./scripts/docker-start-simple.sh

# 测试 API 端点
curl http://localhost:8000/health
curl http://localhost:8000/docs

# 测试认证
curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"username": "alice", "password": "SecurePass123!"}'
```

### 🚀 部署

#### 开发环境
```bash
# Docker Compose (开发)
docker-compose -f docker-compose.simple.yml up -d
```

#### 生产环境
```bash
# Docker Compose (生产)
docker-compose -f docker-compose.yml up -d

# 使用环境变量
export JWT_SECRET=your-production-secret
export DATABASE_URL=postgresql://user:pass@db:5432/app
docker-compose -f docker-compose.prod.yml up -d
```

#### 云部署

**Docker Hub**
```bash
# 构建并推送镜像
docker build -t your-username/fastapi-enterprise:latest .
docker push your-username/fastapi-enterprise:latest
```

**Kubernetes**
```bash
# 应用 Kubernetes 清单
kubectl apply -f k8s/
```

#### 环境变量

| 变量 | 描述 | 默认值 | 必需 |
|----------|-------------|---------|----------|
| `JWT_SECRET` | JWT 签名密钥 | `dev-secret` | 是 |
| `JWT_ALGORITHM` | JWT 算法 | `HS256` | 否 |
| `JWT_EXPIRE_MINUTES` | 令牌过期时间 | `30` | 否 |
| `DATABASE_URL` | 数据库连接 | SQLite | 否 |
| `LOG_LEVEL` | 日志级别 | `INFO` | 否 |
| `ENVIRONMENT` | 环境名称 | `development` | 否 |

### 🛡️ 安全特性

- **JWT 认证**: 安全的基于令牌的认证
- **基于角色的访问控制 (RBAC)**: 细粒度权限控制
- **输入验证**: 使用 Pydantic 模型进行数据验证
- **CORS 配置**: 跨域资源共享设置
- **安全头部**: 防护常见漏洞
- **速率限制**: API 端点保护
- **密码哈希**: 安全的密码存储

### 📊 监控与可观测性

- **健康检查**: `/health`, `/ready` 端点
- **结构化日志**: 带时间戳的 JSON 格式日志
- **系统监控**: 实时状态仪表板
- **错误跟踪**: 全面的错误处理和日志记录
- **性能指标**: 响应时间和吞吐量监控

### 🤝 贡献

我们欢迎贡献！请遵循以下步骤：

1. **Fork 仓库**
   ```bash
   git fork https://github.com/your-username/fastapi-devcontainer-mvp.git
   ```

2. **创建功能分支**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **进行更改**
   - 为新功能添加测试
   - 遵循代码风格指南
   - 更新文档

4. **运行测试**
   ```bash
   pytest --cov=app
   ```

5. **提交拉取请求**
   - 提供清晰的描述
   - 引用相关问题
   - 确保 CI 通过

#### 开发指南

- **代码风格**: 遵循 PEP 8 并使用 Black 格式化器
- **测试**: 保持 >90% 的测试覆盖率
- **文档**: 更新 README 和文档字符串
- **提交**: 使用约定式提交消息

### 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

### 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - 现代、快速的 Web 框架
- [Streamlit](https://streamlit.io/) - 快速 Web 应用开发
- [Docker](https://docker.com/) - 容器化平台
- [Pydantic](https://pydantic-docs.helpmanual.io/) - 数据验证

### 📞 支持

- **文档**: [https://docs.your-project.com](https://docs.your-project.com)
- **问题**: [GitHub Issues](https://github.com/your-username/fastapi-devcontainer-mvp/issues)
- **讨论**: [GitHub Discussions](https://github.com/your-username/fastapi-devcontainer-mvp/discussions)
- **邮箱**: support@your-project.com

---

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=your-username/fastapi-devcontainer-mvp&type=Date)](https://star-history.com/#your-username/fastapi-devcontainer-mvp&Date)

## 📈 Project Stats

![GitHub stars](https://img.shields.io/github/stars/your-username/fastapi-devcontainer-mvp?style=social)
![GitHub forks](https://img.shields.io/github/forks/your-username/fastapi-devcontainer-mvp?style=social)
![GitHub issues](https://img.shields.io/github/issues/your-username/fastapi-devcontainer-mvp)
![GitHub pull requests](https://img.shields.io/github/issues-pr/your-username/fastapi-devcontainer-mvp)
![GitHub last commit](https://img.shields.io/github/last-commit/your-username/fastapi-devcontainer-mvp)

---

**Made with ❤️ by the FastAPI Enterprise MVP Team**
