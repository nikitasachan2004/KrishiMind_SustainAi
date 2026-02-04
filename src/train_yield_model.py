"""
Yield Model Training Module
===========================
Trains and evaluates multiple regression models for crop yield prediction.
Implements model selection with cross-validation and saves best model.

Author: AgroPro ML Team
"""

import pandas as pd
import numpy as np
import logging
import json
import pickle
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

logger = logging.getLogger(__name__)

# ============================================================================
# CONSTANTS
# ============================================================================
MODELS_DIR = Path(__file__).parent.parent / "models"
ARTIFACTS_DIR = Path(__file__).parent.parent / "artifacts"
RANDOM_STATE = 42

# Model configurations (optimized for faster training on large datasets)
MODEL_CONFIGS = {
    "RandomForest": {
        "class": RandomForestRegressor,
        "params": {
            "n_estimators": 50,
            "max_depth": 12,
            "min_samples_split": 10,
            "min_samples_leaf": 5,
            "random_state": RANDOM_STATE,
            "n_jobs": -1,
        }
    },
    "GradientBoosting": {
        "class": GradientBoostingRegressor,
        "params": {
            "n_estimators": 50,
            "max_depth": 6,
            "learning_rate": 0.1,
            "min_samples_split": 10,
            "min_samples_leaf": 5,
            "random_state": RANDOM_STATE,
            "subsample": 0.8,
        }
    },
}

# Try to import XGBoost/LightGBM
try:
    from xgboost import XGBRegressor
    MODEL_CONFIGS["XGBoost"] = {
        "class": XGBRegressor,
        "params": {
            "n_estimators": 50,
            "max_depth": 6,
            "learning_rate": 0.1,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "random_state": RANDOM_STATE,
            "n_jobs": -1,
            "verbosity": 0,
        }
    }
    logger.info("XGBoost available")
except ImportError:
    logger.info("XGBoost not installed, skipping")

try:
    from lightgbm import LGBMRegressor
    MODEL_CONFIGS["LightGBM"] = {
        "class": LGBMRegressor,
        "params": {
            "n_estimators": 50,
            "max_depth": 6,
            "learning_rate": 0.1,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "random_state": RANDOM_STATE,
            "n_jobs": -1,
            "verbose": -1,
        }
    }
    logger.info("LightGBM available")
except ImportError:
    logger.info("LightGBM not installed, skipping")


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """
    Compute regression metrics.
    
    Args:
        y_true: Ground truth values
        y_pred: Predicted values
        
    Returns:
        Dictionary of metric name to value
    """
    return {
        "R2": float(r2_score(y_true, y_pred)),
        "RMSE": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "MAE": float(mean_absolute_error(y_true, y_pred)),
    }


def train_single_model(
    model_name: str,
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray,
    cv_folds: int = 5
) -> Tuple[Any, Dict[str, Any]]:
    """
    Train and evaluate a single model.
    
    Args:
        model_name: Name of the model configuration
        X_train: Training features
        y_train: Training targets
        X_test: Test features
        y_test: Test targets
        cv_folds: Number of cross-validation folds
        
    Returns:
        Tuple of (trained model, metrics dictionary)
    """
    if model_name not in MODEL_CONFIGS:
        raise ValueError(f"Unknown model: {model_name}")
    
    config = MODEL_CONFIGS[model_name]
    model_class = config["class"]
    params = config["params"]
    
    logger.info(f"\n{'='*40}")
    logger.info(f"Training {model_name}...")
    logger.info(f"{'='*40}")
    
    # Initialize model
    model = model_class(**params)
    
    # Cross-validation
    logger.info(f"Running {cv_folds}-fold cross-validation...")
    cv_scores = cross_val_score(model, X_train, y_train, cv=cv_folds, scoring="r2")
    cv_r2_mean = float(cv_scores.mean())
    cv_r2_std = float(cv_scores.std())
    
    logger.info(f"CV R2: {cv_r2_mean:.4f} (+/- {cv_r2_std:.4f})")
    
    # Train on full training set
    model.fit(X_train, y_train)
    
    # Evaluate on test set
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)
    
    train_metrics = compute_metrics(y_train, y_pred_train)
    test_metrics = compute_metrics(y_test, y_pred_test)
    
    logger.info(f"Train - R2: {train_metrics['R2']:.4f}, RMSE: {train_metrics['RMSE']:.4f}")
    logger.info(f"Test  - R2: {test_metrics['R2']:.4f}, RMSE: {test_metrics['RMSE']:.4f}")
    
    # Get feature importance if available
    feature_importance = None
    if hasattr(model, "feature_importances_"):
        feature_importance = model.feature_importances_.tolist()
    
    results = {
        "model_name": model_name,
        "cv_r2_mean": cv_r2_mean,
        "cv_r2_std": cv_r2_std,
        "train_metrics": train_metrics,
        "test_metrics": test_metrics,
        "feature_importance": feature_importance,
        "params": {k: str(v) if not isinstance(v, (int, float, bool, type(None))) else v 
                   for k, v in params.items()},
    }
    
    return model, results


