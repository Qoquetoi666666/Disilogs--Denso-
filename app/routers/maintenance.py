from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.db import get_db


router = APIRouter(
    prefix="/maintenance",
    tags=["Maintenance"],
)


@router.post("/")
def create_maintenance_record(
    payload: schemas.MaintenanceCreate,
    db: Session = Depends(get_db),
):
    machine = (
        db.query(models.Machine)
        .filter(
            models.Machine.machine_id
            == payload.machine_id
        )
        .first()
    )

    if not machine:
        raise HTTPException(
            status_code=404,
            detail="Machine not found",
        )

    record = models.MaintenanceRecord(
        **payload.model_dump(),
        source="technician",
        confidence=1.0,
        review_status="approved",
    )

    db.add(record)

    machine.last_maintenance = (
        str(record.created_at.date())
        if record.created_at
        else machine.last_maintenance
    )

    db.commit()
    db.refresh(record)

    return {
        "status": "saved",
        "message": (
            "Maintenance record added "
            "to Digi-Log"
        ),
        "record": record,
    }


@router.get("/{machine_id}")
def list_maintenance_records(
    machine_id: str,
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

    if not machine:
        raise HTTPException(
            status_code=404,
            detail="Machine not found",
        )

    records = (
        db.query(models.MaintenanceRecord)
        .filter(
            models.MaintenanceRecord.machine_id
            == machine_id
        )
        .order_by(
            models.MaintenanceRecord.created_at.desc()
        )
        .all()
    )

    return {
        "machine_id": machine_id,
        "count": len(records),
        "records": records,
    }
