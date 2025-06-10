"""
Enterprise-grade structured logging configuration.
"""
import logging
import sys
from typing import Any, Dict

import structlog
from structlog.stdlib import LoggerFactory

from app.core.config import settings


def setup_logging() -> None:
    """Configure structured logging for the application."""
    
    # Configure structlog
    structlog.configure(
        processors=[
            # Add timestamp
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            # JSON formatting for production, pretty printing for development
            structlog.processors.JSONRenderer() if not settings.DEBUG 
            else structlog.dev.ConsoleRenderer(colors=True),
        ],
        context_class=dict,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.LOG_LEVEL.upper()),
    )
    
    # Set log levels for third-party libraries
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.DEBUG else logging.WARNING
    )


def get_logger(name: str = None) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


class LoggerMixin:
    """Mixin class to add logging capabilities to any class."""
    
    @property
    def logger(self) -> structlog.stdlib.BoundLogger:
        """Get logger instance for this class."""
        return structlog.get_logger(self.__class__.__name__)


def log_function_call(func_name: str, **kwargs: Any) -> None:
    """Log function call with parameters."""
    logger = structlog.get_logger()
    logger.debug(
        "Function called",
        function=func_name,
        parameters=kwargs
    )


def log_database_query(query: str, params: Dict[str, Any] = None) -> None:
    """Log database query execution."""
    logger = structlog.get_logger()
    logger.debug(
        "Database query executed",
        query=query,
        parameters=params or {}
    )


def log_api_call(
    method: str, 
    url: str, 
    status_code: int, 
    duration: float,
    user_id: str = None
) -> None:
    """Log API call details."""
    logger = structlog.get_logger()
    logger.info(
        "API call completed",
        method=method,
        url=url,
        status_code=status_code,
        duration=duration,
        user_id=user_id
    )


def log_security_event(
    event_type: str,
    user_id: str = None,
    ip_address: str = None,
    details: Dict[str, Any] = None
) -> None:
    """Log security-related events."""
    logger = structlog.get_logger()
    logger.warning(
        "Security event",
        event_type=event_type,
        user_id=user_id,
        ip_address=ip_address,
        details=details or {}
    )


def log_business_event(
    event_type: str,
    user_id: str = None,
    entity_id: str = None,
    details: Dict[str, Any] = None
) -> None:
    """Log business logic events."""
    logger = structlog.get_logger()
    logger.info(
        "Business event",
        event_type=event_type,
        user_id=user_id,
        entity_id=entity_id,
        details=details or {}
    )