def train_yield_model(
    X: np.ndarray,
    y: np.ndarray,
    feature_names: List[str],
    test_size: float = 0.2,
    cv_folds: int = 5
) -> Tuple[Any, Dict[str, Any]]:
    """
    Train multiple models and select the best one based on R2.
    
    Args:
        X: Feature matrix
        y: Target array
        feature_names: List of feature names
        test_size: Fraction for test split
        cv_folds: Number of CV folds
        
    Returns:
        Tuple of (best model, all results dictionary)
    """
    logger.info("=" * 60)
    logger.info("YIELD MODEL TRAINING")
    logger.info("=" * 60)
    logger.info(f"Data shape: X={X.shape}, y={y.shape}")
    logger.info(f"Features: {feature_names}")
    
    # Filter out rows with NaN/inf in target
    valid_mask = np.isfinite(y) & (y > 0)
    X_valid = X[valid_mask]
    y_valid = y[valid_mask]
    
    logger.info(f"Valid samples: {len(y_valid):,} / {len(y):,}")
    
    if len(y_valid) < 100:
        raise ValueError("Insufficient valid samples for training")
    
    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X_valid, y_valid, 
        test_size=test_size, 
        random_state=RANDOM_STATE
    )
    
    logger.info(f"Train size: {len(y_train):,}, Test size: {len(y_test):,}")
    
    # Train all models
    all_results = {}
    best_model = None
    best_r2 = -float("inf")
    best_model_name = None
    
    for model_name in MODEL_CONFIGS.keys():
        try:
            model, results = train_single_model(
                model_name, X_train, y_train, X_test, y_test, cv_folds
            )
            
            all_results[model_name] = results
            
            # Track best model by test R2
            test_r2 = results["test_metrics"]["R2"]
            if test_r2 > best_r2:
                best_r2 = test_r2
                best_model = model
                best_model_name = model_name
                
        except Exception as e:
            logger.error(f"Failed to train {model_name}: {e}")
            all_results[model_name] = {"error": str(e)}
    
    logger.info("\n" + "=" * 60)
    logger.info(f"BEST MODEL: {best_model_name} (Test R2: {best_r2:.4f})")
    logger.info("=" * 60)
    
    # Add summary to results
    summary = {
        "best_model": best_model_name,
        "best_test_r2": best_r2,
        "feature_names": feature_names,
        "n_samples": len(y_valid),
        "n_train": len(y_train),
        "n_test": len(y_test),
        "models_trained": list(all_results.keys()),
    }
    
    return best_model, {"summary": summary, "models": all_results}


def save_yield_model(
    model: Any,
    results: Dict[str, Any],
    feature_names: List[str]
) -> None:
    """
    Save trained yield model and artifacts.
    
    Args:
        model: Trained model object
        results: Training results dictionary
        feature_names: List of feature names
    """
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Save model
    model_path = MODELS_DIR / "yield_model.pkl"
    with open(model_path, "wb") as f:
        pickle.dump(model, f)
    logger.info(f"Saved model to {model_path}")
    
    # Save feature list
    features_path = ARTIFACTS_DIR / "yield_features.json"
    feature_artifact = {
        "feature_names": feature_names,
        "model_type": results["summary"]["best_model"],
        "test_r2": results["summary"]["best_test_r2"],
    }
    
    with open(features_path, "w") as f:
        json.dump(feature_artifact, f, indent=2)
    logger.info(f"Saved features to {features_path}")


def load_yield_model() -> Tuple[Any, Dict[str, Any]]:
    """
    Load trained yield model and feature info.
    
    Returns:
        Tuple of (model, feature_info)
    """
    model_path = MODELS_DIR / "yield_model.pkl"
    features_path = ARTIFACTS_DIR / "yield_features.json"
    
    if not model_path.exists():
        raise FileNotFoundError(f"Model not found: {model_path}")
    
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    
    feature_info = {}
    if features_path.exists():
        with open(features_path, "r") as f:
            feature_info = json.load(f)
    
    logger.info(f"Loaded yield model: {feature_info.get('model_type', 'unknown')}")
    return model, feature_info


if __name__ == "__main__":
    # Test yield model training
    logging.basicConfig(level=logging.INFO)
    
    from data_loader import load_master_training_table
    from feature_builder import FeatureBuilder
    
    # Load data
    df = load_master_training_table()
    
    if df is not None:
        # Build features
        builder = FeatureBuilder()
        df_processed, feature_cols = builder.build_features(df)
        X, y, feature_names = builder.get_feature_matrix(df_processed)
        
        # Train model
        best_model, results = train_yield_model(X, y, feature_names)
        
        # Save
        save_yield_model(best_model, results, feature_names)
        
        print("\nTraining complete!")
        print(f"Best model: {results['summary']['best_model']}")
        print(f"Test R2: {results['summary']['best_test_r2']:.4f}")
