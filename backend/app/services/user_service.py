"""
User service layer with business logic and data access.
Enhanced with comprehensive enterprise-grade logging.
"""
import time
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.core.security import get_password_hash, verify_password
from app.models.user import User, UserSession
from app.schemas.user import UserCreate, UserUpdate, UserRegister
from app.core.logging_config import get_logger, get_structured_logger, performance_logger, security_logger
from app.utils.logging_decorators import log_function_call, log_performance, log_errors

# Initialize loggers
logger = get_logger("services.user")
structured_logger = get_structured_logger("services.user")
audit_logger = get_logger("audit.user")


class UserService:
    """
    Service class for user-related operations with comprehensive logging.

    This service handles all user-related business logic including:
    - User authentication and authorization
    - User CRUD operations
    - Password management
    - Account security features
    - User search and pagination

    All operations are logged with detailed context for audit and monitoring.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.logger = logger
        self.structured_logger = structured_logger

        # Log service initialization
        self.logger.info(
            "UserService initialized",
            extra={
                "service": "UserService",
                "database_session": str(id(db)),
                "event_type": "service_init"
            }
        )
    
    @log_function_call(logger_name="services.user")
    @log_performance(threshold_ms=100.0)
    @log_errors(logger_name="services.user")
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """
        Get user by ID with comprehensive logging.

        Args:
            user_id: UUID of the user to retrieve

        Returns:
            User object if found, None otherwise

        Logs:
            - Query execution time
            - User found/not found status
            - Any database errors
        """
        start_time = time.time()

        self.logger.debug(
            "Fetching user by ID",
            extra={
                "user_id": str(user_id),
                "operation": "get_by_id",
                "event_type": "user_query_start"
            }
        )

        try:
            result = await self.db.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()

            duration_ms = (time.time() - start_time) * 1000

            if user:
                self.logger.info(
                    "User found by ID",
                    extra={
                        "user_id": str(user_id),
                        "username": user.username,
                        "email": user.email,
                        "is_active": user.is_active,
                        "duration_ms": duration_ms,
                        "operation": "get_by_id",
                        "event_type": "user_found"
                    }
                )

                # Log to structured logger for analytics
                self.structured_logger.info(
                    "User retrieved",
                    user_id=str(user_id),
                    username=user.username,
                    operation="get_by_id",
                    duration_ms=duration_ms
                )
            else:
                self.logger.warning(
                    "User not found by ID",
                    extra={
                        "user_id": str(user_id),
                        "duration_ms": duration_ms,
                        "operation": "get_by_id",
                        "event_type": "user_not_found"
                    }
                )

            return user

        except SQLAlchemyError as e:
            duration_ms = (time.time() - start_time) * 1000
            self.logger.error(
                "Database error getting user by ID",
                extra={
                    "user_id": str(user_id),
                    "duration_ms": duration_ms,
                    "operation": "get_by_id",
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "event_type": "database_error"
                },
                exc_info=True
            )
            return None
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.logger.error(
                "Unexpected error getting user by ID",
                extra={
                    "user_id": str(user_id),
                    "duration_ms": duration_ms,
                    "operation": "get_by_id",
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "event_type": "unexpected_error"
                },
                exc_info=True
            )
            return None
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        try:
            result = await self.db.execute(
                select(User).where(User.email == email)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error("Error getting user by email", email=email, error=str(e))
            return None
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        try:
            result = await self.db.execute(
                select(User).where(User.username == username)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error("Error getting user by username", username=username, error=str(e))
            return None
    
    @log_function_call(logger_name="services.user.auth", log_args=False)  # Don't log password
    @log_performance(threshold_ms=200.0)
    @log_errors(logger_name="services.user.auth")
    async def authenticate(self, username: str, password: str, ip_address: str = None, user_agent: str = None) -> Optional[User]:
        """
        Authenticate user with username/email and password.

        This is a critical security method that performs comprehensive logging
        for audit and security monitoring purposes.

        Args:
            username: Username or email for authentication
            password: User password (not logged for security)
            ip_address: Client IP address for security logging
            user_agent: Client user agent for security logging

        Returns:
            User object if authentication successful, None otherwise

        Security Logs:
            - All authentication attempts (success/failure)
            - Account lockout events
            - Failed login attempt increments
            - Suspicious activity detection
        """
        start_time = time.time()
        auth_context = {
            "username": username,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "operation": "authenticate",
            "timestamp": datetime.utcnow().isoformat()
        }

        self.logger.info(
            "Authentication attempt started",
            extra={
                **auth_context,
                "event_type": "auth_attempt_start"
            }
        )

        # Log to security logger
        security_logger.log_login_attempt(
            username=username,
            success=False,  # Will be updated if successful
            ip_address=ip_address or "unknown",
            user_agent=user_agent or "unknown"
        )

        try:
            # Try to find user by username or email
            user = await self.get_by_username(username)
            if not user:
                user = await self.get_by_email(username)

            duration_ms = (time.time() - start_time) * 1000

            if not user:
                self.logger.warning(
                    "Authentication failed - user not found",
                    extra={
                        **auth_context,
                        "duration_ms": duration_ms,
                        "failure_reason": "user_not_found",
                        "event_type": "auth_failed"
                    }
                )
                return None

            # Add user context to logging
            auth_context.update({
                "user_id": str(user.id),
                "user_email": user.email,
                "user_active": user.is_active,
                "failed_login_attempts": getattr(user, 'failed_login_attempts', 0)
            })

            # Check if account is locked
            if user.is_account_locked():
                duration_ms = (time.time() - start_time) * 1000
                self.logger.warning(
                    "Authentication failed - account locked",
                    extra={
                        **auth_context,
                        "duration_ms": duration_ms,
                        "failure_reason": "account_locked",
                        "event_type": "auth_failed_locked"
                    }
                )

                # Log security event
                security_logger.log_suspicious_activity(
                    description=f"Login attempt on locked account: {username}",
                    user_id=str(user.id),
                    ip_address=ip_address
                )

                return None

            # Check if account is active
            if not user.is_active:
                duration_ms = (time.time() - start_time) * 1000
                self.logger.warning(
                    "Authentication failed - account inactive",
                    extra={
                        **auth_context,
                        "duration_ms": duration_ms,
                        "failure_reason": "account_inactive",
                        "event_type": "auth_failed_inactive"
                    }
                )
                return None

            # Verify password
            if not user.verify_password(password):
                # Increment failed login attempts
                user.increment_failed_login()
                await self.db.commit()

                duration_ms = (time.time() - start_time) * 1000
                new_failed_attempts = getattr(user, 'failed_login_attempts', 0)

                self.logger.warning(
                    "Authentication failed - invalid password",
                    extra={
                        **auth_context,
                        "duration_ms": duration_ms,
                        "failure_reason": "invalid_password",
                        "failed_attempts_count": new_failed_attempts,
                        "event_type": "auth_failed_password"
                    }
                )

                # Check for suspicious activity (multiple failed attempts)
                if new_failed_attempts >= 3:
                    security_logger.log_suspicious_activity(
                        description=f"Multiple failed login attempts: {new_failed_attempts}",
                        user_id=str(user.id),
                        ip_address=ip_address
                    )

                return None

            # Successful authentication
            # Reset failed login attempts
            user.reset_failed_login()
            await self.db.commit()

            duration_ms = (time.time() - start_time) * 1000

            self.logger.info(
                "Authentication successful",
                extra={
                    **auth_context,
                    "duration_ms": duration_ms,
                    "user_role": user.role,
                    "last_login": user.last_login_at.isoformat() if user.last_login_at else None,
                    "event_type": "auth_success"
                }
            )

            # Log successful authentication to security logger
            security_logger.log_login_attempt(
                username=username,
                success=True,
                ip_address=ip_address or "unknown",
                user_agent=user_agent or "unknown"
            )

            # Log to structured logger for analytics
            self.structured_logger.info(
                "User authenticated",
                user_id=str(user.id),
                username=user.username,
                email=user.email,
                role=user.role,
                ip_address=ip_address,
                duration_ms=duration_ms
            )

            return user

        except SQLAlchemyError as e:
            duration_ms = (time.time() - start_time) * 1000
            self.logger.error(
                "Database error during authentication",
                extra={
                    **auth_context,
                    "duration_ms": duration_ms,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "event_type": "auth_database_error"
                },
                exc_info=True
            )
            return None
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.logger.error(
                "Unexpected error during authentication",
                extra={
                    **auth_context,
                    "duration_ms": duration_ms,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "event_type": "auth_unexpected_error"
                },
                exc_info=True
            )
            return None
    
    @log_function_call(logger_name="services.user.create")
    @log_performance(threshold_ms=500.0)
    @log_errors(logger_name="services.user.create")
    async def create_user(self, user_data: UserCreate, created_by: str = None, ip_address: str = None) -> User:
        """
        Create a new user with comprehensive audit logging.

        Args:
            user_data: User creation data
            created_by: ID of user who created this account (for admin creation)
            ip_address: IP address of the request

        Returns:
            Created User object

        Raises:
            IntegrityError: If username or email already exists
            SQLAlchemyError: For other database errors

        Logs:
            - User creation attempt
            - Validation steps
            - Database operations
            - Success/failure with full context
        """
        start_time = time.time()
        creation_context = {
            "email": user_data.email,
            "username": user_data.username,
            "full_name": user_data.full_name,
            "created_by": created_by,
            "ip_address": ip_address,
            "operation": "create_user",
            "timestamp": datetime.utcnow().isoformat()
        }

        self.logger.info(
            "User creation attempt started",
            extra={
                **creation_context,
                "event_type": "user_creation_start"
            }
        )

        # Log to audit logger
        audit_logger.info(
            "User creation initiated",
            extra={
                **creation_context,
                "event_type": "audit_user_creation_start"
            }
        )

        try:
            # Check for existing username
            existing_username = await self.get_by_username(user_data.username)
            if existing_username:
                duration_ms = (time.time() - start_time) * 1000
                self.logger.warning(
                    "User creation failed - username already exists",
                    extra={
                        **creation_context,
                        "duration_ms": duration_ms,
                        "failure_reason": "username_exists",
                        "existing_user_id": str(existing_username.id),
                        "event_type": "user_creation_failed"
                    }
                )
                raise IntegrityError("Username already exists", None, None)

            # Check for existing email
            existing_email = await self.get_by_email(user_data.email)
            if existing_email:
                duration_ms = (time.time() - start_time) * 1000
                self.logger.warning(
                    "User creation failed - email already exists",
                    extra={
                        **creation_context,
                        "duration_ms": duration_ms,
                        "failure_reason": "email_exists",
                        "existing_user_id": str(existing_email.id),
                        "event_type": "user_creation_failed"
                    }
                )
                raise IntegrityError("Email already exists", None, None)

            self.logger.debug(
                "User validation passed, creating user instance",
                extra={
                    **creation_context,
                    "event_type": "user_validation_passed"
                }
            )

            # Create user instance
            user = User(
                email=user_data.email,
                username=user_data.username,
                full_name=user_data.full_name,
                bio=user_data.bio,
                avatar_url=user_data.avatar_url,
                role="user",  # Default role
                is_active=True,
                is_verified=False,  # Require email verification
            )

            # Set password (this will be hashed)
            user.set_password(user_data.password)

            self.logger.debug(
                "User instance created, saving to database",
                extra={
                    **creation_context,
                    "user_role": user.role,
                    "user_active": user.is_active,
                    "user_verified": user.is_verified,
                    "event_type": "user_instance_created"
                }
            )

            # Add to database
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)

            duration_ms = (time.time() - start_time) * 1000

            # Update context with created user info
            creation_context.update({
                "user_id": str(user.id),
                "duration_ms": duration_ms
            })

            self.logger.info(
                "User created successfully",
                extra={
                    **creation_context,
                    "event_type": "user_creation_success"
                }
            )

            # Log to audit logger
            audit_logger.info(
                "User created",
                extra={
                    **creation_context,
                    "event_type": "audit_user_created"
                }
            )

            # Log to structured logger for analytics
            self.structured_logger.info(
                "New user registered",
                user_id=str(user.id),
                username=user.username,
                email=user_data.email,
                full_name=user_data.full_name,
                created_by=created_by,
                ip_address=ip_address,
                duration_ms=duration_ms
            )

            return user

        except IntegrityError as e:
            await self.db.rollback()
            duration_ms = (time.time() - start_time) * 1000

            self.logger.error(
                "User creation failed - integrity constraint violation",
                extra={
                    **creation_context,
                    "duration_ms": duration_ms,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "event_type": "user_creation_integrity_error"
                },
                exc_info=True
            )
            raise

        except SQLAlchemyError as e:
            await self.db.rollback()
            duration_ms = (time.time() - start_time) * 1000

            self.logger.error(
                "User creation failed - database error",
                extra={
                    **creation_context,
                    "duration_ms": duration_ms,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "event_type": "user_creation_database_error"
                },
                exc_info=True
            )
            raise

        except Exception as e:
            await self.db.rollback()
            duration_ms = (time.time() - start_time) * 1000

            self.logger.error(
                "User creation failed - unexpected error",
                extra={
                    **creation_context,
                    "duration_ms": duration_ms,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "event_type": "user_creation_unexpected_error"
                },
                exc_info=True
            )
            raise
    
    async def update_user(self, user_id: UUID, user_data: UserUpdate) -> Optional[User]:
        """Update user information."""
        try:
            user = await self.get_by_id(user_id)
            if not user:
                return None
            
            # Update fields
            update_data = user_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(user, field, value)
            
            user.updated_at = datetime.utcnow()
            
            await self.db.commit()
            await self.db.refresh(user)
            
            logger.info("User updated", user_id=str(user.id))
            return user
            
        except Exception as e:
            await self.db.rollback()
            logger.error("Error updating user", user_id=str(user_id), error=str(e))
            raise
    
    async def update_password(self, user_id: UUID, current_password: str, new_password: str) -> bool:
        """Update user password."""
        try:
            user = await self.get_by_id(user_id)
            if not user:
                return False
            
            # Verify current password
            if not user.verify_password(current_password):
                return False
            
            # Set new password
            user.set_password(new_password)
            
            await self.db.commit()
            
            logger.info("Password updated", user_id=str(user.id))
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error("Error updating password", user_id=str(user_id), error=str(e))
            return False
    
    @log_function_call(logger_name="services.user.login")
    @log_performance(threshold_ms=100.0)
    async def update_last_login(self, user_id: UUID, ip_address: str, user_agent: str = None) -> bool:
        """
        Update user's last login timestamp and IP address.

        Args:
            user_id: ID of the user
            ip_address: IP address of the login
            user_agent: User agent string (optional)

        Returns:
            True if update successful, False otherwise

        Logs:
            - Login timestamp updates
            - IP address tracking
            - Update success/failure
        """
        start_time = time.time()
        login_context = {
            "user_id": str(user_id),
            "ip_address": ip_address,
            "user_agent": user_agent,
            "operation": "update_last_login"
        }

        self.logger.debug(
            "Updating last login information",
            extra={
                **login_context,
                "event_type": "last_login_update_start"
            }
        )

        try:
            user = await self.get_by_id(user_id)
            if not user:
                duration_ms = (time.time() - start_time) * 1000
                self.logger.warning(
                    "Cannot update last login - user not found",
                    extra={
                        **login_context,
                        "duration_ms": duration_ms,
                        "event_type": "last_login_update_user_not_found"
                    }
                )
                return False

            # Store previous login info for logging
            previous_login = user.last_login_at

            # Update login information
            user.last_login_at = datetime.utcnow()
            # Note: If you have an IP address field in User model, update it here
            # user.last_login_ip = ip_address

            await self.db.commit()

            duration_ms = (time.time() - start_time) * 1000

            self.logger.info(
                "Last login updated successfully",
                extra={
                    **login_context,
                    "duration_ms": duration_ms,
                    "previous_login": previous_login.isoformat() if previous_login else None,
                    "new_login": user.last_login_at.isoformat(),
                    "username": user.username,
                    "event_type": "last_login_updated"
                }
            )

            # Log to structured logger for analytics
            self.structured_logger.info(
                "User login tracked",
                user_id=str(user_id),
                username=user.username,
                ip_address=ip_address,
                user_agent=user_agent,
                previous_login=previous_login.isoformat() if previous_login else None,
                duration_ms=duration_ms
            )

            return True

        except SQLAlchemyError as e:
            duration_ms = (time.time() - start_time) * 1000
            self.logger.error(
                "Database error updating last login",
                extra={
                    **login_context,
                    "duration_ms": duration_ms,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "event_type": "last_login_update_database_error"
                },
                exc_info=True
            )
            return False
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.logger.error(
                "Unexpected error updating last login",
                extra={
                    **login_context,
                    "duration_ms": duration_ms,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "event_type": "last_login_update_unexpected_error"
                },
                exc_info=True
            )
            return False
    
    async def deactivate_user(self, user_id: UUID) -> bool:
        """Deactivate a user account."""
        try:
            user = await self.get_by_id(user_id)
            if not user:
                return False
            
            user.is_active = False
            user.updated_at = datetime.utcnow()
            
            await self.db.commit()
            
            logger.info("User deactivated", user_id=str(user.id))
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error("Error deactivating user", user_id=str(user_id), error=str(e))
            return False
    
    async def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get list of users with pagination."""
        try:
            result = await self.db.execute(
                select(User)
                .offset(skip)
                .limit(limit)
                .order_by(User.created_at.desc())
            )
            return result.scalars().all()
            
        except Exception as e:
            logger.error("Error getting users", error=str(e))
            return []
    
    async def search_users(self, query: str, skip: int = 0, limit: int = 100) -> List[User]:
        """Search users by username, email, or full name."""
        try:
            search_pattern = f"%{query}%"
            result = await self.db.execute(
                select(User)
                .where(
                    (User.username.ilike(search_pattern)) |
                    (User.email.ilike(search_pattern)) |
                    (User.full_name.ilike(search_pattern))
                )
                .offset(skip)
                .limit(limit)
                .order_by(User.created_at.desc())
            )
            return result.scalars().all()
            
        except Exception as e:
            logger.error("Error searching users", query=query, error=str(e))
            return []
