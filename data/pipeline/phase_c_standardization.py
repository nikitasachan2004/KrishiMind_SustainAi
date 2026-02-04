#!/usr/bin/env python3
"""
Phase C: Schema Standardization
===============================
Standardize all datasets to consistent schema:
- Lowercase column names
- snake_case format
- Standardized district/state names
- ISO date format (YYYY-MM-DD)
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
from tqdm import tqdm

from config import CONFIG
from utils import standardize_columns, normalize_district_name, normalize_state_name

logger = logging.getLogger(__name__)


# =============================================================================
# COLUMN STANDARDIZATION
# =============================================================================

def standardize_column_schema(df: pd.DataFrame, schema_type: str) -> pd.DataFrame:
    """Apply schema-specific standardization."""
    
    # First pass: standardize column names
    df = standardize_columns(df)
    
    # Schema-specific renames
    schema_renames = {
        'rainfall': {
            'precip': 'rainfall',
            'precipitation': 'rainfall',
            'rain': 'rainfall',
            'rf': 'rainfall',
            'latitude': 'lat',
            'longitude': 'lon',
            'long': 'lon',
        },
        'temperature': {
            'max_temp': 'tmax',
            't_max': 'tmax',
            'temperature_max': 'tmax',
            'min_temp': 'tmin',
            't_min': 'tmin',
            'temperature_min': 'tmin',
            'avg_temp': 'tavg',
            'mean_temp': 'tavg',
            'latitude': 'lat',
            'longitude': 'lon',
        },
        'crop_yield': {
            'crop_name': 'crop',
            'district_name': 'district',
            'state_name': 'state',
            'area_ha': 'area',
            'production_tonnes': 'production',
            'yield_kg_ha': 'yield',
            'yield_kg_per_ha': 'yield',
        },
        'soil': {
            'district_name': 'district',
            'state_name': 'state',
            'ph_value': 'ph',
            'organic_carbon': 'oc',
            'nitrogen_kg_ha': 'nitrogen',
            'phosphorus_kg_ha': 'phosphorus',
            'potassium_kg_ha': 'potassium',
        },
        'mandi': {
            'commodity': 'crop',
            'commodity_name': 'crop',
            'modal_price': 'price_modal',
            'min_price': 'price_min',
            'max_price': 'price_max',
            'market': 'mandi',
            'arrival_date': 'date',
        }
    }
    
    if schema_type in schema_renames:
        df = df.rename(columns=schema_renames[schema_type])
    
    return df


def standardize_date_column(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize date columns to ISO format."""
    date_cols = [c for c in df.columns if 'date' in c.lower() or c.lower() in ['year', 'month', 'day']]
    
    for col in date_cols:
        if col in df.columns:
            try:
                if col.lower() == 'year':
                    continue
                df[col] = pd.to_datetime(df[col], errors='coerce')
                df[col] = df[col].dt.strftime('%Y-%m-%d')
            except Exception as e:
                logger.debug(f"Could not parse dates in {col}: {e}")
    
    return df


