from fastapi import FastAPI

from app.db import Base, engine
from app.routers import (
    machines,
    maintenance,
    scanning,
    documents,
    knowhow,
)


Base.metadata.create_all(
    bind=engine
)


app = FastAPI(
    title="Digi-Logs",
    description=(
        "CNC Maintenance Knowledge "
        "Digitization System"
    ),
    version="0.1.0",
)


app.include_router(
    machines.router
)

app.include_router(
    maintenance.router
)

app.include_router(
    scanning.router
)

app.include_router(
    documents.router
)

app.include_router(
    knowhow.router
)


@app.get("/")
def root():
    return {
        "system": "Digi-Logs",
        "version": "0.1.0",
        "status": "online",
        "mode": "LOCAL",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "deployment": "local",
        "cloud_required": False,
        "database": "SQLite",
    }
