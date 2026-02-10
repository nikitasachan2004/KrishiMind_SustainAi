"""
KrishiMind SustainAI - Pydantic Schemas
Request/Response validation models
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from enum import Enum


class SeasonEnum(str, Enum):
    """Valid season values"""
    KHARIF = "Kharif"
    RABI = "Rabi"
    SUMMER = "Summer"
    AUTUMN = "Autumn"
    WINTER = "Winter"
    WHOLE_YEAR = "Whole Year"


class ScenarioInput(BaseModel):
    """Climate scenario modifications"""
    rainfall_delta: float = Field(
        default=0.0,
        ge=-1.0,
        le=1.0,
        description="Rainfall change as fraction (-1.0 to 1.0 = -100% to +100%)"
    )
    temp_delta: float = Field(
        default=0.0,
        ge=-5.0,
        le=10.0,
        description="Temperature change in °C"
    )


class CropPlanRequest(BaseModel):
    """Request schema for crop planning endpoint"""
    district: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="District name (e.g., 'Guntur', 'Nagpur')"
    )
    season: SeasonEnum = Field(
        ...,
        description="Growing season"
    )
    area: float = Field(
        ...,
        gt=0,
        le=10000,
        description="Area in hectares (must be > 0)"
    )
    scenario: Optional[ScenarioInput] = Field(
        default=None,
        description="Optional climate scenario modifications"
    )
    
    @field_validator('district')
    @classmethod
    def validate_district(cls, v):
        """Ensure district name is properly formatted"""
        if not v.strip():
            raise ValueError('District name cannot be empty')
        return v.strip().title()
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "district": "Guntur",
                "season": "Kharif",
                "area": 10.0,
                "scenario": {
                    "rainfall_delta": 0.0,
                    "temp_delta": 0.0
                }
            }
        }
    }


class SustainabilityMetrics(BaseModel):
    """Proxy sustainability metrics for a crop recommendation"""
    water_use_estimate: float = Field(..., description="Proxy water use index (index-hectare-days)")
    water_saved_vs_baseline: float = Field(..., description="Pct water saved vs highest-demand crop")
    fertilizer_proxy: float = Field(..., description="Proxy fertilizer load (0-1, lower = better)")
    carbon_proxy: float = Field(..., description="Proxy carbon footprint (index-hectare units)")
    risk_reduction_pct: float = Field(..., description="Climate risk reduction percentage")
    sustainability_score: float = Field(..., description="Composite sustainability score (0-1)")


class CropRecommendation(BaseModel):
    """Individual crop recommendation"""
    rank: int = Field(..., description="Recommendation rank (1 = best)")
    crop: str = Field(..., description="Crop name")
    composite_score: float = Field(..., description="Multi-criteria score (0-1)")
    predicted_yield_tonnes_per_ha: float = Field(..., description="Predicted yield")
    predicted_price_inr_per_tonne: float = Field(..., description="Predicted price")
    expected_revenue_inr_per_ha: float = Field(..., description="Revenue per hectare")
    total_revenue_inr: float = Field(..., description="Total revenue for given area")
    risk_level: str = Field(..., description="Risk assessment: low/medium/high")
    sustainability_metrics: Optional[SustainabilityMetrics] = Field(
        default=None, description="Proxy sustainability impact metrics"
    )
    proxy_metrics: bool = Field(
        default=True, description="True — sustainability values are proxy estimates, not field-measured"
    )


class CropPlanResponse(BaseModel):
    """Response schema for crop planning endpoint"""
    status: str = Field(..., description="Request status: success/error")
    district: str = Field(..., description="Input district")
    season: str = Field(..., description="Input season")
    area_hectares: float = Field(..., description="Input area")
    scenario_applied: str = Field(..., description="Scenario name applied")
    recommendations: List[CropRecommendation] = Field(
        ...,
        description="Ranked crop recommendations"
    )
    disclaimer: str = Field(
        default="District-level aggregation. Not farm-specific advice.",
        description="Risk disclosure"
    )
    sustainability_disclosure: str = Field(
        default=(
            "Sustainability metrics are proxy estimates derived from agronomic "
            "literature constants and soil indices. They are decision-support "
            "indicators, not field-measured values. District-level aggregation "
            "used — no field-level geo precision claimed."
        ),
        description="Sustainability proxy methodology disclosure"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "success",
                "district": "Guntur",
                "season": "Kharif",
                "area_hectares": 10.0,
                "scenario_applied": "baseline",
                "recommendations": [
                    {
                        "rank": 1,
                        "crop": "Sugarcane",
                        "composite_score": 0.963,
                        "predicted_yield_tonnes_per_ha": 73.28,
                        "predicted_price_inr_per_tonne": 3626,
                        "expected_revenue_inr_per_ha": 265742,
                        "total_revenue_inr": 2657420,
                        "risk_level": "low"
                    }
                ],
                "disclaimer": "District-level aggregation. Not farm-specific advice."
            }
        }
    }

class ErrorResponse(BaseModel):
    """Error response schema"""
    status: str = Field(default="error")
    error_code: str = Field(..., description="Error identifier")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional error details"
    )


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    models_loaded: bool = Field(..., description="Models ready for inference")
    version: str = Field(..., description="API version")
    timestamp: str = Field(..., description="Response timestamp")
