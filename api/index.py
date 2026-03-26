import sys
import os

# Ensure project root is in Python path for backend imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from backend.main import app
except Exception as e:
    # Fallback: return the error so we can debug
    from fastapi import FastAPI
    app = FastAPI()

    @app.get("/api/health")
    def health():
        return {"status": "error", "detail": str(e)}

    @app.get("/api/{path:path}")
    def catchall(path: str):
        return {"status": "error", "detail": str(e)}
