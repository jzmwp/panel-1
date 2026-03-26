import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.config import settings
from backend.database import engine, Base
from backend.api import reports, chat, documents

logging.basicConfig(level=getattr(logging, settings.log_level))

app = FastAPI(title="Panel 1 — Mine Reporting System", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables (for dev; production uses Alembic)
Base.metadata.create_all(bind=engine)

app.include_router(reports.router)
app.include_router(chat.router)
app.include_router(documents.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "project": "Panel 1"}
