#!/usr/bin/env python3
"""
Phase D: Data Cleaning
======================
Apply cleaning rules to all datasets:
- Remove physically invalid values
- Interpolate gaps
- Remove outliers (IQR method)
- Handle missing values
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from tqdm import tqdm

from config import CONFIG

logger = logging.getLogger(__name__)


# =============================================================================
# VALIDATION RULES
# =============================================================================

VALID_RANGES = {
    # Climate
    'rainfall': (0, 500),      # mm/day
    'tmax': (-10, 55),         # Celsius
    'tmin': (-20, 45),         # Celsius
    'tavg': (-15, 50),         # Celsius
    'avg_temp': (-15, 50),     # Celsius
    'humidity': (0, 100),      # Percentage
    
    # Coordinates
    'lat': (6.0, 38.0),        # India bounds
    'lon': (66.0, 100.0),      # India bounds
    
    # Crop
    'area': (0, 1e9),          # hectares
    'production': (0, 1e10),   # tonnes
    'yield': (0, 50000),       # kg/ha
    
    # Soil
    'ph': (3, 11),
    'oc': (0, 10),             # organic carbon %
    'nitrogen': (0, 1000),     # kg/ha
    'phosphorus': (0, 500),    # kg/ha
    'potassium': (0, 1000),    # kg/ha
    
    # Prices
    'price_modal': (0, 100000),
    'price_min': (0, 100000),
    'price_max': (0, 100000),
    
    # Year
    'year': (1990, 2030),
}


# =============================================================================
# CLEANING FUNCTIONS
# =============================================================================

def remove_invalid_values(df: pd.DataFrame, validation_rules: Dict = None) -> Tuple[pd.DataFrame, Dict]:
    """Remove values outside valid ranges."""
    rules = validation_rules or VALID_RANGES
    stats = {'removed_rows': 0, 'invalid_values': {}}
    
    initial_len = len(df)
    
    for col in df.columns:
        if col in rules:
            min_val, max_val = rules[col]
            
            if col in df.columns and df[col].dtype in ['float64', 'float32', 'int64', 'int32']:
                invalid_mask = (df[col] < min_val) | (df[col] > max_val)
                invalid_count = invalid_mask.sum()
                
                if invalid_count > 0:
                    stats['invalid_values'][col] = invalid_count
                    df.loc[invalid_mask, col] = np.nan
    
    stats['removed_rows'] = initial_len - len(df.dropna(how='all'))
    
    return df, stats


def remove_outliers_iqr(df: pd.DataFrame, columns: List[str] = None, 
                        multiplier: float = 3.0) -> Tuple[pd.DataFrame, Dict]:
    """Remove outliers using IQR method."""
    stats = {'outliers_removed': {}}
    
    if columns is None:
        # Default numeric columns to check
        columns = [c for c in df.columns if df[c].dtype in ['float64', 'float32', 'int64', 'int32']]
        # Exclude coordinate and year columns
        columns = [c for c in columns if c not in ['lat', 'lon', 'year', 'month', 'day']]
    
    for col in columns:
        if col not in df.columns:
            continue
        
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - multiplier * IQR
        upper_bound = Q3 + multiplier * IQR
        
        outlier_mask = (df[col] < lower_bound) | (df[col] > upper_bound)
        outlier_count = outlier_mask.sum()
        
        if outlier_count > 0:
            stats['outliers_removed'][col] = outlier_count
            df.loc[outlier_mask, col] = np.nan
    
    return df, stats


def interpolate_gaps(df: pd.DataFrame, columns: List[str] = None,
                     method: str = 'linear', max_gap: int = 3) -> Tuple[pd.DataFrame, Dict]:
    """Interpolate missing values."""
    stats = {'interpolated': {}}
    
    if columns is None:
        columns = [c for c in df.columns if df[c].dtype in ['float64', 'float32']]
    
    for col in columns:
        if col not in df.columns:
            continue
        
        missing_before = df[col].isna().sum()
        
        if missing_before > 0:
            df[col] = df[col].interpolate(method=method, limit=max_gap)
            missing_after = df[col].isna().sum()
            filled = missing_before - missing_after
            
            if filled > 0:
                stats['interpolated'][col] = filled
    
    return df, stats


def fill_missing_with_median(df: pd.DataFrame, columns: List[str] = None,
                             group_by: List[str] = None) -> Tuple[pd.DataFrame, Dict]:
    """Fill remaining missing values with median (optionally grouped)."""
    stats = {'filled': {}}
    
    if columns is None:
        columns = [c for c in df.columns if df[c].dtype in ['float64', 'float32', 'int64', 'int32']]
    
    for col in columns:
        if col not in df.columns:
            continue
        
        missing_before = df[col].isna().sum()
        
        if missing_before > 0:
            if group_by and all(g in df.columns for g in group_by):
                df[col] = df.groupby(group_by)[col].transform(
                    lambda x: x.fillna(x.median())
                )
            
            # Fill any remaining with global median
            median_val = df[col].median()
            if pd.notna(median_val):
                df[col] = df[col].fillna(median_val)
            
            missing_after = df[col].isna().sum()
            filled = missing_before - missing_after
            
            if filled > 0:
                stats['filled'][col] = filled
    
    return df, stats


def drop_insufficient_rows(df: pd.DataFrame, required_cols: List[str] = None,
                           min_valid_ratio: float = 0.5) -> Tuple[pd.DataFrame, Dict]:
    """Drop rows with too many missing values."""
    initial_len = len(df)
    
    if required_cols:
        # Drop rows missing any required column
        df = df.dropna(subset=required_cols)
    
    # Count valid values per row (excluding coordinate/id columns)
    data_cols = [c for c in df.columns if c not in ['lat', 'lon', 'year', 'month', 'day', 'date', 'district', 'state', 'crop']]
    
    if data_cols:
        valid_count = df[data_cols].notna().sum(axis=1)
        min_valid = int(len(data_cols) * min_valid_ratio)
        df = df[valid_count >= min_valid]
    
    stats = {'dropped_rows': initial_len - len(df)}
    
    return df, stats


# =============================================================================
# DATASET-SPECIFIC CLEANING
# =============================================================================

def clean_rainfall() -> Dict:
    """Clean rainfall data."""
    logger.info("Cleaning rainfall data...")
    
    result = {'files': 0, 'records': 0, 'removed': 0}
    
    input_dir = CONFIG.CLEANED_DIR / "rainfall_standardized"
    output_dir = CONFIG.CLEANED_DIR / "rainfall_cleaned"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if not input_dir.exists():
        # Try base rainfall dir
        input_dir = CONFIG.BASE_DIR / "rainfall_csv"
    
    if not input_dir.exists():
        logger.warning("No rainfall data to clean")
        return result
    
    csv_files = list(input_dir.glob('*.csv'))
    
    for filepath in tqdm(csv_files, desc="Cleaning rainfall"):
        try:
            df = pd.read_csv(filepath)
            initial_len = len(df)
            
            # Remove invalid values
            df, stats1 = remove_invalid_values(df)
            
            # Remove outliers
            df, stats2 = remove_outliers_iqr(df, columns=['rainfall'])
            
            # Interpolate gaps (time series)
            df, stats3 = interpolate_gaps(df, columns=['rainfall'])
            
            # Drop rows with missing rainfall
            df = df.dropna(subset=['rainfall'])
            
            # Save
            output_file = output_dir / f"{filepath.stem}_clean.csv"
            df.to_csv(output_file, index=False)
            
            result['files'] += 1
            result['records'] += len(df)
            result['removed'] += initial_len - len(df)
            
        except Exception as e:
            logger.error(f"Failed to clean {filepath}: {e}")
    
    logger.info(f"Rainfall cleaned: {result['files']} files, {result['records']:,} records")
    return result


def clean_temperature() -> Dict:
    """Clean temperature data."""
    logger.info("Cleaning temperature data...")
    
    result = {'records': 0, 'removed': 0}
    
    input_file = CONFIG.CLEANED_DIR / "temperature_standardized.csv"
    
    if not input_file.exists():
        logger.warning("Temperature standardized file not found")
        return result
    
    df = pd.read_csv(input_file)
    initial_len = len(df)
    
    # Remove invalid values
    df, stats1 = remove_invalid_values(df)
    
    # Remove outliers
    temp_cols = [c for c in ['tmax', 'tmin', 'tavg', 'avg_temp'] if c in df.columns]
    df, stats2 = remove_outliers_iqr(df, columns=temp_cols)
    
    # Interpolate gaps
    df, stats3 = interpolate_gaps(df, columns=temp_cols)
    
    # Validate tmax > tmin
    if 'tmax' in df.columns and 'tmin' in df.columns:
        invalid_temp = df['tmax'] < df['tmin']
        if invalid_temp.sum() > 0:
            logger.warning(f"Found {invalid_temp.sum()} records where tmax < tmin, swapping")
            df.loc[invalid_temp, ['tmax', 'tmin']] = df.loc[invalid_temp, ['tmin', 'tmax']].values
    
    # Drop rows missing all temperature values
    df = df.dropna(subset=temp_cols, how='all')
    
    # Save
    output_file = CONFIG.CLEANED_DIR / "temperature_cleaned.csv"
    df.to_csv(output_file, index=False)
    
    result['records'] = len(df)
    result['removed'] = initial_len - len(df)
    
    logger.info(f"Temperature cleaned: {result['records']:,} records, removed {result['removed']:,}")
    return result


def clean_crop_yield() -> Dict:
    """Clean crop yield data."""
    logger.info("Cleaning crop yield data...")
    
    result = {'records': 0, 'removed': 0, 'outliers': 0}
    
    input_file = CONFIG.CLEANED_DIR / "crop_yield_standardized.csv"
    
    if not input_file.exists():
        logger.warning("Crop yield standardized file not found")
        return result
    
    df = pd.read_csv(input_file)
    initial_len = len(df)
    
    # Remove invalid values
    df, stats1 = remove_invalid_values(df)
    
    # Remove outliers by crop (yield varies widely)
    if 'yield' in df.columns and 'crop' in df.columns:
        outliers_removed = 0
        for crop in df['crop'].unique():
            crop_mask = df['crop'] == crop
            crop_df = df[crop_mask].copy()
            
            Q1 = crop_df['yield'].quantile(0.25)
            Q3 = crop_df['yield'].quantile(0.75)
            IQR = Q3 - Q1
            
            lower = Q1 - 3 * IQR
            upper = Q3 + 3 * IQR
            
            outlier_mask = crop_mask & ((df['yield'] < lower) | (df['yield'] > upper))
            outliers_removed += outlier_mask.sum()
            df.loc[outlier_mask, 'yield'] = np.nan
        
        result['outliers'] = outliers_removed
    
    # Fill missing yields with group median
    if 'yield' in df.columns and 'crop' in df.columns and 'state' in df.columns:
        df, stats4 = fill_missing_with_median(df, columns=['yield'], group_by=['crop', 'state'])
    
    # Recompute yield if area and production exist
    if all(c in df.columns for c in ['area', 'production', 'yield']):
        can_compute = (df['area'] > 0) & (df['production'] >= 0) & df['yield'].isna()
        df.loc[can_compute, 'yield'] = (df.loc[can_compute, 'production'] / df.loc[can_compute, 'area']) * 1000
    
    # Drop rows missing critical fields
    required = [c for c in ['crop', 'district', 'year'] if c in df.columns]
    if required:
        df = df.dropna(subset=required)
    
    # Save
    output_file = CONFIG.CLEANED_DIR / "crop_yield_cleaned.csv"
    df.to_csv(output_file, index=False)
    
    result['records'] = len(df)
    result['removed'] = initial_len - len(df)
    
    logger.info(f"Crop yield cleaned: {result['records']:,} records, removed {result['removed']:,}")
    return result


def clean_soil() -> Dict:
    """Clean soil data."""
    logger.info("Cleaning soil data...")
    
    result = {'records': 0, 'removed': 0}
    
    input_file = CONFIG.CLEANED_DIR / "soil_standardized.csv"
    
    if not input_file.exists():
        logger.warning("Soil standardized file not found")
        return result
    
    df = pd.read_csv(input_file)
    initial_len = len(df)
    
    # Remove invalid values
    df, stats1 = remove_invalid_values(df)
    
    # Remove outliers
    soil_cols = [c for c in ['ph', 'oc', 'nitrogen', 'phosphorus', 'potassium'] if c in df.columns]
    df, stats2 = remove_outliers_iqr(df, columns=soil_cols, multiplier=3.0)
    
    # Fill missing with district median, then global median
    df, stats3 = fill_missing_with_median(df, columns=soil_cols, group_by=['district'] if 'district' in df.columns else None)
    
    # Drop rows missing district
    if 'district' in df.columns:
        df = df.dropna(subset=['district'])
    
    # Save
    output_file = CONFIG.CLEANED_DIR / "soil_cleaned.csv"
    df.to_csv(output_file, index=False)
    
    result['records'] = len(df)
    result['removed'] = initial_len - len(df)
    
    logger.info(f"Soil cleaned: {result['records']:,} records")
    return result


def clean_mandi() -> Dict:
    """Clean mandi price data."""
    logger.info("Cleaning mandi data...")
    
    result = {'records': 0, 'removed': 0}
    
    input_file = CONFIG.CLEANED_DIR / "mandi_standardized.csv"
    
    if not input_file.exists():
        logger.warning("Mandi standardized file not found")
        return result
    
    df = pd.read_csv(input_file)
    
    if df.empty:
        logger.warning("Mandi data is empty")
        return result
    
    initial_len = len(df)
    
    # Remove invalid values
    df, stats1 = remove_invalid_values(df)
    
    # Remove outliers by crop
    price_cols = [c for c in ['price_modal', 'price_min', 'price_max'] if c in df.columns]
    
    if 'crop' in df.columns and price_cols:
        for crop in df['crop'].unique():
            crop_mask = df['crop'] == crop
            for col in price_cols:
                Q1 = df.loc[crop_mask, col].quantile(0.25)
                Q3 = df.loc[crop_mask, col].quantile(0.75)
                IQR = Q3 - Q1
                
                outlier_mask = crop_mask & ((df[col] < Q1 - 3*IQR) | (df[col] > Q3 + 3*IQR))
                df.loc[outlier_mask, col] = np.nan
    
    # Validate price_min <= price_modal <= price_max
    if all(c in df.columns for c in ['price_min', 'price_modal', 'price_max']):
        invalid_order = (df['price_min'] > df['price_modal']) | (df['price_modal'] > df['price_max'])
        if invalid_order.sum() > 0:
            logger.warning(f"Found {invalid_order.sum()} records with inconsistent prices")
            # Keep modal, drop others
            df.loc[invalid_order, ['price_min', 'price_max']] = np.nan
    
    # Drop rows missing crop or price
    required = ['crop']
    if 'price_modal' in df.columns:
        required.append('price_modal')
    
    df = df.dropna(subset=required)
    
    # Save
    output_file = CONFIG.CLEANED_DIR / "mandi_cleaned.csv"
    df.to_csv(output_file, index=False)
    
    result['records'] = len(df)
    result['removed'] = initial_len - len(df)
    
    logger.info(f"Mandi cleaned: {result['records']:,} records")
    return result


# =============================================================================
# MAIN CLEANING
# =============================================================================

def run_data_cleaning() -> Dict:
    """Run all data cleaning."""
    logger.info("=" * 60)
    logger.info("PHASE D: DATA CLEANING")
    logger.info("=" * 60)
    
    results = {}
    
    print("\n🌧️ Cleaning rainfall...")
    results['rainfall'] = clean_rainfall()
    
    print("\n🌡️ Cleaning temperature...")
    results['temperature'] = clean_temperature()
    
    print("\n🌾 Cleaning crop yield...")
    results['crop_yield'] = clean_crop_yield()
    
    print("\n🌍 Cleaning soil...")
    results['soil'] = clean_soil()
    
    print("\n📈 Cleaning mandi prices...")
    results['mandi'] = clean_mandi()
    
    # Summary
    print("\n📊 Data Cleaning Summary:")
    print("-" * 50)
    total_removed = 0
    for name, res in results.items():
        records = res.get('records', 0)
        removed = res.get('removed', 0)
        total_removed += removed
        print(f"  {name}: {records:,} records (removed {removed:,})")
    print(f"\n  Total records removed: {total_removed:,}")
    
    return results


if __name__ == "__main__":
    from utils import setup_logging
    setup_logging(CONFIG.LOGS_DIR)
    run_data_cleaning()
