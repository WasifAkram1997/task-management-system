import pytest
import pytest_asyncio
import asyncio
import redis.asyncio as redis
from redis.asyncio.connection import ConnectionPool
from fastapi.testclient import TestClient
from main import app
from config import get_settings

# Session-scoped event loop for async fixtures
@pytest.fixture(scope="session")
def event_loop():
    """Create a session-scoped event loop"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

# Get settings for password
settings = get_settings()

# Test Redis client (connects to localhost since tests run outside Docker)
test_redis_pool = None
test_redis_client = None

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_redis():
    """Setup test Redis on DB 1"""
    global test_redis_pool, test_redis_client

    # Create connection pool for localhost (tests run outside Docker)
    test_redis_pool = ConnectionPool(
        host="localhost",  # Use localhost for local tests
        port=6379,
        db=1,
        password=settings.REDIS_PASSWORD,
        decode_responses=True,
    )

    test_redis_client = redis.Redis(connection_pool=test_redis_pool)

    # Switch to test database (DB 1)
    # await test_redis_client.execute_command("SELECT", 1)

    yield

    # Cleanup
    await test_redis_client.flushdb()
    await test_redis_client.aclose()
    await test_redis_pool.disconnect()

@pytest_asyncio.fixture(scope="function", autouse=True)
async def redis_cleanup():
    """Clear Redis before each test"""
    await test_redis_client.flushdb()
    yield

@pytest.fixture(scope="function")  
def client():
    """Test client for API Gateway"""
    yield TestClient(app)