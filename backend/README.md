# FastAPI Enterprise MVP - Backend

This is the backend component of the FastAPI Enterprise MVP project, built with modern Python technologies and enterprise-grade features.

## Features

- **FastAPI**: Modern, fast web framework for building APIs
- **JWT Authentication**: Secure token-based authentication
- **Role-Based Access Control**: Fine-grained permissions
- **SQLAlchemy**: Async ORM for database operations
- **Pydantic**: Data validation and serialization
- **Structured Logging**: JSON-formatted logs with correlation IDs
- **Prometheus Metrics**: Application monitoring
- **Comprehensive Testing**: Unit and integration tests

## Quick Start

### With uv (Recommended)

```bash
# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Install dependencies
uv pip install -e .[dev]

# Run the application
uvicorn app.main:app --reload
```

### With pip

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -e .[dev]

# Run the application
uvicorn app.main:app --reload
```

## API Documentation

Once the server is running, visit:

- **Interactive API docs**: http://localhost:8000/docs
- **Alternative docs**: http://localhost:8000/redoc
- **Health check**: http://localhost:8000/health
- **Metrics**: http://localhost:8000/metrics

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test types
pytest -m unit
pytest -m integration
```

## Development

```bash
# Format code
black app/
isort app/

# Lint code
ruff check app/

# Type checking
mypy app/
```

## Project Structure

```
backend/
├── app/
│   ├── api/           # API routes and endpoints
│   ├── core/          # Core functionality
│   ├── models/        # Database models
│   ├── schemas/       # Pydantic schemas
│   ├── services/      # Business logic
│   └── main.py        # Application entry point
├── tests/             # Test suite
└── pyproject.toml     # Dependencies and configuration
```

## Environment Variables

Create a `.env` file in the project root with:

```env
JWT_SECRET=your-secret-key
DATABASE_URL=postgresql://user:pass@localhost/db
REDIS_URL=redis://localhost:6379/0
LOG_LEVEL=INFO
```

## License

MIT License
