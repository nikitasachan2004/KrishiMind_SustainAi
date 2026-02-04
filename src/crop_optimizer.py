"""
Crop Optimizer Module
=====================
Ranks crops for a given district and season based on multi-criteria scoring.
Combines yield, revenue, climate stability, and soil match.

Author: AgroPro ML Team
"""

import numpy as np
import pandas as pd
import logging
import pickle
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass

# Handle imports for both module and standalone execution
try:
    from .revenue_engine import RevenueEngine
except ImportError:
    from revenue_engine import RevenueEngine

logger = logging.getLogger(__name__)

# ============================================================================
# CONSTANTS
# ============================================================================
MODELS_DIR = Path(__file__).parent.parent / "models"

# Scoring weights (must sum to 1.0)
SCORE_WEIGHTS = {
    "yield": 0.4,
    "revenue": 0.3,
    "climate_stability": 0.2,
    "soil_match": 0.1,
}


@dataclass
class CropScore:
    """Detailed scoring breakdown for a crop."""
    crop_name: str
    district: str
    season: str
    
    # Predictions
    predicted_yield: float
    predicted_price: float
    predicted_revenue: float
    
    # Component scores (normalized 0-1)
    yield_score: float
    revenue_score: float
    climate_stability_score: float
    soil_match_score: float
    
    # Final composite score
    composite_score: float
    
    # Risk factors
    rainfall_anomaly: float
    heatwave_count: int
    soil_quality_index: float


