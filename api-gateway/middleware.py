from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from jose import jwt, JWTError

from typing import Optional, Callable
import time
import logging
import json

from config import get_settings
from services import get_redis_client


settings = get_settings()
logger = logging.getLogger(__name__)
redis_service = get_redis_client()


def extract_user_id_from_request(request: Request) -> Optional[str]:
    """Extract user_id from JWT Bearer token.

    Shared helper used by both rate limiting and logging middleware.
    Returns None for unauthenticated requests (never raises).
    """
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        token = auth_header.replace("Bearer ", "")
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_exp": False},
        )
        return payload.get("sub")
    except JWTError:
        return None


class RateLimitMiddleware(BaseHTTPMiddleware):
    """User-aware rate limiting using Redis.

    IP-based rate limiting is handled by Nginx at the connection level.
    This middleware only enforces per-user limits for authenticated requests.
    Unauthenticated requests pass through (Nginx already rate-limits them by IP).
    """

    async def dispatch(self, request: Request, call_next: Callable) -> JSONResponse:
        user_id = extract_user_id_from_request(request)

        # Only rate-limit authenticated users at the app level.
        # Anonymous/IP-based limiting is handled by Nginx (limit_req_zone).
        if user_id:
            rate_limit_key = f"ratelimit:user:{user_id}"
            try:
                request_count = await redis_service.increment_rate_limit(
                    key=rate_limit_key, window=settings.RATE_LIMIT_WINDOW
                )
                remaining = max(0, settings.RATE_LIMIT_REQUESTS - request_count)

                if request_count > settings.RATE_LIMIT_REQUESTS:
                    logger.warning(
                        json.dumps({
                            "event": "rate_limit_exceeded",
                            "user_id": user_id,
                            "count": request_count,
                            "limit": settings.RATE_LIMIT_REQUESTS,
                        })
                    )
                    return JSONResponse(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        content={
                            "error": "Rate limit exceeded",
                            "detail": f"Maximum {settings.RATE_LIMIT_REQUESTS} requests per {settings.RATE_LIMIT_WINDOW} seconds",
                        },
                        headers={
                            "X-RateLimit-Limit": str(settings.RATE_LIMIT_REQUESTS),
                            "X-RateLimit-Remaining": "0",
                            "Retry-After": str(settings.RATE_LIMIT_WINDOW),
                        },
                    )
            except Exception as e:
                logger.error(f"Rate limit check failed: {e}")
                remaining = settings.RATE_LIMIT_REQUESTS
        else:
            remaining = settings.RATE_LIMIT_REQUESTS

        response = await call_next(request)

        # Always attach rate-limit headers for authenticated users
        if user_id:
            response.headers["X-RateLimit-Limit"] = str(settings.RATE_LIMIT_REQUESTS)
            response.headers["X-RateLimit-Remaining"] = str(remaining)

        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """Structured JSON logging with business context.

    Basic access logging (method, path, status, latency) is handled by Nginx.
    This middleware adds what Nginx can't: authenticated user identity, which
    enables audit trails and per-user debugging.
    """

    async def dispatch(self, request: Request, call_next: Callable):
        start_time = time.time()

        user_id = extract_user_id_from_request(request)

        response = await call_next(request)

        duration_ms = (time.time() - start_time) * 1000

        log_entry = {
            "event": "request",
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "duration_ms": round(duration_ms, 2),
            "user_id": user_id or "anonymous",
        }

        if response.status_code >= 400:
            logger.warning(json.dumps(log_entry))
        else:
            logger.info(json.dumps(log_entry))

        return response
