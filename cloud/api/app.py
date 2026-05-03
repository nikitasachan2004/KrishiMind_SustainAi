"""
KrishiMind SustainAI - FastAPI Application
Production-ready API for crop planning and optimization
"""

import os
import sys
import logging
import base64
import requests
from datetime import datetime
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cloud.api.schemas import (
    CropPlanRequest,
    CropPlanResponse,
    ErrorResponse,
    HealthResponse
)
from cloud.api.model_loader import model_loader, ModelLoadError
from cloud.api.predict import get_predictor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('krishimind_api')


# API Version
API_VERSION = "1.0.0"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup/shutdown lifecycle manager.
    Loads models at startup, validates all required artifacts.
    """
    logger.info("=" * 60)
    logger.info("KRISHIMIND SUSTAINAI - API STARTUP")
    logger.info("=" * 60)
    
    try:
        # Load all models at startup
        model_loader.load_all()
        logger.info("✅ API ready to serve requests")
    except ModelLoadError as e:
        logger.error(f"❌ STARTUP FAILED: {e}")
        logger.error("API will not start without required model artifacts")
        raise SystemExit(1)
    
    yield  # Application runs here
    
    # Shutdown
    logger.info("🛑 KrishiMind SustainAI shutting down...")


# Create FastAPI application
app = FastAPI(
    title="KrishiMind SustainAI — Sustainable Crop & Resource Optimization Engine",
    description="""
    🌾 **Sustainable Crop Planning & Resource Optimization Engine**
    
    AI-powered agricultural advisory system providing:
    - District-level crop recommendations
    - Yield predictions using ML models
    - Price forecasting from mandi data
    - Climate scenario simulations
    - **Sustainability impact scoring** (water, fertilizer, carbon proxies)
    
    ---
    
    ⚠️ **Disclaimer**: District-level aggregation only. 
    Not farm-specific advice. Consult local experts before farming decisions.
    
    Sustainability metrics are proxy estimates derived from agronomic
    literature constants and soil indices. They are decision-support
    indicators, not field-measured values.
    """,
    version=API_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": "KrishiMind SustainAI",
        "version": API_VERSION,
        "description": "Crop Planning & Resource Optimization Engine",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    Returns model status and API version.
    """
    return HealthResponse(
        status="healthy" if model_loader.is_loaded() else "degraded",
        models_loaded=model_loader.is_loaded(),
        version=API_VERSION,
        timestamp=datetime.utcnow().isoformat()
    )


@app.post(
    "/predict/crop-plan",
    response_model=CropPlanResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Validation Error"},
        500: {"model": ErrorResponse, "description": "Server Error"}
    },
    tags=["Predictions"]
)
async def predict_crop_plan(request: CropPlanRequest):
    """
    🌾 **Crop Planning Prediction**
    
    Returns optimized crop recommendations for a district/season combination.
    
    **Input:**
    - `district`: District name (e.g., "Guntur")
    - `season`: Growing season (Kharif/Rabi/Summer/etc.)
    - `area`: Farm area in hectares
    - `scenario`: Optional climate modifications
    
    **Output:**
    - Ranked crop recommendations with:
      - Predicted yield (tonnes/ha)
      - Predicted price (₹/tonne)
      - Expected revenue
      - Risk assessment
    
    ---
    
    ⚠️ **Disclaimer**: Results are district-level aggregations.
    Not suitable for farm-specific decisions.
    """
    try:
        # Get predictor
        predictor = get_predictor()
        
        # Run optimization
        recommendations = predictor.optimize(
            district=request.district,
            season=request.season.value,
            area=request.area,
            scenario=request.scenario,
            top_n=5
        )
        
        # Get scenario name
        scenario_name = predictor.get_scenario_name(request.scenario)

        disease_result = None
        if request.image_path:
            try:
                # Read and encode image to base64
                image_path = Path(request.image_path)
                if image_path.exists():
                    with open(image_path, "rb") as f:
                        image_data = base64.b64encode(f.read()).decode("utf-8")
                    
                    # Call HuggingFace Space API
                    hf_space_url = "https://Nishantgupta911-krishimind-disease.hf.space/run/predict"
                    payload = {"data": [f"data:image/jpeg;base64,{image_data}"]}
                    
                    response = requests.post(hf_space_url, json=payload, timeout=30)
                    
                    if response.status_code == 200:
                        api_response = response.json()
                        # Parse Gradio response format
                        if "data" in api_response and len(api_response["data"]) > 0:
                            disease_result = api_response["data"][0]
                    else:
                        logger.warning(f"HF Space API error: {response.status_code}")
                else:
                    logger.warning(f"Image not found: {request.image_path}")
            except Exception as e:
                logger.warning(f"Disease detection failed: {e}")
                disease_result = None
        
        # Build response
        return CropPlanResponse(
            status="success",
            district=request.district,
            season=request.season.value,
            area_hectares=request.area,
            scenario_applied=scenario_name,
            recommendations=recommendations,
            plant_disease=disease_result,
            disclaimer="District-level aggregation. Not farm-specific advice."
        )
        
    except Exception as e:
        logger.error(f"Prediction error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": "PREDICTION_ERROR",
                "message": str(e)
            }
        )


@app.get("/model/info", tags=["Models"])
async def model_info():
    """
    Get information about loaded models.
    """
    return model_loader.get_model_info()


@app.exception_handler(ModelLoadError)
async def model_load_error_handler(request, exc: ModelLoadError):
    """Handle model loading errors"""
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "status": "error",
            "error_code": "MODEL_NOT_LOADED",
            "message": str(exc)
        }
    )


@app.exception_handler(ValueError)
async def value_error_handler(request, exc: ValueError):
    """Handle validation errors"""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "status": "error",
            "error_code": "VALIDATION_ERROR",
            "message": str(exc)
        }
    )


# Run with: uvicorn app:app --host 0.0.0.0 --port 8000 --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
