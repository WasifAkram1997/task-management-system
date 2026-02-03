"""Service clients for API Gateway. Redis and HTTP client connection pool."""

import redis.asyncio as redis
from redis.asyncio.connection import ConnectionPool
from redis.exceptions import RedisError, ConnectionError as RedisConnectionError
import httpx
from typing import Optional
import logging
from config import get_settings

#Get settings instance
settings = get_settings()

#Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#Redis service
class RedisService:
    def __init__(self):
        self.pool: Optional[ConnectionPool] = None
        self.client: Optional[redis.Redis] = None
    
    async def connect(self) -> None:
        try:
            # Create connection pool
            self.pool = ConnectionPool(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                max_connections=settings.REDIS_MAX_CONNECTIONS,
                decode_responses=True,  # Auto-decode bytes to strings
                socket_connect_timeout=5,  # 5s to establish connection
                socket_timeout=5,  # 5s to complete read/write
                retry_on_timeout=True,  # Retry if operation times out
            )

            self.client = redis.Redis(connection_pool=self.pool)

            await self.client.ping()

            logger.info(
                f"✓ Redis connected: {settings.REDIS_HOST}:{settings.REDIS_PORT} "
                f"(pool size: {settings.REDIS_MAX_CONNECTIONS})"
            )
        except RedisConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise RuntimeError(f"Redis connection failed")
    
    async def disconnect(self):
        if self.client:
            await self.client.close()
        
        if self.pool:
            await self.pool.disconnect()
        
        logger.info("Redis disconnected")
    
    async def health_check(self) -> bool:
        try:
            if not self.client:
                return False
            
            await self.client.ping()
            logger.info("Redis health check passed")
            return True
        except RedisError:
            logger.error("Redis health check failed")
            return False
    async def increment_rate_limit(self, key: str, window: int) -> int:
        if not self.client:
            logger.error("Redis client not connected")
            return 0 #Fail open
        try:
            count = await self.client.incr(key)
            if count == 1:
                await self.client.expire(key, window)
            return count
        except RedisError as e:
            logger.error(f"Rate limit increment failed: {e}")
            return 0
        
#HTTP Service
class HTTPClientService:
    def __init__(self):
        self.client: Optional[httpx.AsyncClient] = None
    async def connect(self) -> None:
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(settings.HTTP_TIMEOUT),
            limits=httpx.Limits(
                max_connections=100,
                max_keepalive_connections=20
            ),
            follow_redirects=True,
        )
        logger.info("HTTP client initialized")

    async def disconnect(self) -> None:
        if self.client:
            await self.client.aclose()
        logger.info("HTTP client closed")

redis_service = RedisService()
http_client_service = HTTPClientService()

def get_redis_client() -> RedisService:
    return redis_service

def get_http_client() -> HTTPClientService:
    return http_client_service

    