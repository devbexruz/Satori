from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.api.v1.router import api_router

# Auto-create tables on startup (if not already existing)
# In production, migrations (Alembic) are preferred, but this is perfect for the microservice dev setup.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="SatoriDocs microservice for modular document structuring, Markdown/JSON/Docx exports, and Gemini LangChain AI generation."
)

# Setup CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health", tags=["health"])
def health_check():
    """
    Healthcheck endpoint for SatoriDocs microservice.
    """
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "version": "1.0.0"
    }

@app.get("/", tags=["root"])
def root_endpoint():
    """
    Root endpoint redirect explanation.
    """
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API. Go to /docs for interactive Swagger UI."
    }