class CropOptimizer:
    """
    Multi-criteria crop optimization engine.
    
    For a given district + season, evaluates all candidate crops and ranks
    them based on:
        - Predicted yield (40%)
        - Expected revenue (30%)
        - Climate stability (20%)
        - Soil match (10%)
    """
    
    def __init__(
        self,
        yield_model: Any = None,
        price_model: Any = None,
        feature_builder: Any = None,
        weights: Dict[str, float] = None,
    ):
        """
        Initialize crop optimizer.
        
        Args:
            yield_model: Trained yield prediction model
            price_model: Trained price prediction model (or trainer instance)
            feature_builder: Feature builder for yield model
            weights: Custom scoring weights (optional)
        """
        self.yield_model = yield_model
        self.price_model = price_model
        self.feature_builder = feature_builder
        self.revenue_engine = RevenueEngine()
        self.weights = weights or SCORE_WEIGHTS
        
        # Validate weights sum to 1
        weight_sum = sum(self.weights.values())
        if abs(weight_sum - 1.0) > 0.01:
            logger.warning(f"Weights sum to {weight_sum}, normalizing...")
            self.weights = {k: v / weight_sum for k, v in self.weights.items()}
        
        logger.info(f"CropOptimizer initialized with weights: {self.weights}")
    
    def load_models(self) -> None:
        """Load trained models from disk."""
        # Load yield model
        yield_model_path = MODELS_DIR / "yield_model.pkl"
        if yield_model_path.exists():
            with open(yield_model_path, "rb") as f:
                self.yield_model = pickle.load(f)
            logger.info("Loaded yield model")
        else:
            logger.warning("Yield model not found")
        
        # Load price model
        price_model_path = MODELS_DIR / "price_model.pkl"
        if price_model_path.exists():
            with open(price_model_path, "rb") as f:
                data = pickle.load(f)
                self.price_model = data
            logger.info("Loaded price model")
        else:
            logger.warning("Price model not found")
    
    def predict_yield(
        self,
        crop_name: str,
        district: str,
        season: str,
        climate_features: Dict[str, float],
        soil_features: Dict[str, float],
    ) -> float:
        """
        Predict yield for a specific crop-district-season combination.
        
        Args:
            crop_name: Name of the crop
            district: District name
            season: Season name
            climate_features: Dict with rainfall_mean, rainfall_anomaly, etc.
            soil_features: Dict with soil_quality_index
            
        Returns:
            Predicted yield (tonnes/hectare)
        """
        if self.yield_model is None:
            logger.warning("No yield model, returning default yield")
            return 1.5  # Default yield
        
        if self.feature_builder is None:
            logger.warning("No feature builder, returning default yield")
            return 1.5
        
        try:
            # Build feature vector
            # This is a simplified version - real implementation would use proper encoding
            feature_dict = {
                "rainfall_mean": climate_features.get("rainfall_mean", 100),
                "rainfall_anomaly": climate_features.get("rainfall_anomaly", 0),
                "monsoon_rainfall": climate_features.get("monsoon_rainfall", 800),
                "avg_temp_mean": climate_features.get("avg_temp_mean", 28),
                "heatwave_count": climate_features.get("heatwave_count", 0),
                "growing_degree_days": climate_features.get("growing_degree_days", 15),
                "soil_quality_index": soil_features.get("soil_quality_index", 1.0),
                "season": season,
                "crop_name": crop_name,
                "district_name": district,
            }
            
            # Create dataframe
            df = pd.DataFrame([feature_dict])
            
            # Transform features
            df_processed, _ = self.feature_builder.build_features(df, fit=False)
            X, _, feature_names = self.feature_builder.get_feature_matrix(df_processed, target_col=None)
            
            # Predict
            prediction = self.yield_model.predict(X)[0]
            return max(0.1, float(prediction))  # Ensure positive yield
            
        except Exception as e:
            logger.warning(f"Yield prediction failed for {crop_name}: {e}")
            return 1.5  # Default fallback
    
    def predict_price(
        self,
        crop_name: str,
        district: str,
        month: int = 6,
    ) -> float:
        """
        Predict price for a crop.
        
        Args:
            crop_name: Name of the crop
            district: District name
            month: Month for price prediction
            
        Returns:
            Predicted price per tonne
        """
        if self.price_model is None:
            logger.warning("No price model, returning default price")
            return 2000  # Default price
        
        try:
            if isinstance(self.price_model, dict):
                # If loaded from pickle, extract components
                model = self.price_model.get("model")
                encoders = self.price_model.get("label_encoders", {})
                
                # Encode inputs
                crop_encoded = 0
                district_encoded = 0
                
                if "crop" in encoders:
                    enc = encoders["crop"]
                    if crop_name in enc.classes_:
                        crop_encoded = list(enc.classes_).index(crop_name)
                
                if "district" in encoders:
                    enc = encoders["district"]
                    if district in enc.classes_:
                        district_encoded = list(enc.classes_).index(district)
                
                X = np.array([[crop_encoded, district_encoded, month]])
                prediction = model.predict(X)[0]
                return max(500, float(prediction))  # Ensure reasonable price
            else:
                # If it's a trainer instance with predict method
                return self.price_model.predict(crop_name, district, month)
                
        except Exception as e:
            logger.warning(f"Price prediction failed for {crop_name}: {e}")
            return 2000  # Default fallback
    
    def calculate_climate_stability(
        self,
        rainfall_anomaly: float,
        heatwave_count: int,
    ) -> float:
        """
        Calculate climate stability score (0-1).
        
        Higher score = more stable/favorable climate.
        
        Args:
            rainfall_anomaly: Standardized rainfall anomaly
            heatwave_count: Number of heatwave events
            
        Returns:
            Climate stability score (0-1)
        """
        # Rainfall component (penalize severe anomalies)
        rainfall_score = 1.0 - min(abs(rainfall_anomaly), 2.0) / 2.0
        
        # Heatwave component (penalize high counts)
        heatwave_score = max(0, 1.0 - heatwave_count / 10.0)
        
        # Combined score
        stability = 0.6 * rainfall_score + 0.4 * heatwave_score
        return max(0, min(1, stability))
    
    def calculate_soil_match(
        self,
        soil_quality_index: float,
        crop_name: str,
    ) -> float:
        """
        Calculate soil suitability score for a crop.
        
        Args:
            soil_quality_index: Overall soil quality (0-1)
            crop_name: Name of the crop
            
        Returns:
            Soil match score (0-1)
        """
        # Base score is the soil quality index
        # Could be extended with crop-specific soil requirements
        base_score = min(1.0, max(0.0, soil_quality_index))
        
        # Crop-specific adjustments (simplified)
        # In production, this would use a crop-soil compatibility matrix
        crop_adjustments = {
            "rice": 1.0,  # Rice tolerates various soils
            "wheat": 0.95,
            "cotton": 0.9,
            "sugarcane": 1.0,
            "groundnut": 0.85,
        }
        
        crop_lower = crop_name.lower()
        adjustment = 1.0
        for crop_key, adj in crop_adjustments.items():
            if crop_key in crop_lower:
                adjustment = adj
                break
        
        return base_score * adjustment
    
    def normalize_scores(self, scores: List[float]) -> List[float]:
        """
        Min-max normalize scores to 0-1 range.
        
        Args:
            scores: List of raw scores
            
        Returns:
            Normalized scores
        """
        if not scores:
            return []
        
        min_val = min(scores)
        max_val = max(scores)
        
        if max_val == min_val:
            return [1.0] * len(scores)
        
        return [(s - min_val) / (max_val - min_val) for s in scores]
    
    def optimize(
        self,
        district: str,
        season: str,
        candidate_crops: List[str],
        climate_features: Dict[str, float],
        soil_features: Dict[str, float],
        top_n: int = 3,
    ) -> List[CropScore]:
        """
        Rank crops for a district-season combination.
        
        Args:
            district: District name
            season: Season name
            candidate_crops: List of crop names to evaluate
            climate_features: Climate feature values
            soil_features: Soil feature values
            top_n: Number of top crops to return
            
        Returns:
            List of CropScore objects, sorted by composite score (descending)
        """
        logger.info("=" * 60)
        logger.info(f"Optimizing crops for {district} - {season}")
        logger.info("=" * 60)
        
        if not candidate_crops:
            logger.warning("No candidate crops provided")
            return []
        
        # Extract climate features
        rainfall_anomaly = climate_features.get("rainfall_anomaly", 0.0)
        heatwave_count = int(climate_features.get("heatwave_count", 0))
        soil_quality = soil_features.get("soil_quality_index", 1.0)
        
        # Evaluate each crop
        crop_evaluations = []
        
        for crop_name in candidate_crops:
            # Predict yield
            pred_yield = self.predict_yield(
                crop_name, district, season, climate_features, soil_features
            )
            
            # Predict price
            pred_price = self.predict_price(crop_name, district)
            
            # Calculate revenue
            revenue_output = self.revenue_engine.calculate(
                predicted_yield=pred_yield,
                predicted_price=pred_price,
                rainfall_anomaly=rainfall_anomaly,
                heatwave_count=heatwave_count,
                soil_quality_index=soil_quality,
            )
            
            # Calculate component scores
            climate_stability = self.calculate_climate_stability(
                rainfall_anomaly, heatwave_count
            )
            soil_match = self.calculate_soil_match(soil_quality, crop_name)
            
            crop_evaluations.append({
                "crop_name": crop_name,
                "yield": pred_yield,
                "price": pred_price,
                "revenue": revenue_output.adjusted_revenue,
                "climate_stability": climate_stability,
                "soil_match": soil_match,
                "rainfall_anomaly": rainfall_anomaly,
                "heatwave_count": heatwave_count,
                "soil_quality_index": soil_quality,
            })
        
        # Normalize scores
        yields = [e["yield"] for e in crop_evaluations]
        revenues = [e["revenue"] for e in crop_evaluations]
        
        norm_yields = self.normalize_scores(yields)
        norm_revenues = self.normalize_scores(revenues)
        
        # Calculate composite scores
        results = []
        
        for i, eval_data in enumerate(crop_evaluations):
            # Component scores
            yield_score = norm_yields[i]
            revenue_score = norm_revenues[i]
            climate_score = eval_data["climate_stability"]
            soil_score = eval_data["soil_match"]
            
            # Weighted composite
            composite = (
                self.weights["yield"] * yield_score +
                self.weights["revenue"] * revenue_score +
                self.weights["climate_stability"] * climate_score +
                self.weights["soil_match"] * soil_score
            )
            
            crop_score = CropScore(
                crop_name=eval_data["crop_name"],
                district=district,
                season=season,
                predicted_yield=eval_data["yield"],
                predicted_price=eval_data["price"],
                predicted_revenue=eval_data["revenue"],
                yield_score=yield_score,
                revenue_score=revenue_score,
                climate_stability_score=climate_score,
                soil_match_score=soil_score,
                composite_score=composite,
                rainfall_anomaly=eval_data["rainfall_anomaly"],
                heatwave_count=eval_data["heatwave_count"],
                soil_quality_index=eval_data["soil_quality_index"],
            )
            
            results.append(crop_score)
        
        # Sort by composite score (descending)
        results.sort(key=lambda x: x.composite_score, reverse=True)
        
        # Log top results
        logger.info(f"\nTop {top_n} crops for {district} - {season}:")
        for i, score in enumerate(results[:top_n], 1):
            logger.info(f"  {i}. {score.crop_name}: "
                       f"Score={score.composite_score:.3f}, "
                       f"Yield={score.predicted_yield:.2f}, "
                       f"Revenue=₹{score.predicted_revenue:,.0f}")
        
        return results[:top_n]


