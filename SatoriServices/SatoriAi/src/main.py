from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.api.v1.router import api_router

# Auto-create database tables on startup (PostgreSQL or SQLite fallback)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="SatoriAi intelligence coordinator, utilizing RAG memory and integrating SatoriDocs capabilitiesConversations."
)

# Enable CORS for frontend integrations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount endpoints under v1 path
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health", tags=["health"])
def health_check():
    """
    Healthcheck endpoint.
    """
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "version": "1.0.0"
    }

@app.get("/", tags=["root"])
def root_endpoint():
    """
    Redirect information.
    """
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API. Navigate to /docs for Swagger specifications."
    }
