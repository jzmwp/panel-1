import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.config import settings
from backend.database import engine, Base
from backend.api import reports, chat, documents

logging.basicConfig(level=getattr(logging, settings.log_level))

app = FastAPI(title="Panel 1 — Mine Reporting System", version="0.1.0")

import os

allowed_origins = [
    "http://localhost:5173",
    "http://localhost:3000",
]
# Allow Vercel deployment URLs
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

# Create tables (for dev; production uses Alembic)
Base.metadata.create_all(bind=engine)

app.include_router(reports.router)
app.include_router(chat.router)
app.include_router(documents.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "project": "Panel 1"}
