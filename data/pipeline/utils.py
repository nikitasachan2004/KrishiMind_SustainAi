#!/usr/bin/env python3
"""
Pipeline Utilities
==================
Shared utility functions for the agricultural data pipeline.
"""

import os
import re
import sys
import json
import logging
import hashlib
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from functools import wraps
import time

import numpy as np
import pandas as pd
from tqdm import tqdm


# =============================================================================
# LOGGING SETUP
# =============================================================================

def setup_logging(log_dir: Path, log_file: str = "pipeline.log") -> logging.Logger:
    """Configure logging with file and console handlers."""
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / log_file
    
    # Clear existing handlers
    logging.getLogger().handlers = []
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(module)-20s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File handler
    file_handler = logging.FileHandler(log_path, mode='a')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


# =============================================================================
# CHECKPOINT / RESUME SYSTEM
# =============================================================================

class CheckpointManager:
    """Manage pipeline checkpoints for resume capability."""
    
    def __init__(self, checkpoint_file: Path):
        self.checkpoint_file = checkpoint_file
        self.checkpoint_file.parent.mkdir(parents=True, exist_ok=True)
        self.state = self._load_state()
    
    def _load_state(self) -> Dict:
        """Load checkpoint state from file."""
        if self.checkpoint_file.exists():
            try:
                with open(self.checkpoint_file, 'r') as f:
                    return json.load(f)
            except:
                return {'completed_phases': [], 'phase_data': {}}
        return {'completed_phases': [], 'phase_data': {}}
    
    def _save_state(self):
        """Save checkpoint state to file."""
        with open(self.checkpoint_file, 'w') as f:
            json.dump(self.state, f, indent=2, default=str)
    
    def is_phase_complete(self, phase: str) -> bool:
        """Check if a phase has been completed."""
        return phase in self.state['completed_phases']
    
    def mark_phase_complete(self, phase: str, data: Optional[Dict] = None):
        """Mark a phase as complete."""
        if phase not in self.state['completed_phases']:
            self.state['completed_phases'].append(phase)
        if data:
            self.state['phase_data'][phase] = data
        self.state['last_updated'] = datetime.now().isoformat()
        self._save_state()
    
    def get_phase_data(self, phase: str) -> Optional[Dict]:
        """Get data saved for a phase."""
        return self.state['phase_data'].get(phase)
    
    def reset(self):
        """Reset all checkpoints."""
        self.state = {'completed_phases': [], 'phase_data': {}}
        self._save_state()


# =============================================================================
# RETRY DECORATOR
# =============================================================================

def retry_with_backoff(max_retries: int = 3, backoff_factor: float = 2.0):
    """Decorator for retrying functions with exponential backoff."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    wait_time = backoff_factor ** attempt
                    logging.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
            raise last_exception
        return wrapper
    return decorator


# =============================================================================
# STRING UTILITIES
# =============================================================================

def to_snake_case(name: str) -> str:
    """Convert string to snake_case."""
    if not name or pd.isna(name):
        return ''
    name = str(name).strip()
    name = re.sub(r'[^\w\s]', '', name)
    name = re.sub(r'\s+', '_', name)
    name = re.sub(r'([a-z])([A-Z])', r'\1_\2', name)
    return name.lower().strip('_')


def normalize_string(s: str) -> str:
    """Normalize string: strip, lowercase, remove extra spaces."""
    if not s or pd.isna(s):
        return ''
    return ' '.join(str(s).strip().lower().split())


def normalize_district_name(name: str) -> str:
    """Normalize district names for matching."""
    if not name or pd.isna(name):
        return ''
    
    name = str(name).strip().title()
    
    # Common replacements
    replacements = {
        'And': '&',
        ' & ': ' And ',
        'Dist.': '',
        'District': '',
        '(': '',
        ')': '',
    }
    
    for old, new in replacements.items():
        name = name.replace(old, new)
    
    return ' '.join(name.split()).strip()


def normalize_crop_name(name: str) -> str:
    """Normalize crop names for matching."""
    if not name or pd.isna(name):
        return ''
    
    name = str(name).strip().title()
    
    # Standard mappings
    mappings = {
        'Paddy': 'Rice',
        'Ground Nut': 'Groundnut',
        'Soya Bean': 'Soybean',
        'Soyabean': 'Soybean',
        'Arhar': 'Tur',
        'Pigeon Pea': 'Tur',
        'Red Gram': 'Tur',
        'Bengal Gram': 'Gram',
        'Chickpea': 'Gram',
        'Black Gram': 'Urad',
        'Green Gram': 'Moong',
        'Pearl Millet': 'Bajra',
        'Sorghum': 'Jowar',
        'Finger Millet': 'Ragi',
        'Sesamum': 'Sesame',
        'Rape': 'Mustard',
        'Rapeseed': 'Mustard',
    }
    
    for old, new in mappings.items():
        if old.lower() in name.lower():
            name = new
            break
    
    return name


# =============================================================================
# DATE UTILITIES
# =============================================================================

def parse_date(date_val: Any) -> Optional[str]:
    """Parse various date formats to ISO format."""
    if pd.isna(date_val):
        return None
    
    date_str = str(date_val).strip()
    
    # Common formats to try
    formats = [
        '%Y-%m-%d',
        '%d-%m-%Y',
        '%d/%m/%Y',
        '%Y/%m/%d',
        '%d-%b-%Y',
        '%d %b %Y',
        '%Y%m%d',
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime('%Y-%m-%d')
        except:
            continue
    
    # Try pandas
    try:
        dt = pd.to_datetime(date_val)
        return dt.strftime('%Y-%m-%d')
    except:
        return None


def parse_year(year_val: Any) -> Optional[int]:
    """Parse year from various formats."""
    if pd.isna(year_val):
        return None
    
    year_str = str(year_val).strip()
    
    # Handle '1998-99' format
    match = re.match(r'(\d{4})-\d{2}', year_str)
    if match:
        return int(match.group(1))
    
    # Handle plain year
    match = re.match(r'^(\d{4})$', year_str)
    if match:
        return int(match.group(1))
    
    return None


# =============================================================================
# DATA UTILITIES
# =============================================================================

def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize DataFrame column names."""
    df = df.copy()
    df.columns = [to_snake_case(str(col)) for col in df.columns]
    return df


