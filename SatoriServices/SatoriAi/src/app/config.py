import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Database Configuration
    DATABASE_URL: str = "postgresql://satori_user:admin1234@localhost:5434/satori"
    
    # Gemini AI Configuration
    GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY", None)
    GEMINI_MODEL: str = "gemini-1.5-flash"
    
    # Shared JWT authentication settings matching SatoriBackend
    JWT_SECRET_KEY: str = "sekret kalit, uni ozgartiring va xavfsiz saqlang"
    JWT_ISSUER: str = "SatoriApi"
    JWT_AUDIENCE: str = "SatoriUsers"
    
    # SatoriDocs Microservice URL
    SATORIDOCS_URL: str = "http://localhost:8000/api/v1"
    
    # App General Settings
    PROJECT_NAME: str = "SatoriAi"
    API_V1_STR: str = "/api/v1"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
