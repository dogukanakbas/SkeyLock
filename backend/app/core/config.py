from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "IoT Security Scanner"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./iot_security.db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Security
    JWT_SECRET: str = "your-super-secret-jwt-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    ALLOWED_HOSTS: List[str] = ["http://localhost:3000", "http://localhost:3001", "http://localhost:8000", "http://localhost:8002", "*"]
    
    # Stripe Payment
    STRIPE_SECRET_KEY: str = "sk_test_your_stripe_secret_key"
    STRIPE_PUBLIC_KEY: str = "pk_test_your_stripe_public_key"
    STRIPE_WEBHOOK_SECRET: str = "whsec_your_webhook_secret"
    
    # Email Settings
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    
    # Subscription Plans
    DEMO_DAYS: int = 7
    STARTER_PRICE: int = 2900  # $29.00 in cents
    PROFESSIONAL_PRICE: int = 9900  # $99.00 in cents
    ENTERPRISE_PRICE: int = 29900  # $299.00 in cents
    
    # Agent Settings
    AGENT_VERSION: str = "1.0.0"
    AGENT_UPDATE_URL: str = "https://api.iotsecurity.com/agent/update"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()