from fastapi import FastAPI, Request
from contextlib import asynccontextmanager

from config import get_settings
from services import get_redis_client, get_http_client
from middleware import RateLimitMiddleware, LoggingMiddleware
from routes import proxy_request

settings = get_settings()
redis_service = get_redis_client()
http_client = get_http_client()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await redis_service.connect()
    await http_client.connect()
    yield
    # Shutdown
    await redis_service.disconnect()
    await http_client.disconnect()

app = FastAPI(lifespan=lifespan, title=settings.APP_NAME, version=settings.VERSION)

# Add Middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware)

# Define Routes
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy(request: Request, path: str):
    return await proxy_request(request, path)

