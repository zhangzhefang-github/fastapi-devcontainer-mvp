"""
Examples of how to use the logging system in the FastAPI application.
"""
import asyncio
import time
from typing import Dict, List, Optional

from app.core.logging_config import get_logger, get_structured_logger, performance_logger, security_logger
from app.utils.logging_decorators import log_function_call, log_performance, log_errors


# Get loggers
logger = get_logger("examples")
structured_logger = get_structured_logger("examples")


class UserService:
    """Example service class with comprehensive logging."""
    
    def __init__(self):
        self.logger = get_logger("services.user")
        self.users_db = {}  # Mock database
    
    @log_function_call(logger_name="services.user")
    @log_performance(threshold_ms=100.0)
    @log_errors(logger_name="services.user")
    async def create_user(self, user_data: Dict) -> Dict:
        """Create a new user with comprehensive logging."""
        user_id = user_data.get("id")
        username = user_data.get("username")
        
        self.logger.info(
            f"Creating user: {username}",
            extra={
                "user_id": user_id,
                "username": username,
                "operation": "create_user",
                "event_type": "user_creation_start"
            }
        )
        
        # Simulate some processing time
        await asyncio.sleep(0.05)
        
        # Check if user already exists
        if username in self.users_db:
            self.logger.warning(
                f"User creation failed - username already exists: {username}",
                extra={
                    "username": username,
                    "operation": "create_user",
                    "event_type": "user_creation_failed",
                    "reason": "username_exists"
                }
            )
            raise ValueError(f"Username {username} already exists")
        
        # Create user
        self.users_db[username] = user_data
        
        self.logger.info(
            f"User created successfully: {username}",
            extra={
                "user_id": user_id,
                "username": username,
                "operation": "create_user",
                "event_type": "user_creation_success"
            }
        )
        
        return user_data
    
    @log_function_call(logger_name="services.user", log_result=False)
    def get_user(self, username: str) -> Optional[Dict]:
        """Get user by username."""
        self.logger.debug(f"Fetching user: {username}")
        
        user = self.users_db.get(username)
        
        if user:
            self.logger.info(
                f"User found: {username}",
                extra={
                    "username": username,
                    "operation": "get_user",
                    "event_type": "user_found"
                }
            )
        else:
            self.logger.warning(
                f"User not found: {username}",
                extra={
                    "username": username,
                    "operation": "get_user",
                    "event_type": "user_not_found"
                }
            )
        
        return user
    
    @log_performance(threshold_ms=200.0)
    async def bulk_operation(self, user_ids: List[str]) -> Dict:
        """Example of bulk operation with performance logging."""
        start_time = time.time()
        
        self.logger.info(
            f"Starting bulk operation for {len(user_ids)} users",
            extra={
                "operation": "bulk_operation",
                "user_count": len(user_ids),
                "event_type": "bulk_operation_start"
            }
        )
        
        results = {"processed": 0, "errors": 0}
        
        for user_id in user_ids:
            try:
                # Simulate processing
                await asyncio.sleep(0.01)
                results["processed"] += 1
                
                # Log progress every 10 users
                if results["processed"] % 10 == 0:
                    self.logger.debug(
                        f"Bulk operation progress: {results['processed']}/{len(user_ids)}",
                        extra={
                            "operation": "bulk_operation",
                            "processed": results["processed"],
                            "total": len(user_ids),
                            "event_type": "bulk_operation_progress"
                        }
                    )
            
            except Exception as e:
                results["errors"] += 1
                self.logger.error(
                    f"Error processing user {user_id}: {str(e)}",
                    extra={
                        "operation": "bulk_operation",
                        "user_id": user_id,
                        "error": str(e),
                        "event_type": "bulk_operation_error"
                    }
                )
        
        duration_ms = (time.time() - start_time) * 1000
        
        self.logger.info(
            f"Bulk operation completed: {results['processed']} processed, {results['errors']} errors",
            extra={
                "operation": "bulk_operation",
                "duration_ms": duration_ms,
                "results": results,
                "event_type": "bulk_operation_complete"
            }
        )
        
        return results


