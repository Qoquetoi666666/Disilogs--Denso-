from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class MachineCreate(BaseModel):
    machine_id: str
    asset_code: str

    manufacturer: Optional[str] = None
    series: Optional[str] = None
    model: Optional[str] = None

    location: Optional[str] = None

    install_date: Optional[str] = None
    warranty_expiry: Optional[str] = None

    status: str = "ACTIVE"

    last_maintenance: Optional[str] = None
    next_maintenance: Optional[str] = None


class MachineOut(MachineCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class MaintenanceCreate(BaseModel):
    machine_id: str

    symptom: str
    error_code: Optional[str] = None

    cause: Optional[str] = None
    action: str

    parts: Optional[str] = None
    downtime_min: Optional[float] = None

    result: Optional[str] = None
    technician: Optional[str] = None


class MaintenanceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    machine_id: str

    symptom: Optional[str]
    error_code: Optional[str]

    cause: Optional[str]
    action: Optional[str]

    parts: Optional[str]
    downtime_min: Optional[float]

    result: Optional[str]
    technician: Optional[str]

    source: str
    confidence: float
    review_status: str

    created_at: datetime
