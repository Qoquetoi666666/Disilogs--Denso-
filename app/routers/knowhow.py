from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app import models
from app.db import get_db


router = APIRouter(
    prefix="/knowhow",
    tags=["Know-how"],
)


# =========================================================
# REQUEST SCHEMAS
# =========================================================

class KnowHowDraftCreate(BaseModel):
    machine_id: str
    title: str

    observation: Optional[str] = None
    hypothesis: Optional[str] = None
    evidence: Optional[str] = None

    diagnostic_check: Optional[str] = None
    ruled_out_causes: Optional[str] = None
    recommended_action: Optional[str] = None

    verification: Optional[str] = None
    result: Optional[str] = None

    maintenance_record_id: Optional[int] = None
    document_id: Optional[int] = None
    source_page: Optional[int] = Field(
        default=None,
        ge=1,
    )

    source_type: str = "technician"

    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )

    created_by: Optional[str] = None


class ReviewPayload(BaseModel):
    reviewer: str
    note: Optional[str] = None


# =========================================================
# HELPERS
# =========================================================

def serialize_knowhow(item):
    return {
        "id": item.id,
        "knowhow_id": item.knowhow_id,
        "machine_id": item.machine_id,
        "title": item.title,

        "observation": item.observation,
        "hypothesis": item.hypothesis,
        "evidence": item.evidence,

        "diagnostic_check": item.diagnostic_check,
        "ruled_out_causes": item.ruled_out_causes,
        "recommended_action": item.recommended_action,

        "verification": item.verification,
        "result": item.result,

        "maintenance_record_id": item.maintenance_record_id,
        "document_id": item.document_id,
        "source_page": item.source_page,
        "source_type": item.source_type,

        "status": item.status,
        "confidence": item.confidence,

        "created_by": item.created_by,
        "reviewed_by": item.reviewed_by,
        "review_note": item.review_note,

        "created_at": (
            item.created_at.isoformat()
            if item.created_at
            else None
        ),

        "updated_at": (
            item.updated_at.isoformat()
            if item.updated_at
            else None
        ),
    }


def get_machine_or_404(
    db: Session,
    machine_id: str,
):
    machine = (
        db.query(models.Machine)
        .filter(
            models.Machine.machine_id
            == machine_id
        )
        .first()
    )

    if not machine:
        raise HTTPException(
            status_code=404,
            detail="Machine not found",
        )

    return machine


def get_knowhow_or_404(
    db: Session,
    knowhow_id: str,
):
    item = (
        db.query(models.KnowHowCase)
        .filter(
            models.KnowHowCase.knowhow_id
            == knowhow_id
        )
        .first()
    )

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Know-how case not found",
        )

    return item


def validate_sources(
    db: Session,
    machine_id: str,
    maintenance_record_id: Optional[int],
    document_id: Optional[int],
):
    if maintenance_record_id is not None:
        record = (
            db.query(models.MaintenanceRecord)
            .filter(
                models.MaintenanceRecord.id
                == maintenance_record_id
            )
            .first()
        )

        if not record:
            raise HTTPException(
                status_code=404,
                detail="Maintenance record not found",
            )

        if record.machine_id != machine_id:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Maintenance record belongs "
                    "to another machine"
                ),
            )

    if document_id is not None:
        document = (
            db.query(models.Document)
            .filter(
                models.Document.id
                == document_id
            )
            .first()
        )

        if not document:
            raise HTTPException(
                status_code=404,
                detail="Document not found",
            )

        if document.machine_id != machine_id:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Document belongs "
                    "to another machine"
                ),
            )


def generate_knowhow_id(
    db: Session,
    machine_id: str,
):
    prefix_machine = machine_id.replace(
        "-",
        "",
    )

    prefix = (
        f"KH-{prefix_machine}-"
    )

    existing = (
        db.query(models.KnowHowCase)
        .filter(
            models.KnowHowCase.knowhow_id
            .like(f"{prefix}%")
        )
        .all()
    )

    numbers = []

    for item in existing:
        try:
            number = int(
                item.knowhow_id
                .rsplit("-", 1)[1]
            )

            numbers.append(number)

        except (ValueError, IndexError):
            pass

    next_number = (
        max(numbers) + 1
        if numbers
        else 1
    )

    return (
        f"{prefix}{next_number:03d}"
    )


# =========================================================
# CREATE DRAFT
# =========================================================

