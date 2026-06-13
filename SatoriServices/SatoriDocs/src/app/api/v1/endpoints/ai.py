from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import ChatRequest, ChatResponse
from app import services
from app.auth import get_current_user

# Secure the entire router under JWT authentication
router = APIRouter(dependencies=[Depends(get_current_user)])

@router.post("/chat", response_model=ChatResponse)
def ai_chat(
    req: ChatRequest, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    AI Document assistant conversational endpoint. 
    Verifies token and executes query tools (search, outline, read, edit) in the user's scope.
    """
    try:
        response_text = services.run_ai_chat_agent(
            db=db,
            user_id=current_user["id"],
            message=req.message,
            document_id=req.document_id
        )
        return ChatResponse(response=response_text)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"SatoriAI agent error: {str(e)}"
        )
