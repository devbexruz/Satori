from fastapi import APIRouter
from app.api.v1.endpoints import chat

api_router = APIRouter()

# Mount all conversational agent routes under the '/ai' prefix
api_router.include_router(chat.router, prefix="/ai", tags=["ai"])
