"""
Environment configuration management system.
Provides centralized configuration for different deployment environments.
"""
import os
from enum import Enum
from typing import Dict, Any, Optional
from pathlib import Path

from pydantic import BaseSettings, Field
from pydantic_settings import SettingsConfigDict


class Environment(str, Enum):
    """Supported deployment environments."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class ServiceMode(str, Enum):
    """Service operation modes."""
    STANDALONE = "standalone"  # Single service mode
    MICROSERVICE = "microservice"  # Full microservice mode
    DEMO = "demo"  # Demo/mock mode


class DatabaseConfig(BaseSettings):
    """Database configuration."""
    url: str = Field(default="sqlite:///./app.db")
    echo: bool = Field(default=False)
    pool_size: int = Field(default=5)
    max_overflow: int = Field(default=10)
    pool_timeout: int = Field(default=30)
    pool_recycle: int = Field(default=3600)


class RedisConfig(BaseSettings):
    """Redis configuration."""
    url: str = Field(default="redis://localhost:6379/0")
    max_connections: int = Field(default=10)
    socket_timeout: int = Field(default=5)
    socket_connect_timeout: int = Field(default=5)
    retry_on_timeout: bool = Field(default=True)


class AuthConfig(BaseSettings):
    """Authentication configuration."""
    secret_key: str = Field(default="your-secret-key-change-in-production")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)
    refresh_token_expire_days: int = Field(default=7)
    password_min_length: int = Field(default=8)
    max_login_attempts: int = Field(default=5)
    account_lockout_duration_minutes: int = Field(default=30)


class LoggingConfig(BaseSettings):
    """Logging configuration."""
    level: str = Field(default="INFO")
    format: str = Field(default="detailed")
    to_file: bool = Field(default=True)
    file_max_size: int = Field(default=10485760)  # 10MB
    file_backup_count: int = Field(default=5)
    json_format: bool = Field(default=False)
    enable_performance: bool = Field(default=True)
    enable_security: bool = Field(default=True)
    enable_access: bool = Field(default=True)


class APIConfig(BaseSettings):
    """API configuration."""
    title: str = Field(default="FastAPI Enterprise MVP")
    version: str = Field(default="1.0.0")
    description: str = Field(default="Enterprise-grade FastAPI application")
    docs_url: Optional[str] = Field(default="/docs")
    redoc_url: Optional[str] = Field(default="/redoc")
    openapi_url: Optional[str] = Field(default="/openapi.json")
    api_v1_prefix: str = Field(default="/api/v1")


class CORSConfig(BaseSettings):
    """CORS configuration."""
    origins: list[str] = Field(default=["http://localhost:8501", "http://127.0.0.1:8501"])
    methods: list[str] = Field(default=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    headers: list[str] = Field(default=["*"])
    credentials: bool = Field(default=True)


class MonitoringConfig(BaseSettings):
    """Monitoring configuration."""
    enable_metrics: bool = Field(default=True)
    enable_tracing: bool = Field(default=True)
    enable_health_checks: bool = Field(default=True)
    metrics_endpoint: str = Field(default="/metrics")
    health_endpoint: str = Field(default="/health")
    ready_endpoint: str = Field(default="/ready")


class EnvironmentSettings(BaseSettings):
    """
    Centralized environment configuration.
    
    This class provides a single source of truth for all application configuration,
    with environment-specific overrides and validation.
    """
    
    # Core settings
    environment: Environment = Field(default=Environment.DEVELOPMENT)
    service_mode: ServiceMode = Field(default=ServiceMode.STANDALONE)
    debug: bool = Field(default=False)
    testing: bool = Field(default=False)
    
    # Service discovery
    service_name: str = Field(default="fastapi-enterprise-mvp")
    service_version: str = Field(default="1.0.0")
    service_host: str = Field(default="0.0.0.0")
    service_port: int = Field(default=8000)
    
    # External service URLs
    frontend_url: str = Field(default="http://localhost:8501")
    backend_url: str = Field(default="http://localhost:8000")
    
    # Component configurations
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    auth: AuthConfig = Field(default_factory=AuthConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    api: APIConfig = Field(default_factory=APIConfig)
    cors: CORSConfig = Field(default_factory=CORSConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore"
    )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._apply_environment_overrides()
    
    def _apply_environment_overrides(self):
        """Apply environment-specific configuration overrides."""
        
        if self.environment == Environment.DEVELOPMENT:
            self.debug = True
            self.logging.level = "DEBUG"
            self.logging.format = "colored"
            self.api.docs_url = "/docs"
            self.api.redoc_url = "/redoc"
            
        elif self.environment == Environment.TESTING:
            self.testing = True
            self.debug = True
            self.logging.level = "WARNING"
            self.logging.to_file = False
            self.database.url = "sqlite:///./test.db"
            self.redis.url = "redis://localhost:6379/1"
            
        elif self.environment == Environment.STAGING:
            self.debug = False
            self.logging.level = "INFO"
            self.logging.json_format = True
            self.api.docs_url = "/docs"  # Keep docs in staging
            
        elif self.environment == Environment.PRODUCTION:
            self.debug = False
            self.logging.level = "INFO"
            self.logging.json_format = True
            self.api.docs_url = None  # Disable docs in production
            self.api.redoc_url = None
            self.api.openapi_url = None
    
    def get_database_url(self) -> str:
        """Get the appropriate database URL for the current environment."""
        return self.database.url
    
    def get_redis_url(self) -> str:
        """Get the appropriate Redis URL for the current environment."""
        return self.redis.url
    
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == Environment.DEVELOPMENT
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == Environment.PRODUCTION
    
    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.environment == Environment.TESTING
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get service information for health checks and discovery."""
        return {
            "name": self.service_name,
            "version": self.service_version,
            "environment": self.environment.value,
            "mode": self.service_mode.value,
            "host": self.service_host,
            "port": self.service_port,
            "debug": self.debug,
            "testing": self.testing
        }
    
    def get_cors_config(self) -> Dict[str, Any]:
        """Get CORS configuration."""
        return {
            "allow_origins": self.cors.origins,
            "allow_methods": self.cors.methods,
            "allow_headers": self.cors.headers,
            "allow_credentials": self.cors.credentials
        }


# Global settings instance
settings = EnvironmentSettings()


def get_settings() -> EnvironmentSettings:
    """Get the global settings instance."""
    return settings


def reload_settings() -> EnvironmentSettings:
    """Reload settings from environment variables."""
    global settings
    settings = EnvironmentSettings()
    return settings