def standardize_district_names(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize district and state names."""
    
    if 'district' in df.columns:
        df['district'] = df['district'].apply(normalize_district_name)
    
    if 'state' in df.columns:
        df['state'] = df['state'].apply(normalize_state_name)
    
    return df


def standardize_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure numeric columns are proper types."""
    
    # Columns that should be numeric
    numeric_cols = [
        'lat', 'lon', 'rainfall', 'tmax', 'tmin', 'tavg', 'avg_temp',
        'area', 'production', 'yield', 'ph', 'oc', 'nitrogen', 
        'phosphorus', 'potassium', 'price_modal', 'price_min', 'price_max',
        'year'
    ]
    
    for col in df.columns:
        if col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df


# =============================================================================
# DATASET-SPECIFIC STANDARDIZATION
# =============================================================================

def standardize_rainfall() -> Dict:
    """Standardize rainfall data."""
    logger.info("Standardizing rainfall data...")
    
    result = {'files': 0, 'records': 0}
    
    input_dir = CONFIG.DATA_DIR / "rainfall_csv"
    output_dir = CONFIG.CLEANED_DIR / "rainfall_standardized"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if not input_dir.exists():
        # Check base dir
        input_dir = CONFIG.BASE_DIR / "rainfall_csv"
    
    if not input_dir.exists():
        logger.warning("Rainfall CSV directory not found")
        return result
    
    csv_files = list(input_dir.glob('*.csv'))
    
    for filepath in tqdm(csv_files, desc="Standardizing rainfall"):
        try:
            df = pd.read_csv(filepath)
            df = standardize_column_schema(df, 'rainfall')
            df = standardize_date_column(df)
            df = standardize_numeric_columns(df)
            
            # Validate columns
            required = ['date', 'lat', 'lon', 'rainfall']
            missing = [c for c in required if c not in df.columns]
            
            if missing:
                logger.warning(f"Missing columns in {filepath.name}: {missing}")
                continue
            
            # Save standardized file
            output_file = output_dir / f"{filepath.stem}_std.csv"
            df.to_csv(output_file, index=False)
            
            result['files'] += 1
            result['records'] += len(df)
            
        except Exception as e:
            logger.error(f"Failed to standardize {filepath}: {e}")
    
    logger.info(f"Rainfall standardized: {result['files']} files, {result['records']:,} records")
    return result


def standardize_temperature() -> Dict:
    """Standardize temperature data."""
    logger.info("Standardizing temperature data...")
    
    result = {'records': 0}
    
    # Try merged file first
    input_file = CONFIG.DATA_DIR / "temperature_merged.csv"
    if not input_file.exists():
        # Try individual tmax/tmin files
        tmax_files = list((CONFIG.BASE_DIR / "imd_climate_data" / "csv_tmax").glob('*.csv')) if (CONFIG.BASE_DIR / "imd_climate_data" / "csv_tmax").exists() else []
        tmin_files = list((CONFIG.BASE_DIR / "imd_climate_data" / "csv_tmin").glob('*.csv')) if (CONFIG.BASE_DIR / "imd_climate_data" / "csv_tmin").exists() else []
        
        if not tmax_files and not tmin_files:
            logger.warning("No temperature data found")
            return result
        
        # Process individual files
        dfs = []
        for f in tmax_files + tmin_files:
            df = pd.read_csv(f)
            df = standardize_column_schema(df, 'temperature')
            dfs.append(df)
        
        if dfs:
            df = pd.concat(dfs, ignore_index=True)
        else:
            return result
    else:
        df = pd.read_csv(input_file)
    
    df = standardize_column_schema(df, 'temperature')
    df = standardize_date_column(df)
    df = standardize_numeric_columns(df)
    
    # Save
    output_file = CONFIG.CLEANED_DIR / "temperature_standardized.csv"
    df.to_csv(output_file, index=False)
    
    result['records'] = len(df)
    logger.info(f"Temperature standardized: {result['records']:,} records")
    
    return result


def standardize_crop_yield() -> Dict:
    """Standardize crop yield data."""
    logger.info("Standardizing crop yield data...")
    
    result = {'records': 0, 'crops': 0, 'districts': 0}
    
    # Find crop yield file
    possible_files = [
        CONFIG.BASE_DIR / "crop-wise-area-production-yield.csv",
        CONFIG.DATA_DIR / "crop_yield.csv",
        CONFIG.CLEANED_DIR / "crop_yield_cleaned.csv"
    ]
    
    input_file = None
    for f in possible_files:
        if f.exists():
            input_file = f
            break
    
    if input_file is None:
        logger.warning("Crop yield data not found")
        return result
    
    df = pd.read_csv(input_file)
    df = standardize_column_schema(df, 'crop_yield')
    df = standardize_district_names(df)
    df = standardize_numeric_columns(df)
    
    # Standardize crop names
    if 'crop' in df.columns:
        df['crop'] = df['crop'].str.strip().str.title()
        df['crop'] = df['crop'].replace({
            'Arhar/Tur': 'Tur',
            'Moong(Green Gram)': 'Moong',
            'Urad(Black Gram)': 'Urad',
            'Ragi': 'Finger Millet',
            'Sesamum': 'Sesame',
            'Sugarcane(Gur)': 'Sugarcane',
        })
    
    # Save
    output_file = CONFIG.CLEANED_DIR / "crop_yield_standardized.csv"
    df.to_csv(output_file, index=False)
    
    result['records'] = len(df)
    result['crops'] = df['crop'].nunique() if 'crop' in df.columns else 0
    result['districts'] = df['district'].nunique() if 'district' in df.columns else 0
    
    logger.info(f"Crop yield standardized: {result['records']:,} records, {result['crops']} crops, {result['districts']} districts")
    
    return result


def standardize_soil() -> Dict:
    """Standardize soil data."""
    logger.info("Standardizing soil data...")
    
    result = {'records': 0}
    
    possible_files = [
        CONFIG.BASE_DIR / "soil.csv",
        CONFIG.DATA_DIR / "soil.csv",
        CONFIG.CLEANED_DIR / "soil_cleaned.csv"
    ]
    
    input_file = None
    for f in possible_files:
        if f.exists():
            input_file = f
            break
    
    if input_file is None:
        logger.warning("Soil data not found")
        return result
    
    df = pd.read_csv(input_file)
    df = standardize_column_schema(df, 'soil')
    df = standardize_district_names(df)
    df = standardize_numeric_columns(df)
    
    # Save
    output_file = CONFIG.CLEANED_DIR / "soil_standardized.csv"
    df.to_csv(output_file, index=False)
    
    result['records'] = len(df)
    logger.info(f"Soil standardized: {result['records']:,} records")
    
    return result


def standardize_mandi() -> Dict:
    """Standardize mandi/market price data."""
    logger.info("Standardizing mandi data...")
    
    result = {'records': 0}
    
    possible_files = [
        CONFIG.BASE_DIR / "mandi_prices_full.csv",
        CONFIG.DATA_DIR / "mandi_prices.csv",
        CONFIG.CLEANED_DIR / "mandi_cleaned.csv"
    ]
    
    input_file = None
    for f in possible_files:
        if f.exists():
            input_file = f
            break
    
    if input_file is None:
        logger.warning("Mandi data not found")
        return result
    
    df = pd.read_csv(input_file)
    
    if df.empty:
        logger.warning("Mandi data is empty")
        return result
    
    df = standardize_column_schema(df, 'mandi')
    df = standardize_district_names(df)
    df = standardize_date_column(df)
    df = standardize_numeric_columns(df)
    
    # Standardize crop names
    if 'crop' in df.columns:
        df['crop'] = df['crop'].str.strip().str.title()
    
    # Save
    output_file = CONFIG.CLEANED_DIR / "mandi_standardized.csv"
    df.to_csv(output_file, index=False)
    
    result['records'] = len(df)
    logger.info(f"Mandi standardized: {result['records']:,} records")
    
    return result


def standardize_crop_calendar() -> Dict:
    """Standardize crop calendar data."""
    logger.info("Standardizing crop calendar...")
    
    result = {'records': 0, 'crops': 0}
    
    possible_files = [
        CONFIG.BASE_DIR / "crop_calendar.csv",
        CONFIG.DATA_DIR / "crop_calendar.csv"
    ]
    
    input_file = None
    for f in possible_files:
        if f.exists():
            input_file = f
            break
    
    if input_file is None:
        logger.warning("Crop calendar not found")
        return result
    
    df = pd.read_csv(input_file)
    df = standardize_columns(df)
    
    # Standardize crop names
    if 'crop' in df.columns:
        df['crop'] = df['crop'].str.strip().str.title()
    
    # Ensure month columns are integers
    month_cols = ['sowing_start_month', 'sowing_end_month', 'harvest_start_month', 'harvest_end_month']
    for col in month_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
    
    # Save
    output_file = CONFIG.CLEANED_DIR / "crop_calendar_standardized.csv"
    df.to_csv(output_file, index=False)
    
    result['records'] = len(df)
    result['crops'] = df['crop'].nunique() if 'crop' in df.columns else 0
    
    logger.info(f"Crop calendar standardized: {result['records']} records, {result['crops']} crops")
    
    return result


# =============================================================================
# MAIN STANDARDIZATION
# =============================================================================

def run_schema_standardization() -> Dict:
    """Run all schema standardizations."""
    logger.info("=" * 60)
    logger.info("PHASE C: SCHEMA STANDARDIZATION")
    logger.info("=" * 60)
    
    # Ensure output directory exists
    CONFIG.CLEANED_DIR.mkdir(parents=True, exist_ok=True)
    
    results = {}
    
    print("\n🌧️ Standardizing rainfall...")
    results['rainfall'] = standardize_rainfall()
    
    print("\n🌡️ Standardizing temperature...")
    results['temperature'] = standardize_temperature()
    
    print("\n🌾 Standardizing crop yield...")
    results['crop_yield'] = standardize_crop_yield()
    
    print("\n🌍 Standardizing soil...")
    results['soil'] = standardize_soil()
    
    print("\n📈 Standardizing mandi prices...")
    results['mandi'] = standardize_mandi()
    
    print("\n📅 Standardizing crop calendar...")
    results['crop_calendar'] = standardize_crop_calendar()
    
    # Summary
    print("\n📊 Schema Standardization Summary:")
    print("-" * 50)
    for name, res in results.items():
        records = res.get('records', res.get('files', 0))
        print(f"  {name}: {records:,} records")
    
    return results


if __name__ == "__main__":
    from utils import setup_logging
    setup_logging(CONFIG.LOGS_DIR)
    run_schema_standardization()
