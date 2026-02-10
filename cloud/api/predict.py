"""
KrishiMind SustainAI - Prediction Logic
Inference-only pipeline using pre-trained models
"""

import sys
import logging
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cloud.api.model_loader import get_model_loader, ensure_models_loaded
from cloud.api.schemas import CropPlanRequest, CropRecommendation, SustainabilityMetrics, ScenarioInput
from src.sustainability.impact_engine import SustainabilityImpactEngine

logger = logging.getLogger('predict')


class CropPredictor:
    """
    Crop prediction and optimization using pre-trained models.
    Inference only - no training occurs here.
    """
    
    # Default crops for optimization
    DEFAULT_CROPS = [
        'Rice', 'Wheat', 'Maize', 'Sugarcane', 'Cotton(Lint)',
        'Groundnut', 'Soybean', 'Arhar/Tur', 'Gram', 'Bajra'
    ]
    
    # Default climate values (median from training data)
    DEFAULT_CLIMATE = {
        'rainfall_anomaly': -0.03,
        'monsoon_rainfall': 295.2,
        'heatwave_count': 2.0,
        'growing_degree_days': 15.87,
        'soil_quality_index': 0.83
    }
    
    # Default prices by crop (median mandi prices INR/tonne)
    # Fallback when price model lacks coverage
    DEFAULT_PRICES = {
        'Rice': 2680,
        'Wheat': 1931,
        'Maize': 2580,
        'Sugarcane': 3626,
        'Cotton(Lint)': 6620,
        'Groundnut': 5550,
        'Soybean': 3470,
        'Arhar/Tur': 6300,
        'Gram': 5100,
        'Bajra': 2350
    }
    
    def __init__(self):
        """Initialize predictor with loaded models"""
        ensure_models_loaded()
        self.loader = get_model_loader()
        self.yield_model = self.loader.get_yield_model()
        self.price_model = self.loader.get_price_model()
        self.yield_features = self.loader.get_yield_features()
        self.price_features = self.loader.get_price_features()
        
        # Sustainability impact engine (deterministic — no ML)
        self.sustainability_engine = SustainabilityImpactEngine()
        
        # Build encoding maps from features
        self._build_encodings()
    
    def _build_encodings(self):
        """Build label encoding maps from stored features"""
        label_encodings = self.yield_features.get('label_encodings', {})
        
        # Season encoding
        seasons = label_encodings.get('season', [])
        self.season_map = {s: i for i, s in enumerate(seasons)}
        
        # Crop encoding
        crops = label_encodings.get('crop_name', [])
        self.crop_map = {c: i for i, c in enumerate(crops)}
        
        # District encoding
        districts = label_encodings.get('district_name', [])
        self.district_map = {d: i for i, d in enumerate(districts)}
        
        # Price model encodings
        price_encodings = self.price_features.get('encodings', {})
        self.price_crop_map = price_encodings.get('crop', {})
        self.price_district_map = price_encodings.get('district', {})
    
    def _encode_season(self, season: str) -> int:
        """Encode season string to integer"""
        return self.season_map.get(season, 0)
    
    def _encode_crop(self, crop: str) -> int:
        """Encode crop string to integer"""
        return self.crop_map.get(crop, 0)
    
    def _encode_district(self, district: str) -> int:
        """Encode district string to integer"""
        # Try exact match first
        if district in self.district_map:
            return self.district_map[district]
        
        # Try case-insensitive match
        district_lower = district.lower()
        for d, idx in self.district_map.items():
            if d.lower() == district_lower:
                return idx
        
        # Return 0 for unknown districts
        logger.warning(f"Unknown district: {district}, using default encoding")
        return 0
    
    def _build_yield_features(
        self,
        crop: str,
        district: str,
        season: str,
        scenario: Optional[ScenarioInput] = None
    ) -> np.ndarray:
        """
        Build feature vector for yield prediction.
        
        Features (in order):
        1. rainfall_anomaly
        2. monsoon_rainfall
        3. heatwave_count
        4. growing_degree_days
        5. soil_quality_index
        6. season_encoded
        7. crop_name_encoded
        8. district_name_encoded
        """
        # Start with default climate values
        climate = self.DEFAULT_CLIMATE.copy()
        
        # Apply scenario modifications
        if scenario:
            # Rainfall delta: -1.0 to 1.0 = -100% to +100%
            if scenario.rainfall_delta != 0:
                climate['rainfall_anomaly'] += scenario.rainfall_delta
                climate['monsoon_rainfall'] *= (1 + scenario.rainfall_delta)
            
            # Temperature delta affects heatwave count
            if scenario.temp_delta != 0:
                # Rough heuristic: +1°C = +1 heatwave day
                climate['heatwave_count'] += max(0, scenario.temp_delta)
                # Also affects growing degree days
                climate['growing_degree_days'] += scenario.temp_delta * 0.5
        
        # Build feature vector
        features = np.array([
            climate['rainfall_anomaly'],
            climate['monsoon_rainfall'],
            climate['heatwave_count'],
            climate['growing_degree_days'],
            climate['soil_quality_index'],
            self._encode_season(season),
            self._encode_crop(crop),
            self._encode_district(district)
        ]).reshape(1, -1)
        
        return features
    
    def predict_yield(
        self,
        crop: str,
        district: str,
        season: str,
        scenario: Optional[ScenarioInput] = None
    ) -> float:
        """
        Predict yield (tonnes/hectare) for a crop-district-season combination.
        """
        features = self._build_yield_features(crop, district, season, scenario)
        
        try:
            yield_pred = self.yield_model.predict(features)[0]
            # Ensure non-negative yield
            return max(0.01, float(yield_pred))
        except Exception as e:
            logger.error(f"Yield prediction failed: {e}")
            return 1.0  # Default fallback
    
    def predict_price(self, crop: str, district: str, month: int = 6) -> float:
        """
        Predict price (INR/tonne) for a crop.
        Uses median fallback if crop not in training data.
        """
        # Check if crop is in price model's training data
        crop_encoded = self.price_crop_map.get(crop)
        district_encoded = self.price_district_map.get(district, 0)
        
        if crop_encoded is not None:
            try:
                features = np.array([crop_encoded, district_encoded, month]).reshape(1, -1)
                price_pred = self.price_model.predict(features)[0]
                return max(100, float(price_pred))
            except Exception as e:
                logger.warning(f"Price prediction failed for {crop}: {e}")
        
        # Fallback to median price by crop
        # NOTE: Using real mandi data median, not synthetic
        return self.DEFAULT_PRICES.get(crop, 3000)
    
    def calculate_revenue(
        self,
        yield_per_ha: float,
        price_per_tonne: float,
        scenario: Optional[ScenarioInput] = None
    ) -> float:
        """
        Calculate risk-adjusted revenue per hectare.
        Applies penalties for adverse climate scenarios.
        """
        base_revenue = yield_per_ha * price_per_tonne
        
        # Apply climate risk penalties
        if scenario:
            penalty = 1.0
            
            # Drought penalty
            if scenario.rainfall_delta < -0.3:
                penalty *= 0.85  # -15% for severe drought
            elif scenario.rainfall_delta < -0.1:
                penalty *= 0.95  # -5% for mild drought
            
            # Heat stress penalty
            if scenario.temp_delta > 3.0:
                penalty *= 0.90  # -10% for severe warming
            elif scenario.temp_delta > 1.5:
                penalty *= 0.95  # -5% for moderate warming
            
            base_revenue *= penalty
        
        return round(base_revenue, 2)
    
    def calculate_composite_score(
        self,
        yield_pred: float,
        revenue: float,
        scenario: Optional[ScenarioInput] = None
    ) -> float:
        """
        Calculate multi-criteria composite score.
        
        Weights:
        - yield: 0.4
        - revenue: 0.3
        - climate_stability: 0.2
        - soil_match: 0.1
        """
        # Normalize yield (assuming max ~100 tonnes/ha for sugarcane)
        yield_score = min(1.0, yield_pred / 100.0)
        
        # Normalize revenue (assuming max ~300,000 INR/ha)
        revenue_score = min(1.0, revenue / 300000.0)
        
        # Climate stability (penalize extreme scenarios)
        climate_score = 1.0
        if scenario:
            if abs(scenario.rainfall_delta) > 0.3:
                climate_score -= 0.2
            if abs(scenario.temp_delta) > 2.0:
                climate_score -= 0.2
            climate_score = max(0.5, climate_score)
        
        # Soil match (using default quality index)
        soil_score = self.DEFAULT_CLIMATE['soil_quality_index']
        
        # Weighted composite
        composite = (
            0.4 * yield_score +
            0.3 * revenue_score +
            0.2 * climate_score +
            0.1 * soil_score
        )
        
        return round(composite, 4)
    
    def assess_risk(
        self,
        composite_score: float,
        scenario: Optional[ScenarioInput] = None
    ) -> str:
        """Assess risk level based on score and scenario"""
        if scenario:
            # Increase risk for adverse scenarios
            if scenario.rainfall_delta < -0.3 or scenario.temp_delta > 3.0:
                if composite_score > 0.6:
                    return "medium"
                return "high"
        
        if composite_score > 0.7:
            return "low"
        elif composite_score > 0.4:
            return "medium"
        return "high"
    
    def optimize(
        self,
        district: str,
        season: str,
        area: float,
        scenario: Optional[ScenarioInput] = None,
        top_n: int = 5
    ) -> List[CropRecommendation]:
        """
        Optimize crop selection for given district/season.
        Returns ranked list of recommendations.
        """
        recommendations = []
        
        for crop in self.DEFAULT_CROPS:
            # Predict yield
            yield_pred = self.predict_yield(crop, district, season, scenario)
            
            # Predict price
            price_pred = self.predict_price(crop, district)
            
            # Calculate revenue per hectare
            revenue_per_ha = self.calculate_revenue(yield_pred, price_pred, scenario)
            
            # Calculate composite score
            score = self.calculate_composite_score(yield_pred, revenue_per_ha, scenario)
            
            # Assess risk
            risk = self.assess_risk(score, scenario)
            
            # Total revenue for given area
            total_revenue = revenue_per_ha * area
            
            recommendations.append({
                'crop': crop,
                'composite_score': score,
                'predicted_yield_tonnes_per_ha': round(yield_pred, 2),
                'predicted_price_inr_per_tonne': round(price_pred, 0),
                'expected_revenue_inr_per_ha': round(revenue_per_ha, 0),
                'total_revenue_inr': round(total_revenue, 0),
                'risk_level': risk
            })
        
        # Sort by composite score (descending)
        recommendations.sort(key=lambda x: x['composite_score'], reverse=True)
        
        # ── Sustainability enrichment (deterministic, no ML) ──
        soil_quality = self.DEFAULT_CLIMATE['soil_quality_index']
        self.sustainability_engine.enrich_crop_results(
            crop_rankings=recommendations,
            soil_quality_index=soil_quality,
            area=area,
            season=season,
        )
        
        # Add ranks and convert to schema
        result = []
        for i, rec in enumerate(recommendations[:top_n], 1):
            sus = rec.pop('sustainability_metrics', None)
            proxy = rec.pop('proxy_metrics', True)
            result.append(CropRecommendation(
                rank=i,
                sustainability_metrics=SustainabilityMetrics(**sus) if sus else None,
                proxy_metrics=proxy,
                **rec
            ))
        
        return result
    
    def get_scenario_name(self, scenario: Optional[ScenarioInput]) -> str:
        """Get human-readable scenario name"""
        if scenario is None:
            return "baseline"
        
        parts = []
        
        if scenario.rainfall_delta < -0.3:
            parts.append("severe_drought")
        elif scenario.rainfall_delta < -0.1:
            parts.append("mild_drought")
        elif scenario.rainfall_delta > 0.2:
            parts.append("wet")
        
        if scenario.temp_delta > 3.0:
            parts.append("severe_warming")
        elif scenario.temp_delta > 1.5:
            parts.append("moderate_warming")
        elif scenario.temp_delta < -1.0:
            parts.append("cooling")
        
        if not parts:
            if scenario.rainfall_delta != 0 or scenario.temp_delta != 0:
                return "custom_scenario"
            return "baseline"
        
        return "_".join(parts)


# Global predictor instance
_predictor = None


def get_predictor() -> CropPredictor:
    """Get or create the global predictor instance"""
    global _predictor
    if _predictor is None:
        _predictor = CropPredictor()
    return _predictor
