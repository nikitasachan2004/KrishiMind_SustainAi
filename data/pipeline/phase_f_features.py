#!/usr/bin/env python3
"""
Phase F: Feature Engineering
============================
Create derived features for modeling:
- Climate features: seasonal_rainfall, GDD, heatwave_count, rainfall_anomaly
- Price features: rolling averages, volatility
- Soil features: soil_quality_index
- Crop features: season labels
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
from tqdm import tqdm

from config import CONFIG

logger = logging.getLogger(__name__)


# =============================================================================
# CLIMATE FEATURES
# =============================================================================

def compute_seasonal_rainfall(df: pd.DataFrame) -> pd.DataFrame:
    """Compute seasonal rainfall aggregates."""
    logger.info("Computing seasonal rainfall...")
    
    if 'date' not in df.columns or 'rainfall' not in df.columns:
        return df
    
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    
    # Define seasons (India)
    def get_season(month):
        if month in [6, 7, 8, 9]:  # June-September
            return 'monsoon'
        elif month in [10, 11]:  # Post-monsoon
            return 'post_monsoon'
        elif month in [12, 1, 2]:  # Winter
            return 'winter'
        else:  # March-May
            return 'summer'
    
    df['season'] = df['month'].apply(get_season)
    
    # Aggregate by district, year, season
    group_cols = ['district', 'state', 'year', 'season'] if 'state' in df.columns else ['district', 'year', 'season']
    group_cols = [c for c in group_cols if c in df.columns]
    
    if not group_cols:
        return df
    
    seasonal = df.groupby(group_cols).agg({
        'rainfall': ['sum', 'mean', 'max', 'std', 'count']
    }).reset_index()
    
    seasonal.columns = [f"{a}_{b}" if b else a for a, b in seasonal.columns]
    seasonal = seasonal.rename(columns={
        'rainfall_sum': 'seasonal_rainfall_total',
        'rainfall_mean': 'seasonal_rainfall_mean',
        'rainfall_max': 'seasonal_rainfall_max',
        'rainfall_std': 'seasonal_rainfall_std',
        'rainfall_count': 'rainy_days'
    })
    
    return seasonal


def compute_rainfall_anomaly(df: pd.DataFrame) -> pd.DataFrame:
    """Compute rainfall anomaly from long-term mean."""
    logger.info("Computing rainfall anomaly...")
    
    if 'rainfall' not in df.columns:
        return df
    
    df = df.copy()
    
    # Compute long-term mean by district and month
    group_cols = ['district', 'month'] if 'month' in df.columns else ['district']
    group_cols = [c for c in group_cols if c in df.columns]
    
    if not group_cols:
        return df
    
    # Historical mean
    historical_mean = df.groupby(group_cols)['rainfall'].transform('mean')
    historical_std = df.groupby(group_cols)['rainfall'].transform('std')
    
    # Anomaly (z-score)
    df['rainfall_anomaly'] = (df['rainfall'] - historical_mean) / (historical_std + 1e-6)
    
    return df


def compute_gdd(df: pd.DataFrame, base_temp: float = 10.0, 
                max_temp: float = 30.0) -> pd.DataFrame:
    """Compute Growing Degree Days (GDD)."""
    logger.info("Computing GDD...")
    
    df = df.copy()
    
    # Need tmax and tmin, or avg_temp
    if 'tmax' in df.columns and 'tmin' in df.columns:
        # Cap temperatures
        tmax_capped = df['tmax'].clip(upper=max_temp)
        tmin_capped = df['tmin'].clip(lower=base_temp)
        
        # Daily GDD
        avg_temp = (tmax_capped + tmin_capped) / 2
        df['gdd_daily'] = (avg_temp - base_temp).clip(lower=0)
    elif 'avg_temp' in df.columns:
        df['gdd_daily'] = (df['avg_temp'] - base_temp).clip(lower=0)
    elif 'tavg' in df.columns:
        df['gdd_daily'] = (df['tavg'] - base_temp).clip(lower=0)
    else:
        return df
    
    return df


def compute_heatwave_count(df: pd.DataFrame, threshold: float = 40.0) -> pd.DataFrame:
    """Count heatwave days (consecutive days above threshold)."""
    logger.info("Computing heatwave metrics...")
    
    df = df.copy()
    
    temp_col = 'tmax' if 'tmax' in df.columns else ('avg_temp' if 'avg_temp' in df.columns else None)
    
    if temp_col is None:
        return df
    
    # Flag hot days
    df['hot_day'] = (df[temp_col] > threshold).astype(int)
    
    return df


def aggregate_climate_features_annual(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate daily climate features to annual."""
    logger.info("Aggregating climate features to annual...")
    
    df = df.copy()
    
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df['year'] = df['date'].dt.year
    
    if 'year' not in df.columns:
        return df
    
    group_cols = ['district', 'year']
    if 'state' in df.columns:
        group_cols = ['district', 'state', 'year']
    
    group_cols = [c for c in group_cols if c in df.columns]
    
    agg_dict = {}
    
    if 'rainfall' in df.columns:
        agg_dict['rainfall'] = ['sum', 'mean', 'max']
    
    if 'rainfall_anomaly' in df.columns:
        agg_dict['rainfall_anomaly'] = 'mean'
    
    if 'gdd_daily' in df.columns:
        agg_dict['gdd_daily'] = 'sum'
    
    if 'hot_day' in df.columns:
        agg_dict['hot_day'] = 'sum'
    
    if 'tmax' in df.columns:
        agg_dict['tmax'] = ['mean', 'max']
    
    if 'tmin' in df.columns:
        agg_dict['tmin'] = ['mean', 'min']
    
    if not agg_dict:
        return df
    
    annual = df.groupby(group_cols).agg(agg_dict).reset_index()
    
    # Flatten column names
    annual.columns = [f"{a}_{b}" if b else a for a, b in annual.columns]
    
    # Rename
    rename_map = {
        'rainfall_sum': 'annual_rainfall',
        'rainfall_mean': 'avg_daily_rainfall',
        'rainfall_max': 'max_daily_rainfall',
        'rainfall_anomaly_mean': 'rainfall_anomaly',
        'gdd_daily_sum': 'gdd_annual',
        'hot_day_sum': 'heatwave_days',
        'tmax_mean': 'avg_tmax',
        'tmax_max': 'max_tmax',
        'tmin_mean': 'avg_tmin',
        'tmin_min': 'min_tmin'
    }
    
    annual = annual.rename(columns=rename_map)
    
    return annual


# =============================================================================
# PRICE FEATURES
# =============================================================================

def compute_price_features(df: pd.DataFrame) -> pd.DataFrame:
    """Compute price-based features."""
    logger.info("Computing price features...")
    
    if df.empty:
        return df
    
    price_col = 'price_modal' if 'price_modal' in df.columns else None
    if price_col is None:
        return df
    
    df = df.copy()
    
    # Sort by date
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.sort_values('date')
    
    # Group by crop and district
    group_cols = ['crop', 'district'] if 'district' in df.columns else ['crop']
    group_cols = [c for c in group_cols if c in df.columns]
    
    if not group_cols:
        return df
    
    # Rolling features
    for window in [7, 30, 90]:
        col_name = f'price_ma_{window}d'
        df[col_name] = df.groupby(group_cols)[price_col].transform(
            lambda x: x.rolling(window, min_periods=1).mean()
        )
    
    # Price volatility (std)
    df['price_volatility_30d'] = df.groupby(group_cols)[price_col].transform(
        lambda x: x.rolling(30, min_periods=1).std()
    )
    
    # Price change
    df['price_pct_change'] = df.groupby(group_cols)[price_col].transform(
        lambda x: x.pct_change()
    )
    
    return df


def aggregate_price_features_annual(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate price features to annual level."""
    logger.info("Aggregating price features to annual...")
    
    if df.empty:
        return df
    
    df = df.copy()
    
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df['year'] = df['date'].dt.year
    
    if 'year' not in df.columns:
        return df
    
    group_cols = ['crop', 'district', 'year']
    if 'state' in df.columns:
        group_cols = ['crop', 'district', 'state', 'year']
    
    group_cols = [c for c in group_cols if c in df.columns]
    
    agg_dict = {}
    
    if 'price_modal' in df.columns:
        agg_dict['price_modal'] = ['mean', 'min', 'max', 'std']
    
    if 'price_volatility_30d' in df.columns:
        agg_dict['price_volatility_30d'] = 'mean'
    
    if not agg_dict:
        return df
    
    annual = df.groupby(group_cols).agg(agg_dict).reset_index()
    
    # Flatten columns
    annual.columns = [f"{a}_{b}" if b else a for a, b in annual.columns]
    
    rename_map = {
        'price_modal_mean': 'avg_price',
        'price_modal_min': 'min_price',
        'price_modal_max': 'max_price',
        'price_modal_std': 'price_std',
        'price_volatility_30d_mean': 'avg_volatility'
    }
    
    annual = annual.rename(columns=rename_map)
    
    return annual


# =============================================================================
# SOIL FEATURES
# =============================================================================

def compute_soil_quality_index(df: pd.DataFrame) -> pd.DataFrame:
    """Compute composite soil quality index."""
    logger.info("Computing soil quality index...")
    
    df = df.copy()
    
    # Components: pH (optimal 6-7), organic carbon, N, P, K
    scores = []
    
    # pH score (optimal 6-7)
    if 'ph' in df.columns:
        # Transform to 0-1 score (peak at 6.5)
        ph_score = 1 - np.abs(df['ph'] - 6.5) / 3.5
        ph_score = ph_score.clip(0, 1)
        scores.append(ph_score)
    
    # Organic carbon score (higher is better, max around 5%)
    if 'oc' in df.columns:
        oc_score = (df['oc'] / 5).clip(0, 1)
        scores.append(oc_score)
    
    # Nutrient scores (normalize to 0-1)
    for nutrient, max_val in [('nitrogen', 500), ('phosphorus', 100), ('potassium', 500)]:
        if nutrient in df.columns:
            nutrient_score = (df[nutrient] / max_val).clip(0, 1)
            scores.append(nutrient_score)
    
    if scores:
        # Average of all component scores
        df['soil_quality_index'] = np.mean(scores, axis=0)
    
    return df


# =============================================================================
# CROP FEATURES
# =============================================================================

def add_crop_season_features(df: pd.DataFrame, crop_calendar: pd.DataFrame) -> pd.DataFrame:
    """Add crop season features from calendar."""
    logger.info("Adding crop season features...")
    
    if crop_calendar.empty:
        return df
    
    df = df.copy()
    
    # Prepare calendar lookup
    if 'crop' not in crop_calendar.columns:
        return df
    
    crop_calendar = crop_calendar.copy()
    crop_calendar['crop_lower'] = crop_calendar['crop'].str.lower().str.strip()
    
    calendar_dict = crop_calendar.set_index('crop_lower').to_dict('index')
    
    def get_season_info(crop_name):
        if pd.isna(crop_name):
            return None, None, None
        
        crop_lower = str(crop_name).lower().strip()
        
        if crop_lower in calendar_dict:
            info = calendar_dict[crop_lower]
            return (
                info.get('season_label', 'Unknown'),
                info.get('sowing_start_month'),
                info.get('harvest_start_month')
            )
        
        # Try partial match
        for cal_crop, info in calendar_dict.items():
            if cal_crop in crop_lower or crop_lower in cal_crop:
                return (
                    info.get('season_label', 'Unknown'),
                    info.get('sowing_start_month'),
                    info.get('harvest_start_month')
                )
        
        return 'Unknown', None, None
    
    if 'crop' in df.columns:
        season_info = df['crop'].apply(get_season_info)
        df['season_label'] = [x[0] for x in season_info]
        df['sowing_month'] = [x[1] for x in season_info]
        df['harvest_month'] = [x[2] for x in season_info]
    
    return df


# =============================================================================
# MAIN FEATURE ENGINEERING
# =============================================================================

def run_feature_engineering() -> Dict:
    """Run all feature engineering."""
    logger.info("=" * 60)
    logger.info("PHASE F: FEATURE ENGINEERING")
    logger.info("=" * 60)
    
    results = {}
    
    # Load crop calendar
    calendar_file = CONFIG.CLEANED_DIR / "crop_calendar_standardized.csv"
    if calendar_file.exists():
        crop_calendar = pd.read_csv(calendar_file)
    else:
        crop_calendar = pd.DataFrame()
    
    # =========================
    # Climate Features
    # =========================
    print("\n🌧️ Engineering rainfall features...")
    
    rainfall_file = CONFIG.CLEANED_DIR / "rainfall_district.csv"
    if rainfall_file.exists():
        rainfall_df = pd.read_csv(rainfall_file)
        
        # Compute features
        rainfall_df = compute_rainfall_anomaly(rainfall_df)
        
        # Aggregate to annual
        rainfall_annual = aggregate_climate_features_annual(rainfall_df)
        
        # Seasonal aggregates
        rainfall_seasonal = compute_seasonal_rainfall(rainfall_df)
        
        # Save
        rainfall_annual.to_csv(CONFIG.CLEANED_DIR / "rainfall_features.csv", index=False)
        rainfall_seasonal.to_csv(CONFIG.CLEANED_DIR / "rainfall_seasonal.csv", index=False)
        
        results['rainfall_features'] = len(rainfall_annual)
        print(f"  Created {len(rainfall_annual)} rainfall feature records")
    else:
        results['rainfall_features'] = 0
        print("  No rainfall data to process")
    
    # =========================
    # Temperature Features
    # =========================
    print("\n🌡️ Engineering temperature features...")
    
    temp_file = CONFIG.CLEANED_DIR / "temperature_district.csv"
    if not temp_file.exists():
        temp_file = CONFIG.CLEANED_DIR / "temperature_cleaned.csv"
    
    if temp_file.exists():
        temp_df = pd.read_csv(temp_file)
        
        # Compute features
        temp_df = compute_gdd(temp_df)
        temp_df = compute_heatwave_count(temp_df)
        
        # Aggregate to annual
        temp_annual = aggregate_climate_features_annual(temp_df)
        
        # Save
        temp_annual.to_csv(CONFIG.CLEANED_DIR / "temperature_features.csv", index=False)
        
        results['temperature_features'] = len(temp_annual)
        print(f"  Created {len(temp_annual)} temperature feature records")
    else:
        results['temperature_features'] = 0
        print("  No temperature data to process")
    
    # =========================
    # Price Features
    # =========================
    print("\n📈 Engineering price features...")
    
    mandi_file = CONFIG.CLEANED_DIR / "mandi_district.csv"
    if not mandi_file.exists():
        mandi_file = CONFIG.CLEANED_DIR / "mandi_cleaned.csv"
    
    if mandi_file.exists():
        mandi_df = pd.read_csv(mandi_file)
        
        if not mandi_df.empty:
            # Compute features
            mandi_df = compute_price_features(mandi_df)
            
            # Aggregate to annual
            price_annual = aggregate_price_features_annual(mandi_df)
            
            # Save
            price_annual.to_csv(CONFIG.CLEANED_DIR / "price_features.csv", index=False)
            
            results['price_features'] = len(price_annual)
            print(f"  Created {len(price_annual)} price feature records")
        else:
            results['price_features'] = 0
            print("  Mandi data is empty")
    else:
        results['price_features'] = 0
        print("  No mandi data to process")
    
    # =========================
    # Soil Features
    # =========================
    print("\n🌍 Engineering soil features...")
    
    soil_file = CONFIG.CLEANED_DIR / "soil_district.csv"
    if not soil_file.exists():
        soil_file = CONFIG.CLEANED_DIR / "soil_cleaned.csv"
    
    if soil_file.exists():
        soil_df = pd.read_csv(soil_file)
        
        # Compute features
        soil_df = compute_soil_quality_index(soil_df)
        
        # Save
        soil_df.to_csv(CONFIG.CLEANED_DIR / "soil_features.csv", index=False)
        
        results['soil_features'] = len(soil_df)
        print(f"  Created {len(soil_df)} soil feature records")
    else:
        results['soil_features'] = 0
        print("  No soil data to process")
    
    # =========================
    # Crop Features
    # =========================
    print("\n🌾 Adding crop season features...")
    
    crop_file = CONFIG.CLEANED_DIR / "crop_yield_cleaned.csv"
    if crop_file.exists():
        crop_df = pd.read_csv(crop_file)
        
        # Add season features
        crop_df = add_crop_season_features(crop_df, crop_calendar)
        
        # Save
        crop_df.to_csv(CONFIG.CLEANED_DIR / "crop_yield_features.csv", index=False)
        
        results['crop_features'] = len(crop_df)
        print(f"  Updated {len(crop_df)} crop records with season features")
    else:
        results['crop_features'] = 0
        print("  No crop yield data to process")
    
    # Summary
    print("\n📊 Feature Engineering Summary:")
    print("-" * 50)
    for name, count in results.items():
        print(f"  {name}: {count:,} records")
    
    return results


if __name__ == "__main__":
    from utils import setup_logging
    setup_logging(CONFIG.LOGS_DIR)
    run_feature_engineering()
