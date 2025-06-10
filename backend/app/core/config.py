"""
Enterprise-grade configuration management with Pydantic Settings.
"""
import secrets
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, EmailStr, HttpUrl, field_validator
from pydantic_settings import BaseSettings
# PostgresDsn is not needed for this simple config


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application
    APP_NAME: str = "FastAPI Enterprise MVP"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    JWT_SECRET: str = secrets.token_urlsafe(32)
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 30
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "fastapi_app"
    POSTGRES_PORT: str = "5432"
    DATABASE_URL: Optional[str] = None
    
    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info) -> Any:
        if isinstance(v, str):
            return v
        # For Pydantic v2, we'll use a simple string construction
        values = info.data if hasattr(info, 'data') else {}
        user = values.get("POSTGRES_USER", "postgres")
        password = values.get("POSTGRES_PASSWORD", "postgres")
        host = values.get("POSTGRES_SERVER", "localhost")
        port = values.get("POSTGRES_PORT", "5432")
        db = values.get("POSTGRES_DB", "fastapi_app")
        return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60
    
    # Monitoring
    ENABLE_METRICS: bool = True
    ENABLE_TRACING: bool = True

    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "detailed"  # detailed, simple, json, colored
    LOG_TO_FILE: bool = True
    LOG_FILE_MAX_SIZE: int = 10485760  # 10MB
    LOG_FILE_BACKUP_COUNT: int = 5
    LOG_JSON_FORMAT: bool = False
    ENABLE_PERFORMANCE_LOGGING: bool = True
    ENABLE_SECURITY_LOGGING: bool = True
    ENABLE_ACCESS_LOGGING: bool = True

    # Environment detection
    ENVIRONMENT: str = "development"
    
    # External Services
    SENTRY_DSN: Optional[HttpUrl] = None
    
    # Email (Optional)
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    @field_validator("EMAILS_FROM_NAME", mode="before")
    @classmethod
    def get_project_name(cls, v: Optional[str], info) -> str:
        if not v:
            values = info.data if hasattr(info, 'data') else {}
            return values.get("APP_NAME", "FastAPI Enterprise MVP")
        return v
    
    # Testing
    TESTING: bool = False
    
    # Superuser
    FIRST_SUPERUSER: EmailStr = "admin@example.com"
    FIRST_SUPERUSER_PASSWORD: str = "changethis"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


class DevelopmentSettings(Settings):
    """Development environment settings."""
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    LOG_FORMAT: str = "colored"
    LOG_JSON_FORMAT: bool = False
    ENVIRONMENT: str = "development"
    TESTING: bool = False


class TestingSettings(Settings):
    """Testing environment settings."""
    DEBUG: bool = True
    TESTING: bool = True
    LOG_LEVEL: str = "WARNING"
    LOG_TO_FILE: bool = False
    ENVIRONMENT: str = "testing"
    DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"
    REDIS_URL: str = "redis://localhost:6379/1"


class ProductionSettings(Settings):
    """Production environment settings."""
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    LOG_JSON_FORMAT: bool = True
    ENVIRONMENT: str = "production"
    
    @field_validator("SECRET_KEY", mode="before")
    @classmethod
    def secret_key_required(cls, v: str) -> str:
        if not v or v == "changethis":
            raise ValueError("SECRET_KEY must be set in production")
        return v


def get_settings() -> Settings:
    """Factory function to get settings based on environment."""
    import os
    
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionSettings()
    elif env == "testing":
        return TestingSettings()
    else:
        return DevelopmentSettings()


# Global settings instance
settings = get_settings()
