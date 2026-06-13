from fastapi import APIRouter
from app.api.v1.endpoints import documents, modules, sections, ai

api_router = APIRouter()

api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(modules.router, prefix="/modules", tags=["modules"])
api_router.include_router(sections.router, prefix="/sections", tags=["sections"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
