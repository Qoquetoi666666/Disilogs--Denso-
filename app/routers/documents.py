from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)

from sqlalchemy.orm import Session

from app import models
from app.db import get_db
from app.services.document_service import (
    process_pdf,
    load_extracted_document,
)


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


@router.post("/upload")
async def upload_document(
    machine_id: str = Form(...),
    title: str = Form(...),
    document_type: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    machine = (
        db.query(models.Machine)
        .filter(
            models.Machine.machine_id
            == machine_id
        )
        .first()
    )

    if machine is None:
        raise HTTPException(
            status_code=404,
            detail="Machine not found.",
        )

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Missing filename.",
        )

    if not file.filename.lower().endswith(
        ".pdf"
    ):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    content = await file.read()

    try:
        processed = process_pdf(
            file.filename,
            content,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"PDF processing failed: {exc}",
        )

    document = models.Document(
        machine_id=machine_id,
        title=title,
        filename=processed[
            "filename"
        ],
        document_type=document_type,
        source_path=processed[
            "pdf_path"
        ],
        indexed=False,
        document_key=processed[
            "document_key"
        ],
        extracted_path=processed[
            "extracted_path"
        ],
        page_count=processed[
            "page_count"
        ],
        total_characters=processed[
            "total_characters"
        ],
        status="READY",
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return {
        "status": "uploaded",
        "document": {
            "id": document.id,
            "document_key":
                document.document_key,
            "machine_id":
                document.machine_id,
            "title":
                document.title,
            "filename":
                document.filename,
            "document_type":
                document.document_type,
            "page_count":
                document.page_count,
            "total_characters":
                document.total_characters,
            "indexed":
                document.indexed,
            "status":
                document.status,
        },
    }


@router.get("/{machine_id}")
def list_documents(
    machine_id: str,
    db: Session = Depends(get_db),
):
    documents = (
        db.query(models.Document)
        .filter(
            models.Document.machine_id
            == machine_id
        )
        .order_by(
            models.Document.id.desc()
        )
        .all()
    )

    return {
        "machine_id": machine_id,
        "count": len(documents),
        "documents": [
            {
                "id": doc.id,
                "document_key":
                    doc.document_key,
                "title":
                    doc.title,
                "filename":
                    doc.filename,
                "document_type":
                    doc.document_type,
                "page_count":
                    doc.page_count,
                "total_characters":
                    doc.total_characters,
                "indexed":
                    doc.indexed,
                "status":
                    doc.status,
            }
            for doc in documents
        ],
    }


@router.get("/item/{document_id}")
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = (
        db.query(models.Document)
        .filter(
            models.Document.id
            == document_id
        )
        .first()
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    extracted = None

    if document.document_key:
        try:
            extracted = (
                load_extracted_document(
                    document.document_key
                )
            )
        except FileNotFoundError:
            extracted = None

    return {
        "document": {
            "id": document.id,
            "document_key":
                document.document_key,
            "machine_id":
                document.machine_id,
            "title":
                document.title,
            "filename":
                document.filename,
            "document_type":
                document.document_type,
            "source_path":
                document.source_path,
            "page_count":
                document.page_count,
            "total_characters":
                document.total_characters,
            "indexed":
                document.indexed,
            "status":
                document.status,
        },
        "extracted": extracted,
    }
