"""
Vercel Serverless Function entry point for CityCare Hospital Management System.
Redirects incoming API requests to the FastAPI application.
"""

import sys
from pathlib import Path

# Add api and api/backend to sys.path so everything is self-contained
API_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(API_DIR / "backend"))
sys.path.insert(0, str(API_DIR))

# Import the configured FastAPI app
try:
    from backend.main import app
except ImportError:
    from main import app
