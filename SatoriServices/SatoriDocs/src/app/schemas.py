from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime

# --- SECTION SCHEMAS ---

class SectionBase(BaseModel):
    title: str = Field(..., description="Title of the section heading")
    level: int = Field(1, ge=1, le=5, description="Heading level: 1=H1, 2=H2, 3=H3, 4=H4, 5=H5")
    content: Optional[str] = Field(None, description="Markdown/text content of the section")
    order: int = Field(0, description="Order of the section within the parent/module")

class SectionCreate(SectionBase):
    module_id: UUID = Field(..., description="The ID of the parent module")
    parent_id: Optional[UUID] = Field(None, description="The ID of the parent section (for nesting)")

class SectionUpdate(BaseModel):
    title: Optional[str] = None
    level: Optional[int] = Field(None, ge=1, le=5)
    content: Optional[str] = None
    order: Optional[int] = None
    parent_id: Optional[UUID] = None

class SectionResponse(SectionBase):
    id: UUID
    module_id: UUID
    parent_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    children: List["SectionResponse"] = []

    class Config:
        from_attributes = True

# Rebuild model to resolve self-referential annotations
SectionResponse.model_rebuild()


# --- MODULE SCHEMAS ---

class ModuleBase(BaseModel):
    title: str = Field(..., description="Title of the module")
    description: Optional[str] = Field(None, description="Brief description of the module")
    order: int = Field(0, description="Ordering key")

class ModuleCreate(ModuleBase):
    document_id: UUID

class ModuleUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    order: Optional[int] = None

class ModuleResponse(ModuleBase):
    id: UUID
    document_id: UUID
    created_at: datetime
    updated_at: datetime
    sections: List[SectionResponse] = []

    class Config:
        from_attributes = True


# --- DOCUMENT SCHEMAS ---

class DocumentBase(BaseModel):
    title: str = Field(..., description="Title of the document")
    description: Optional[str] = Field(None, description="General description of the document")

class DocumentCreate(DocumentBase):
    pass

class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class DocumentResponse(DocumentBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    modules: List[ModuleResponse] = []

    class Config:
        from_attributes = True


# --- AI GENERATION SCHEMAS ---

class SectionOutline(BaseModel):
    title: str = Field(..., description="Heading title of the section")
    level: int = Field(1, ge=1, le=5, description="Heading level from 1 (H1) to 5 (H5)")
    children: List["SectionOutline"] = Field(default=[], description="Nested sub-sections under this heading")

SectionOutline.model_rebuild()

class ModuleOutline(BaseModel):
    title: str = Field(..., description="Title of the module")
    description: Optional[str] = Field(None, description="Brief description of what this module covers")
    sections: List[SectionOutline] = Field(default=[], description="List of top-level sections in the module")

class DocumentOutline(BaseModel):
    title: str = Field(..., description="Title of the document")
    description: Optional[str] = Field(None, description="General description of the document")
    modules: List[ModuleOutline] = Field(default=[], description="List of modules in the document")


# --- API REQUESTS FOR AI ---

class OutlineGenerateRequest(BaseModel):
    topic: str = Field(..., min_length=3, description="Topic/prompt to generate the document outline")
    description: Optional[str] = Field(None, description="Additional context or requirements for the document")

class SectionGenerateRequest(BaseModel):
    prompt_instruction: Optional[str] = Field(None, description="Custom instruction for the AI (e.g. 'explain how Python decorators work')")

class SectionEditRequest(BaseModel):
    instruction: str = Field(..., description="Natural language instructions for SatoriAi to edit the content (e.g. 'translate to English', 'make it concise')")


# --- CHAT SCHEMAS ---

class ChatRequest(BaseModel):
    message: str = Field(..., description="The user's chat message to the SatoriAI assistant")
    document_id: Optional[UUID] = Field(None, description="Optional document ID to focus the query on")

class ChatResponse(BaseModel):
    response: str = Field(..., description="The AI assistant's text response")