class AuthService:
    """Example authentication service with security logging."""
    
    def __init__(self):
        self.logger = get_logger("services.auth")
    
    def login_attempt(self, username: str, password: str, ip_address: str, user_agent: str) -> bool:
        """Example login with security logging."""
        
        # Log login attempt
        security_logger.log_login_attempt(
            username=username,
            success=False,  # Will be updated if successful
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Simulate authentication logic
        if username == "admin" and password == "wrong_password":
            # Failed login
            self.logger.warning(
                f"Failed login attempt for admin user",
                extra={
                    "username": username,
                    "ip_address": ip_address,
                    "user_agent": user_agent,
                    "event_type": "failed_login",
                    "security_event": True
                }
            )
            return False
        
        # Successful login
        security_logger.log_login_attempt(
            username=username,
            success=True,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.logger.info(
            f"Successful login for user: {username}",
            extra={
                "username": username,
                "ip_address": ip_address,
                "event_type": "successful_login"
            }
        )
        
        return True
    
    def access_protected_resource(self, user_id: str, resource: str, action: str) -> bool:
        """Example of protected resource access with logging."""
        
        # Simulate permission check
        if user_id == "user123" and resource == "admin_panel":
            # Permission denied
            security_logger.log_permission_denied(
                user_id=user_id,
                resource=resource,
                action=action
            )
            return False
        
        self.logger.info(
            f"Access granted to {resource} for user {user_id}",
            extra={
                "user_id": user_id,
                "resource": resource,
                "action": action,
                "event_type": "access_granted"
            }
        )
        
        return True


class DatabaseService:
    """Example database service with performance logging."""
    
    def __init__(self):
        self.logger = get_logger("services.database")
    
    @log_performance(threshold_ms=50.0)
    async def execute_query(self, query: str, params: Optional[Dict] = None) -> List[Dict]:
        """Example database query with performance logging."""
        start_time = time.time()
        
        self.logger.debug(
            f"Executing query: {query[:100]}...",
            extra={
                "query_preview": query[:100],
                "has_params": params is not None,
                "event_type": "query_start"
            }
        )
        
        # Simulate query execution
        await asyncio.sleep(0.02)  # Simulate DB latency
        
        # Mock result
        result = [{"id": 1, "name": "test"}]
        
        duration_ms = (time.time() - start_time) * 1000
        
        # Log query performance
        performance_logger.log_database_query(
            query=query,
            duration_ms=duration_ms,
            rows_affected=len(result)
        )
        
        self.logger.info(
            f"Query executed successfully",
            extra={
                "duration_ms": duration_ms,
                "rows_returned": len(result),
                "event_type": "query_complete"
            }
        )
        
        return result


class ExternalAPIService:
    """Example external API service with logging."""
    
    def __init__(self):
        self.logger = get_logger("services.external_api")
    
    @log_errors(logger_name="services.external_api")
    async def call_external_service(self, service_name: str, endpoint: str, data: Dict) -> Dict:
        """Example external API call with logging."""
        start_time = time.time()
        
        self.logger.info(
            f"Calling external service: {service_name}",
            extra={
                "service": service_name,
                "endpoint": endpoint,
                "event_type": "external_api_start"
            }
        )
        
        try:
            # Simulate API call
            await asyncio.sleep(0.1)
            
            # Mock response
            response = {"status": "success", "data": "mock_data"}
            status_code = 200
            
            duration_ms = (time.time() - start_time) * 1000
            
            # Log API performance
            performance_logger.log_external_api(
                service=service_name,
                endpoint=endpoint,
                status_code=status_code,
                duration_ms=duration_ms
            )
            
            self.logger.info(
                f"External API call successful: {service_name}",
                extra={
                    "service": service_name,
                    "endpoint": endpoint,
                    "status_code": status_code,
                    "duration_ms": duration_ms,
                    "event_type": "external_api_success"
                }
            )
            
            return response
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            
            self.logger.error(
                f"External API call failed: {service_name} - {str(e)}",
                extra={
                    "service": service_name,
                    "endpoint": endpoint,
                    "duration_ms": duration_ms,
                    "error": str(e),
                    "event_type": "external_api_error"
                },
                exc_info=True
            )
            
            raise


# Example usage functions
async def demonstrate_logging():
    """Demonstrate various logging patterns."""
    
    logger.info("Starting logging demonstration")
    
    # User service examples
    user_service = UserService()
    
    try:
        # Create users
        await user_service.create_user({"id": "1", "username": "alice", "email": "alice@example.com"})
        await user_service.create_user({"id": "2", "username": "bob", "email": "bob@example.com"})
        
        # Get user
        user = user_service.get_user("alice")
        
        # Bulk operation
        await user_service.bulk_operation(["1", "2", "3", "4", "5"])
        
    except Exception as e:
        logger.error(f"Error in user service demo: {str(e)}", exc_info=True)
    
    # Auth service examples
    auth_service = AuthService()
    
    # Login attempts
    auth_service.login_attempt("alice", "correct_password", "192.168.1.100", "Mozilla/5.0...")
    auth_service.login_attempt("admin", "wrong_password", "192.168.1.100", "Mozilla/5.0...")
    
    # Access control
    auth_service.access_protected_resource("user123", "admin_panel", "read")
    auth_service.access_protected_resource("admin456", "user_data", "read")
    
    # Database service examples
    db_service = DatabaseService()
    await db_service.execute_query("SELECT * FROM users WHERE active = true", {"active": True})
    
    # External API service examples
    api_service = ExternalAPIService()
    await api_service.call_external_service("payment_gateway", "/api/v1/charge", {"amount": 100})
    
    logger.info("Logging demonstration completed")


# Structured logging examples
def demonstrate_structured_logging():
    """Demonstrate structured logging with structlog."""
    
    # Basic structured logging
    structured_logger.info("User action performed", 
                          user_id="12345", 
                          action="profile_update", 
                          ip_address="192.168.1.100")
    
    # Complex structured data
    structured_logger.info("API request processed",
                          request_id="req-789",
                          method="POST",
                          path="/api/v1/users",
                          status_code=201,
                          duration_ms=45.2,
                          user_agent="FastAPI-Client/1.0")
    
    # Error with context
    try:
        raise ValueError("Example error for demonstration")
    except Exception:
        structured_logger.error("Processing failed",
                               user_id="12345",
                               operation="data_processing",
                               error_type="validation_error",
                               exc_info=True)


if __name__ == "__main__":
    # Run demonstrations
    print("Running logging demonstrations...")
    
    # Run async demo
    asyncio.run(demonstrate_logging())
    
    # Run structured logging demo
    demonstrate_structured_logging()
    
    print("Demonstrations completed. Check the logs directory for output.")
