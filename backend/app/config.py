"""
Configuration management using Pydantic Settings.
Loads environment variables from .env file.
"""

from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "FullStack Agent App"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/agentapp"
    
    # JWT Authentication
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    AUTH_PROVIDER: Literal["local", "supabase"] = "local"
    
    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:4321", "http://localhost:3000"]
    
    # Agent Framework Selection
    AGENT_FRAMEWORK: Literal["crewai", "agno", "langchain"] = "crewai"
    
    # OpenAI API (optional - can use mock mode)
    OPENAI_API_KEY: str = "mock-key"
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    AGENT_MOCK_MODE: bool = True  # Set to False to use real OpenAI API
    
    # Redis (optional)
    REDIS_URL: str | None = None

    # Supabase (optional)
    SUPABASE_URL: str | None = None
    SUPABASE_ANON_KEY: str | None = None
    SUPABASE_SERVICE_ROLE_KEY: str | None = None
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


# Global settings instance
settings = Settings()
