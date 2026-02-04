"""
Feature Builder Module
======================
Handles feature engineering, preprocessing, and encoding for model training.
Ensures reproducibility with deterministic transformations.

Author: AgroPro ML Team
"""

import pandas as pd
import numpy as np
import logging
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from sklearn.preprocessing import LabelEncoder

logger = logging.getLogger(__name__)

# ============================================================================
# CONSTANTS
# ============================================================================
CATEGORICAL_COLUMNS = ["season", "crop_name", "district_name"]
NUMERIC_COLUMNS = [
    "rainfall_mean",
    "rainfall_anomaly",
    "monsoon_rainfall", 
    "avg_temp_mean",
    "heatwave_count",
    "growing_degree_days",
    "soil_quality_index",
]

ARTIFACTS_DIR = Path(__file__).parent.parent / "artifacts"


class FeatureBuilder:
    """
    Feature engineering and preprocessing for crop yield modeling.
    Maintains encoders for consistent transformation across train/inference.
    """
    
    def __init__(self, random_state: int = 42):
        """
        Initialize feature builder.
        
        Args:
            random_state: Seed for reproducibility
        """
        self.random_state = random_state
        self.label_encoders: Dict[str, LabelEncoder] = {}
        self.feature_stats: Dict[str, Dict] = {}
        self.fitted = False
        
        logger.info(f"FeatureBuilder initialized with random_state={random_state}")
    
    def handle_missing_values(
        self, 
        df: pd.DataFrame,
        numeric_strategy: str = "median",
        categorical_strategy: str = "mode"
    ) -> pd.DataFrame:
        """
        Handle missing values in the dataset.
        
        Args:
            df: Input DataFrame
            numeric_strategy: 'mean', 'median', or 'zero' for numeric columns
            categorical_strategy: 'mode' or 'unknown' for categorical columns
            
        Returns:
            DataFrame with imputed values
        """
        df = df.copy()
        
        # Handle numeric columns
        numeric_cols = [c for c in NUMERIC_COLUMNS if c in df.columns]
        for col in numeric_cols:
            if df[col].isna().any():
                missing_count = df[col].isna().sum()
                
                if numeric_strategy == "median":
                    fill_value = df[col].median()
                elif numeric_strategy == "mean":
                    fill_value = df[col].mean()
                else:
                    fill_value = 0
                    
                df[col] = df[col].fillna(fill_value)
                
                # Store for inference
                self.feature_stats[col] = {
                    "fill_value": fill_value,
                    "missing_count": int(missing_count)
                }
                
                logger.info(f"Imputed {col}: {missing_count} missing → {fill_value:.4f}")
        
        # Handle categorical columns
        cat_cols = [c for c in CATEGORICAL_COLUMNS if c in df.columns]
        for col in cat_cols:
            if df[col].isna().any():
                missing_count = df[col].isna().sum()
                
                if categorical_strategy == "mode":
                    fill_value = df[col].mode().iloc[0] if len(df[col].mode()) > 0 else "UNKNOWN"
                else:
                    fill_value = "UNKNOWN"
                    
                df[col] = df[col].fillna(fill_value)
                logger.info(f"Imputed {col}: {missing_count} missing → '{fill_value}'")
        
        return df
    
    def encode_categoricals(
        self, 
        df: pd.DataFrame,
        fit: bool = True
    ) -> pd.DataFrame:
        """
        Label encode categorical columns.
        
        Args:
            df: Input DataFrame
            fit: If True, fit new encoders. If False, use existing encoders.
            
        Returns:
            DataFrame with encoded categorical columns
        """
        df = df.copy()
        
        cat_cols = [c for c in CATEGORICAL_COLUMNS if c in df.columns]
        
        for col in cat_cols:
            if fit:
                # Fit new encoder
                encoder = LabelEncoder()
                df[f"{col}_encoded"] = encoder.fit_transform(df[col].astype(str))
                self.label_encoders[col] = encoder
                
                # Log encoding mapping
                classes = list(encoder.classes_)
                logger.info(f"Encoded {col}: {len(classes)} unique values")
                
            else:
                # Use existing encoder
                if col not in self.label_encoders:
                    raise ValueError(f"No encoder fitted for column: {col}")
                    
                encoder = self.label_encoders[col]
                
                # Handle unseen categories
                known_classes = set(encoder.classes_)
                df[col] = df[col].astype(str).apply(
                    lambda x: x if x in known_classes else encoder.classes_[0]
                )
                df[f"{col}_encoded"] = encoder.transform(df[col])
        
        return df
    
    def build_features(
        self, 
        df: pd.DataFrame,
        fit: bool = True
    ) -> Tuple[pd.DataFrame, List[str]]:
        """
        Full feature engineering pipeline.
        
        Args:
            df: Raw input DataFrame
            fit: If True, fit transformers. If False, use existing.
            
        Returns:
            Tuple of (transformed DataFrame, list of feature names)
        """
        logger.info("=" * 60)
        logger.info("Building features...")
        logger.info("=" * 60)
        
        # Step 1: Handle missing values
        df = self.handle_missing_values(df)
        
        # Step 2: Encode categoricals
        df = self.encode_categoricals(df, fit=fit)
        
        # Step 3: Build feature list
        feature_cols = []
        
        # Add numeric features
        for col in NUMERIC_COLUMNS:
            if col in df.columns:
                feature_cols.append(col)
        
        # Add encoded categorical features
        for col in CATEGORICAL_COLUMNS:
            encoded_col = f"{col}_encoded"
            if encoded_col in df.columns:
                feature_cols.append(encoded_col)
        
        if fit:
            self.fitted = True
            self.feature_columns = feature_cols
            
        logger.info(f"Built {len(feature_cols)} features: {feature_cols}")
        
        return df, feature_cols
    
    def get_feature_matrix(
        self, 
        df: pd.DataFrame,
        target_col: str = "yield_per_hectare"
    ) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """
        Get X, y arrays ready for model training.
        
        Args:
            df: Processed DataFrame
            target_col: Name of target column
            
        Returns:
            Tuple of (X features array, y target array, feature names)
        """
        if not self.fitted:
            df, feature_cols = self.build_features(df, fit=True)
        else:
            feature_cols = self.feature_columns
            
        X = df[feature_cols].values
        y = df[target_col].values if target_col in df.columns else None
        
        logger.info(f"Feature matrix shape: {X.shape}")
        if y is not None:
            logger.info(f"Target shape: {y.shape}")
        
        return X, y, feature_cols
    
    def save_artifacts(self, output_dir: Optional[Path] = None) -> None:
        """
        Save feature engineering artifacts for reproducibility.
        
        Args:
            output_dir: Directory to save artifacts (default: artifacts/)
        """
        output_dir = output_dir or ARTIFACTS_DIR
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save feature list
        features_path = output_dir / "yield_features.json"
        artifacts = {
            "feature_columns": self.feature_columns if hasattr(self, 'feature_columns') else [],
            "categorical_columns": CATEGORICAL_COLUMNS,
            "numeric_columns": NUMERIC_COLUMNS,
            "feature_stats": self.feature_stats,
            "label_encodings": {
                col: list(enc.classes_) 
                for col, enc in self.label_encoders.items()
            }
        }
        
        with open(features_path, 'w') as f:
            json.dump(artifacts, f, indent=2, default=str)
            
        logger.info(f"Saved feature artifacts to {features_path}")
    
    def load_artifacts(self, input_dir: Optional[Path] = None) -> None:
        """
        Load feature engineering artifacts.
        
        Args:
            input_dir: Directory to load artifacts from
        """
        input_dir = input_dir or ARTIFACTS_DIR
        features_path = input_dir / "yield_features.json"
        
        if not features_path.exists():
            raise FileNotFoundError(f"Artifacts not found: {features_path}")
        
        with open(features_path, 'r') as f:
            artifacts = json.load(f)
        
        self.feature_columns = artifacts.get("feature_columns", [])
        self.feature_stats = artifacts.get("feature_stats", {})
        
        # Reconstruct label encoders
        for col, classes in artifacts.get("label_encodings", {}).items():
            encoder = LabelEncoder()
            encoder.classes_ = np.array(classes)
            self.label_encoders[col] = encoder
        
        self.fitted = True
        logger.info(f"Loaded artifacts with {len(self.feature_columns)} features")


def create_price_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create features for price prediction model.
    
    Args:
        df: Commodity price DataFrame
        
    Returns:
        DataFrame with price features
    """
    df = df.copy()
    
    # Parse arrival date if available
    date_col = None
    for col in ["Arrival_Date", "arrival_date", "date"]:
        if col in df.columns:
            date_col = col
            break
    
    if date_col:
        df["date_parsed"] = pd.to_datetime(df[date_col], errors="coerce")
        df["month"] = df["date_parsed"].dt.month
        df["year"] = df["date_parsed"].dt.year
        logger.info(f"Parsed date column: {date_col}")
    
    return df


if __name__ == "__main__":
    # Test feature builder
    logging.basicConfig(level=logging.INFO)
    
    from data_loader import load_master_training_table
    
    df = load_master_training_table()
    if df is not None:
        builder = FeatureBuilder()
        df_processed, features = builder.build_features(df)
        X, y, feature_names = builder.get_feature_matrix(df_processed)
        
        print(f"\nProcessed data shape: {df_processed.shape}")
        print(f"Features: {feature_names}")
        print(f"X shape: {X.shape}, y shape: {y.shape if y is not None else 'N/A'}")
        
        builder.save_artifacts()
