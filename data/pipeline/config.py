#!/usr/bin/env python3
"""
Pipeline Configuration
======================
Central configuration for the agricultural data pipeline.
"""

from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import os

@dataclass
class PipelineConfig:
    """Central configuration for the pipeline."""
    
    # Base paths
    BASE_DIR: Path = Path("/Users/nishant/Downloads/new")
    
    # Input paths
    RAINFALL_RAW_DIR: Path = field(default_factory=lambda: Path("/Users/nishant/Downloads/new/imd_climate_data/rainfall"))
    TMAX_CSV_DIR: Path = field(default_factory=lambda: Path("/Users/nishant/Downloads/new/imd_climate_data/csv_tmax"))
    TMIN_CSV_DIR: Path = field(default_factory=lambda: Path("/Users/nishant/Downloads/new/imd_climate_data/csv_tmin"))
    CROP_YIELD_FILE: Path = field(default_factory=lambda: Path("/Users/nishant/Downloads/new/crop-wise-area-production-yield.csv"))
    SOIL_FILE: Path = field(default_factory=lambda: Path("/Users/nishant/Downloads/new/soil.csv"))
    MANDI_FILE: Path = field(default_factory=lambda: Path("/Users/nishant/Downloads/new/mandi_prices_full.csv"))
    CROP_CALENDAR_PDF: Path = field(default_factory=lambda: Path("/Users/nishant/Downloads/new/New_Crop_Calendar_20.09.18.pdf"))
    DISTRICT_LATLON_FILE: Path = field(default_factory=lambda: Path("/Users/nishant/Downloads/new/district_lat_lon.csv"))
    HUMIDITY_FILE: Path = field(default_factory=lambda: Path("/Users/nishant/Downloads/new/humadity.csv"))
    
    # Output paths
    DATA_DIR: Path = field(default_factory=lambda: Path("/Users/nishant/Downloads/new/data"))
    LOGS_DIR: Path = field(default_factory=lambda: Path("/Users/nishant/Downloads/new/logs"))
    EDA_DIR: Path = field(default_factory=lambda: Path("/Users/nishant/Downloads/new/eda_reports"))
    TEMP_DIR: Path = field(default_factory=lambda: Path("/Users/nishant/Downloads/new/.pipeline_temp"))
    
    # Processing parameters
    CHUNK_SIZE: int = 100000
    MAX_MISSING_PCT: float = 0.40
    HEATWAVE_THRESHOLD: float = 40.0
    MAX_TEMP_VALID: float = 60.0
    MIN_TEMP_VALID: float = -50.0
    IQR_MULTIPLIER: float = 1.5
    GDD_BASE_TEMP: float = 10.0
    
    # Season definitions (India)
    MONSOON_MONTHS: List[int] = field(default_factory=lambda: [6, 7, 8, 9])
    KHARIF_MONTHS: List[int] = field(default_factory=lambda: [6, 7, 8, 9, 10])
    RABI_MONTHS: List[int] = field(default_factory=lambda: [11, 12, 1, 2, 3, 4])
    
    # API endpoints for auto-fetch
    NASA_POWER_API: str = "https://power.larc.nasa.gov/api/temporal/daily/point"
    DATA_GOV_IN_API: str = "https://api.data.gov.in/resource"
    
    # State checkpoint file for resume
    CHECKPOINT_FILE: Path = field(default_factory=lambda: Path("/Users/nishant/Downloads/new/.pipeline_temp/checkpoint.json"))
    
    def __post_init__(self):
        """Create directories if they don't exist."""
        for dir_path in [self.DATA_DIR, self.LOGS_DIR, self.EDA_DIR, self.TEMP_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)


# Required datasets and their expected schemas
REQUIRED_DATASETS = {
    'yield': {
        'required_columns': ['year', 'district_name', 'crop_name', 'area', 'production'],
        'optional_columns': ['yield', 'state_name', 'season'],
        'key_columns': ['year', 'district_name', 'crop_name'],
    },
    'soil': {
        'required_columns': ['district'],
        'optional_columns': ['zn', 'fe', 'cu', 'mn', 'b', 's', 'ph'],
        'key_columns': ['district'],
    },
    'rainfall': {
        'required_columns': ['date', 'lat', 'lon', 'rainfall'],
        'optional_columns': [],
        'key_columns': ['date', 'lat', 'lon'],
    },
    'temperature': {
        'required_columns': ['date', 'lat', 'lon'],
        'optional_columns': ['tmax', 'tmin', 'avg_temp'],
        'key_columns': ['date', 'lat', 'lon'],
    },
    'price': {
        'required_columns': ['district', 'commodity'],
        'optional_columns': ['date', 'modal_price', 'min_price', 'max_price'],
        'key_columns': ['district', 'date', 'commodity'],
    },
    'district_coords': {
        'required_columns': ['district'],
        'optional_columns': ['lat', 'lon', 'state'],
        'key_columns': ['district'],
    },
    'crop_calendar': {
        'required_columns': ['crop', 'sowing_start_month'],
        'optional_columns': ['sowing_end_month', 'harvest_start_month', 'harvest_end_month', 'season_label'],
        'key_columns': ['crop'],
    },
}

# Standard column name mappings
COLUMN_MAPPINGS = {
    # District variations
    'district': ['district', 'district_name', 'distname', 'dist_name', 'district name'],
    'state': ['state', 'state_name', 'statename', 'state name'],
    'crop': ['crop', 'crop_name', 'cropname', 'commodity', 'crop name'],
    'year': ['year', 'yr', 'crop_year'],
    'date': ['date', 'arrival_date', 'price_date', 'reported_date'],
    'lat': ['lat', 'latitude', 'lat_centroid'],
    'lon': ['lon', 'longitude', 'lng', 'long', 'lon_centroid'],
}

# Global config instance
CONFIG = PipelineConfig()
