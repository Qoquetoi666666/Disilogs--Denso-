from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)

from sqlalchemy.orm import relationship

from app.db import Base


class Machine(Base):
    __tablename__ = "machines"

    id = Column(Integer, primary_key=True, index=True)

    machine_id = Column(
        String,
        unique=True,
        nullable=False,
        index=True,
    )

    asset_code = Column(
        String,
        unique=True,
        nullable=False,
        index=True,
    )

    manufacturer = Column(String)
    series = Column(String)
    model = Column(String)

    location = Column(String)

    install_date = Column(String)
    warranty_expiry = Column(String)

    status = Column(
        String,
        default="ACTIVE",
    )

    last_maintenance = Column(String)
    next_maintenance = Column(String)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    maintenance_records = relationship(
        "MaintenanceRecord",
        back_populates="machine",
    )



class MaintenanceRecord(Base):
    __tablename__ = "maintenance_records"

    id = Column(Integer, primary_key=True, index=True)

    machine_id = Column(
        String,
        ForeignKey("machines.machine_id"),
        nullable=False,
        index=True,
    )

    symptom = Column(Text)
    error_code = Column(String)

    cause = Column(Text)
    action = Column(Text)

    parts = Column(Text)

    downtime_min = Column(Float)

    result = Column(Text)

    technician = Column(String)

    source = Column(
        String,
        default="technician",
    )

    confidence = Column(
        Float,
        default=1.0,
    )

    review_status = Column(
        String,
        default="approved",
    )

    approved_by = Column(String)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    machine = relationship(
        "Machine",
        back_populates="maintenance_records",
    )


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)

    machine_id = Column(
        String,
        ForeignKey("machines.machine_id"),
        nullable=True,
        index=True,
    )

    title = Column(String)

    filename = Column(String)

    document_type = Column(String)

    source_path = Column(String)

    indexed = Column(
        Boolean,
        default=False,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )
    document_key = Column(
    String,
    unique=True,
    index=True,
    nullable=True,
)

extracted_path = Column(
    String,
    nullable=True,
)

page_count = Column(
    Integer,
    default=0,
)

total_characters = Column(
    Integer,
    default=0,
)

status = Column(
    String,
    default="READY",
)
  
machine = relationship(
    "Machine",
    back_populates="documents",
)


class ReviewItem(Base):
    __tablename__ = "review_items"

    id = Column(Integer, primary_key=True, index=True)

    item_type = Column(String)

    source_id = Column(Integer)

    field_name = Column(String)

    extracted_value = Column(Text)

    confidence = Column(Float)

    status = Column(
        String,
        default="pending",
    )

    reviewer = Column(String)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )


class QueryLog(Base):
    __tablename__ = "query_logs"

    id = Column(Integer, primary_key=True, index=True)

    machine_id = Column(String, index=True)

    question = Column(Text)

    answer = Column(Text)

    retrieval_score = Column(Float)

    abstained = Column(
        Boolean,
        default=False,
    )

    useful_feedback = Column(
        Boolean,
        nullable=True,
    )

    latency_ms = Column(Float)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )
