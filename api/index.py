from fastapi import FastAPI
from fastapi.responses import JSONResponse
import sys
import os
import traceback

app = FastAPI()

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_error = None
try:
    from backend.main import app  # noqa: F811
except Exception as e:
    _error = traceback.format_exc()

if _error:
    @app.get("/api/{path:path}")
    def error_handler(path: str = ""):
        return JSONResponse(status_code=500, content={"error": _error})
