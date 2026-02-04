"""
Price Model Training Module
===========================
Trains a price prediction model from commodity price data.
Predicts modal price based on crop, district, and temporal features.

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
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

logger = logging.getLogger(__name__)

# ============================================================================
# CONSTANTS
# ============================================================================
MODELS_DIR = Path(__file__).parent.parent / "models"
ARTIFACTS_DIR = Path(__file__).parent.parent / "artifacts"
RANDOM_STATE = 42

# Price model configuration
PRICE_MODEL_CONFIG = {
    "n_estimators": 100,
    "max_depth": 12,
    "min_samples_split": 5,
    "min_samples_leaf": 2,
    "random_state": RANDOM_STATE,
    "n_jobs": -1,
}


class PriceModelTrainer:
    """
    Trains and manages the commodity price prediction model.
    """
    
    def __init__(self, random_state: int = RANDOM_STATE):
        """
        Initialize price model trainer.
        
        Args:
            random_state: Seed for reproducibility
        """
        self.random_state = random_state
        self.model = None
        self.label_encoders: Dict[str, LabelEncoder] = {}
        self.feature_names: List[str] = []
        self.metrics: Dict[str, Any] = {}
        
        logger.info(f"PriceModelTrainer initialized with random_state={random_state}")
    
    def clean_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean column names by removing _x0020_ and other artifacts.
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with cleaned column names
        """
        df = df.copy()
        df.columns = [
            col.replace("_x0020_", "_")
               .replace("__", "_")
               .strip("_")
               .lower()
            for col in df.columns
        ]
        logger.info(f"Cleaned columns: {list(df.columns)}")
        return df
    
    def prepare_price_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare commodity price data for model training.
        
        Args:
            df: Raw commodity price DataFrame
            
        Returns:
            Processed DataFrame with features and target
        """
        df = self.clean_column_names(df)
        
        # Find and parse date column
        date_col = None
        for col in ["arrival_date", "date", "arrival_dt"]:
            if col in df.columns:
                date_col = col
                break
        
        if date_col:
            df["date_parsed"] = pd.to_datetime(df[date_col], errors="coerce")
            df["month"] = df["date_parsed"].dt.month
            df["year"] = df["date_parsed"].dt.year
            logger.info(f"Parsed date column: {date_col}")
        else:
            # Default month if no date
            df["month"] = 6
            logger.warning("No date column found, using default month=6")
        
        # Find price column (target)
        price_col = None
        for col in ["modal_price", "price", "modal", "avg_price"]:
            if col in df.columns:
                price_col = col
                break
        
        if price_col is None:
            logger.error(f"No price column found in: {list(df.columns)}")
            raise ValueError("Cannot find price target column")
        
        df["modal_price"] = pd.to_numeric(df[price_col], errors="coerce")
        
        # Find crop column
        crop_col = None
        for col in ["commodity", "crop", "crop_name", "variety"]:
            if col in df.columns:
                crop_col = col
                break
        
        if crop_col:
            df["crop"] = df[crop_col].astype(str)
        else:
            df["crop"] = "UNKNOWN"
            logger.warning("No crop column found")
        
        # Find district column
        district_col = None
        for col in ["district", "district_name", "market"]:
            if col in df.columns:
                district_col = col
                break
        
        if district_col:
            df["district"] = df[district_col].astype(str)
        else:
            df["district"] = "UNKNOWN"
            logger.warning("No district column found")
        
        # Aggregate: avg modal price by crop × district × month
        agg_df = df.groupby(["crop", "district", "month"]).agg(
            modal_price=("modal_price", "mean")
        ).reset_index()
        
        logger.info(f"Aggregated to {len(agg_df):,} crop-district-month combinations")
        
        return agg_df
    
    def encode_features(self, df: pd.DataFrame, fit: bool = True) -> pd.DataFrame:
        """
        Encode categorical features for model training.
        
        Args:
            df: DataFrame with crop and district columns
            fit: If True, fit new encoders
            
        Returns:
            DataFrame with encoded features
        """
        df = df.copy()
        
        categorical_cols = ["crop", "district"]
        
        for col in categorical_cols:
            if col not in df.columns:
                continue
                
            if fit:
                encoder = LabelEncoder()
                df[f"{col}_encoded"] = encoder.fit_transform(df[col].astype(str))
                self.label_encoders[col] = encoder
                logger.info(f"Encoded {col}: {len(encoder.classes_)} unique values")
            else:
                if col not in self.label_encoders:
                    raise ValueError(f"No encoder for {col}")
                encoder = self.label_encoders[col]
                
                # Handle unseen categories
                known = set(encoder.classes_)
                df[col] = df[col].astype(str).apply(
                    lambda x: x if x in known else encoder.classes_[0]
                )
                df[f"{col}_encoded"] = encoder.transform(df[col])
        
        return df
    
    def train(
        self, 
        df: pd.DataFrame,
        test_size: float = 0.2,
        cv_folds: int = 5
    ) -> Dict[str, Any]:
        """
        Train the price prediction model.
        
        Args:
            df: Prepared and encoded DataFrame
            test_size: Fraction for test split
            cv_folds: Number of cross-validation folds
            
        Returns:
            Dictionary of training results and metrics
        """
        logger.info("=" * 60)
        logger.info("PRICE MODEL TRAINING")
        logger.info("=" * 60)
        
        # Prepare features
        self.feature_names = ["crop_encoded", "district_encoded", "month"]
        
        # Ensure required columns exist
        missing = [f for f in self.feature_names if f not in df.columns]
        if missing:
            raise ValueError(f"Missing feature columns: {missing}")
        
        if "modal_price" not in df.columns:
            raise ValueError("Missing target column: modal_price")
        
        # Extract X, y
        X = df[self.feature_names].values
        y = df["modal_price"].values
        
        # Filter valid samples
        valid_mask = np.isfinite(y) & (y > 0)
        X = X[valid_mask]
        y = y[valid_mask]
        
        logger.info(f"Data shape: X={X.shape}, y={y.shape}")
        
        if len(y) < 50:
            raise ValueError("Insufficient valid samples for price model training")
        
        # Train/test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=self.random_state
        )
        
        logger.info(f"Train: {len(y_train):,}, Test: {len(y_test):,}")
        
        # Initialize and train model
        self.model = RandomForestRegressor(**PRICE_MODEL_CONFIG)
        
        # Cross-validation
        logger.info(f"Running {cv_folds}-fold cross-validation...")
        cv_scores = cross_val_score(self.model, X_train, y_train, cv=cv_folds, scoring="r2")
        cv_r2_mean = float(cv_scores.mean())
        cv_r2_std = float(cv_scores.std())
        
        logger.info(f"CV R2: {cv_r2_mean:.4f} (+/- {cv_r2_std:.4f})")
        
        # Train on full training set
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred_train = self.model.predict(X_train)
        y_pred_test = self.model.predict(X_test)
        
        train_metrics = {
            "R2": float(r2_score(y_train, y_pred_train)),
            "RMSE": float(np.sqrt(mean_squared_error(y_train, y_pred_train))),
            "MAE": float(mean_absolute_error(y_train, y_pred_train)),
        }
        
        test_metrics = {
            "R2": float(r2_score(y_test, y_pred_test)),
            "RMSE": float(np.sqrt(mean_squared_error(y_test, y_pred_test))),
            "MAE": float(mean_absolute_error(y_test, y_pred_test)),
        }
        
        logger.info(f"Train - R2: {train_metrics['R2']:.4f}, RMSE: {train_metrics['RMSE']:.2f}")
        logger.info(f"Test  - R2: {test_metrics['R2']:.4f}, RMSE: {test_metrics['RMSE']:.2f}")
        
        # Store metrics
        self.metrics = {
            "model_name": "RandomForest",
            "cv_r2_mean": cv_r2_mean,
            "cv_r2_std": cv_r2_std,
            "train_metrics": train_metrics,
            "test_metrics": test_metrics,
            "feature_names": self.feature_names,
            "feature_importance": self.model.feature_importances_.tolist(),
            "n_samples": len(y),
            "n_train": len(y_train),
            "n_test": len(y_test),
        }
        
        return self.metrics
    
    def predict(
        self, 
        crop: str, 
        district: str, 
        month: int
    ) -> float:
        """
        Predict price for a crop-district-month combination.
        
        Args:
            crop: Crop name
            district: District name
            month: Month (1-12)
            
        Returns:
            Predicted modal price
        """
        if self.model is None:
            raise ValueError("Model not trained")
        
        # Encode inputs
        crop_encoded = 0
        district_encoded = 0
        
        if "crop" in self.label_encoders:
            enc = self.label_encoders["crop"]
            if crop in enc.classes_:
                crop_encoded = enc.transform([crop])[0]
            else:
                logger.warning(f"Unknown crop: {crop}, using default encoding")
        
        if "district" in self.label_encoders:
            enc = self.label_encoders["district"]
            if district in enc.classes_:
                district_encoded = enc.transform([district])[0]
            else:
                logger.warning(f"Unknown district: {district}, using default encoding")
        
        X = np.array([[crop_encoded, district_encoded, month]])
        return float(self.model.predict(X)[0])
    
    def save(self) -> None:
        """Save trained model and artifacts."""
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
        
        # Save model
        model_path = MODELS_DIR / "price_model.pkl"
        with open(model_path, "wb") as f:
            pickle.dump({
                "model": self.model,
                "label_encoders": self.label_encoders,
                "feature_names": self.feature_names,
            }, f)
        logger.info(f"Saved price model to {model_path}")
        
        # Save artifacts
        artifacts_path = ARTIFACTS_DIR / "price_features.json"
        artifacts = {
            "feature_names": self.feature_names,
            "metrics": self.metrics,
            "label_encodings": {
                col: list(enc.classes_)
                for col, enc in self.label_encoders.items()
            }
        }
        
        with open(artifacts_path, "w") as f:
            json.dump(artifacts, f, indent=2, default=str)
        logger.info(f"Saved price artifacts to {artifacts_path}")
    
    def load(self) -> None:
        """Load trained model and artifacts."""
        model_path = MODELS_DIR / "price_model.pkl"
        
        if not model_path.exists():
            raise FileNotFoundError(f"Price model not found: {model_path}")
        
        with open(model_path, "rb") as f:
            data = pickle.load(f)
        
        self.model = data["model"]
        self.label_encoders = data["label_encoders"]
        self.feature_names = data["feature_names"]
        
        logger.info("Loaded price model")


def train_price_model(price_df: pd.DataFrame) -> Tuple[PriceModelTrainer, Dict[str, Any]]:
    """
    Convenience function to train price model.
    
    Args:
        price_df: Raw commodity price DataFrame
        
    Returns:
        Tuple of (trainer instance, metrics)
    """
    trainer = PriceModelTrainer()
    
    # Prepare data
    prepared_df = trainer.prepare_price_data(price_df)
    
    # Encode features
    encoded_df = trainer.encode_features(prepared_df, fit=True)
    
    # Train
    metrics = trainer.train(encoded_df)
    
    # Save
    trainer.save()
    
    return trainer, metrics


def create_synthetic_price_data() -> pd.DataFrame:
    """
    Create synthetic price data for demo when real data is unavailable.
    
    Returns:
        DataFrame with synthetic price data
    """
    logger.warning("Creating synthetic price data for demo purposes")
    
    np.random.seed(RANDOM_STATE)
    
    crops = ["Rice", "Wheat", "Cotton", "Sugarcane", "Groundnut", "Maize", "Soybean"]
    districts = ["Guntur", "Krishna", "Nizamabad", "Warangal", "Karimnagar"]
    months = list(range(1, 13))
    
    records = []
    for crop in crops:
        base_price = np.random.uniform(1500, 4000)
        for district in districts:
            district_factor = np.random.uniform(0.9, 1.1)
            for month in months:
                # Seasonal variation
                seasonal = 1.0 + 0.1 * np.sin(2 * np.pi * month / 12)
                price = base_price * district_factor * seasonal * np.random.uniform(0.95, 1.05)
                
                records.append({
                    "commodity": crop,
                    "district": district,
                    "arrival_date": f"2024-{month:02d}-15",
                    "modal_price": price,
                })
    
    df = pd.DataFrame(records)
    logger.info(f"Created synthetic price data: {len(df)} records")
    return df


if __name__ == "__main__":
    # Test price model training
    logging.basicConfig(level=logging.INFO)
    
    from data_loader import load_commodity_prices
    
    price_df = load_commodity_prices()
    
    if price_df is None:
        logger.warning("No real price data, using synthetic data")
        price_df = create_synthetic_price_data()
    
    trainer, metrics = train_price_model(price_df)
    
    print("\nPrice model training complete!")
    print(f"Test R2: {metrics['test_metrics']['R2']:.4f}")
    print(f"Test RMSE: {metrics['test_metrics']['RMSE']:.2f}")
    
    # Test prediction
    test_price = trainer.predict("Rice", "Guntur", 6)
    print(f"\nSample prediction (Rice, Guntur, June): {test_price:.2f}")
