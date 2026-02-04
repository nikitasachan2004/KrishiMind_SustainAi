"""
Model Evaluation Module
=======================
Evaluates trained models and generates comprehensive metrics reports.
Outputs JSON-formatted reports for model performance tracking.

Author: AgroPro ML Team
"""

import json
import logging
import pickle
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# ============================================================================
# CONSTANTS
# ============================================================================
MODELS_DIR = Path(__file__).parent.parent / "models"
ARTIFACTS_DIR = Path(__file__).parent.parent / "artifacts"
REPORTS_DIR = Path(__file__).parent.parent / "reports"


def load_model_artifacts() -> Dict[str, Any]:
    """
    Load all model artifacts for evaluation.
    
    Returns:
        Dictionary with model data and artifacts
    """
    artifacts = {}
    
    # Load yield model
    yield_model_path = MODELS_DIR / "yield_model.pkl"
    if yield_model_path.exists():
        with open(yield_model_path, "rb") as f:
            artifacts["yield_model"] = pickle.load(f)
        logger.info("Loaded yield model")
    
    # Load yield features
    yield_features_path = ARTIFACTS_DIR / "yield_features.json"
    if yield_features_path.exists():
        with open(yield_features_path, "r") as f:
            artifacts["yield_features"] = json.load(f)
    
    # Load price model
    price_model_path = MODELS_DIR / "price_model.pkl"
    if price_model_path.exists():
        with open(price_model_path, "rb") as f:
            artifacts["price_model"] = pickle.load(f)
        logger.info("Loaded price model")
    
    # Load price features
    price_features_path = ARTIFACTS_DIR / "price_features.json"
    if price_features_path.exists():
        with open(price_features_path, "r") as f:
            artifacts["price_features"] = json.load(f)
    
    return artifacts


def get_feature_importance(
    model: Any,
    feature_names: List[str],
) -> Dict[str, float]:
    """
    Extract feature importance from a model.
    
    Args:
        model: Trained model with feature_importances_ attribute
        feature_names: List of feature names
        
    Returns:
        Dictionary mapping feature names to importance values
    """
    if not hasattr(model, "feature_importances_"):
        return {}
    
    importances = model.feature_importances_
    
    if len(importances) != len(feature_names):
        logger.warning(f"Feature count mismatch: {len(importances)} vs {len(feature_names)}")
        return {}
    
    # Sort by importance
    importance_dict = dict(zip(feature_names, importances))
    sorted_importance = dict(
        sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
    )
    
    return sorted_importance


