from fastapi import FastAPI
import sys
import os

app = FastAPI()

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import app  # noqa: F811
