"""
Application configuration settings.
"""
from pydantic_settings import BaseSettings
from pydantic import Field, computed_field
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    DATABASE_URL: str = "mysql+pymysql://root:password@localhost:3306/auction_navigator?charset=utf8mb4"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # CORS: store as string from env (comma-separated), expose as list via property
    cors_origins_raw: str = Field(
        default="http://localhost:5173,http://localhost:3000",
        alias="CORS_ORIGINS",
        description="Comma-separated list of allowed origins",
    )
    FRONTEND_DOMAIN: Optional[str] = None  # Production frontend domain

    @computed_field
    @property
    def CORS_ORIGINS(self) -> List[str]:
        if self.FRONTEND_DOMAIN:
            return [self.FRONTEND_DOMAIN]
        return [x.strip() for x in self.cors_origins_raw.split(",") if x.strip()]
    
    # API
    API_V1_PREFIX: str = "/api"
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # Scraping
    SCRAPER_RATE_LIMIT_REQUESTS: int = 10  # Requests per window
    SCRAPER_RATE_LIMIT_WINDOW: int = 60  # Window in seconds
    SCRAPER_RETRY_MAX_ATTEMPTS: int = 3
    SCRAPER_RETRY_BACKOFF_FACTOR: float = 2.0
    SCRAPER_TIMEOUT: int = 30  # Request timeout in seconds
    
    # Celery
    CELERY_BROKER_URL: Optional[str] = None  # Override REDIS_URL if needed
    CELERY_RESULT_BACKEND: Optional[str] = None  # Override REDIS_URL if needed
    CELERY_TASK_RETRY_DELAY: int = 60  # Seconds
    
    # Email
    EMAIL_PROVIDER: str = "stub"  # stub, sendgrid, mailgun
    EMAIL_FROM_ADDRESS: str = "noreply@auctionnavigator.com"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
