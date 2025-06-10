"""
Service discovery and health check system.
Provides automatic service registration, discovery, and health monitoring.
"""
import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
import httpx
import logging

from app.core.environment import get_settings
from app.core.logging_config import get_logger

logger = get_logger("service_discovery")


class ServiceStatus(str, Enum):
    """Service health status."""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"
    STARTING = "starting"
    STOPPING = "stopping"


class ServiceInfo:
    """Service information and metadata."""
    
    def __init__(
        self,
        name: str,
        url: str,
        health_endpoint: str = "/health",
        version: str = "1.0.0",
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.name = name
        self.url = url
        self.health_endpoint = health_endpoint
        self.version = version
        self.metadata = metadata or {}
        self.status = ServiceStatus.UNKNOWN
        self.last_check = None
        self.last_healthy = None
        self.consecutive_failures = 0
        self.response_time_ms = None
    
    @property
    def health_url(self) -> str:
        """Get the full health check URL."""
        return f"{self.url.rstrip('/')}{self.health_endpoint}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "url": self.url,
            "health_endpoint": self.health_endpoint,
            "version": self.version,
            "metadata": self.metadata,
            "status": self.status.value,
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "last_healthy": self.last_healthy.isoformat() if self.last_healthy else None,
            "consecutive_failures": self.consecutive_failures,
            "response_time_ms": self.response_time_ms
        }


class ServiceRegistry:
    """
    Service registry for managing service discovery and health checks.
    
    This class maintains a registry of all services in the system and
    provides health monitoring capabilities.
    """
    
    def __init__(self):
        self.services: Dict[str, ServiceInfo] = {}
        self.health_check_interval = 30  # seconds
        self.health_check_timeout = 5  # seconds
        self.max_consecutive_failures = 3
        self._health_check_task: Optional[asyncio.Task] = None
        self._running = False
    
    def register_service(
        self,
        name: str,
        url: str,
        health_endpoint: str = "/health",
        version: str = "1.0.0",
        metadata: Optional[Dict[str, Any]] = None
    ) -> ServiceInfo:
        """Register a new service."""
        service = ServiceInfo(
            name=name,
            url=url,
            health_endpoint=health_endpoint,
            version=version,
            metadata=metadata
        )
        
        self.services[name] = service
        
        logger.info(
            f"Service registered: {name}",
            extra={
                "service_name": name,
                "service_url": url,
                "health_endpoint": health_endpoint,
                "version": version,
                "event_type": "service_registered"
            }
        )
        
        return service
    
    def unregister_service(self, name: str) -> bool:
        """Unregister a service."""
        if name in self.services:
            del self.services[name]
            logger.info(
                f"Service unregistered: {name}",
                extra={
                    "service_name": name,
                    "event_type": "service_unregistered"
                }
            )
            return True
        return False
    
    def get_service(self, name: str) -> Optional[ServiceInfo]:
        """Get service information by name."""
        return self.services.get(name)
    
    def get_healthy_services(self) -> List[ServiceInfo]:
        """Get all healthy services."""
        return [
            service for service in self.services.values()
            if service.status == ServiceStatus.HEALTHY
        ]
    
    def get_all_services(self) -> Dict[str, ServiceInfo]:
        """Get all registered services."""
        return self.services.copy()
    
    async def check_service_health(self, service: ServiceInfo) -> ServiceStatus:
        """Check the health of a specific service."""
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=self.health_check_timeout) as client:
                response = await client.get(service.health_url)
                
                response_time_ms = (time.time() - start_time) * 1000
                service.response_time_ms = response_time_ms
                service.last_check = datetime.utcnow()
                
                if response.status_code == 200:
                    service.status = ServiceStatus.HEALTHY
                    service.last_healthy = datetime.utcnow()
                    service.consecutive_failures = 0
                    
                    logger.debug(
                        f"Health check passed: {service.name}",
                        extra={
                            "service_name": service.name,
                            "response_time_ms": response_time_ms,
                            "status_code": response.status_code,
                            "event_type": "health_check_passed"
                        }
                    )
                else:
                    service.status = ServiceStatus.UNHEALTHY
                    service.consecutive_failures += 1
                    
                    logger.warning(
                        f"Health check failed: {service.name} - HTTP {response.status_code}",
                        extra={
                            "service_name": service.name,
                            "status_code": response.status_code,
                            "consecutive_failures": service.consecutive_failures,
                            "event_type": "health_check_failed"
                        }
                    )
                
        except asyncio.TimeoutError:
            service.status = ServiceStatus.UNHEALTHY
            service.consecutive_failures += 1
            service.last_check = datetime.utcnow()
            
            logger.warning(
                f"Health check timeout: {service.name}",
                extra={
                    "service_name": service.name,
                    "timeout_seconds": self.health_check_timeout,
                    "consecutive_failures": service.consecutive_failures,
                    "event_type": "health_check_timeout"
                }
            )
            
        except Exception as e:
            service.status = ServiceStatus.UNHEALTHY
            service.consecutive_failures += 1
            service.last_check = datetime.utcnow()
            
            logger.error(
                f"Health check error: {service.name} - {str(e)}",
                extra={
                    "service_name": service.name,
                    "error": str(e),
                    "consecutive_failures": service.consecutive_failures,
                    "event_type": "health_check_error"
                },
                exc_info=True
            )
        
        return service.status
    
    async def check_all_services(self):
        """Check the health of all registered services."""
        if not self.services:
            return
        
        logger.debug(f"Checking health of {len(self.services)} services")
        
        # Run health checks concurrently
        tasks = [
            self.check_service_health(service)
            for service in self.services.values()
        ]
        
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Log summary
        healthy_count = len(self.get_healthy_services())
        total_count = len(self.services)
        
        logger.info(
            f"Health check completed: {healthy_count}/{total_count} services healthy",
            extra={
                "healthy_services": healthy_count,
                "total_services": total_count,
                "event_type": "health_check_summary"
            }
        )
    
    async def start_health_monitoring(self):
        """Start the health monitoring background task."""
        if self._running:
            logger.warning("Health monitoring is already running")
            return
        
        self._running = True
        logger.info("Starting health monitoring")
        
        while self._running:
            try:
                await self.check_all_services()
                await asyncio.sleep(self.health_check_interval)
            except Exception as e:
                logger.error(
                    f"Error in health monitoring loop: {str(e)}",
                    extra={
                        "error": str(e),
                        "event_type": "health_monitoring_error"
                    },
                    exc_info=True
                )
                await asyncio.sleep(self.health_check_interval)
    
    def stop_health_monitoring(self):
        """Stop the health monitoring background task."""
        self._running = False
        if self._health_check_task:
            self._health_check_task.cancel()
        logger.info("Health monitoring stopped")
    
    def get_registry_status(self) -> Dict[str, Any]:
        """Get the overall registry status."""
        services_status = {}
        for name, service in self.services.items():
            services_status[name] = service.to_dict()
        
        healthy_count = len(self.get_healthy_services())
        total_count = len(self.services)
        
        return {
            "registry_status": "healthy" if healthy_count == total_count else "degraded",
            "total_services": total_count,
            "healthy_services": healthy_count,
            "unhealthy_services": total_count - healthy_count,
            "services": services_status,
            "last_updated": datetime.utcnow().isoformat()
        }


