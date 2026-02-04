"""
Data Loader Module
==================
Handles loading and validation of all input datasets for the AgroPro pipeline.
All input files are READ ONLY - never modified.

Author: AgroPro ML Team
"""

import pandas as pd
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONSTANTS - Approved Input Data Paths (READ ONLY)
# ============================================================================
BASE_DATA_DIR = Path(__file__).parent.parent / "data"

DATA_PATHS = {
    "master_training": BASE_DATA_DIR / "output" / "master_training_table.csv",
    "rainfall_features": BASE_DATA_DIR / "cleaned_data" / "rainfall_features.csv",
    "temperature_features": BASE_DATA_DIR / "cleaned_data" / "temperature_features.csv",
    "soil_cleaned": BASE_DATA_DIR / "cleaned_data" / "soil_cleaned.csv",
    "commodity_price": BASE_DATA_DIR / "commodity_price.csv",
    "crop_calendar": BASE_DATA_DIR / "crop_calendar.csv",
}

# Required columns for yield model
YIELD_FEATURES = [
    "rainfall_mean",
    "rainfall_anomaly", 
    "monsoon_rainfall",
    "avg_temp_mean",
    "heatwave_count",
    "growing_degree_days",
    "soil_quality_index",
    "season",
    "crop_name",
    "district_name",
]

YIELD_TARGET = "yield_per_hectare"


def load_csv_safe(filepath: Path, description: str = "") -> Optional[pd.DataFrame]:
    """
    Safely load a CSV file with error handling.
    
    Args:
        filepath: Path to the CSV file
        description: Human-readable description for logging
        
    Returns:
        DataFrame if successful, None if file doesn't exist or fails to load
    """
    try:
        if not filepath.exists():
            logger.warning(f"File not found: {filepath} ({description})")
            return None
        
        df = pd.read_csv(filepath)
        logger.info(f"Loaded {description}: {len(df):,} rows, {len(df.columns)} columns")
        return df
        
    except Exception as e:
        logger.error(f"Failed to load {filepath}: {e}")
        return None


def load_master_training_table() -> Optional[pd.DataFrame]:
    """
    Load the master training table with yield data.
    
    Returns:
        DataFrame with crop yield and feature data
    """
    df = load_csv_safe(
        DATA_PATHS["master_training"],
        "Master Training Table"
    )
    
    if df is not None:
        # Log available columns for debugging
        logger.info(f"Available columns: {list(df.columns)}")
        
        # Check for required target column
        if YIELD_TARGET not in df.columns:
            logger.error(f"Missing target column: {YIELD_TARGET}")
            return None
            
    return df


def load_rainfall_features() -> Optional[pd.DataFrame]:
    """Load rainfall feature data."""
    return load_csv_safe(
        DATA_PATHS["rainfall_features"],
        "Rainfall Features"
    )


def load_temperature_features() -> Optional[pd.DataFrame]:
    """Load temperature feature data."""
    return load_csv_safe(
        DATA_PATHS["temperature_features"],
        "Temperature Features"
    )


def load_soil_data() -> Optional[pd.DataFrame]:
    """Load soil quality data."""
    return load_csv_safe(
        DATA_PATHS["soil_cleaned"],
        "Soil Data"
    )


def load_commodity_prices() -> Optional[pd.DataFrame]:
    """
    Load commodity price data and clean column names.
    
    Returns:
        DataFrame with cleaned column names (removes _x0020_ artifacts)
    """
    df = load_csv_safe(
        DATA_PATHS["commodity_price"],
        "Commodity Prices"
    )
    
    if df is not None:
        # Clean column names - remove _x0020_ artifacts
        df.columns = [col.replace("_x0020_", "_").replace("__", "_").strip("_") 
                      for col in df.columns]
        logger.info(f"Cleaned price columns: {list(df.columns)}")
        
    return df


def load_crop_calendar() -> Optional[pd.DataFrame]:
    """Load crop calendar data."""
    return load_csv_safe(
        DATA_PATHS["crop_calendar"],
        "Crop Calendar"
    )


def load_all_data() -> Dict[str, Optional[pd.DataFrame]]:
    """
    Load all available datasets.
    
    Returns:
        Dictionary mapping dataset names to DataFrames (or None if unavailable)
    """
    logger.info("=" * 60)
    logger.info("Loading all datasets...")
    logger.info("=" * 60)
    
    data = {
        "master_training": load_master_training_table(),
        "rainfall_features": load_rainfall_features(),
        "temperature_features": load_temperature_features(),
        "soil_cleaned": load_soil_data(),
        "commodity_price": load_commodity_prices(),
        "crop_calendar": load_crop_calendar(),
    }
    
    # Summary
    available = sum(1 for v in data.values() if v is not None)
    logger.info(f"Loaded {available}/{len(data)} datasets successfully")
    
    return data


def validate_yield_data(df: pd.DataFrame) -> Tuple[bool, list]:
    """
    Validate that yield model data has required columns.
    
    Args:
        df: DataFrame to validate
        
    Returns:
        Tuple of (is_valid, missing_columns)
    """
    required = YIELD_FEATURES + [YIELD_TARGET]
    missing = [col for col in required if col not in df.columns]
    
    if missing:
        logger.warning(f"Missing columns for yield model: {missing}")
        return False, missing
    
    logger.info("Yield data validation passed")
    return True, []


def get_yield_model_data(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """
    Extract and validate data for yield model training.
    
    Args:
        df: Master training table
        
    Returns:
        DataFrame with only yield model columns, or None if validation fails
    """
    is_valid, missing = validate_yield_data(df)
    
    if not is_valid:
        # Try to work with available columns
        available_features = [f for f in YIELD_FEATURES if f in df.columns]
        if YIELD_TARGET not in df.columns:
            logger.error(f"Cannot proceed without target: {YIELD_TARGET}")
            return None
            
        logger.warning(f"Using {len(available_features)}/{len(YIELD_FEATURES)} available features")
        return df[available_features + [YIELD_TARGET]].copy()
    
    return df[YIELD_FEATURES + [YIELD_TARGET]].copy()


if __name__ == "__main__":
    # Test data loading
    logger.info("Testing data loader...")
    data = load_all_data()
    
    for name, df in data.items():
        if df is not None:
            print(f"\n{name}:")
            print(f"  Shape: {df.shape}")
            print(f"  Columns: {list(df.columns)[:10]}...")
