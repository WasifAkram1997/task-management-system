"""
Configuration settings for the Task Service
"""

from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    TASK_DB_PASSWORD: str
    JWT_SECRET_KEY: str

    #RabbitMQ settings:
    RABBITMQ_USER: str = ""
    RABBITMQ_PASSWORD: str = ""
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_QUEUE: str = "notifications"

    # App settings with defaults
    APP_NAME: str = "Task Service"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    HOST: str = "0.0.0.0"
    PORT: int = 8002

    JWT_ALGORITHM: str = "HS256"

    DATABASE_URL: str = "postgresql://postgres:{TASK_DB_PASSWORD}@localhost:5434/task_db"

    class Config:
        env_file = "../.env"
        case_sensitive = True
        extra = "ignore"

    def get_database_url(self) -> str:
        """Return database url with password filled in from env"""
        return self.DATABASE_URL.format(TASK_DB_PASSWORD=self.TASK_DB_PASSWORD)
    
@lru_cache()
def get_settings() -> Settings:
    """Get cached settings. Loaded once. Single instance"""
    return Settings()