def evaluate_yield_model(artifacts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluate yield model performance.
    
    Args:
        artifacts: Dictionary containing model and features
        
    Returns:
        Evaluation metrics dictionary
    """
    if "yield_model" not in artifacts:
        return {"error": "Yield model not found"}
    
    model = artifacts["yield_model"]
    features_info = artifacts.get("yield_features", {})
    
    # Get feature importance
    feature_names = features_info.get("feature_names", [])
    importance = get_feature_importance(model, feature_names)
    
    # Model metadata
    model_type = type(model).__name__
    
    evaluation = {
        "model_type": model_type,
        "status": "trained",
        "feature_names": feature_names,
        "n_features": len(feature_names),
        "feature_importance": {k: round(v, 4) for k, v in importance.items()},
    }
    
    # Add metrics from features info if available
    if "test_r2" in features_info:
        evaluation["test_r2"] = features_info["test_r2"]
    
    # Get model parameters if available
    if hasattr(model, "get_params"):
        params = model.get_params()
        # Only keep key parameters
        key_params = ["n_estimators", "max_depth", "learning_rate", "random_state"]
        evaluation["parameters"] = {
            k: v for k, v in params.items() 
            if k in key_params and v is not None
        }
    
    return evaluation


def evaluate_price_model(artifacts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluate price model performance.
    
    Args:
        artifacts: Dictionary containing model and features
        
    Returns:
        Evaluation metrics dictionary
    """
    if "price_model" not in artifacts:
        return {"error": "Price model not found"}
    
    price_data = artifacts["price_model"]
    features_info = artifacts.get("price_features", {})
    
    # Extract model from container
    if isinstance(price_data, dict):
        model = price_data.get("model")
        feature_names = price_data.get("feature_names", [])
    else:
        model = price_data
        feature_names = features_info.get("feature_names", [])
    
    if model is None:
        return {"error": "Could not extract price model"}
    
    # Get feature importance
    importance = get_feature_importance(model, feature_names)
    
    # Model metadata
    model_type = type(model).__name__
    
    evaluation = {
        "model_type": model_type,
        "status": "trained",
        "feature_names": feature_names,
        "n_features": len(feature_names),
        "feature_importance": {k: round(v, 4) for k, v in importance.items()},
    }
    
    # Add metrics from features info if available
    metrics = features_info.get("metrics", {})
    if metrics:
        if "test_metrics" in metrics:
            evaluation["test_metrics"] = metrics["test_metrics"]
        if "cv_r2_mean" in metrics:
            evaluation["cv_r2_mean"] = metrics["cv_r2_mean"]
            evaluation["cv_r2_std"] = metrics.get("cv_r2_std", 0)
    
    # Get model parameters
    if hasattr(model, "get_params"):
        params = model.get_params()
        key_params = ["n_estimators", "max_depth", "learning_rate", "random_state"]
        evaluation["parameters"] = {
            k: v for k, v in params.items() 
            if k in key_params and v is not None
        }
    
    return evaluation


def generate_model_metrics_report(
    yield_metrics: Optional[Dict[str, Any]] = None,
    price_metrics: Optional[Dict[str, Any]] = None,
    additional_info: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Generate comprehensive model metrics report.
    
    Args:
        yield_metrics: Yield model evaluation results
        price_metrics: Price model evaluation results
        additional_info: Any additional information to include
        
    Returns:
        Complete metrics report dictionary
    """
    report = {
        "report_metadata": {
            "generated_at": datetime.now().isoformat(),
            "report_type": "model_metrics",
            "version": "1.0",
        },
        "yield_model": yield_metrics or {"status": "not_evaluated"},
        "price_model": price_metrics or {"status": "not_evaluated"},
    }
    
    if additional_info:
        report["additional_info"] = additional_info
    
    # Calculate summary statistics
    summary = {
        "models_evaluated": 0,
        "models_successful": 0,
    }
    
    for model_key in ["yield_model", "price_model"]:
        model_data = report.get(model_key, {})
        if model_data.get("status") != "not_evaluated":
            summary["models_evaluated"] += 1
            if "error" not in model_data:
                summary["models_successful"] += 1
    
    report["summary"] = summary
    
    return report


def save_metrics_report(report: Dict[str, Any], filename: str = "model_metrics.json") -> Path:
    """
    Save metrics report to JSON file.
    
    Args:
        report: Report dictionary
        filename: Output filename
        
    Returns:
        Path to saved report
    """
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    
    output_path = REPORTS_DIR / filename
    
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2, default=str)
    
    logger.info(f"Saved metrics report to {output_path}")
    return output_path


def evaluate_models() -> Dict[str, Any]:
    """
    Main function to evaluate all models and generate report.
    
    Returns:
        Complete evaluation report
    """
    logger.info("=" * 60)
    logger.info("MODEL EVALUATION")
    logger.info("=" * 60)
    
    # Load artifacts
    artifacts = load_model_artifacts()
    
    # Evaluate models
    yield_metrics = evaluate_yield_model(artifacts)
    price_metrics = evaluate_price_model(artifacts)
    
    # Generate report
    report = generate_model_metrics_report(
        yield_metrics=yield_metrics,
        price_metrics=price_metrics,
        additional_info={
            "artifacts_loaded": list(artifacts.keys()),
        }
    )
    
    # Save report
    output_path = save_metrics_report(report)
    
    # Log summary
    logger.info("\nEvaluation Summary:")
    logger.info(f"  Yield Model: {yield_metrics.get('model_type', 'N/A')}")
    if "test_r2" in yield_metrics:
        logger.info(f"    Test R2: {yield_metrics['test_r2']:.4f}")
    
    logger.info(f"  Price Model: {price_metrics.get('model_type', 'N/A')}")
    if "test_metrics" in price_metrics:
        logger.info(f"    Test R2: {price_metrics['test_metrics'].get('R2', 'N/A')}")
    
    logger.info(f"\nReport saved to: {output_path}")
    
    return report


def print_model_summary(report: Dict[str, Any]) -> None:
    """
    Print a human-readable summary of the model report.
    
    Args:
        report: Model metrics report
    """
    print("\n" + "=" * 60)
    print("MODEL EVALUATION SUMMARY")
    print("=" * 60)
    
    # Yield model
    yield_info = report.get("yield_model", {})
    print(f"\n📊 YIELD MODEL")
    print(f"   Type: {yield_info.get('model_type', 'N/A')}")
    print(f"   Features: {yield_info.get('n_features', 'N/A')}")
    
    if "test_r2" in yield_info:
        print(f"   Test R²: {yield_info['test_r2']:.4f}")
    
    if "feature_importance" in yield_info and yield_info["feature_importance"]:
        print("   Top Features:")
        for i, (feat, imp) in enumerate(list(yield_info["feature_importance"].items())[:5], 1):
            print(f"      {i}. {feat}: {imp:.4f}")
    
    # Price model
    price_info = report.get("price_model", {})
    print(f"\n💰 PRICE MODEL")
    print(f"   Type: {price_info.get('model_type', 'N/A')}")
    print(f"   Features: {price_info.get('n_features', 'N/A')}")
    
    if "test_metrics" in price_info:
        metrics = price_info["test_metrics"]
        print(f"   Test R²: {metrics.get('R2', 'N/A'):.4f}")
        print(f"   Test RMSE: {metrics.get('RMSE', 'N/A'):.2f}")
    
    if "feature_importance" in price_info and price_info["feature_importance"]:
        print("   Feature Importance:")
        for feat, imp in price_info["feature_importance"].items():
            print(f"      - {feat}: {imp:.4f}")
    
    # Summary
    summary = report.get("summary", {})
    print(f"\n📋 SUMMARY")
    print(f"   Models Evaluated: {summary.get('models_evaluated', 0)}")
    print(f"   Successful: {summary.get('models_successful', 0)}")
    print(f"   Report Generated: {report.get('report_metadata', {}).get('generated_at', 'N/A')}")
    print("=" * 60)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    report = evaluate_models()
    print_model_summary(report)
