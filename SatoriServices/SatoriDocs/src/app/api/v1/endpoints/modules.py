from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.models import Module, Section, Document
from app.schemas import ModuleCreate, ModuleResponse, ModuleUpdate
from app import services
from app.auth import get_current_user

# Secure the entire router under JWT authentication
router = APIRouter(dependencies=[Depends(get_current_user)])

@router.post("/", response_model=ModuleResponse, status_code=status.HTTP_201_CREATED)
def create_module(
    module_in: ModuleCreate, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new module within a document, verifying user ownership of the document.
    """
    # Verify document exists and belongs to the current user
    doc = db.query(Document).filter(
        Document.id == module_in.document_id, 
        Document.user_id == current_user["id"]
    ).first()
    
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found or access denied"
        )
        
    db_module = Module(
        document_id=module_in.document_id,
        title=module_in.title,
        description=module_in.description,
        order=module_in.order
    )
    db.add(db_module)
    db.commit()
    db.refresh(db_module)
    return db_module

@router.get("/", response_model=List[ModuleResponse])
def read_modules(
    document_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    List modules of a document, verifying document ownership.
    """
    query = db.query(Module).join(Document)
    
    # Filter by user's documents
    query = query.filter(Document.user_id == current_user["id"])
    
    if document_id:
        query = query.filter(Module.document_id == document_id)
        
    return query.order_by(Module.order).offset(skip).limit(limit).all()

@router.get("/{module_id}", response_model=ModuleResponse)
def read_module(
    module_id: UUID, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Retrieve module details, verifying ownership of the parent document.
    """
    db_module = db.query(Module).join(Document).filter(
        Module.id == module_id, 
        Document.user_id == current_user["id"]
    ).first()
    
    if not db_module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found or access denied"
        )
    return db_module

@router.put("/{module_id}", response_model=ModuleResponse)
def update_module(
    module_id: UUID, 
    module_in: ModuleUpdate, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update module details, verifying ownership of the parent document.
    """
    db_module = db.query(Module).join(Document).filter(
        Module.id == module_id, 
        Document.user_id == current_user["id"]
    ).first()
    
    if not db_module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found or access denied"
        )
        
    if module_in.title is not None:
        db_module.title = module_in.title
    if module_in.description is not None:
        db_module.description = module_in.description
    if module_in.order is not None:
        db_module.order = module_in.order
        
    db.commit()
    db.refresh(db_module)
    return db_module

@router.delete("/{module_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_module(
    module_id: UUID, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a module, verifying ownership of the parent document.
    """
    db_module = db.query(Module).join(Document).filter(
        Module.id == module_id, 
        Document.user_id == current_user["id"]
    ).first()
    
    if not db_module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found or access denied"
        )
        
    db.delete(db_module)
    db.commit()
    return None

@router.post("/{module_id}/generate-sections", response_model=ModuleResponse)
def generate_sections(
    module_id: UUID, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    AI-generates section outlines for this module, verifying ownership.
    """
    db_module = db.query(Module).join(Document).filter(
        Module.id == module_id, 
        Document.user_id == current_user["id"]
    ).first()
    
    if not db_module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found or access denied"
        )
        
    try:
        sections_outline = services.generate_module_sections(
            module_title=db_module.title, 
            module_desc=db_module.description
        )
        
        # Clear existing sections under this module
        db.query(Section).filter(Section.module_id == module_id).delete()
        
        # Recursively save sections
        def save_sections_recursive(sections_list, parent_id=None):
            for s_idx, s_outline in enumerate(sections_list):
                db_section = Section(
                    module_id=module_id,
                    parent_id=parent_id,
                    title=s_outline.title,
                    level=s_outline.level,
                    content="",  # Blank initially
                    order=s_idx
                )
                db.add(db_section)
                db.flush()
                
                if s_outline.children:
                    save_sections_recursive(s_outline.children, db_section.id)
                    
        save_sections_recursive(sections_outline)
        db.commit()
        db.refresh(db_module)
        return db_module
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate sections: {str(e)}"
        )
