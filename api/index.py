import sys
import os
from fastapi import FastAPI

# Ensure project root is in Python path for backend imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_import_error = None
try:
    from backend.main import app as _real_app
    app = _real_app
except Exception as e:
    _import_error = str(e)
    app = FastAPI()

    @app.get("/api/{path:path}")
    def catchall(path: str = ""):
        return {"status": "import_error", "detail": _import_error}
