# KrishiMind SustainAI - Data Dictionary

## Overview

This document describes all data sources, features, and transformations used in the KrishiMind SustainAI system.

---

## 1. Master Training Table

**File:** `data/output/master_training_table.csv`  
**Records:** 343,768  
**Purpose:** Primary dataset for yield model training

### Schema

| Column | Type | Description | Source |
|--------|------|-------------|--------|
| `id` | int | Unique record identifier | Generated |
| `year` | int | Crop year (1997-2020) | ICRISAT |
| `state_name` | str | State name | ICRISAT |
| `state_code` | str | State code | ICRISAT |
| `district_name` | str | District name | ICRISAT |
| `district_code` | str | District code | ICRISAT |
| `season` | str | Growing season (Kharif/Rabi/Summer/etc.) | ICRISAT |
| `crop_code` | str | Crop identifier | ICRISAT |
| `crop_name` | str | Crop name | ICRISAT |
| `crop_type` | str | Crop category | ICRISAT |
| `area` | float | Cultivated area (hectares) | ICRISAT |
| `area_unit` | str | Area unit (Hectare) | ICRISAT |
| `production` | float | Total production (tonnes) | ICRISAT |
| `production_unit` | str | Production unit (Tonnes) | ICRISAT |
| `yield` | float | Raw yield value | ICRISAT |
| `yield_unit` | str | Yield unit | ICRISAT |
| `yield_per_hectare` | float | **TARGET VARIABLE** - Yield (t/ha) | Calculated |
| `zn` | float | Soil Zinc content (mg/kg) | Soil Health Card |
| `fe` | float | Soil Iron content (mg/kg) | Soil Health Card |
| `cu` | float | Soil Copper content (mg/kg) | Soil Health Card |
| `mn` | float | Soil Manganese content (mg/kg) | Soil Health Card |
| `b` | float | Soil Boron content (mg/kg) | Soil Health Card |
| `s` | float | Soil Sulfur content (mg/kg) | Soil Health Card |
| `zn_adequate` | bool | Zinc adequacy flag | Calculated |
| `fe_adequate` | bool | Iron adequacy flag | Calculated |
| `cu_adequate` | bool | Copper adequacy flag | Calculated |
| `mn_adequate` | bool | Manganese adequacy flag | Calculated |
| `b_adequate` | bool | Boron adequacy flag | Calculated |
| `s_adequate` | bool | Sulfur adequacy flag | Calculated |
| `soil_quality_index` | float | Composite soil score (0-1) | Calculated |
| `seasonal_rainfall` | float | Total seasonal rainfall (mm) | IMD |
| `monsoon_rainfall` | float | June-Sept rainfall (mm) | IMD |
| `rainfall_anomaly` | float | Deviation from normal (-1 to +1) | Calculated |
| `growing_degree_days` | float | Accumulated thermal units | IMD |
| `heatwave_count` | int | Days exceeding heat threshold | IMD |
| `avg_temp` | float | Average temperature (°C) | IMD |

---

## 2. Rainfall Features

**File:** `data/cleaned_data/rainfall_features.csv`  
**Records:** 12,784  
**Purpose:** Rainfall aggregation by district-year-season

### Schema

| Column | Type | Description |
|--------|------|-------------|
| `district_name` | str | District name |
| `year` | int | Year |
| `season` | str | Season |
| `rainfall_mean` | float | Mean rainfall (mm) |
| `rainfall_std` | float | Rainfall standard deviation |
| `rainfall_min` | float | Minimum rainfall |
| `rainfall_max` | float | Maximum rainfall |
| `rainfall_sum` | float | Total rainfall |
| `monsoon_rainfall` | float | June-Sept total |
| `pre_monsoon_rainfall` | float | March-May total |
| `post_monsoon_rainfall` | float | Oct-Dec total |
| `rainfall_anomaly` | float | Deviation from 30-year normal |
| `drought_flag` | bool | Anomaly < -0.2 |

---

## 3. Temperature Features

**File:** `data/cleaned_data/temperature_features.csv`  
**Records:** 10,650  
**Purpose:** Temperature aggregation by district-year-season

