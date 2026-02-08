"""
Relative agronomic proxy constants derived from FAO-style references
for hackathon decision-support estimation.

These values are NOT field-measured absolutes. They represent relative
indices suitable for comparative crop ranking and resource-use estimation
at district-level aggregation. Do not use for precision agriculture or
regulatory reporting.

Sources (indicative):
    - FAO AQUASTAT crop water requirement guidelines
    - FAO fertilizer use statistics (regional aggregates)
    - ICAR crop production handbooks (general season lengths)

All values are unit-less relative indices unless noted otherwise.
"""

# ────────────────────────────────────────────────────────────────
# CROP_CONSTANTS
# ────────────────────────────────────────────────────────────────
#   crop_water_factor   : relative water demand index (0–1 scale,
#                         1 = highest demand e.g. paddy rice)
#   fertilizer_intensity: relative NPK application index (0–1)
#   season_length_days  : typical growing-season duration (days)
# ────────────────────────────────────────────────────────────────

CROP_CONSTANTS: dict = {
    "Rice": {
        "crop_water_factor": 1.00,
        "fertilizer_intensity": 0.75,
        "season_length_days": 120,
    },
    "Wheat": {
        "crop_water_factor": 0.55,
        "fertilizer_intensity": 0.70,
        "season_length_days": 135,
    },
    "Maize": {
        "crop_water_factor": 0.60,
        "fertilizer_intensity": 0.65,
        "season_length_days": 100,
    },
    "Sugarcane": {
        "crop_water_factor": 0.95,
        "fertilizer_intensity": 0.85,
        "season_length_days": 330,
    },
    "Cotton(Lint)": {
        "crop_water_factor": 0.70,
        "fertilizer_intensity": 0.60,
        "season_length_days": 160,
    },
    "Groundnut": {
        "crop_water_factor": 0.40,
        "fertilizer_intensity": 0.35,
        "season_length_days": 110,
    },
    "Soybean": {
        "crop_water_factor": 0.45,
        "fertilizer_intensity": 0.30,
        "season_length_days": 100,
    },
    "Arhar/Tur": {
        "crop_water_factor": 0.35,
        "fertilizer_intensity": 0.25,
        "season_length_days": 160,
    },
    "Gram": {
        "crop_water_factor": 0.30,
        "fertilizer_intensity": 0.25,
        "season_length_days": 105,
    },
    "Bajra": {
        "crop_water_factor": 0.30,
        "fertilizer_intensity": 0.30,
        "season_length_days": 85,
    },
}

# Fallback for crops not explicitly listed
DEFAULT_CONSTANTS: dict = {
    "crop_water_factor": 0.50,
    "fertilizer_intensity": 0.50,
    "season_length_days": 120,
}


def get_crop_constants(crop_name: str) -> dict:
    """
    Return the constant dictionary for a crop.
    Falls back to DEFAULT_CONSTANTS for unknown crops.
    """
    return CROP_CONSTANTS.get(crop_name, DEFAULT_CONSTANTS)
