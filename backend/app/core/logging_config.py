"""
Enterprise-grade logging configuration for FastAPI application.
"""
import logging
import logging.config
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional
import json
from datetime import datetime
import structlog
from pythonjsonlogger import jsonlogger

from app.core.config import settings


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with structured data."""
        # Create base log entry
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add extra fields if present
        if hasattr(record, 'user_id'):
            log_entry["user_id"] = record.user_id
        if hasattr(record, 'request_id'):
            log_entry["request_id"] = record.request_id
        if hasattr(record, 'correlation_id'):
            log_entry["correlation_id"] = record.correlation_id
        if hasattr(record, 'duration'):
            log_entry["duration_ms"] = record.duration
        if hasattr(record, 'status_code'):
            log_entry["status_code"] = record.status_code
        if hasattr(record, 'method'):
            log_entry["method"] = record.method
        if hasattr(record, 'path'):
            log_entry["path"] = record.path
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info)
            }
        
        return json.dumps(log_entry, ensure_ascii=False)


class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output."""
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors."""
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


def get_logging_config() -> Dict[str, Any]:
    """Get logging configuration based on environment."""
    
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Base configuration
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "detailed": {
                "format": "%(asctime)s [%(levelname)-8s] %(name)-30s: %(message)s [%(filename)s:%(lineno)d]",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "simple": {
                "format": "%(levelname)s: %(message)s"
            },
            "json": {
                "()": StructuredFormatter,
            },
            "colored": {
                "()": ColoredFormatter,
                "format": "%(asctime)s [%(levelname)-8s] %(name)-25s: %(message)s",
                "datefmt": "%H:%M:%S"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "colored" if settings.ENVIRONMENT == "development" else "detailed",
                "stream": "ext://sys.stdout"
            },
            "file_info": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "detailed",
                "filename": str(log_dir / "app.log"),
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf8"
            },
            "file_error": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "detailed",
                "filename": str(log_dir / "error.log"),
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf8"
            },
            "file_json": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "json",
                "filename": str(log_dir / "app.json"),
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf8"
            }
        },
        "loggers": {
            "app": {
                "level": "DEBUG" if settings.ENVIRONMENT == "development" else "INFO",
                "handlers": ["console", "file_info", "file_error", "file_json"],
                "propagate": False
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console", "file_info"],
                "propagate": False
            },
            "uvicorn.access": {
                "level": "INFO",
                "handlers": ["file_info"],
                "propagate": False
            },
            "sqlalchemy": {
                "level": "WARNING",
                "handlers": ["console", "file_info"],
                "propagate": False
            },
            "alembic": {
                "level": "INFO",
                "handlers": ["console", "file_info"],
                "propagate": False
            }
        },
        "root": {
            "level": "INFO",
            "handlers": ["console"]
        }
    }
    
    # Add performance logging in production
    if settings.ENVIRONMENT == "production":
        config["handlers"]["file_performance"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "json",
            "filename": str(log_dir / "performance.log"),
            "maxBytes": 10485760,  # 10MB
            "backupCount": 10,
            "encoding": "utf8"
        }
        config["loggers"]["app.performance"] = {
            "level": "INFO",
            "handlers": ["file_performance"],
            "propagate": False
        }
    
    return config


def setup_logging() -> None:
    """Setup logging configuration."""
    config = get_logging_config()
    logging.config.dictConfig(config)
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(f"app.{name}")


def get_structured_logger(name: str):
    """Get a structured logger instance."""
    return structlog.get_logger(f"app.{name}")


# Performance logging utilities
class PerformanceLogger:
    """Performance logging utility."""
    
    def __init__(self, logger_name: str = "performance"):
        self.logger = get_logger(logger_name)
    
    def log_request(self, method: str, path: str, status_code: int, 
                   duration_ms: float, user_id: Optional[str] = None,
                   request_id: Optional[str] = None):
        """Log request performance."""
        self.logger.info(
            "Request completed",
            extra={
                "method": method,
                "path": path,
                "status_code": status_code,
                "duration": duration_ms,
                "user_id": user_id,
                "request_id": request_id
            }
        )
    
    def log_database_query(self, query: str, duration_ms: float,
                          rows_affected: Optional[int] = None):
        """Log database query performance."""
        self.logger.info(
            "Database query executed",
            extra={
                "query": query[:200] + "..." if len(query) > 200 else query,
                "duration": duration_ms,
                "rows_affected": rows_affected
            }
        )
    
    def log_external_api(self, service: str, endpoint: str, 
                        status_code: int, duration_ms: float):
        """Log external API call performance."""
        self.logger.info(
            "External API call",
            extra={
                "service": service,
                "endpoint": endpoint,
                "status_code": status_code,
                "duration": duration_ms
            }
        )


# Security logging utilities
class SecurityLogger:
    """Security logging utility."""
    
    def __init__(self):
        self.logger = get_logger("security")
    
    def log_login_attempt(self, username: str, success: bool, 
                         ip_address: str, user_agent: str):
        """Log login attempt."""
        level = logging.INFO if success else logging.WARNING
        self.logger.log(
            level,
            f"Login {'successful' if success else 'failed'} for user: {username}",
            extra={
                "username": username,
                "success": success,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "event_type": "login_attempt"
            }
        )
    
    def log_permission_denied(self, user_id: str, resource: str, action: str):
        """Log permission denied event."""
        self.logger.warning(
            f"Permission denied for user {user_id} on {resource}:{action}",
            extra={
                "user_id": user_id,
                "resource": resource,
                "action": action,
                "event_type": "permission_denied"
            }
        )
    
    def log_suspicious_activity(self, description: str, user_id: Optional[str] = None,
                               ip_address: Optional[str] = None):
        """Log suspicious activity."""
        self.logger.error(
            f"Suspicious activity detected: {description}",
            extra={
                "description": description,
                "user_id": user_id,
                "ip_address": ip_address,
                "event_type": "suspicious_activity"
            }
        )


# Initialize loggers
performance_logger = PerformanceLogger()
security_logger = SecurityLogger()