@router.post("/draft")
def create_knowhow_draft(
    payload: KnowHowDraftCreate,
    db: Session = Depends(get_db),
):
    get_machine_or_404(
        db,
        payload.machine_id,
    )

    validate_sources(
        db=db,
        machine_id=payload.machine_id,
        maintenance_record_id=(
            payload.maintenance_record_id
        ),
        document_id=payload.document_id,
    )

    knowhow_id = generate_knowhow_id(
        db,
        payload.machine_id,
    )

    item = models.KnowHowCase(
        knowhow_id=knowhow_id,
        machine_id=payload.machine_id,
        title=payload.title,

        observation=payload.observation,
        hypothesis=payload.hypothesis,
        evidence=payload.evidence,

        diagnostic_check=(
            payload.diagnostic_check
        ),

        ruled_out_causes=(
            payload.ruled_out_causes
        ),

        recommended_action=(
            payload.recommended_action
        ),

        verification=payload.verification,
        result=payload.result,

        maintenance_record_id=(
            payload.maintenance_record_id
        ),

        document_id=payload.document_id,
        source_page=payload.source_page,
        source_type=payload.source_type,

        status="DRAFT",
        confidence=payload.confidence,

        created_by=payload.created_by,
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    return {
        "status": "created",
        "message": "Know-how draft created",
        "knowhow": serialize_knowhow(item),
    }


# =========================================================
# LIST BY MACHINE
# =========================================================

@router.get("/machine/{machine_id}")
def list_machine_knowhow(
    machine_id: str,
    db: Session = Depends(get_db),
):
    get_machine_or_404(
        db,
        machine_id,
    )

    items = (
        db.query(models.KnowHowCase)
        .filter(
            models.KnowHowCase.machine_id
            == machine_id
        )
        .order_by(
            models.KnowHowCase.created_at.desc()
        )
        .all()
    )

    counts = {
        "total": len(items),
        "draft": 0,
        "under_review": 0,
        "approved": 0,
        "rejected": 0,
    }

    for item in items:
        status = (
            item.status or ""
        ).upper()

        if status == "DRAFT":
            counts["draft"] += 1

        elif status == "UNDER_REVIEW":
            counts["under_review"] += 1

        elif status == "APPROVED":
            counts["approved"] += 1

        elif status == "REJECTED":
            counts["rejected"] += 1

    return {
        "machine_id": machine_id,
        "counts": counts,
        "knowhow": [
            serialize_knowhow(item)
            for item in items
        ],
    }


# =========================================================
# DETAIL
# =========================================================

@router.get("/{knowhow_id}")
def get_knowhow_detail(
    knowhow_id: str,
    db: Session = Depends(get_db),
):
    item = get_knowhow_or_404(
        db,
        knowhow_id,
    )

    return {
        "knowhow": serialize_knowhow(item)
    }


# =========================================================
# SUBMIT FOR REVIEW
# =========================================================

@router.post("/{knowhow_id}/submit")
def submit_knowhow(
    knowhow_id: str,
    db: Session = Depends(get_db),
):
    item = get_knowhow_or_404(
        db,
        knowhow_id,
    )

    if item.status not in (
        "DRAFT",
        "REJECTED",
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "Only DRAFT or REJECTED "
                "know-how can be submitted"
            ),
        )

    item.status = "UNDER_REVIEW"
    item.reviewed_by = None
    item.review_note = None
    item.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(item)

    return {
        "status": "submitted",
        "message": (
            "Know-how submitted for review"
        ),
        "knowhow": serialize_knowhow(item),
    }


# =========================================================
# APPROVE
# =========================================================

@router.post("/{knowhow_id}/approve")
def approve_knowhow(
    knowhow_id: str,
    payload: ReviewPayload,
    db: Session = Depends(get_db),
):
    item = get_knowhow_or_404(
        db,
        knowhow_id,
    )

    if item.status != "UNDER_REVIEW":
        raise HTTPException(
            status_code=400,
            detail=(
                "Know-how must be UNDER_REVIEW "
                "before approval"
            ),
        )

    item.status = "APPROVED"
    item.reviewed_by = payload.reviewer
    item.review_note = payload.note
    item.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(item)

    return {
        "status": "approved",
        "message": "Know-how approved",
        "knowhow": serialize_knowhow(item),
    }


# =========================================================
# REJECT
# =========================================================

@router.post("/{knowhow_id}/reject")
def reject_knowhow(
    knowhow_id: str,
    payload: ReviewPayload,
    db: Session = Depends(get_db),
):
    item = get_knowhow_or_404(
        db,
        knowhow_id,
    )

    if item.status != "UNDER_REVIEW":
        raise HTTPException(
            status_code=400,
            detail=(
                "Know-how must be UNDER_REVIEW "
                "before rejection"
            ),
        )

    item.status = "REJECTED"
    item.reviewed_by = payload.reviewer
    item.review_note = payload.note
    item.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(item)

    return {
        "status": "rejected",
        "message": "Know-how rejected",
        "knowhow": serialize_knowhow(item),
    }
