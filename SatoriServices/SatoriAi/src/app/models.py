import uuid
import datetime
from sqlalchemy import Column, String, Text, DateTime, Uuid
from app.database import Base

class UserKnowledge(Base):
    """
    RAG profile memory table. Stores facts and learnings about the user.
    To remain database-agnostic (supporting Postgres/SQLite fallback),
    embeddings are stored as serialized JSON strings of floats.
    """
    __tablename__ = "user_knowledge"
    
    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid, nullable=False)
    fact = Column(Text, nullable=False)
    embedding_str = Column(Text, nullable=False) # JSON-serialized float array
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class ChatMessage(Base):
    """
    History log table for chat conversation sessions.
    """
    __tablename__ = "chat_messages"
    
    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    session_id = Column(String(255), nullable=False, index=True)
    user_id = Column(Uuid, nullable=False)
    role = Column(String(50), nullable=False) # "user" or "assistant"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
