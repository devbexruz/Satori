import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Database configuration
    # Default is configured for the host mapping of the satori-db container (localhost:5434)
    DATABASE_URL: str = "postgresql://satori_user:admin1234@localhost:5434/satori"
    
    # Gemini AI configuration
    GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY", None)
    GEMINI_MODEL: str = "gemini-1.5-flash"
    
    # App general settings
    PROJECT_NAME: str = "SatoriDocs"
    API_V1_STR: str = "/api/v1"
    
    # JWT authentication settings matching SatoriBackend
    JWT_SECRET_KEY: str = "sekret kalit, uni ozgartiring va xavfsiz saqlang"
    JWT_ISSUER: str = "SatoriApi"
    JWT_AUDIENCE: str = "SatoriUsers"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
