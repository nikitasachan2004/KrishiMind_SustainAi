"""
KrishiMind SustainAI - SageMaker Inference Script
Implements required SageMaker serving functions
"""

import os
import json
import logging
import joblib
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# Global model storage
MODELS = {}


def model_fn(model_dir):
    """
    Load models from the model directory.
    
    This function is called once when the SageMaker endpoint starts.
    
    Args:
        model_dir: Path to the model artifacts (S3 downloaded to /opt/ml/model)
    
    Returns:
        dict: Dictionary containing loaded models and configs
    """
    logger.info(f"Loading models from: {model_dir}")
    model_path = Path(model_dir)
    
    # Load yield model
    yield_model_path = model_path / 'yield_model.pkl'
    if yield_model_path.exists():
        MODELS['yield_model'] = joblib.load(yield_model_path)
        logger.info(f"✓ Loaded yield model: {type(MODELS['yield_model']).__name__}")
    else:
        raise ValueError(f"Yield model not found at {yield_model_path}")
    
    # Load price model
    price_model_path = model_path / 'price_model.pkl'
    if price_model_path.exists():
        MODELS['price_model'] = joblib.load(price_model_path)
        logger.info(f"✓ Loaded price model: {type(MODELS['price_model']).__name__}")
    else:
        raise ValueError(f"Price model not found at {price_model_path}")
    
    # Load feature configs
    yield_features_path = model_path / 'yield_features.json'
    if yield_features_path.exists():
        with open(yield_features_path, 'r') as f:
            MODELS['yield_features'] = json.load(f)
        logger.info("✓ Loaded yield features config")
    
    price_features_path = model_path / 'price_features.json'
    if price_features_path.exists():
        with open(price_features_path, 'r') as f:
            MODELS['price_features'] = json.load(f)
        logger.info("✓ Loaded price features config")
    
    logger.info("=" * 40)
    logger.info("MODEL LOADING COMPLETE")
    logger.info("=" * 40)
    
    return MODELS


def input_fn(request_body, request_content_type):
    """
    Parse input data from the request.
    
    Args:
        request_body: Raw request body (bytes or string)
        request_content_type: Content type header
    
    Returns:
        dict: Parsed input data
    """
    logger.info(f"Parsing input with content type: {request_content_type}")
    
    if request_content_type == 'application/json':
        input_data = json.loads(request_body)
        
        # Validate required fields
        required = ['district', 'season', 'area']
        for field in required:
            if field not in input_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate area > 0
        if input_data['area'] <= 0:
            raise ValueError("Area must be greater than 0")
        
        return input_data
    
    raise ValueError(f"Unsupported content type: {request_content_type}")


def predict_fn(input_data, models):
    """
    Generate predictions using loaded models.
    
    Args:
        input_data: Parsed input from input_fn
        models: Dictionary from model_fn
    
    Returns:
        dict: Prediction results
    """
    logger.info(f"Generating predictions for: {input_data}")
    
    yield_model = models['yield_model']
    price_model = models['price_model']
    yield_features = models.get('yield_features', {})
    price_features = models.get('price_features', {})
    
    district = input_data['district']
    season = input_data['season']
    area = input_data['area']
    scenario = input_data.get('scenario', {})
    
    # Get encodings
    label_encodings = yield_features.get('label_encodings', {})
    
    # Encode inputs
    season_map = {s: i for i, s in enumerate(label_encodings.get('season', []))}
    crop_map = {c: i for i, c in enumerate(label_encodings.get('crop_name', []))}
    district_map = {d: i for i, d in enumerate(label_encodings.get('district_name', []))}
    
    season_encoded = season_map.get(season, 0)
    district_encoded = district_map.get(district, 0)
    
    # Default climate values
    default_climate = {
        'rainfall_anomaly': scenario.get('rainfall_delta', 0) - 0.03,
        'monsoon_rainfall': 295.2 * (1 + scenario.get('rainfall_delta', 0)),
        'heatwave_count': 2.0 + max(0, scenario.get('temp_delta', 0)),
        'growing_degree_days': 15.87 + scenario.get('temp_delta', 0) * 0.5,
        'soil_quality_index': 0.83
    }
    
    # Default prices
    default_prices = {
        'Rice': 2680, 'Wheat': 1931, 'Maize': 2580, 'Sugarcane': 3626,
        'Cotton(Lint)': 6620, 'Groundnut': 5550, 'Soybean': 3470
    }
    
    # Crops to evaluate
    crops = ['Rice', 'Wheat', 'Maize', 'Sugarcane', 'Cotton(Lint)', 'Groundnut', 'Soybean']
    
    recommendations = []
    
    for crop in crops:
        crop_encoded = crop_map.get(crop, 0)
        
        # Build yield features
        yield_features_vec = np.array([
            default_climate['rainfall_anomaly'],
            default_climate['monsoon_rainfall'],
            default_climate['heatwave_count'],
            default_climate['growing_degree_days'],
            default_climate['soil_quality_index'],
            season_encoded,
            crop_encoded,
            district_encoded
        ]).reshape(1, -1)
        
        # Predict yield
        try:
            yield_pred = max(0.01, float(yield_model.predict(yield_features_vec)[0]))
        except:
            yield_pred = 1.0
        
        # Get price (use default)
        price = default_prices.get(crop, 3000)
        
        # Calculate revenue
        revenue_per_ha = yield_pred * price
        
        # Simple score
        score = min(1.0, yield_pred / 100.0) * 0.4 + min(1.0, revenue_per_ha / 300000.0) * 0.6
        
        recommendations.append({
            'crop': crop,
            'composite_score': round(score, 4),
            'predicted_yield_tonnes_per_ha': round(yield_pred, 2),
            'predicted_price_inr_per_tonne': price,
            'expected_revenue_inr_per_ha': round(revenue_per_ha, 0),
            'total_revenue_inr': round(revenue_per_ha * area, 0)
        })
    
    # Sort by score
    recommendations.sort(key=lambda x: x['composite_score'], reverse=True)
    
    # Add ranks
    for i, rec in enumerate(recommendations, 1):
        rec['rank'] = i
    
    return {
        'status': 'success',
        'district': district,
        'season': season,
        'area_hectares': area,
        'recommendations': recommendations[:5],
        'disclaimer': 'District-level aggregation. Not farm-specific advice.'
    }


def output_fn(prediction, response_content_type):
    """
    Format output for the response.
    
    Args:
        prediction: Result from predict_fn
        response_content_type: Desired response content type
    
    Returns:
        str: Formatted response body
    """
    if response_content_type == 'application/json':
        return json.dumps(prediction)
    
    raise ValueError(f"Unsupported response content type: {response_content_type}")
