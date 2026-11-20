from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.database import get_db
from app.schemas import ChatRequest, ChatResponse, MessageResponse, ProfileLearnRequest, ProfileFactResponse
from app.models import ChatMessage
from app.auth import get_current_user
from app import services

# Protect all endpoints inside this router under JWT authentication
router = APIRouter(dependencies=[Depends(get_current_user)])

@router.post("/chat", response_model=ChatResponse)
def chat_with_agent(
    req: ChatRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Conversational chat agent endpoint. Exposes tools to interact with documents
    on SatoriDocs and automatically loads personal context.
    """
    session_id = req.session_id or f"session_{uuid.uuid4()}"
    try:
        response_text = services.run_satori_agent(
            db=db,
            user_id=current_user["id"],
            token=current_user["token"],
            session_id=session_id,
            message=req.message
        )
        return ChatResponse(response=response_text, session_id=session_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"SatoriAI agent exception: {str(e)}"
        )

@router.get("/history/{session_id}", response_model=List[MessageResponse])
def get_chat_history(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Retrieve conversational message logs for a specific session ID, restricted by user ownership.
    """
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id,
        ChatMessage.user_id == current_user["id"]
    ).order_by(ChatMessage.created_at.asc()).all()
    return messages

@router.get("/sessions")
def get_chat_sessions(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Retrieve unique chat session IDs and their titles (based on the first message) for the user.
    """
    from app.models import ChatMessage
    from sqlalchemy import func
    
    # Subquery to find the first message per session
    subq = db.query(
        ChatMessage.session_id,
        func.min(ChatMessage.created_at).label("first_msg_time")
    ).filter(
        ChatMessage.user_id == current_user["id"]
    ).group_by(
        ChatMessage.session_id
    ).subquery()
    
    first_messages = db.query(
        ChatMessage.session_id,
        ChatMessage.content,
        ChatMessage.created_at
    ).join(
        subq,
        (ChatMessage.session_id == subq.c.session_id) & 
        (ChatMessage.created_at == subq.c.first_msg_time)
    ).order_by(
        ChatMessage.created_at.desc()
    ).all()
    
    return [
        {
            "id": m.session_id,
            "title": m.content[:40] + ("..." if len(m.content) > 40 else ""),
            "created_at": m.created_at
        }
        for m in first_messages
    ]

@router.post("/profile", response_model=ProfileFactResponse, status_code=status.HTTP_201_CREATED)
def add_profile_fact(
    req: ProfileLearnRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Ingests a custom detail or preference about the user into their RAG database memory.
    """
    try:
        db_fact = services.learn_user_fact(
            db=db,
            user_id=current_user["id"],
            fact=req.fact
        )
        return db_fact
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/profile", response_model=List[ProfileFactResponse])
def get_profile_facts(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Retrieve all custom details/preferences saved for the authenticated user.
    """
    from app.models import UserKnowledge
    facts = db.query(UserKnowledge).filter(
        UserKnowledge.user_id == current_user["id"]
    ).order_by(UserKnowledge.created_at.desc()).all()
    return facts

@router.delete("/profile/{fact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_profile_fact(
    fact_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a saved detail/preference from the user's RAG memory by its ID.
    """
    from app.models import UserKnowledge
    db_fact = db.query(UserKnowledge).filter(
        UserKnowledge.id == fact_id,
        UserKnowledge.user_id == current_user["id"]
    ).first()
    if not db_fact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fact not found or not owned by user"
        )
    db.delete(db_fact)
    db.commit()
