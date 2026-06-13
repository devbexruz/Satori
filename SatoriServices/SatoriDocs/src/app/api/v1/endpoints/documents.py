from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse, PlainTextResponse
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.models import Document
from app.schemas import (
    DocumentCreate, DocumentResponse, DocumentUpdate,
    OutlineGenerateRequest
)
from app import services
from app.auth import get_current_user

# Secure the entire router under JWT authentication
router = APIRouter(dependencies=[Depends(get_current_user)])

@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def create_document(
    doc_in: DocumentCreate, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new document linked to the authenticated user.
    """
    db_doc = Document(
        user_id=current_user["id"], 
        title=doc_in.title, 
        description=doc_in.description
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    return db_doc

@router.get("/", response_model=List[DocumentResponse])
def read_documents(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    List all documents belonging to the authenticated user.
    """
    return db.query(Document).filter(Document.user_id == current_user["id"]).offset(skip).limit(limit).all()

@router.get("/{document_id}", response_model=DocumentResponse)
def read_document(
    document_id: UUID, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Retrieve document details, verifying ownership.
    """
    db_doc = db.query(Document).filter(
        Document.id == document_id, 
        Document.user_id == current_user["id"]
    ).first()
    
    if not db_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    return db_doc

@router.put("/{document_id}", response_model=DocumentResponse)
def update_document(
    document_id: UUID, 
    doc_in: DocumentUpdate, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update document title or description, verifying ownership.
    """
    db_doc = db.query(Document).filter(
        Document.id == document_id, 
        Document.user_id == current_user["id"]
    ).first()
    
    if not db_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
        
    if doc_in.title is not None:
        db_doc.title = doc_in.title
    if doc_in.description is not None:
        db_doc.description = doc_in.description
    db.commit()
    db.refresh(db_doc)
    return db_doc

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: UUID, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a document, verifying ownership (cascades).
    """
    db_doc = db.query(Document).filter(
        Document.id == document_id, 
        Document.user_id == current_user["id"]
    ).first()
    
    if not db_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    db.delete(db_doc)
    db.commit()
    return None

@router.get("/{document_id}/export/md", response_class=PlainTextResponse)
def export_markdown(
    document_id: UUID, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Export the document as a Markdown string, verifying ownership.
    """
    db_doc = db.query(Document).filter(
        Document.id == document_id, 
        Document.user_id == current_user["id"]
    ).first()
    
    if not db_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    md_content = services.export_document_to_markdown(db_doc)
    return md_content

@router.get("/{document_id}/export/json")
def export_json(
    document_id: UUID, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Export the document hierarchy as a JSON object, verifying ownership.
    """
    db_doc = db.query(Document).filter(
        Document.id == document_id, 
        Document.user_id == current_user["id"]
    ).first()
    
    if not db_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    return services.export_document_to_json(db_doc)

@router.get("/{document_id}/export/docx")
def export_docx(
    document_id: UUID, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Generate and download the Microsoft Word (.docx) file, verifying ownership.
    """
    db_doc = db.query(Document).filter(
        Document.id == document_id, 
        Document.user_id == current_user["id"]
    ).first()
    
    if not db_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    file_stream = services.export_document_to_docx(db_doc)
    safe_title = "".join(c for c in db_doc.title if c.isalnum() or c in (" ", "_", "-")).rstrip()
    filename = f"{safe_title or 'document'}.docx"
    
    return StreamingResponse(
        file_stream,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename=\"{filename}\""}
    )

@router.post("/{document_id}/generate-outline", response_model=DocumentResponse)
def generate_outline(
    document_id: UUID, 
    req: OutlineGenerateRequest, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    AI-generates outline of modules and sections for this document, verifying ownership.
    """
    db_doc = db.query(Document).filter(
        Document.id == document_id, 
        Document.user_id == current_user["id"]
    ).first()
    
    if not db_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    try:
        outline = services.generate_document_outline(topic=req.topic, description=req.description)
        updated_doc = services.create_document_from_outline(db, document_id, outline)
        return updated_doc
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate outline: {str(e)}"
        )
