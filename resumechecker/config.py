"""
Configuration settings for the Automated Resume Relevance Check System.
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Data directories
DATA_DIR = os.path.join(BASE_DIR, "data")
RESUME_DIR = os.path.join(DATA_DIR, "resumes")
JD_DIR = os.path.join(DATA_DIR, "job_descriptions")

# Database settings
DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "resume_checker.db")

# API keys (load from environment variables in production)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Scoring weights
WEIGHTS = {
    "hard_match": 0.6,  # Weight for keyword and skill matching
    "semantic_match": 0.4,  # Weight for semantic similarity
}

# Verdict thresholds
VERDICT_THRESHOLDS = {
    "high": 75,  # Score >= 75 is considered high suitability
    "medium": 50,  # Score >= 50 and < 75 is considered medium suitability
    "low": 0,  # Score < 50 is considered low suitability
}

# Web application settings
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5000
FLASK_DEBUG = True

# API settings
API_URL = "http://localhost:8000/analyze"

# Streamlit settings
STREAMLIT_PORT = 8501

# File upload settings
ALLOWED_EXTENSIONS = {"pdf", "docx"}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

# Upload settings dictionary for FastAPI
UPLOAD_SETTINGS = {
    "allowed_extensions": ALLOWED_EXTENSIONS,
    "max_content_length": MAX_CONTENT_LENGTH
}