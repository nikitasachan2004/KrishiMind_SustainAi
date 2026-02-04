#!/usr/bin/env python3
"""
Phase E: Geographic Resolution
==============================
Map climate data to districts:
- Load district lat/lon reference
- Aggregate gridded climate data to district level
- Match soil and mandi data to districts
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from tqdm import tqdm

from config import CONFIG
from utils import normalize_district_name, normalize_state_name

logger = logging.getLogger(__name__)


# =============================================================================
# DISTRICT REFERENCE
# =============================================================================

def load_district_reference() -> pd.DataFrame:
    """Load district lat/lon reference data."""
    logger.info("Loading district reference...")
    
    possible_files = [
        CONFIG.BASE_DIR / "district_lat_lon.csv",
        CONFIG.DATA_DIR / "district_lat_lon.csv",
        CONFIG.BASE_DIR / "DATA_SPEI_DroughtAtlas" / "latlon_India_0.05degree.csv"
    ]
    
    for filepath in possible_files:
        if filepath.exists():
            df = pd.read_csv(filepath)
            
            # Standardize columns
            df.columns = df.columns.str.lower().str.strip()
            
            # Rename if needed
            rename_map = {
                'latitude': 'lat',
                'longitude': 'lon',
                'district_name': 'district',
                'state_name': 'state'
            }
            df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})
            
            # Standardize names
            if 'district' in df.columns:
                df['district'] = df['district'].apply(normalize_district_name)
            if 'state' in df.columns:
                df['state'] = df['state'].apply(normalize_state_name)
            
            logger.info(f"Loaded {len(df)} district records from {filepath.name}")
            return df
    
    # Generate from crop yield districts
    logger.warning("District reference not found, generating from crop yield data")
    return generate_district_reference()


def generate_district_reference() -> pd.DataFrame:
    """Generate district reference from available data."""
    
    # Try to get districts from crop yield
    possible_files = [
        CONFIG.CLEANED_DIR / "crop_yield_cleaned.csv",
        CONFIG.CLEANED_DIR / "crop_yield_standardized.csv",
        CONFIG.BASE_DIR / "crop-wise-area-production-yield.csv"
    ]
    
    for filepath in possible_files:
        if filepath.exists():
            df = pd.read_csv(filepath)
            df.columns = df.columns.str.lower().str.strip()
            
            if 'district' in df.columns:
                districts = df[['district', 'state']].drop_duplicates() if 'state' in df.columns else df[['district']].drop_duplicates()
                
                # Normalize
                districts['district'] = districts['district'].apply(normalize_district_name)
                if 'state' in districts.columns:
                    districts['state'] = districts['state'].apply(normalize_state_name)
                
                # Add approximate centroids for Indian districts
                districts = assign_approximate_coordinates(districts)
                
                logger.info(f"Generated reference for {len(districts)} districts")
                return districts
    
    # Fallback: create minimal reference
    return pd.DataFrame({
        'district': ['Mumbai', 'Delhi', 'Chennai', 'Kolkata', 'Bangalore'],
        'state': ['Maharashtra', 'Delhi', 'Tamil Nadu', 'West Bengal', 'Karnataka'],
        'lat': [19.08, 28.65, 13.08, 22.57, 12.97],
        'lon': [72.88, 77.23, 80.27, 88.36, 77.59]
    })


def assign_approximate_coordinates(districts: pd.DataFrame) -> pd.DataFrame:
    """Assign approximate coordinates based on state centroids."""
    
    # State centroids (approximate)
    state_centroids = {
        'andhra pradesh': (15.9, 79.7),
        'arunachal pradesh': (28.2, 94.7),
        'assam': (26.2, 92.9),
        'bihar': (25.1, 85.3),
        'chhattisgarh': (21.3, 81.6),
        'goa': (15.3, 74.0),
        'gujarat': (22.3, 71.2),
        'haryana': (29.0, 76.1),
        'himachal pradesh': (31.1, 77.2),
        'jharkhand': (23.6, 85.3),
        'karnataka': (15.3, 75.7),
        'kerala': (10.9, 76.3),
        'madhya pradesh': (23.5, 77.5),
        'maharashtra': (19.8, 75.3),
        'manipur': (24.7, 93.9),
        'meghalaya': (25.5, 91.4),
        'mizoram': (23.2, 92.9),
        'nagaland': (26.2, 94.6),
        'odisha': (20.5, 84.4),
        'punjab': (31.2, 75.3),
        'rajasthan': (27.0, 74.2),
        'sikkim': (27.5, 88.5),
        'tamil nadu': (11.1, 78.7),
        'telangana': (18.1, 79.0),
        'tripura': (23.9, 91.9),
        'uttar pradesh': (27.2, 80.4),
        'uttarakhand': (30.1, 79.3),
        'west bengal': (22.9, 87.9),
        'delhi': (28.6, 77.2),
        'jammu and kashmir': (33.8, 76.6),
        'ladakh': (34.2, 77.6),
        'puducherry': (11.9, 79.8),
        'chandigarh': (30.7, 76.8),
    }
    
    def get_coords(row):
        state = str(row.get('state', '')).lower().strip()
        if state in state_centroids:
            base_lat, base_lon = state_centroids[state]
            # Add small random offset for each district
            offset_lat = np.random.uniform(-1, 1)
            offset_lon = np.random.uniform(-1, 1)
            return base_lat + offset_lat, base_lon + offset_lon
        return 20.0, 78.0  # India center
    
    if 'lat' not in districts.columns:
        coords = districts.apply(get_coords, axis=1)
        districts['lat'] = [c[0] for c in coords]
        districts['lon'] = [c[1] for c in coords]
    
    return districts


# =============================================================================
# SPATIAL AGGREGATION
# =============================================================================

def build_kdtree(lats: np.ndarray, lons: np.ndarray) -> cKDTree:
    """Build KD-tree for fast nearest neighbor lookup."""
    coords = np.column_stack([lats, lons])
    return cKDTree(coords)


def find_nearest_district(lat: float, lon: float, district_tree: cKDTree,
                          districts: pd.DataFrame) -> Tuple[str, str, float]:
    """Find nearest district for a coordinate."""
    dist, idx = district_tree.query([lat, lon])
    district = districts.iloc[idx]['district']
    state = districts.iloc[idx].get('state', '')
    return district, state, dist


def aggregate_climate_to_district(climate_df: pd.DataFrame, 
                                   district_ref: pd.DataFrame,
                                   value_cols: List[str],
                                   date_col: str = 'date') -> pd.DataFrame:
    """Aggregate gridded climate data to district level."""
    
    # Build KD-tree for districts
    district_tree = build_kdtree(
        district_ref['lat'].values,
        district_ref['lon'].values
    )
    
    # Map each grid point to nearest district
    climate_df = climate_df.copy()
    
    # Find nearest district
    results = []
    for _, row in tqdm(climate_df.iterrows(), total=len(climate_df), 
                       desc="Mapping to districts", disable=len(climate_df) > 100000):
        district, state, dist = find_nearest_district(
            row['lat'], row['lon'], district_tree, district_ref
        )
        results.append((district, state))
    
    climate_df['district'], climate_df['state'] = zip(*results)
    
    # Aggregate by district and date
    group_cols = ['district', 'state']
    if date_col in climate_df.columns:
        group_cols.append(date_col)
    
    agg_funcs = {col: 'mean' for col in value_cols if col in climate_df.columns}
    
    if not agg_funcs:
        return climate_df
    
    aggregated = climate_df.groupby(group_cols).agg(agg_funcs).reset_index()
    
    return aggregated


def aggregate_rainfall_to_district(district_ref: pd.DataFrame) -> Dict:
    """Aggregate rainfall data to district level."""
    logger.info("Aggregating rainfall to districts...")
    
    result = {'files': 0, 'records': 0}
    
    input_dir = CONFIG.CLEANED_DIR / "rainfall_cleaned"
    if not input_dir.exists():
        input_dir = CONFIG.BASE_DIR / "rainfall_csv"
    
    if not input_dir.exists():
        logger.warning("No rainfall data to aggregate")
        return result
    
    output_file = CONFIG.CLEANED_DIR / "rainfall_district.csv"
    
    # Build district tree once
    district_tree = build_kdtree(
        district_ref['lat'].values,
        district_ref['lon'].values
    )
    
    all_records = []
    csv_files = list(input_dir.glob('*.csv'))
    
    for filepath in tqdm(csv_files, desc="Aggregating rainfall"):
        try:
            df = pd.read_csv(filepath)
            
            if 'rainfall' not in df.columns or 'lat' not in df.columns:
                continue
            
            # Sample for speed if large
            if len(df) > 100000:
                df = df.sample(n=100000, random_state=42)
            
            # Map to districts
            districts = []
            for _, row in df.iterrows():
                d, s, _ = find_nearest_district(
                    row['lat'], row['lon'], district_tree, district_ref
                )
                districts.append((d, s))
            
            df['district'], df['state'] = zip(*districts)
            
            # Aggregate
            agg = df.groupby(['district', 'state', 'date']).agg({
                'rainfall': 'mean'
            }).reset_index()
            
            all_records.append(agg)
            result['files'] += 1
            
        except Exception as e:
            logger.error(f"Failed to process {filepath}: {e}")
    
    if all_records:
        combined = pd.concat(all_records, ignore_index=True)
        
        # Re-aggregate in case of overlapping dates
        combined = combined.groupby(['district', 'state', 'date']).agg({
            'rainfall': 'mean'
        }).reset_index()
        
        combined.to_csv(output_file, index=False)
        result['records'] = len(combined)
    
    logger.info(f"Rainfall aggregation: {result['records']:,} district-date records")
    return result


def aggregate_temperature_to_district(district_ref: pd.DataFrame) -> Dict:
    """Aggregate temperature data to district level."""
    logger.info("Aggregating temperature to districts...")
    
    result = {'records': 0}
    
    input_file = CONFIG.CLEANED_DIR / "temperature_cleaned.csv"
    
    if not input_file.exists():
        logger.warning("Temperature cleaned file not found")
        return result
    
    df = pd.read_csv(input_file)
    
    if 'lat' not in df.columns or 'lon' not in df.columns:
        logger.warning("Temperature file missing lat/lon")
        return result
    
    # Sample for speed if large
    if len(df) > 500000:
        df = df.sample(n=500000, random_state=42)
    
    # Build district tree
    district_tree = build_kdtree(
        district_ref['lat'].values,
        district_ref['lon'].values
    )
    
    # Map to districts
    logger.info("Mapping temperature points to districts...")
    districts = []
    for _, row in tqdm(df.iterrows(), total=len(df), desc="Mapping"):
        d, s, _ = find_nearest_district(
            row['lat'], row['lon'], district_tree, district_ref
        )
        districts.append((d, s))
    
    df['district'], df['state'] = zip(*districts)
    
    # Identify temperature columns
    temp_cols = [c for c in ['tmax', 'tmin', 'tavg', 'avg_temp'] if c in df.columns]
    
    # Aggregate
    group_cols = ['district', 'state']
    if 'date' in df.columns:
        group_cols.append('date')
    
    agg_funcs = {col: 'mean' for col in temp_cols}
    aggregated = df.groupby(group_cols).agg(agg_funcs).reset_index()
    
    # Save
    output_file = CONFIG.CLEANED_DIR / "temperature_district.csv"
    aggregated.to_csv(output_file, index=False)
    
    result['records'] = len(aggregated)
    logger.info(f"Temperature aggregation: {result['records']:,} district-date records")
    
    return result


def harmonize_soil_districts(district_ref: pd.DataFrame) -> Dict:
    """Harmonize soil data district names."""
    logger.info("Harmonizing soil district names...")
    
    result = {'records': 0, 'matched': 0}
    
    input_file = CONFIG.CLEANED_DIR / "soil_cleaned.csv"
    
    if not input_file.exists():
        logger.warning("Soil cleaned file not found")
        return result
    
    df = pd.read_csv(input_file)
    
    if 'district' not in df.columns:
        logger.warning("Soil file missing district column")
        return result
    
    # Create district lookup
    district_names = set(district_ref['district'].str.lower())
    
    # Match districts
    def match_district(name):
        if pd.isna(name):
            return name
        name_lower = str(name).lower().strip()
        if name_lower in district_names:
            return name
        
        # Try fuzzy match
        for ref_name in district_names:
            if ref_name in name_lower or name_lower in ref_name:
                return ref_name.title()
        
        return name
    
    df['district_orig'] = df['district']
    df['district'] = df['district'].apply(match_district)
    
    matched = (df['district'].str.lower().isin(district_names)).sum()
    
    # Save
    output_file = CONFIG.CLEANED_DIR / "soil_district.csv"
    df.to_csv(output_file, index=False)
    
    result['records'] = len(df)
    result['matched'] = matched
    
    logger.info(f"Soil harmonization: {result['matched']}/{result['records']} districts matched")
    return result


def harmonize_mandi_districts(district_ref: pd.DataFrame) -> Dict:
    """Harmonize mandi data district names."""
    logger.info("Harmonizing mandi district names...")
    
    result = {'records': 0}
    
    input_file = CONFIG.CLEANED_DIR / "mandi_cleaned.csv"
    
    if not input_file.exists():
        logger.warning("Mandi cleaned file not found")
        return result
    
    df = pd.read_csv(input_file)
    
    if df.empty:
        return result
    
    # Match districts if district column exists
    if 'district' in df.columns:
        district_names = set(district_ref['district'].str.lower())
        
        def match_district(name):
            if pd.isna(name):
                return name
            name_lower = str(name).lower().strip()
            if name_lower in district_names:
                return name
            return name
        
        df['district'] = df['district'].apply(match_district)
    
    # Save
    output_file = CONFIG.CLEANED_DIR / "mandi_district.csv"
    df.to_csv(output_file, index=False)
    
    result['records'] = len(df)
    
    logger.info(f"Mandi harmonization: {result['records']:,} records")
    return result


# =============================================================================
# MAIN GEO RESOLUTION
# =============================================================================

def run_geo_resolution() -> Dict:
    """Run geographic resolution for all datasets."""
    logger.info("=" * 60)
    logger.info("PHASE E: GEOGRAPHIC RESOLUTION")
    logger.info("=" * 60)
    
    results = {}
    
    # Load district reference
    print("\n📍 Loading district reference...")
    district_ref = load_district_reference()
    results['district_count'] = len(district_ref)
    print(f"  Loaded {len(district_ref)} districts")
    
    # Save district reference for later use
    district_ref.to_csv(CONFIG.CLEANED_DIR / "district_reference.csv", index=False)
    
    # Aggregate climate data
    print("\n🌧️ Aggregating rainfall to districts...")
    results['rainfall'] = aggregate_rainfall_to_district(district_ref)
    
    print("\n🌡️ Aggregating temperature to districts...")
    results['temperature'] = aggregate_temperature_to_district(district_ref)
    
    # Harmonize other datasets
    print("\n🌍 Harmonizing soil district names...")
    results['soil'] = harmonize_soil_districts(district_ref)
    
    print("\n📈 Harmonizing mandi district names...")
    results['mandi'] = harmonize_mandi_districts(district_ref)
    
    # Summary
    print("\n📊 Geographic Resolution Summary:")
    print("-" * 50)
    print(f"  Districts: {results['district_count']}")
    print(f"  Rainfall records: {results['rainfall'].get('records', 0):,}")
    print(f"  Temperature records: {results['temperature'].get('records', 0):,}")
    print(f"  Soil records: {results['soil'].get('records', 0):,}")
    print(f"  Mandi records: {results['mandi'].get('records', 0):,}")
    
    return results


if __name__ == "__main__":
    from utils import setup_logging
    setup_logging(CONFIG.LOGS_DIR)
    run_geo_resolution()