# Global service registry instance
service_registry = ServiceRegistry()


def get_service_registry() -> ServiceRegistry:
    """Get the global service registry instance."""
    return service_registry


def register_default_services():
    """Register default services based on configuration."""
    settings = get_settings()
    
    # Register backend service (self)
    service_registry.register_service(
        name="backend",
        url=settings.backend_url,
        health_endpoint="/health",
        version=settings.service_version,
        metadata={
            "type": "api",
            "environment": settings.environment.value,
            "mode": settings.service_mode.value
        }
    )
    
    # Register frontend service
    service_registry.register_service(
        name="frontend",
        url=settings.frontend_url,
        health_endpoint="/_stcore/health",
        version="1.0.0",
        metadata={
            "type": "web",
            "framework": "streamlit"
        }
    )
    
    # Register database service (if using external database)
    if "postgresql" in settings.database.url:
        # For PostgreSQL, we'll create a custom health check endpoint
        service_registry.register_service(
            name="database",
            url="http://localhost:5432",
            health_endpoint="/health",  # Custom endpoint
            version="15.0",
            metadata={
                "type": "database",
                "engine": "postgresql"
            }
        )
    
    # Register Redis service (if configured)
    if "redis" in settings.redis.url:
        service_registry.register_service(
            name="redis",
            url="http://localhost:6379",
            health_endpoint="/health",  # Custom endpoint
            version="7.0",
            metadata={
                "type": "cache",
                "engine": "redis"
            }
        )
    
    logger.info("Default services registered in service registry")
