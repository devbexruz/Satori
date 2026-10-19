"""
SATORI ECOSYSTEM — ItachiAssist Backend
========================================
backend/app/config.py

Konfiguratsiya — .env fayldan o'qiladi.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Server
    HOST: str = "127.0.0.1"
    PORT: int = 8765

    # PostgreSQL (SatoriBackend ning DB si bilan ulash mumkin)
    DATABASE_URL: str = "postgresql+asyncpg://satori:satori@localhost:5432/satoridb"

    # Redis (Celery uchun)
    REDIS_URL: str = "redis://localhost:6379/0"

    # AI API kalitlar
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""

    # AI Model routing
    LLM_FAST_MODEL: str = "gemini-2.0-flash-lite"
    LLM_DEEP_MODEL: str = "gemini-2.5-pro"
    LLM_FAST_MAX_TOKENS: int = 150      # Bu dan katta → Deep model
    LLM_CONTEXT_WINDOW_MINUTES: int = 30

    # Satori Core Backend
    SATORI_BACKEND_URL: str = "http://localhost:8080"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
