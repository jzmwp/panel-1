import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings

logging.basicConfig(level=getattr(logging, settings.log_level))
logger = logging.getLogger(__name__)

app = FastAPI(title="Panel 1 — Mine Reporting System", version="0.1.0")

allowed_origins = [
    "http://localhost:5173",
    "http://localhost:3000",
]
vercel_url = os.environ.get("VERCEL_URL")
if vercel_url:
    allowed_origins.append(f"https://{vercel_url}")
frontend_url = os.environ.get("FRONTEND_URL")
if frontend_url:
    allowed_origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    """Create tables on startup instead of at import time."""
    try:
        from backend.database import engine, Base
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified")
    except Exception as e:
        logger.error(f"Failed to create tables: {e}")


from backend.api import reports, chat, documents

app.include_router(reports.router)
app.include_router(chat.router)
app.include_router(documents.router)


@app.get("/api/health")
def health():
    db_status = "unknown"
    try:
        from backend.database import SessionLocal
        db = SessionLocal()
        db.execute(__import__('sqlalchemy').text("SELECT 1"))
        db.close()
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {e}"
    return {"status": "ok", "project": "Panel 1", "db": db_status, "db_url": settings.database_url[:30] + "..."}