def find_column(df: pd.DataFrame, possible_names: List[str]) -> Optional[str]:
    """Find a column by checking multiple possible names."""
    df_cols_lower = {col.lower(): col for col in df.columns}
    
    for name in possible_names:
        name_lower = name.lower()
        if name_lower in df_cols_lower:
            return df_cols_lower[name_lower]
        
        # Partial match
        for col_lower, col_orig in df_cols_lower.items():
            if name_lower in col_lower or col_lower in name_lower:
                return col_orig
    
    return None


def detect_file_encoding(filepath: Path) -> str:
    """Detect file encoding."""
    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    
    for encoding in encodings:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                f.read(10000)
            return encoding
        except:
            continue
    
    return 'utf-8'


def read_csv_safe(filepath: Path, **kwargs) -> pd.DataFrame:
    """Safely read CSV with encoding detection."""
    encoding = detect_file_encoding(filepath)
    
    try:
        return pd.read_csv(filepath, encoding=encoding, **kwargs)
    except Exception as e:
        logging.warning(f"Failed to read {filepath}: {e}")
        return pd.DataFrame()


def chunk_dataframe(df: pd.DataFrame, chunk_size: int = 100000):
    """Yield DataFrame in chunks."""
    for i in range(0, len(df), chunk_size):
        yield df.iloc[i:i + chunk_size]


def optimize_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """Optimize DataFrame memory usage."""
    df = df.copy()
    
    for col in df.columns:
        col_type = df[col].dtype
        
        if col_type == 'object':
            if df[col].nunique() / len(df) < 0.5:
                df[col] = df[col].astype('category')
        elif col_type in ['int64', 'int32']:
            df[col] = pd.to_numeric(df[col], downcast='integer')
        elif col_type in ['float64', 'float32']:
            df[col] = pd.to_numeric(df[col], downcast='float')
    
    return df


# =============================================================================
# API UTILITIES
# =============================================================================

@retry_with_backoff(max_retries=3)
def fetch_url(url: str, params: Optional[Dict] = None, 
              timeout: int = 60) -> requests.Response:
    """Fetch URL with retry logic."""
    headers = {
        'User-Agent': 'AgriPipeline/1.0 (Agricultural Data Pipeline)',
    }
    
    response = requests.get(url, params=params, headers=headers, timeout=timeout)
    response.raise_for_status()
    return response


def download_file(url: str, output_path: Path, 
                  desc: str = "Downloading") -> bool:
    """Download file with progress bar."""
    try:
        response = requests.get(url, stream=True, timeout=120)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        with open(output_path, 'wb') as f:
            with tqdm(total=total_size, unit='B', unit_scale=True, desc=desc) as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))
        
        return True
    except Exception as e:
        logging.error(f"Download failed: {e}")
        return False


# =============================================================================
# FILE UTILITIES
# =============================================================================

def get_file_hash(filepath: Path) -> str:
    """Calculate MD5 hash of file."""
    if not filepath.exists():
        return ''
    
    hash_md5 = hashlib.md5()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_md5.update(chunk)
    
    return hash_md5.hexdigest()


def get_file_info(filepath: Path) -> Dict:
    """Get file information."""
    if not filepath.exists():
        return {'exists': False}
    
    stat = filepath.stat()
    return {
        'exists': True,
        'size_mb': stat.st_size / (1024 * 1024),
        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
        'extension': filepath.suffix.lower(),
    }


def clean_temp_files(temp_dir: Path):
    """Clean temporary files."""
    if temp_dir.exists():
        import shutil
        shutil.rmtree(temp_dir)
        logging.info(f"Cleaned temp directory: {temp_dir}")


# =============================================================================
# PROGRESS UTILITIES
# =============================================================================

def print_phase_header(phase_name: str, phase_num: str):
    """Print formatted phase header."""
    print("\n" + "=" * 70)
    print(f"PHASE {phase_num}: {phase_name}")
    print("=" * 70)


def print_summary_box(title: str, items: Dict[str, Any]):
    """Print formatted summary box."""
    print("\n" + "-" * 50)
    print(f"  {title}")
    print("-" * 50)
    for key, value in items.items():
        print(f"  {key}: {value}")
    print("-" * 50)
