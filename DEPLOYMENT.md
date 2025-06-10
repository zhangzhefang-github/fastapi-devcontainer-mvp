# 🚀 FastAPI Enterprise MVP - Deployment Guide

## 📋 Overview

This guide covers deployment strategies for the FastAPI Enterprise MVP application across different environments.

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Nginx       │    │   Streamlit     │    │    FastAPI      │
│  (Reverse Proxy)│◄──►│   (Frontend)    │◄──►│   (Backend)     │
│     Port 80     │    │   Port 8501     │    │   Port 8000     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │     Redis       │    │   Prometheus    │
│   Port 5432     │    │   Port 6379     │    │   Port 9090     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🛠️ Environment Setup

### Development Environment

```bash
# Quick start
./scripts/start.sh dev

# Or manually
make dev

# Or with Docker Compose
docker-compose -f docker-compose.dev.yml up -d
```

**Features:**
- Hot reload for both backend and frontend
- Debug mode enabled
- Development tools included
- Detailed logging
- Auto-restart on code changes

### Production Environment

```bash
# Quick start
./scripts/start.sh prod

# Or manually
make prod

# Or with Docker Compose
docker-compose up -d
```

**Features:**
- Optimized builds
- Security hardening
- Health checks
- Resource limits
- Production logging

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Security
JWT_SECRET=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30

# Database
DATABASE_URL=postgresql://postgres:password@db:5432/fastapi_app
REDIS_URL=redis://redis:6379/0

# Application
APP_NAME=FastAPI Enterprise MVP
DEBUG=false
LOG_LEVEL=INFO
CORS_ORIGINS=["https://yourdomain.com"]

# Monitoring
ENABLE_METRICS=true
SENTRY_DSN=your-sentry-dsn

# Passwords
POSTGRES_PASSWORD=secure-postgres-password
GRAFANA_PASSWORD=secure-grafana-password
```

### SSL/TLS Configuration

For production, enable HTTPS in `nginx/nginx.conf`:

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    # Include location blocks...
}
```

## ☁️ Cloud Deployment

### AWS ECS Deployment

1. **Build and push images:**
```bash
# Build images
docker build -t your-registry/fastapi-backend:latest ./backend
docker build -t your-registry/streamlit-frontend:latest ./frontend

# Push to ECR
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin your-account.dkr.ecr.us-west-2.amazonaws.com
docker push your-registry/fastapi-backend:latest
docker push your-registry/streamlit-frontend:latest
```

2. **Create ECS task definition:**
```json
{
  "family": "fastapi-enterprise-mvp",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "your-registry/fastapi-backend:latest",
      "portMappings": [{"containerPort": 8000}],
      "environment": [
        {"name": "DATABASE_URL", "value": "postgresql://..."},
        {"name": "REDIS_URL", "value": "redis://..."}
      ]
    }
  ]
}
```

### Google Cloud Run

```bash
# Build and deploy backend
gcloud builds submit --tag gcr.io/PROJECT-ID/fastapi-backend ./backend
gcloud run deploy fastapi-backend --image gcr.io/PROJECT-ID/fastapi-backend --platform managed

# Build and deploy frontend
gcloud builds submit --tag gcr.io/PROJECT-ID/streamlit-frontend ./frontend
gcloud run deploy streamlit-frontend --image gcr.io/PROJECT-ID/streamlit-frontend --platform managed
```

### Azure Container Instances

```bash
# Create resource group
az group create --name fastapi-rg --location eastus

# Deploy backend
az container create \
  --resource-group fastapi-rg \
  --name fastapi-backend \
  --image your-registry/fastapi-backend:latest \
  --ports 8000 \
  --environment-variables DATABASE_URL=postgresql://...
```

## 🐳 Kubernetes Deployment

### Helm Chart Structure

```
helm/
├── Chart.yaml
├── values.yaml
└── templates/
    ├── backend-deployment.yaml
    ├── frontend-deployment.yaml
    ├── postgres-deployment.yaml
    ├── redis-deployment.yaml
    ├── nginx-configmap.yaml
    └── ingress.yaml
```

### Deploy with Helm

```bash
# Install
helm install fastapi-mvp ./helm

# Upgrade
helm upgrade fastapi-mvp ./helm

# Uninstall
helm uninstall fastapi-mvp
```

## 📊 Monitoring & Observability

### Prometheus Metrics

The application exposes metrics at `/metrics`:

- `http_requests_total` - Total HTTP requests
- `http_request_duration_seconds` - Request duration
- `active_users` - Currently active users
- `database_connections` - Database connection pool

### Grafana Dashboards

Pre-configured dashboards for:
- Application performance
- Database metrics
- System resources
- User activity

### Logging

Structured JSON logging with:
- Request/response logging
- Security event logging
- Business event logging
- Error tracking with Sentry

## 🔒 Security Considerations

### Production Checklist

- [ ] Change default passwords
- [ ] Use strong JWT secrets
- [ ] Enable HTTPS/TLS
- [ ] Configure CORS properly
- [ ] Set up rate limiting
- [ ] Enable security headers
- [ ] Use non-root containers
- [ ] Scan images for vulnerabilities
- [ ] Set up network policies
- [ ] Configure secrets management

### Security Headers

```nginx
add_header X-Frame-Options DENY always;
add_header X-Content-Type-Options nosniff always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Strict-Transport-Security "max-age=63072000" always;
```

## 🔄 CI/CD Pipeline

### GitHub Actions Example

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          docker-compose -f docker-compose.dev.yml up -d
          docker-compose -f docker-compose.dev.yml exec -T backend pytest

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: |
          # Your deployment commands here
```

## 📈 Scaling Strategies

### Horizontal Scaling

- Use load balancers (Nginx, HAProxy, AWS ALB)
- Scale backend instances based on CPU/memory
- Implement database read replicas
- Use Redis cluster for session storage

### Vertical Scaling

- Increase container resources
- Optimize database queries
- Implement caching strategies
- Use connection pooling

## 🔧 Maintenance

### Database Migrations

```bash
# Create migration
make db-migrate msg="Add new table"

# Apply migrations
make db-upgrade

# Rollback (if needed)
alembic downgrade -1
```

### Backup Strategy

```bash
# Database backup
docker-compose exec db pg_dump -U postgres fastapi_app > backup.sql

# Restore
docker-compose exec -T db psql -U postgres fastapi_app < backup.sql
```

### Health Checks

Monitor these endpoints:
- `/health` - Basic health check
- `/ready` - Readiness check (includes dependencies)
- `/metrics` - Prometheus metrics

## 🆘 Troubleshooting

### Common Issues

1. **Database connection failed**
   - Check DATABASE_URL
   - Verify database is running
   - Check network connectivity

2. **Authentication not working**
   - Verify JWT_SECRET is set
   - Check token expiration
   - Validate CORS settings

3. **High memory usage**
   - Check for memory leaks
   - Optimize database queries
   - Implement pagination

### Debug Commands

```bash
# Check logs
make logs

# Connect to database
make psql

# Connect to Redis
make redis-cli

# Run shell in container
make shell
```

## 📞 Support

For issues and questions:
- Check the logs first
- Review this deployment guide
- Open an issue on GitHub
- Contact the development team
