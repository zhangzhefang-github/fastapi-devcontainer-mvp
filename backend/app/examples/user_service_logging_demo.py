"""
Demonstration of the enhanced UserService with comprehensive logging.
This example shows how the logging works in practice.
"""
import asyncio
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.logging_config import setup_logging, get_logger
from app.services.user_service import UserService
from app.schemas.user import UserCreate
from app.models.user import User, Base

# Setup logging
setup_logging()
logger = get_logger("demo.user_service")

# Mock database setup (in real app, this would be configured properly)
DATABASE_URL = "sqlite+aiosqlite:///./demo.db"


async def create_demo_database():
    """Create demo database and tables."""
    engine = create_async_engine(DATABASE_URL, echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    return engine


async def get_demo_session(engine):
    """Get demo database session."""
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session


async def demo_user_operations():
    """Demonstrate UserService operations with logging."""
    
    logger.info("Starting UserService logging demonstration")
    
    # Create database and session
    engine = await create_demo_database()
    
    async with AsyncSession(engine) as session:
        user_service = UserService(session)
        
        # Demo 1: Create users
        logger.info("=== Demo 1: User Creation ===")
        
        demo_users = [
            UserCreate(
                email="alice@example.com",
                username="alice",
                password="SecurePass123!",
                full_name="Alice Johnson",
                bio="Software developer passionate about Python"
            ),
            UserCreate(
                email="bob@example.com",
                username="bob",
                password="AdminPass456!",
                full_name="Bob Smith",
                bio="System administrator and DevOps engineer"
            ),
            UserCreate(
                email="charlie@example.com",
                username="charlie",
                password="TestPass789!",
                full_name="Charlie Brown",
                bio="QA engineer and testing enthusiast"
            )
        ]
        
        created_users = []
        for user_data in demo_users:
            try:
                user = await user_service.create_user(
                    user_data=user_data,
                    created_by="system",
                    ip_address="192.168.1.100"
                )
                created_users.append(user)
                logger.info(f"Created user: {user.username}")
            except Exception as e:
                logger.error(f"Failed to create user {user_data.username}: {str(e)}")
        
        # Demo 2: Authentication attempts
        logger.info("=== Demo 2: Authentication ===")
        
        # Successful authentication
        auth_user = await user_service.authenticate(
            username="alice",
            password="SecurePass123!",
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0 (Demo Browser)"
        )
        
        if auth_user:
            logger.info(f"Authentication successful for: {auth_user.username}")
            
            # Update last login
            await user_service.update_last_login(
                user_id=auth_user.id,
                ip_address="192.168.1.100",
                user_agent="Mozilla/5.0 (Demo Browser)"
            )
        
        # Failed authentication (wrong password)
        failed_auth = await user_service.authenticate(
            username="alice",
            password="WrongPassword",
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0 (Demo Browser)"
        )
        
        if not failed_auth:
            logger.info("Authentication failed as expected (wrong password)")
        
        # Failed authentication (non-existent user)
        failed_auth2 = await user_service.authenticate(
            username="nonexistent",
            password="AnyPassword",
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0 (Demo Browser)"
        )
        
        if not failed_auth2:
            logger.info("Authentication failed as expected (user not found)")
        
        # Demo 3: User retrieval
        logger.info("=== Demo 3: User Retrieval ===")
        
        if created_users:
            # Get user by ID
            user_by_id = await user_service.get_by_id(created_users[0].id)
            if user_by_id:
                logger.info(f"Retrieved user by ID: {user_by_id.username}")
            
            # Get user by username
            user_by_username = await user_service.get_by_username("bob")
            if user_by_username:
                logger.info(f"Retrieved user by username: {user_by_username.username}")
            
            # Get user by email
            user_by_email = await user_service.get_by_email("charlie@example.com")
            if user_by_email:
                logger.info(f"Retrieved user by email: {user_by_email.username}")
        
        # Demo 4: User search and listing
        logger.info("=== Demo 4: User Search and Listing ===")
        
        # Get all users
        all_users = await user_service.get_users(skip=0, limit=10)
        logger.info(f"Retrieved {len(all_users)} users")
        
        # Search users
        search_results = await user_service.search_users("alice", skip=0, limit=10)
        logger.info(f"Search for 'alice' returned {len(search_results)} results")
        
        # Demo 5: Error scenarios
        logger.info("=== Demo 5: Error Scenarios ===")
        
        # Try to create duplicate user
        try:
            duplicate_user = UserCreate(
                email="alice@example.com",  # Duplicate email
                username="alice_duplicate",
                password="Password123!",
                full_name="Alice Duplicate"
            )
            await user_service.create_user(duplicate_user)
        except Exception as e:
            logger.info(f"Duplicate user creation failed as expected: {type(e).__name__}")
        
        # Try to get non-existent user
        non_existent = await user_service.get_by_id(uuid.uuid4())
        if not non_existent:
            logger.info("Non-existent user lookup returned None as expected")
        
        # Demo 6: Multiple failed login attempts (security logging)
        logger.info("=== Demo 6: Security Scenarios ===")
        
        if created_users:
            # Simulate multiple failed login attempts
            for i in range(5):
                failed_auth = await user_service.authenticate(
                    username=created_users[0].username,
                    password="WrongPassword",
                    ip_address="192.168.1.200",  # Different IP
                    user_agent="Suspicious Browser"
                )
                logger.info(f"Failed login attempt {i+1}")
        
        logger.info("UserService logging demonstration completed")
        
        # Show some statistics
        logger.info("=== Demo Statistics ===")
        logger.info(f"Total users created: {len(created_users)}")
        logger.info(f"Total users in database: {len(all_users)}")
        
    await engine.dispose()


async def demo_performance_logging():
    """Demonstrate performance logging with bulk operations."""
    
    logger.info("Starting performance logging demonstration")
    
    engine = await create_demo_database()
    
    async with AsyncSession(engine) as session:
        user_service = UserService(session)
        
        # Create multiple users to test performance
        start_time = datetime.utcnow()
        
        for i in range(10):
            try:
                user_data = UserCreate(
                    email=f"perftest{i}@example.com",
                    username=f"perftest{i}",
                    password="TestPass123!",
                    full_name=f"Performance Test User {i}"
                )
                
                await user_service.create_user(
                    user_data=user_data,
                    created_by="performance_test",
                    ip_address="127.0.0.1"
                )
                
            except Exception as e:
                logger.error(f"Performance test user {i} creation failed: {str(e)}")
        
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        logger.info(f"Performance test completed in {duration:.2f} seconds")
        
        # Test bulk retrieval
        all_users = await user_service.get_users(skip=0, limit=100)
        logger.info(f"Bulk retrieval of {len(all_users)} users completed")
    
    await engine.dispose()


if __name__ == "__main__":
    print("🚀 Starting UserService Logging Demonstration")
    print("=" * 50)
    
    # Run the demonstrations
    asyncio.run(demo_user_operations())
    
    print("\n" + "=" * 50)
    print("🏃 Starting Performance Logging Demonstration")
    print("=" * 50)
    
    asyncio.run(demo_performance_logging())
    
    print("\n" + "=" * 50)
    print("✅ Demonstration completed!")
    print("📋 Check the logs directory for detailed log output:")
    print("   - logs/app.log (detailed logs)")
    print("   - logs/error.log (error logs)")
    print("   - logs/app.json (structured JSON logs)")
    print("   - logs/security.log (security events)")
    print("   - logs/performance.log (performance metrics)")
    print("\n💡 Use the log management tool to analyze logs:")
    print("   ./scripts/log-manager.sh analyze")
    print("   ./scripts/log-manager.sh search 'user_creation' all 3")
    print("   ./scripts/log-manager.sh follow all")
