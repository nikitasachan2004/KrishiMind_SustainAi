"""
KrishiMind SustainAI - Model Loader
Startup model loading with validation guards
"""

import os
import sys
import json
import logging
import joblib
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('model_loader')


class ModelLoadError(Exception):
    """Raised when model loading fails"""
    pass


class ModelLoader:
    """
    Singleton model loader for KrishiMind SustainAI.
    Loads models once at startup with validation.
    """
    
    _instance = None
    _models_loaded = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not ModelLoader._models_loaded:
            self.yield_model = None
            self.price_model = None
            self.yield_features = None
            self.price_features = None
            self.base_path = self._find_base_path()
    
    def _find_base_path(self) -> Path:
        """Find the project base path"""
        # Try multiple possible locations
        candidates = [
            Path(__file__).parent.parent.parent,  # cloud/api/ -> root
            Path.cwd(),
            Path.cwd().parent,
            Path('/var/task'),  # AWS Lambda
            Path('/opt/ml/model'),  # SageMaker
        ]
        
        for candidate in candidates:
            if (candidate / 'models').exists():
                return candidate
        
        # Default to parent of cloud directory
        return Path(__file__).parent.parent.parent
    
    def _validate_model_file(self, path: Path, name: str) -> None:
        """Validate that a model file exists and is readable"""
        if not path.exists():
            raise ModelLoadError(f"STARTUP FAILURE: {name} not found at {path}")
        
        if path.stat().st_size == 0:
            raise ModelLoadError(f"STARTUP FAILURE: {name} is empty at {path}")
        
        logger.info(f"✓ Validated {name}: {path} ({path.stat().st_size:,} bytes)")
    
    def _validate_json_file(self, path: Path, name: str) -> None:
        """Validate that a JSON file exists and is valid"""
        if not path.exists():
            raise ModelLoadError(f"STARTUP FAILURE: {name} not found at {path}")
        
        try:
            with open(path, 'r') as f:
                json.load(f)
            logger.info(f"✓ Validated {name}: {path}")
        except json.JSONDecodeError as e:
            raise ModelLoadError(f"STARTUP FAILURE: {name} is invalid JSON: {e}")
    
    def load_all(self) -> bool:
        """
        Load all models and feature configs.
        Returns True if successful, raises ModelLoadError otherwise.
        """
        if ModelLoader._models_loaded:
            logger.info("Models already loaded, skipping...")
            return True
        
        logger.info("=" * 60)
        logger.info("KRISHIMIND SUSTAINAI - MODEL STARTUP")
        logger.info("=" * 60)
        logger.info(f"Base path: {self.base_path}")
        
        # Define paths
        yield_model_path = self.base_path / 'models' / 'yield_model.pkl'
        price_model_path = self.base_path / 'models' / 'price_model.pkl'
        yield_features_path = self.base_path / 'artifacts' / 'yield_features.json'
        price_features_path = self.base_path / 'artifacts' / 'price_features.json'
        
        # Validate all files exist before loading
        logger.info("\n[1/4] Validating model files...")
        self._validate_model_file(yield_model_path, "Yield Model")
        self._validate_model_file(price_model_path, "Price Model")
        
        logger.info("\n[2/4] Validating feature configs...")
        self._validate_json_file(yield_features_path, "Yield Features")
        self._validate_json_file(price_features_path, "Price Features")
        
        # Load models
        logger.info("\n[3/4] Loading models into memory...")
        try:
            self.yield_model = joblib.load(yield_model_path)
            logger.info(f"✓ Yield model loaded: {type(self.yield_model).__name__}")
            
            self.price_model = joblib.load(price_model_path)
            logger.info(f"✓ Price model loaded: {type(self.price_model).__name__}")
        except Exception as e:
            raise ModelLoadError(f"Failed to load models: {e}")
        
        # Load feature configs
        logger.info("\n[4/4] Loading feature configurations...")
        try:
            with open(yield_features_path, 'r') as f:
                self.yield_features = json.load(f)
            logger.info(f"✓ Yield features: {len(self.yield_features.get('feature_columns', []))} features")
            
            with open(price_features_path, 'r') as f:
                self.price_features = json.load(f)
            logger.info(f"✓ Price features: {len(self.price_features.get('feature_names', []))} features")
        except Exception as e:
            raise ModelLoadError(f"Failed to load feature configs: {e}")
        
        ModelLoader._models_loaded = True
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ ALL MODELS LOADED SUCCESSFULLY")
        logger.info("=" * 60)
        
        return True
    
    def get_yield_model(self):
        """Get loaded yield model"""
        if not ModelLoader._models_loaded:
            raise ModelLoadError("Models not loaded. Call load_all() first.")
        return self.yield_model
    
    def get_price_model(self):
        """Get loaded price model"""
        if not ModelLoader._models_loaded:
            raise ModelLoadError("Models not loaded. Call load_all() first.")
        return self.price_model
    
    def get_yield_features(self) -> Dict[str, Any]:
        """Get yield feature configuration"""
        if not ModelLoader._models_loaded:
            raise ModelLoadError("Models not loaded. Call load_all() first.")
        return self.yield_features
    
    def get_price_features(self) -> Dict[str, Any]:
        """Get price feature configuration"""
        if not ModelLoader._models_loaded:
            raise ModelLoadError("Models not loaded. Call load_all() first.")
        return self.price_features
    
    def is_loaded(self) -> bool:
        """Check if models are loaded"""
        return ModelLoader._models_loaded
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about loaded models"""
        if not ModelLoader._models_loaded:
            return {"status": "not_loaded"}
        
        return {
            "status": "loaded",
            "yield_model": {
                "type": type(self.yield_model).__name__,
                "n_features": len(self.yield_features.get('feature_columns', [])),
                "features": self.yield_features.get('feature_columns', [])
            },
            "price_model": {
                "type": type(self.price_model).__name__,
                "n_features": len(self.price_features.get('feature_names', [])),
                "features": self.price_features.get('feature_names', [])
            }
        }


# Global model loader instance
model_loader = ModelLoader()


def get_model_loader() -> ModelLoader:
    """Get the global model loader instance"""
    return model_loader


def ensure_models_loaded() -> bool:
    """Ensure models are loaded, raises error if not"""
    if not model_loader.is_loaded():
        return model_loader.load_all()
    return True