def get_default_candidate_crops() -> List[str]:
    """Get list of common crops for optimization."""
    return [
        "Rice",
        "Wheat",
        "Cotton",
        "Sugarcane",
        "Groundnut",
        "Maize",
        "Soybean",
        "Arhar/Tur",
        "Gram",
        "Bajra",
    ]


if __name__ == "__main__":
    # Test crop optimizer
    logging.basicConfig(level=logging.INFO)
    
    optimizer = CropOptimizer()
    optimizer.load_models()
    
    # Sample optimization
    results = optimizer.optimize(
        district="Guntur",
        season="Kharif",
        candidate_crops=get_default_candidate_crops(),
        climate_features={
            "rainfall_mean": 120,
            "rainfall_anomaly": -0.2,
            "monsoon_rainfall": 850,
            "avg_temp_mean": 28,
            "heatwave_count": 2,
            "growing_degree_days": 16,
        },
        soil_features={
            "soil_quality_index": 0.85,
        },
        top_n=5,
    )
    
    print("\n" + "=" * 60)
    print("OPTIMIZATION RESULTS")
    print("=" * 60)
    
    for i, score in enumerate(results, 1):
        print(f"\n{i}. {score.crop_name}")
        print(f"   Composite Score: {score.composite_score:.3f}")
        print(f"   Predicted Yield: {score.predicted_yield:.2f} tonnes/ha")
        print(f"   Predicted Price: ₹{score.predicted_price:,.0f}/tonne")
        print(f"   Expected Revenue: ₹{score.predicted_revenue:,.0f}/ha")
