from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime

class ChatRequest(BaseModel):
    message: str = Field(..., description="The user query or message")
    session_id: Optional[str] = Field(None, description="Active chat session ID. Generated automatically if empty.")

class ChatResponse(BaseModel):
    response: str = Field(..., description="The AI assistant response")
    session_id: str = Field(..., description="The session ID associated with the conversation")

class MessageResponse(BaseModel):
    role: str = Field(..., description="'user' or 'assistant'")
    content: str = Field(..., description="The content of the message")
    created_at: datetime

    class Config:
        from_attributes = True

class ProfileLearnRequest(BaseModel):
    fact: str = Field(..., min_length=3, description="A fact or instruction about the user to commit to vector store")

class ProfileFactResponse(BaseModel):
    id: UUID
    fact: str
    created_at: datetime

    class Config:
        from_attributes = True
