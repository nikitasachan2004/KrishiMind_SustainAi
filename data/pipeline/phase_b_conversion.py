#!/usr/bin/env python3
"""
Phase B: Format Conversion
==========================
Convert raw data formats to standardized CSVs.
- NetCDF/GRD rainfall to CSV
- PDF crop calendar to CSV
- Verify and merge temperature data
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import xarray as xr
from tqdm import tqdm

from config import CONFIG
from utils import read_csv_safe, standardize_columns

logger = logging.getLogger(__name__)


# =============================================================================
# RAINFALL CONVERSION
# =============================================================================

def detect_rainfall_format(filepath: Path) -> str:
    """Detect rainfall file format."""
    suffix = filepath.suffix.lower()
    
    if suffix == '.nc':
        return 'netcdf'
    elif suffix == '.grd':
        return 'binary_grd'
    elif suffix == '.csv':
        return 'csv'
    else:
        # Try reading as netcdf
        try:
            with xr.open_dataset(filepath) as ds:
                return 'netcdf'
        except:
            return 'unknown'


def convert_netcdf_rainfall(filepath: Path) -> pd.DataFrame:
    """Convert NetCDF rainfall file to DataFrame."""
    logger.debug(f"Converting NetCDF: {filepath.name}")
    
    try:
        with xr.open_dataset(filepath) as ds:
            # Get variable names
            var_names = list(ds.data_vars)
            
            # Find rainfall variable
            rain_var = None
            for name in ['rf', 'rainfall', 'RAINFALL', 'precip', 'precipitation', 'rain']:
                if name in var_names:
                    rain_var = name
                    break
            
            if rain_var is None and var_names:
                rain_var = var_names[0]
            
            if rain_var is None:
                logger.warning(f"No rainfall variable in {filepath}")
                return pd.DataFrame()
            
            # Convert to dataframe
            df = ds[rain_var].to_dataframe().reset_index()
            
            # Standardize column names
            rename_map = {}
            for col in df.columns:
                col_lower = str(col).lower()
                if 'time' in col_lower:
                    rename_map[col] = 'date'
                elif 'lat' in col_lower:
                    rename_map[col] = 'lat'
                elif 'lon' in col_lower:
                    rename_map[col] = 'lon'
            
            rename_map[rain_var] = 'rainfall'
            df = df.rename(columns=rename_map)
            
            # Format date
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
            
            # Keep only required columns
            cols = ['date', 'lat', 'lon', 'rainfall']
            df = df[[c for c in cols if c in df.columns]]
            
            # Remove missing values
            df = df.dropna()
            
            return df
            
    except Exception as e:
        logger.error(f"Failed to convert {filepath}: {e}")
        return pd.DataFrame()


def convert_grd_rainfall(filepath: Path) -> pd.DataFrame:
    """Convert IMD GRD binary file to DataFrame."""
    logger.debug(f"Converting GRD: {filepath.name}")
    
    # IMD GRD parameters (0.25 degree resolution)
    nlat, nlon = 129, 135
    lat_start, lat_end = 6.5, 38.5
    lon_start, lon_end = 66.5, 100.0
    
    lats = np.linspace(lat_start, lat_end, nlat)
    lons = np.linspace(lon_start, lon_end, nlon)
    
    try:
        data = np.fromfile(filepath, dtype=np.float32)
        ndays = len(data) // (nlat * nlon)
        
        if ndays == 0:
            logger.warning(f"Empty GRD file: {filepath}")
            return pd.DataFrame()
        
        data = data.reshape(ndays, nlat, nlon)
        
        # Extract year from filename
        year_match = re.search(r'(\d{4})', filepath.stem)
        year = int(year_match.group(1)) if year_match else 2020
        
        start_date = pd.Timestamp(f'{year}-01-01')
        dates = pd.date_range(start=start_date, periods=ndays, freq='D')
        
        records = []
        for d_idx, date in enumerate(dates):
            for lat_idx, lat in enumerate(lats):
                for lon_idx, lon in enumerate(lons):
                    val = data[d_idx, lat_idx, lon_idx]
                    if 0 <= val < 1000:  # Valid range
                        records.append({
                            'date': date.strftime('%Y-%m-%d'),
                            'lat': round(lat, 2),
                            'lon': round(lon, 2),
                            'rainfall': round(float(val), 2)
                        })
        
        return pd.DataFrame(records)
        
    except Exception as e:
        logger.error(f"Failed to convert GRD {filepath}: {e}")
        return pd.DataFrame()


def convert_all_rainfall() -> Dict:
    """Convert all rainfall files to CSV."""
    logger.info("Converting rainfall data...")
    
    result = {
        'files_processed': 0,
        'files_failed': 0,
        'total_records': 0,
        'output_dir': str(CONFIG.DATA_DIR / "rainfall_csv")
    }
    
    output_dir = CONFIG.DATA_DIR / "rainfall_csv"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if already converted
    existing_csvs = list(output_dir.glob('*.csv'))
    if len(existing_csvs) > 5:
        logger.info(f"Rainfall already converted: {len(existing_csvs)} files")
        result['files_processed'] = len(existing_csvs)
        result['skipped'] = True
        return result
    
    # Get raw files
    if not CONFIG.RAINFALL_RAW_DIR.exists():
        logger.warning("Rainfall raw directory not found")
        return result
    
    raw_files = [f for f in CONFIG.RAINFALL_RAW_DIR.glob('*') if f.is_file()]
    
    for filepath in tqdm(raw_files, desc="Converting rainfall"):
        try:
            file_format = detect_rainfall_format(filepath)
            
            if file_format == 'netcdf':
                df = convert_netcdf_rainfall(filepath)
            elif file_format == 'binary_grd':
                df = convert_grd_rainfall(filepath)
            elif file_format == 'csv':
                df = pd.read_csv(filepath)
            else:
                logger.warning(f"Unknown format: {filepath}")
                result['files_failed'] += 1
                continue
            
            if df.empty:
                result['files_failed'] += 1
                continue
            
            # Save CSV
            output_file = output_dir / f"{filepath.stem}.csv"
            df.to_csv(output_file, index=False)
            
            result['files_processed'] += 1
            result['total_records'] += len(df)
            
            # Free memory
            del df
            
        except Exception as e:
            logger.error(f"Failed to process {filepath}: {e}")
            result['files_failed'] += 1
    
    logger.info(f"Rainfall conversion complete: {result['files_processed']} files, {result['total_records']:,} records")
    
    return result


# =============================================================================
# TEMPERATURE PROCESSING
# =============================================================================

def process_temperature_data() -> Dict:
    """Process and merge temperature data."""
    logger.info("Processing temperature data...")
    
    result = {
        'tmax_files': 0,
        'tmin_files': 0,
        'total_records': 0,
        'output_file': str(CONFIG.DATA_DIR / "temperature_merged.csv")
    }
    
    output_file = CONFIG.DATA_DIR / "temperature_merged.csv"
    
    # Check if already processed
    if output_file.exists():
        df = pd.read_csv(output_file, nrows=5)
        if 'avg_temp' in df.columns:
            logger.info("Temperature already processed")
            result['skipped'] = True
            return result
    
    # Load tmax files
    tmax_dfs = []
    if CONFIG.TMAX_CSV_DIR.exists():
        tmax_files = list(CONFIG.TMAX_CSV_DIR.glob('*.csv'))
        for f in tqdm(tmax_files, desc="Loading tmax"):
            df = pd.read_csv(f)
            df = standardize_columns(df)
            tmax_dfs.append(df)
        result['tmax_files'] = len(tmax_files)
    
    # Load tmin files
    tmin_dfs = []
    if CONFIG.TMIN_CSV_DIR.exists():
        tmin_files = list(CONFIG.TMIN_CSV_DIR.glob('*.csv'))
        for f in tqdm(tmin_files, desc="Loading tmin"):
            df = pd.read_csv(f)
            df = standardize_columns(df)
            tmin_dfs.append(df)
        result['tmin_files'] = len(tmin_files)
    
    if not tmax_dfs and not tmin_dfs:
        logger.warning("No temperature data found")
        return result
    
    # Concatenate
    tmax_df = pd.concat(tmax_dfs, ignore_index=True) if tmax_dfs else pd.DataFrame()
    tmin_df = pd.concat(tmin_dfs, ignore_index=True) if tmin_dfs else pd.DataFrame()
    
    # Merge tmax and tmin
    if not tmax_df.empty and not tmin_df.empty:
        temp_df = pd.merge(
            tmax_df, tmin_df,
            on=['date', 'lat', 'lon'],
            how='outer',
            suffixes=('', '_min')
        )
        
        # Rename if needed
        if 'tmin_min' in temp_df.columns:
            temp_df = temp_df.rename(columns={'tmin_min': 'tmin'})
    elif not tmax_df.empty:
        temp_df = tmax_df
    else:
        temp_df = tmin_df
    
    # Compute average temperature
    if 'tmax' in temp_df.columns and 'tmin' in temp_df.columns:
        temp_df['avg_temp'] = (temp_df['tmax'] + temp_df['tmin']) / 2
    elif 'tmax' in temp_df.columns:
        temp_df['avg_temp'] = temp_df['tmax']
    elif 'tmin' in temp_df.columns:
        temp_df['avg_temp'] = temp_df['tmin']
    
    # Save
    temp_df.to_csv(output_file, index=False)
    result['total_records'] = len(temp_df)
    
    logger.info(f"Temperature processing complete: {result['total_records']:,} records")
    
    return result


# =============================================================================
# CROP CALENDAR EXTRACTION
# =============================================================================

def extract_crop_calendar() -> Dict:
    """Extract crop calendar from PDF."""
    logger.info("Processing crop calendar...")
    
    result = {
        'crops': 0,
        'records': 0,
        'output_file': str(CONFIG.DATA_DIR / "crop_calendar.csv")
    }
    
    output_file = CONFIG.DATA_DIR / "crop_calendar.csv"
    
    # Check if already extracted
    existing_csv = CONFIG.BASE_DIR / "crop_calendar.csv"
    if existing_csv.exists():
        df = pd.read_csv(existing_csv)
        if not df.empty:
            # Copy to data dir
            df.to_csv(output_file, index=False)
            result['crops'] = df['crop'].nunique() if 'crop' in df.columns else 0
            result['records'] = len(df)
            result['skipped'] = True
            logger.info(f"Crop calendar already extracted: {result['crops']} crops")
            return result
    
    # Try to extract from PDF
    if not CONFIG.CROP_CALENDAR_PDF.exists():
        logger.warning("Crop calendar PDF not found - creating default calendar")
        df = create_default_crop_calendar()
        df.to_csv(output_file, index=False)
        result['crops'] = df['crop'].nunique()
        result['records'] = len(df)
        return result
    
    # Use pdfplumber for extraction
    try:
        import pdfplumber
        
        records = []
        
        with pdfplumber.open(CONFIG.CROP_CALENDAR_PDF) as pdf:
            for page in tqdm(pdf.pages, desc="Extracting PDF"):
                tables = page.extract_tables()
                for table in tables:
                    if table and len(table) > 1:
                        records.extend(process_calendar_table(table))
        
        if records:
            df = pd.DataFrame(records)
            df = df.drop_duplicates()
            df.to_csv(output_file, index=False)
            result['crops'] = df['crop'].nunique()
            result['records'] = len(df)
        else:
            df = create_default_crop_calendar()
            df.to_csv(output_file, index=False)
            result['crops'] = df['crop'].nunique()
            result['records'] = len(df)
            
    except ImportError:
        logger.warning("pdfplumber not available - using default calendar")
        df = create_default_crop_calendar()
        df.to_csv(output_file, index=False)
        result['crops'] = df['crop'].nunique()
        result['records'] = len(df)
    
    logger.info(f"Crop calendar: {result['crops']} crops, {result['records']} records")
    
    return result


def process_calendar_table(table: List) -> List[Dict]:
    """Process a table from crop calendar PDF."""
    records = []
    
    month_map = {
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
        'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12,
        'january': 1, 'february': 2, 'march': 3, 'april': 4,
        'june': 6, 'july': 7, 'august': 8, 'september': 9,
        'october': 10, 'november': 11, 'december': 12
    }
    
    def parse_month(text):
        if not text:
            return None
        text = str(text).lower().strip()
        for name, num in month_map.items():
            if name in text:
                return num
        return None
    
    for row in table[1:]:  # Skip header
        if not row or len(row) < 2:
            continue
        
        crop = str(row[0]).strip() if row[0] else ''
        if not crop or len(crop) < 2:
            continue
        
        # Skip header-like rows
        if any(kw in crop.lower() for kw in ['crop', 'name', 'season', 'state']):
            continue
        
        sowing_start = parse_month(row[1] if len(row) > 1 else '')
        sowing_end = parse_month(row[2] if len(row) > 2 else '') or sowing_start
        harvest_start = parse_month(row[3] if len(row) > 3 else '')
        harvest_end = parse_month(row[4] if len(row) > 4 else '') or harvest_start
        
        if sowing_start:
            # Detect season
            if sowing_start in [6, 7, 8, 9]:
                season = 'Kharif'
            elif sowing_start in [10, 11, 12, 1]:
                season = 'Rabi'
            else:
                season = 'Zaid'
            
            records.append({
                'crop': crop.title(),
                'sowing_start_month': sowing_start,
                'sowing_end_month': sowing_end,
                'harvest_start_month': harvest_start,
                'harvest_end_month': harvest_end,
                'season_label': season
            })
    
    return records


def create_default_crop_calendar() -> pd.DataFrame:
    """Create default crop calendar for major Indian crops."""
    data = [
        # Kharif
        {'crop': 'Rice', 'sowing_start_month': 6, 'sowing_end_month': 7, 
         'harvest_start_month': 10, 'harvest_end_month': 11, 'season_label': 'Kharif'},
        {'crop': 'Maize', 'sowing_start_month': 6, 'sowing_end_month': 7,
         'harvest_start_month': 9, 'harvest_end_month': 10, 'season_label': 'Kharif'},
        {'crop': 'Jowar', 'sowing_start_month': 6, 'sowing_end_month': 7,
         'harvest_start_month': 10, 'harvest_end_month': 11, 'season_label': 'Kharif'},
        {'crop': 'Bajra', 'sowing_start_month': 6, 'sowing_end_month': 7,
         'harvest_start_month': 9, 'harvest_end_month': 10, 'season_label': 'Kharif'},
        {'crop': 'Tur', 'sowing_start_month': 6, 'sowing_end_month': 7,
         'harvest_start_month': 12, 'harvest_end_month': 2, 'season_label': 'Kharif'},
        {'crop': 'Moong', 'sowing_start_month': 7, 'sowing_end_month': 8,
         'harvest_start_month': 9, 'harvest_end_month': 10, 'season_label': 'Kharif'},
        {'crop': 'Urad', 'sowing_start_month': 7, 'sowing_end_month': 8,
         'harvest_start_month': 9, 'harvest_end_month': 10, 'season_label': 'Kharif'},
        {'crop': 'Groundnut', 'sowing_start_month': 6, 'sowing_end_month': 7,
         'harvest_start_month': 10, 'harvest_end_month': 11, 'season_label': 'Kharif'},
        {'crop': 'Soybean', 'sowing_start_month': 6, 'sowing_end_month': 7,
         'harvest_start_month': 10, 'harvest_end_month': 11, 'season_label': 'Kharif'},
        {'crop': 'Cotton', 'sowing_start_month': 5, 'sowing_end_month': 6,
         'harvest_start_month': 10, 'harvest_end_month': 12, 'season_label': 'Kharif'},
        {'crop': 'Sugarcane', 'sowing_start_month': 2, 'sowing_end_month': 3,
         'harvest_start_month': 12, 'harvest_end_month': 3, 'season_label': 'Kharif'},
        {'crop': 'Sesame', 'sowing_start_month': 6, 'sowing_end_month': 7,
         'harvest_start_month': 9, 'harvest_end_month': 10, 'season_label': 'Kharif'},
        
        # Rabi
        {'crop': 'Wheat', 'sowing_start_month': 10, 'sowing_end_month': 12,
         'harvest_start_month': 3, 'harvest_end_month': 4, 'season_label': 'Rabi'},
        {'crop': 'Gram', 'sowing_start_month': 10, 'sowing_end_month': 11,
         'harvest_start_month': 2, 'harvest_end_month': 3, 'season_label': 'Rabi'},
        {'crop': 'Barley', 'sowing_start_month': 10, 'sowing_end_month': 12,
         'harvest_start_month': 3, 'harvest_end_month': 4, 'season_label': 'Rabi'},
        {'crop': 'Mustard', 'sowing_start_month': 10, 'sowing_end_month': 11,
         'harvest_start_month': 2, 'harvest_end_month': 3, 'season_label': 'Rabi'},
        {'crop': 'Lentil', 'sowing_start_month': 10, 'sowing_end_month': 11,
         'harvest_start_month': 2, 'harvest_end_month': 3, 'season_label': 'Rabi'},
        {'crop': 'Peas', 'sowing_start_month': 10, 'sowing_end_month': 11,
         'harvest_start_month': 2, 'harvest_end_month': 3, 'season_label': 'Rabi'},
        {'crop': 'Potato', 'sowing_start_month': 10, 'sowing_end_month': 11,
         'harvest_start_month': 1, 'harvest_end_month': 3, 'season_label': 'Rabi'},
        {'crop': 'Sunflower', 'sowing_start_month': 11, 'sowing_end_month': 12,
         'harvest_start_month': 3, 'harvest_end_month': 4, 'season_label': 'Rabi'},
        
        # Rabi Rice
        {'crop': 'Rice', 'sowing_start_month': 11, 'sowing_end_month': 12,
         'harvest_start_month': 4, 'harvest_end_month': 5, 'season_label': 'Rabi'},
    ]
    
    return pd.DataFrame(data)


# =============================================================================
# MAIN CONVERSION
# =============================================================================

def run_format_conversion() -> Dict:
    """Run all format conversions."""
    logger.info("=" * 60)
    logger.info("PHASE B: FORMAT CONVERSION")
    logger.info("=" * 60)
    
    results = {}
    
    # Convert rainfall
    print("\n🌧️ Converting rainfall data...")
    results['rainfall'] = convert_all_rainfall()
    
    # Process temperature
    print("\n🌡️ Processing temperature data...")
    results['temperature'] = process_temperature_data()
    
    # Extract crop calendar
    print("\n📅 Extracting crop calendar...")
    results['crop_calendar'] = extract_crop_calendar()
    
    # Summary
    print("\n📊 Format Conversion Summary:")
    print("-" * 50)
    print(f"  Rainfall: {results['rainfall'].get('files_processed', 0)} files")
    print(f"  Temperature: {results['temperature'].get('total_records', 0):,} records")
    print(f"  Crop Calendar: {results['crop_calendar'].get('crops', 0)} crops")
    
    return results


if __name__ == "__main__":
    from utils import setup_logging
    setup_logging(CONFIG.LOGS_DIR)
    run_format_conversion()
