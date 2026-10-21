"""
Vercel Serverless Function entry point for CityCare Hospital Management System.
Redirects incoming API requests to the FastAPI application.
"""

import sys
from pathlib import Path

# Add project root and backend folder to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "backend"))
sys.path.insert(0, str(ROOT_DIR))

# Import the configured FastAPI app
from backend.main import app