### Schema

| Column | Type | Description |
|--------|------|-------------|
| `district_name` | str | District name |
| `year` | int | Year |
| `season` | str | Season |
| `avg_temp_mean` | float | Mean temperature (°C) |
| `avg_temp_std` | float | Temperature standard deviation |
| `tmax_mean` | float | Mean maximum temperature |
| `tmin_mean` | float | Mean minimum temperature |
| `growing_degree_days` | float | Sum of (Tavg - Tbase) for Tavg > Tbase |
| `heatwave_count` | int | Days with Tmax > 40°C |
| `cold_days` | int | Days with Tmin < 10°C |
| `diurnal_range` | float | Tmax - Tmin |

---

## 4. Soil Data

**File:** `data/cleaned_data/soil_cleaned.csv`  
**Records:** 673  
**Purpose:** District-level soil micronutrient data

### Schema

| Column | Type | Description |
|--------|------|-------------|
| `state_name` | str | State name |
| `district_name` | str | District name |
| `zn` | float | Zinc (mg/kg) |
| `fe` | float | Iron (mg/kg) |
| `cu` | float | Copper (mg/kg) |
| `mn` | float | Manganese (mg/kg) |
| `b` | float | Boron (mg/kg) |
| `s` | float | Sulfur (mg/kg) |
| `zn_adequate` | bool | Zn >= 0.6 |
| `fe_adequate` | bool | Fe >= 4.5 |
| `cu_adequate` | bool | Cu >= 0.2 |
| `mn_adequate` | bool | Mn >= 2.0 |
| `b_adequate` | bool | B >= 0.5 |
| `s_adequate` | bool | S >= 10.0 |
| `soil_quality_index` | float | Count of adequate nutrients / 6 |

---

## 5. Model Features

### Yield Model Features (8)

| Feature | Type | Range | Transformation |
|---------|------|-------|----------------|
| `rainfall_anomaly` | float | -1 to +1 | None |
| `monsoon_rainfall` | float | 0-2000 mm | None |
| `heatwave_count` | int | 0-100 | None |
| `growing_degree_days` | float | 0-50 | None |
| `soil_quality_index` | float | 0-1 | None |
| `season_encoded` | int | 0-5 | Label encoding |
| `crop_name_encoded` | int | 0-53 | Label encoding |
| `district_name_encoded` | int | 0-705 | Label encoding |

### Price Model Features (3)

| Feature | Type | Range | Transformation |
|---------|------|-------|----------------|
| `crop_encoded` | int | 0-6 | Label encoding |
| `district_encoded` | int | 0-4 | Label encoding |
| `month` | int | 1-12 | None |

---

## 6. Encoding Maps

### Season Encoding

| Value | Code |
|-------|------|
| Autumn | 0 |
| Kharif | 1 |
| Rabi | 2 |
| Summer | 3 |
| Whole Year | 4 |
| Winter | 5 |

### Top Crops (54 total)

Encoded 0-53 in alphabetical order:
- Arecanut, Arhar/Tur, Bajra, Banana, Barley, Black Pepper, ...
- Rice, Sugarcane, Wheat, ...

---

## 7. Data Quality Notes

### Missing Data Handling

| Field | Missing % | Imputation |
|-------|-----------|------------|
| `rainfall_anomaly` | 74% | Median by district |
| `monsoon_rainfall` | 74% | Median = 295.2 mm |
| `heatwave_count` | 74% | Median = 2 days |
| `growing_degree_days` | 74% | Median = 15.87 |
| `soil_quality_index` | 8% | Median = 0.833 |

### Known Limitations

1. **Geo Resolution**: All features aggregated at district level
2. **Temporal Coverage**: 1997-2020, may not capture recent climate shifts
3. **Crop Coverage**: 54 crops, may not include regional varieties
4. **Price Data**: Sparse mandi coverage, median fallback used

---

## 8. Data Sources

| Source | URL | License |
|--------|-----|---------|
| ICRISAT | http://data.icrisat.org/ | Open |
| IMD | https://www.imd.gov.in/ | Government |
| Soil Health Card | https://soilhealth.dac.gov.in/ | Government |
