"""
Logging middleware for FastAPI application.
"""
import time
import uuid
from typing import Callable
import logging

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.logging_config import get_logger, performance_logger


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests and responses."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = get_logger("middleware.logging")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log details."""
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Start timing
        start_time = time.time()
        
        # Extract request details
        method = request.method
        url = str(request.url)
        path = request.url.path
        query_params = str(request.query_params) if request.query_params else ""
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "")
        
        # Log request start
        self.logger.info(
            f"Request started: {method} {path}",
            extra={
                "request_id": request_id,
                "method": method,
                "path": path,
                "query_params": query_params,
                "client_ip": client_ip,
                "user_agent": user_agent,
                "event_type": "request_start"
            }
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Log successful response
            self.logger.info(
                f"Request completed: {method} {path} - {response.status_code}",
                extra={
                    "request_id": request_id,
                    "method": method,
                    "path": path,
                    "status_code": response.status_code,
                    "duration": duration_ms,
                    "client_ip": client_ip,
                    "event_type": "request_complete"
                }
            )
            
            # Log performance metrics
            performance_logger.log_request(
                method=method,
                path=path,
                status_code=response.status_code,
                duration_ms=duration_ms,
                request_id=request_id
            )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as exc:
            # Calculate duration for failed requests
            duration_ms = (time.time() - start_time) * 1000
            
            # Log error
            self.logger.error(
                f"Request failed: {method} {path} - {type(exc).__name__}: {str(exc)}",
                extra={
                    "request_id": request_id,
                    "method": method,
                    "path": path,
                    "duration": duration_ms,
                    "client_ip": client_ip,
                    "exception_type": type(exc).__name__,
                    "exception_message": str(exc),
                    "event_type": "request_error"
                },
                exc_info=True
            )
            
            # Re-raise the exception
            raise exc
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request."""
        # Check for forwarded headers (when behind proxy)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fallback to direct client IP
        if hasattr(request.client, "host"):
            return request.client.host
        
        return "unknown"


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Middleware for adding correlation ID to requests."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = get_logger("middleware.correlation")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add correlation ID to request context."""
        # Get or generate correlation ID
        correlation_id = request.headers.get("x-correlation-id", str(uuid.uuid4()))
        request.state.correlation_id = correlation_id
        
        # Process request
        response = await call_next(request)
        
        # Add correlation ID to response headers
        response.headers["X-Correlation-ID"] = correlation_id
        
        return response


class SecurityLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for security-related logging."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = get_logger("security")
        self.sensitive_paths = {"/api/v1/auth/login", "/api/v1/auth/register"}
        self.admin_paths = {"/admin", "/api/v1/admin"}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log security-relevant events."""
        path = request.url.path
        method = request.method
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "")
        
        # Log access to sensitive endpoints
        if path in self.sensitive_paths:
            self.logger.info(
                f"Access to sensitive endpoint: {method} {path}",
                extra={
                    "path": path,
                    "method": method,
                    "client_ip": client_ip,
                    "user_agent": user_agent,
                    "event_type": "sensitive_endpoint_access"
                }
            )
        
        # Log access to admin endpoints
        if any(path.startswith(admin_path) for admin_path in self.admin_paths):
            self.logger.warning(
                f"Access to admin endpoint: {method} {path}",
                extra={
                    "path": path,
                    "method": method,
                    "client_ip": client_ip,
                    "user_agent": user_agent,
                    "event_type": "admin_endpoint_access"
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Log failed authentication attempts
        if path in self.sensitive_paths and response.status_code == 401:
            self.logger.warning(
                f"Authentication failed: {method} {path}",
                extra={
                    "path": path,
                    "method": method,
                    "status_code": response.status_code,
                    "client_ip": client_ip,
                    "user_agent": user_agent,
                    "event_type": "authentication_failed"
                }
            )
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request."""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        if hasattr(request.client, "host"):
            return request.client.host
        
        return "unknown"


class ErrorLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for comprehensive error logging."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = get_logger("errors")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log detailed error information."""
        try:
            response = await call_next(request)
            
            # Log client errors (4xx)
            if 400 <= response.status_code < 500:
                self.logger.warning(
                    f"Client error: {request.method} {request.url.path} - {response.status_code}",
                    extra={
                        "method": request.method,
                        "path": request.url.path,
                        "status_code": response.status_code,
                        "client_ip": self._get_client_ip(request),
                        "user_agent": request.headers.get("user-agent", ""),
                        "event_type": "client_error"
                    }
                )
            
            # Log server errors (5xx)
            elif response.status_code >= 500:
                self.logger.error(
                    f"Server error: {request.method} {request.url.path} - {response.status_code}",
                    extra={
                        "method": request.method,
                        "path": request.url.path,
                        "status_code": response.status_code,
                        "client_ip": self._get_client_ip(request),
                        "user_agent": request.headers.get("user-agent", ""),
                        "event_type": "server_error"
                    }
                )
            
            return response
            
        except Exception as exc:
            # Log unhandled exceptions
            self.logger.error(
                f"Unhandled exception: {request.method} {request.url.path} - {type(exc).__name__}",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "exception_type": type(exc).__name__,
                    "exception_message": str(exc),
                    "client_ip": self._get_client_ip(request),
                    "user_agent": request.headers.get("user-agent", ""),
                    "event_type": "unhandled_exception"
                },
                exc_info=True
            )
            raise exc
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request."""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        if hasattr(request.client, "host"):
            return request.client.host
        
        return "unknown"
