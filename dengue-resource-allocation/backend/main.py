"""
Main FastAPI Application
Entry point for the Dengue Resource Allocation API
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.config import (
    API_TITLE,
    API_DESCRIPTION,
    API_VERSION,
    CORS_ORIGINS,
    STORAGE_PATH,
    RISK_MODEL_PATH,
    RESOURCE_MODEL_PATH,
    DEFAULT_RESOURCES
)
from backend.json_store import get_store
from backend.routes import resources, predictions, admin
from ml.predict import DenguePredictionSystem


# Global variables for models
prediction_system = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    
    Task 1: Initialize FastAPI backend
    Task 2: Load ML models on startup
    Task 3: Load JSON data on startup
    """
    print("="*60)
    print("Starting Dengue Resource Allocation API")
    print("="*60)
    
    # Initialize JSON store
    print("\n[1/3] Initializing JSON storage...")
    try:
        store = get_store(str(STORAGE_PATH))
        print(f"✓ Storage initialized at: {STORAGE_PATH}")
        
        # Set default resources if not exist
        available = store.get_available_resources()
        if not available:
            print("  Setting default resources...")
            store.set_available_resources(DEFAULT_RESOURCES)
            print(f"  ✓ Default resources configured")
    except Exception as e:
        print(f"✗ Storage initialization failed: {e}")
        raise
    
    # Load ML models
    print("\n[2/3] Loading ML models...")
    global prediction_system
    try:
        if not RISK_MODEL_PATH.exists():
            print(f"✗ Risk model not found at: {RISK_MODEL_PATH}")
            print("  Please run ML training scripts first")
            raise FileNotFoundError(f"Risk model not found: {RISK_MODEL_PATH}")
        
        if not RESOURCE_MODEL_PATH.exists():
            print(f"✗ Resource model not found at: {RESOURCE_MODEL_PATH}")
            print("  Please run ML training scripts first")
            raise FileNotFoundError(f"Resource model not found: {RESOURCE_MODEL_PATH}")
        
        prediction_system = DenguePredictionSystem(
            risk_model_path=str(RISK_MODEL_PATH),
            resource_model_path=str(RESOURCE_MODEL_PATH)
        )
        
        # Set in predictions module
        predictions.set_prediction_system(prediction_system)
        
        print(f"✓ Risk model loaded: {RISK_MODEL_PATH.name}")
        print(f"✓ Resource model loaded: {RESOURCE_MODEL_PATH.name}")
        print(f"✓ Prediction system ready")
    except Exception as e:
        print(f"✗ Model loading failed: {e}")
        raise
    
    # Verify data
    print("\n[3/3] Verifying system...")
    try:
        data = store.get_all_data()
        print(f"✓ Storage contains {len(data.get('district_predictions', []))} predictions")
        print(f"✓ Storage contains {len(data.get('hotspots', []))} hotspots")
        print(f"✓ Available resources: {len(data.get('available_resources', {}))}")
    except Exception as e:
        print(f"⚠ Warning: {e}")
    
    print("\n" + "="*60)
    print("API Server Ready!")
    print("="*60)
    print(f"API Documentation: http://localhost:8000/docs")
    print(f"Alternative docs: http://localhost:8000/redoc")
    print("="*60 + "\n")
    
    yield
    
    # Cleanup (if needed)
    print("\nShutting down API server...")


# Create FastAPI app
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(resources.router)
app.include_router(predictions.router)
app.include_router(admin.router)


# Root endpoints

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Dengue Resource Allocation API",
        "version": API_VERSION,
        "status": "operational",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "resources": "/resources",
            "predictions": "/predictions",
            "admin": "/admin"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "API is running",
        "models_loaded": prediction_system is not None
    }


@app.get("/info")
async def info():
    """Get API information"""
    return {
        "title": API_TITLE,
        "description": API_DESCRIPTION,
        "version": API_VERSION,
        "features": [
            "District-level dengue risk prediction",
            "Hotspot identification",
            "ML-based resource recommendations",
            "Resource management and assignment",
            "Admin dashboard with analytics"
        ],
        "endpoints": {
            "resources": {
                "GET /resources": "Get available resources",
                "POST /resources": "Update resources",
                "PUT /resources/{name}": "Update specific resource",
                "POST /resources/assign": "Assign resources to district"
            },
            "predictions": {
                "POST /predictions/generate": "Generate new predictions",
                "GET /predictions/districts": "Get all district predictions",
                "GET /predictions/hotspots": "Get hotspots",
                "GET /predictions/recommendations": "Get resource recommendations"
            },
            "admin": {
                "GET /admin/overview": "Get dashboard overview",
                "GET /admin/statistics": "Get detailed statistics",
                "GET /admin/resource-gap": "Analyze resource gaps"
            }
        }
    }


if __name__ == "__main__":
    import uvicorn
    from backend.config import HOST, PORT, RELOAD
    
    uvicorn.run(
        "backend.main:app",
        host=HOST,
        port=PORT,
        reload=RELOAD
    )