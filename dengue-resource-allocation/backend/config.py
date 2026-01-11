"""
Configuration Module
Central configuration for the backend API
"""

from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"

# Data files
PROCESSED_DATA_PATH = DATA_DIR / "processed_data.csv"
STORAGE_PATH = DATA_DIR / "storage.json"

# Model files
RISK_MODEL_PATH = MODELS_DIR / "risk_model.pkl"
RESOURCE_MODEL_PATH = MODELS_DIR / "resource_model.pkl"

# API Configuration
API_TITLE = "Dengue Resource Allocation API"
API_DESCRIPTION = """
API for dengue risk prediction, hotspot identification, and resource allocation.

This system provides:
* District-level dengue risk classification (Low/Medium/High)
* Hotspot identification for high-risk districts
* ML-based resource recommendations (fogging units, inspectors, teams, treatment units)
* Resource management and assignment tracking
"""
API_VERSION = "1.0.0"

# Server settings
HOST = "0.0.0.0"
PORT = 8000
RELOAD = True  # Set to False in production

# CORS settings (adjust for production)
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# Resource defaults
DEFAULT_RESOURCES = {
    "Fogging_Units": 100,
    "Health_Inspectors": 50,
    "Inspection_Teams": 30,
    "Treatment_Units": 80
}

# Risk level configuration
RISK_LEVELS = ["Low", "Medium", "High"]
HOTSPOT_RISK_LEVEL = "High"