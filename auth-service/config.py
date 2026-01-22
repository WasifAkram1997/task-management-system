from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings"""

    AUTH_DB_PASSWORD: str
    JWT_SECRET_KEY: str

    
    APP_NAME: str = "Auth Service"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    HOST: str = "0.0.0.0"
    PORT: int = 8001

    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REDFRESH_TOKEN_EXPIRE_DAYS: int = 7

    DATABASE_URL: str = "postgresql://postgres:{AUTH_DB_PASSWORD}@localhost:5432/auth_db"

    class Config:
        env_file = ".env"

    def get_database_url(self) -> str:
        """Return database url with password filled in from env"""
        return self.DATABASE_URL.format(AUTH_DB_PASSWORD=self.AUTH_DB_PASSWORD)

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()