from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from jose import jwt, JWTError

from typing import Optional, Callable
import time
import logging

from config import get_settings
from services import get_redis_client


settings = get_settings()
logger = logging.getLogger(__name__)
redis_service = get_redis_client()

class RateLimitMiddleware(BaseHTTPMiddleware):

    async def _extract_user_id(self, request: Request) -> Optional[str]:
        """First we need to extract the Authorization header from the request. The check if it has Bearer.
        If not we return None. Then we format the header to get the token. Extract sub from token and return.
        """
        try:
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return None
            token = auth_header.replace("Bearer ", "")
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM], options={"verify_exp": False})
            user_id = payload.get("sub")
            return user_id
        except JWTError:
            return None


    def _get_client_ip(self, request: Request) -> str:
        """client can make direct requests or can be behind a proxy(load balancer for example). First we look for
        X-Forwarded-For header in the request. If we find it we extract the real ip. If not then we can just extract
        the host.
        """
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
            return client_ip
        
        return request.client.host

    async def dispatch(self, request: Request, call_next: Callable) -> JSONResponse:
        """Intercept every request to impose rate limiting"""
        #1 Extract user id/ip
        #First we try to find ip from token, if not found we fallback to limitting by ip
        user_id = self._extract_user_id(request)
        if user_id:
            rate_limit_key = f"ratelimit:user:{user_id}"
        else:
            ip_addr = self._get_client_ip(request)
            rate_limit_key = f"ratelimit:ip:{ip_addr}"

        #2 Check rate limit in redis
        try:
            request_count = await redis_service.increment_rate_limit(key=rate_limit_key, window=settings.RATE_LIMIT_WINDOW)
            remaining = max(0, settings.RATE_LIMIT_REQUESTS - request_count)
            if request_count > settings.RATE_LIMIT_REQUESTS:
                logger.warning(f"Rate limit exceeded for {rate_limit_key}: "
                f"{request_count}/{settings.RATE_LIMIT_REQUESTS}"
                               )

                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "error": "Rate limit exceeded",
                        "detail": f"Maximum {settings.RATE_LIMIT_REQUESTS} requests per {settings.RATE_LIMIT_WINDOW} seconds"
                        },
                    headers={
                        "X-RateLimit-Limit": str(settings.RATE_LIMIT_REQUESTS),
                        "X-RateLimit-Remaining": "0",
                        # "X-RateLimit-Reset": str(self._get_reset_time()),
                        "Retry-After": str(settings.RATE_LIMIT_WINDOW)
                    }
                    

                )
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            remaining = settings.RATE_LIMIT_REQUESTS

        



        #3 If exceeded return 429
        #4 If ok, pass to next layer
        response = await call_next(request)
        #5 Add headers
        response.headers["X-RateLimit-Limit"] = str(settings.RATE_LIMIT_REQUESTS)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        # response.headers["X-RateLimit-Reset"]= str(self._get_reset_time()),


        return response
        

class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Log all requests with timing
    
    Logs:
    - Request method and path
    - Response status code
    - How long request took
    - User ID (if authenticated)
    """
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Start timer
        start_time = time.time()
        
        # Get user ID if available
        user_id = await self._extract_user_id(request)
        user_info = f"user:{user_id}" if user_id else "anonymous"
        
        # Process request
        response = await call_next(request)
        
        # Calculate how long it took
        duration_ms = (time.time() - start_time) * 1000
        
        # Log the request
        logger.info(
            f"{request.method} {request.url.path} - "
            f"{response.status_code} - "
            f"{duration_ms:.2f}ms - "
            f"{user_info}"
        )
        
        return response
    
    async def _extract_user_id(self, request: Request) -> Optional[str]:
        """Extract user_id from token (same as RateLimitMiddleware)"""
        try:
            auth_header = request.headers.get("Authorization")
            
            if not auth_header or not auth_header.startswith("Bearer "):
                return None
            
            token = auth_header.replace("Bearer ", "")
            
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
                options={"verify_exp": False}
            )
            
            return payload.get("sub")
        except:
            return None