"""
Configuration settings for the notification service.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings"""

    #Required from environment
    RABBITMQ_USER: str
    RABBITMQ_PASSWORD: str

    #App info
    APP_NAME: str = "Notification Service"
    VERSION: str = "1.0.0"

    #RabbitMQ settings
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    QUEUE_NAME: str =  "notifications"

    # Email settings
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str
    SMTP_PASSWORD: str
    SMTP_FROM_EMAIL: str

    class Config:
        env_file  = "../.env"
        case_sensitive = True
        extra = "ignore"

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings. Load once"""
    return Settings()