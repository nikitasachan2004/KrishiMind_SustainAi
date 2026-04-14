"""
KrishiMind SustainAI - Unit Tests
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestModelLoader:
    """Tests for model loading functionality"""
    
    def test_models_exist(self):
        """Verify model files exist"""
        base_path = Path(__file__).parent.parent
        
        yield_model = base_path / 'models' / 'yield_model.pkl'
        price_model = base_path / 'models' / 'price_model.pkl'
        
        assert yield_model.exists(), "Yield model not found"
        assert price_model.exists(), "Price model not found"
    
    def test_artifacts_exist(self):
        """Verify artifact files exist"""
        base_path = Path(__file__).parent.parent
        
        yield_features = base_path / 'artifacts' / 'yield_features.json'
        price_features = base_path / 'artifacts' / 'price_features.json'
        
        assert yield_features.exists(), "Yield features not found"
        assert price_features.exists(), "Price features not found"
    
    def test_model_loader_singleton(self):
        """Test ModelLoader is singleton"""
        from cloud.api.model_loader import ModelLoader
        
        loader1 = ModelLoader()
        loader2 = ModelLoader()
        
        assert loader1 is loader2


class TestSchemas:
    """Tests for Pydantic schemas"""
    
    def test_crop_plan_request_valid(self):
        """Test valid request passes validation"""
        from cloud.api.schemas import CropPlanRequest, SeasonEnum
        
        request = CropPlanRequest(
            district="Guntur",
            season=SeasonEnum.KHARIF,
            area=10.0
        )
        
        assert request.district == "Guntur"
        assert request.area == 10.0

    def test_crop_plan_request_optional_image_path(self):
        """Test request accepts optional image path."""
        from cloud.api.schemas import CropPlanRequest, SeasonEnum

        request = CropPlanRequest(
            district="Guntur",
            season=SeasonEnum.KHARIF,
            area=10.0,
            image_path="/tmp/leaf.jpg",
        )

        assert request.image_path == "/tmp/leaf.jpg"
    
    def test_crop_plan_request_negative_area(self):
        """Test negative area fails validation"""
        from cloud.api.schemas import CropPlanRequest, SeasonEnum
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            CropPlanRequest(
                district="Guntur",
                season=SeasonEnum.KHARIF,
                area=-5.0
            )
    
    def test_scenario_input_bounds(self):
        """Test scenario input bounds"""
        from cloud.api.schemas import ScenarioInput
        from pydantic import ValidationError
        
        # Valid scenario
        scenario = ScenarioInput(rainfall_delta=-0.5, temp_delta=2.0)
        assert scenario.rainfall_delta == -0.5
        
        # Invalid rainfall delta (out of bounds)
        with pytest.raises(ValidationError):
            ScenarioInput(rainfall_delta=-1.5, temp_delta=0.0)


class TestPredictor:
    """Tests for prediction logic"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Ensure models are loaded"""
        from cloud.api.model_loader import ensure_models_loaded
        ensure_models_loaded()
    
    def test_encode_season(self):
        """Test season encoding"""
        from cloud.api.predict import get_predictor
        
        predictor = get_predictor()
        
        # Kharif should encode to 1
        assert predictor._encode_season("Kharif") == 1
        
        # Unknown season should return 0
        assert predictor._encode_season("InvalidSeason") == 0
    
    def test_yield_prediction_positive(self):
        """Test yield prediction returns positive value"""
        from cloud.api.predict import get_predictor
        
        predictor = get_predictor()
        
        yield_pred = predictor.predict_yield(
            crop="Rice",
            district="Guntur",
            season="Kharif"
        )
        
        assert yield_pred > 0
    
    def test_price_prediction_positive(self):
        """Test price prediction returns positive value"""
        from cloud.api.predict import get_predictor
        
        predictor = get_predictor()
        
        price_pred = predictor.predict_price(
            crop="Rice",
            district="Guntur"
        )
        
        assert price_pred > 0
    
    def test_optimize_returns_recommendations(self):
        """Test optimize returns non-empty recommendations"""
        from cloud.api.predict import get_predictor
        
        predictor = get_predictor()
        
        recommendations = predictor.optimize(
            district="Guntur",
            season="Kharif",
            area=10.0,
            top_n=5
        )
        
        assert len(recommendations) > 0
        assert len(recommendations) <= 5
        
        # Check first recommendation has required fields
        first = recommendations[0]
        assert first.rank == 1
        assert first.crop is not None
        assert first.composite_score > 0


class TestPlantDiseaseDetection:
    """Tests for plant disease integration wrapper."""

    def test_predict_disease_invalid_path(self):
        """Invalid image paths should not raise and should return fallback."""
        from src.plant_detection.inference.predict import predict_disease

        result = predict_disease("/tmp/does-not-exist.jpg")

        assert result == {"disease": "unknown", "confidence": 0.0}


class TestDataDictionary:
    """Tests for data integrity"""
    
    def test_yield_features_valid_json(self):
        """Test yield features JSON is valid"""
        import json
        base_path = Path(__file__).parent.parent
        
        with open(base_path / 'artifacts' / 'yield_features.json') as f:
            data = json.load(f)
        
        assert 'feature_columns' in data
        assert 'label_encodings' in data
        assert len(data['feature_columns']) == 8
    
    def test_model_metrics_valid_json(self):
        """Test model metrics JSON is valid"""
        import json
        base_path = Path(__file__).parent.parent
        
        with open(base_path / 'reports' / 'model_metrics.json') as f:
            data = json.load(f)
        
        assert 'yield_model' in data
        assert 'price_model' in data
        assert data['summary']['models_evaluated'] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
