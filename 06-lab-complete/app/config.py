import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Production AI Agent"
    app_version: str = "1.0.0"
    environment: str = os.getenv("ENVIRONMENT", "development")
    
    # Server
    host: str = "0.0.0.0"
    port: int = int(os.getenv("PORT", 8000))
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Security
    agent_api_key: str = os.getenv("AGENT_API_KEY", "quoc123")
    jwt_secret: str = os.getenv("JWT_SECRET", "super-secret-key-change-it")
    
    # Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Limits
    rate_limit_per_minute: int = 10
    daily_budget_usd: float = 10.0
    
    # LLM
    llm_model: str = "gpt-4o-mini"

    class Config:
        env_file = ".env"

settings = Settings()
