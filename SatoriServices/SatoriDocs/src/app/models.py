import uuid
import datetime
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Uuid
from sqlalchemy.orm import relationship
from app.database import Base

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    modules = relationship("Module", back_populates="document", cascade="all, delete-orphan", order_by="Module.order")


class Module(Base):
    __tablename__ = "modules"
    
    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    document_id = Column(Uuid, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    document = relationship("Document", back_populates="modules")
    sections = relationship("Section", back_populates="module", cascade="all, delete-orphan", order_by="Section.order")


class Section(Base):
    __tablename__ = "sections"
    
    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    module_id = Column(Uuid, ForeignKey("modules.id", ondelete="CASCADE"), nullable=False)
    parent_id = Column(Uuid, ForeignKey("sections.id", ondelete="CASCADE"), nullable=True)
    title = Column(String(255), nullable=False)
    level = Column(Integer, default=1)  # 1=H1, 2=H2, 3=H3, 4=H4, 5=H5
    content = Column(Text, nullable=True)
    order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    module = relationship("Module", back_populates="sections")
    
    # Self-referential relationship to support nested sections
    parent = relationship("Section", remote_side=[id], back_populates="children")
    children = relationship("Section", back_populates="parent", cascade="all, delete-orphan", order_by="Section.order")
