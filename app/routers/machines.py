from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.db import get_db


router = APIRouter(
    prefix="/machines",
    tags=["Machines"],
)


def find_machine(db: Session, machine_id: str):
    return (
        db.query(models.Machine)
        .filter(models.Machine.machine_id == machine_id)
        .first()
    )


@router.get("/")
def list_machines(
    db: Session = Depends(get_db),
):
    machines = (
        db.query(models.Machine)
        .order_by(models.Machine.machine_id.asc())
        .all()
    )

    return {
        "count": len(machines),
        "machines": machines,
    }


@router.post("/")
def create_machine(
    payload: schemas.MachineCreate,
    db: Session = Depends(get_db),
):
    same_id = find_machine(
        db,
        payload.machine_id,
    )

    if same_id:
        raise HTTPException(
            status_code=409,
            detail="Machine ID already exists",
        )

    same_asset = (
        db.query(models.Machine)
        .filter(
            models.Machine.asset_code
            == payload.asset_code
        )
        .first()
    )

    if same_asset:
        raise HTTPException(
            status_code=409,
            detail="Asset code already exists",
        )

    machine = models.Machine(
        **payload.model_dump()
    )

    db.add(machine)
    db.commit()
    db.refresh(machine)

    return {
        "status": "created",
        "machine": machine,
    }


@router.get("/{machine_id}")
def get_machine(
    machine_id: str,
    db: Session = Depends(get_db),
):
    machine = find_machine(
        db,
        machine_id,
    )

    if not machine:
        raise HTTPException(
            status_code=404,
            detail="Machine not found",
        )

    return machine


@router.get("/{machine_id}/digilog")
def get_digilog(
    machine_id: str,
    db: Session = Depends(get_db),
):
    machine = find_machine(
        db,
        machine_id,
    )

    if not machine:
        raise HTTPException(
            status_code=404,
            detail="Machine not found",
        )

    maintenance = (
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

    documents = (
        db.query(models.Document)
        .filter(
            models.Document.machine_id
            == machine_id
        )
        .order_by(
            models.Document.created_at.desc()
        )
        .all()
    )

    last_failure = None

    if maintenance:
        last_failure = maintenance[0]

    return {
        "machine": machine,
        "summary": {
            "maintenance_count": len(maintenance),
            "document_count": len(documents),
        },
        "last_failure": last_failure,
        "maintenance_history": maintenance,
        "documents": documents,
    }

