"""API gateway service settings"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    """Service settings loaded from environment variables"""

    #Required settings(no default)
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"

    REDIS_PASSWORD: str

    AUTH_SERVICE_URL: str = "http://localhost:8000"
    TASK_SERVICE_URL: str = "http://localhost:8002"

    REDIS_HOST: str = "localhost"
    REDIS_PORT: str = 6379

    REDIS_DB: int = 0
    REDIS_MAX_CONNECTIONS: int = 50
    
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60

    #Service settings
    APP_NAME: str = "API Gateway"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    HTTP_TIMEOUT : int = 30

    class Config:
        env_file = "../.env"
        case_sensitive = True
        exrta = "ignore"

@lru_cache
def get_settings() -> Settings:
        return Settings()    


