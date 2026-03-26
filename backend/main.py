import logging
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config import settings

logging.basicConfig(level=getattr(logging, settings.log_level))
logger = logging.getLogger(__name__)

app = FastAPI(title="Panel 1 — Mine Reporting System", version="0.1.0")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import traceback
    return JSONResponse(status_code=500, content={"error": str(exc), "traceback": traceback.format_exc()})

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


# Create tables eagerly (on_startup may not fire in serverless)
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


@app.get("/api/test-db")
def test_db():
    from backend.database import get_db
    try:
        db = next(get_db())
        from sqlalchemy import text
        result = db.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'"))
        tables = [row[0] for row in result]
        db.close()
        return {"tables": tables}
    except Exception as e:
        import traceback
        return {"error": str(e), "tb": traceback.format_exc()}


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
