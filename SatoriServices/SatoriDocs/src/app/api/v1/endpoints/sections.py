from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.models import Section, Module, Document
from app.schemas import (
    SectionCreate, SectionResponse, SectionUpdate,
    SectionGenerateRequest, SectionEditRequest
)
from app import services
from app.auth import get_current_user

# Secure the entire router under JWT authentication
router = APIRouter(dependencies=[Depends(get_current_user)])

@router.post("/", response_model=SectionResponse, status_code=status.HTTP_201_CREATED)
def create_section(
    section_in: SectionCreate, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new section manually, verifying ownership of the parent document.
    """
    # Verify module exists and belongs to document owned by user
    module = db.query(Module).join(Document).filter(
        Module.id == section_in.module_id, 
        Document.user_id == current_user["id"]
    ).first()
    
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found or access denied"
        )
        
    # Verify parent section if provided belongs to document owned by user
    if section_in.parent_id:
        parent = db.query(Section).join(Module).join(Document).filter(
            Section.id == section_in.parent_id,
            Document.user_id == current_user["id"]
        ).first()
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent section not found or access denied"
            )
            
    db_section = Section(
        module_id=section_in.module_id,
        parent_id=section_in.parent_id,
        title=section_in.title,
        level=section_in.level,
        content=section_in.content,
        order=section_in.order
    )
    db.add(db_section)
    db.commit()
    db.refresh(db_section)
    return db_section

@router.get("/{section_id}", response_model=SectionResponse)
def read_section(
    section_id: UUID, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Retrieve details of a specific section, verifying ownership.
    """
    db_section = db.query(Section).join(Module).join(Document).filter(
        Section.id == section_id,
        Document.user_id == current_user["id"]
    ).first()
    
    if not db_section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Section not found or access denied"
        )
    return db_section

@router.put("/{section_id}", response_model=SectionResponse)
def update_section(
    section_id: UUID, 
    section_in: SectionUpdate, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update section details, verifying ownership.
    """
    db_section = db.query(Section).join(Module).join(Document).filter(
        Section.id == section_id,
        Document.user_id == current_user["id"]
    ).first()
    
    if not db_section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Section not found or access denied"
        )
        
    if section_in.title is not None:
        db_section.title = section_in.title
    if section_in.level is not None:
        db_section.level = section_in.level
    if section_in.content is not None:
        db_section.content = section_in.content
    if section_in.order is not None:
        db_section.order = section_in.order
        
    if section_in.parent_id is not None:
        if section_in.parent_id == section_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A section cannot be its own parent"
            )
        parent = db.query(Section).join(Module).join(Document).filter(
            Section.id == section_in.parent_id,
            Document.user_id == current_user["id"]
        ).first()
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent section not found or access denied"
            )
        db_section.parent_id = section_in.parent_id
        
    db.commit()
    db.refresh(db_section)
    return db_section

@router.delete("/{section_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_section(
    section_id: UUID, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a section, verifying ownership (cascades).
    """
    db_section = db.query(Section).join(Module).join(Document).filter(
        Section.id == section_id,
        Document.user_id == current_user["id"]
    ).first()
    
    if not db_section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Section not found or access denied"
        )
    db.delete(db_section)
    db.commit()
    return None

@router.post("/{section_id}/generate", response_model=SectionResponse)
def generate_content(
    section_id: UUID,
    req: SectionGenerateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    AI-generates content for this section, verifying ownership.
    """
    db_section = db.query(Section).join(Module).join(Document).filter(
        Section.id == section_id,
        Document.user_id == current_user["id"]
    ).first()
    
    if not db_section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Section not found or access denied"
        )
        
    # Build context for AI
    doc_title = db_section.module.document.title
    doc_desc = db_section.module.document.description or ""
    mod_title = db_section.module.title
    mod_desc = db_section.module.description or ""
    
    context = (
        f"Document Title: {doc_title}\n"
        f"Document Description: {doc_desc}\n"
        f"Module Title: {mod_title}\n"
        f"Module Description: {mod_desc}\n"
    )
    
    if db_section.parent:
        context += f"Parent Section Title: {db_section.parent.title}\n"
        
    try:
        content = services.generate_section_content(
            section_title=db_section.title,
            level=db_section.level,
            module_title=mod_title,
            context=context,
            prompt_instruction=req.prompt_instruction
        )
        
        db_section.content = content
        db.commit()
        db.refresh(db_section)
        return db_section
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate section content: {str(e)}"
        )

@router.post("/{section_id}/edit", response_model=SectionResponse)
def edit_content(
    section_id: UUID,
    req: SectionEditRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Refines/edits the existing content of the section, verifying ownership.
    """
    db_section = db.query(Section).join(Module).join(Document).filter(
        Section.id == section_id,
        Document.user_id == current_user["id"]
    ).first()
    
    if not db_section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Section not found or access denied"
        )
        
    doc_title = db_section.module.document.title
    doc_desc = db_section.module.document.description or ""
    context = f"Document: {doc_title}. Description: {doc_desc}."
    
    existing_content = db_section.content or ""
    
    try:
        refined_content = services.refine_section_content(
            content=existing_content,
            instruction=req.instruction,
            context=context
        )
        
        db_section.content = refined_content
        db.commit()
        db.refresh(db_section)
        return db_section
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to edit content: {str(e)}"
        )
