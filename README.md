# KrishiMind SustainAI - Sustainable Crop & Resource Optimization Engine

🌾 **AI-powered agricultural advisory system** that reduces water consumption, fertilizer load, and climate risk through predictive crop planning and scenario-based resource optimization.

> **District-level crop recommendations**, yield predictions, revenue optimization, sustainability impact scoring, and plant disease detection under various climate scenarios.

**Built for AMD Slingshot Hackathon** — **Sustainable AI & Green Tech** domain.

---

## 📑 Table of Contents

- [Quick Start](#quick-start)
- [Sustainable AI Positioning](#sustainable-ai-positioning)
- [Problem Statement](#problem-statement)
- [Solution Architecture](#solution-architecture)
- [System Components](#system-components)
- [Key Features](#key-features)
- [Sustainability Impact Outputs](#sustainability-impact-outputs)
- [Sustainability Engine Description](#sustainability-engine-description)
- [Datasets & Data Pipeline](#datasets--data-pipeline)
- [Feature Engineering](#feature-engineering)
- [Machine Learning Models](#machine-learning-models)
- [Model Performance Metrics](#model-performance-metrics)
- [Plant Disease Detection](#plant-disease-detection)
- [API Endpoints & Schemas](#api-endpoints--schemas)
- [How To Run Locally](#how-to-run-locally)
- [Docker Deployment](#docker-deployment)
- [Cloud Deployment (AWS)](#cloud-deployment-aws)
- [Example API Request / Response](#example-api-request--response)
- [Frontend Applications](#frontend-applications)
- [Project Structure](#project-structure)
- [Dependencies](#dependencies)
- [Risk and Assumption Disclosures](#risk-and-assumption-disclosures)
- [Technical Disclosures](#technical-disclosures)
- [License](#license)
- [Authors & Contributors](#authors--contributors)
- [Acknowledgments](#acknowledgments)

---

## Quick Start

Get up and running in **3 commands** (no GPU, no cloud account required):

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the API server
uvicorn cloud.api.app:app --host 0.0.0.0 --port 8000

# 3. Run tests (in another terminal)
python scripts/final_test_matrix.py
```

**Then:**
- Open API docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Open health check: [http://localhost:8000/health](http://localhost:8000/health)
- Run Streamlit frontend:
```bash
streamlit run frontend_app.py
```

**Optional - generate demo outputs:**
```bash
python scripts/generate_demo_outputs.py
```

---

## Sustainable AI Positioning

KrishiMind SustainAI is a **Sustainable AI** system designed for the AMD Slingshot Hackathon - **Sustainable AI & Green Tech** domain.

| Sustainability Criteria | How KrishiMind Addresses It |
|------------------------|----------------------------|
| **Water reduction** | Quantifies proxy water savings vs highest-demand crop for every recommendation |
| **Fertilizer reduction** | Ranks crops by fertilizer-intensity proxy adjusted for soil quality |
| **Carbon proxy** | Produces per-crop carbon-equivalent footprint estimate |
| **Climate resilience** | Scenario simulator evaluates drought, heat-stress, and combined shocks |
| **Resource-efficient AI** | CPU-only tree models; no GPU, no cloud, no accelerator required |
| **Edge-deployable** | Entire inference pipeline runs in < 256 MB RAM on commodity hardware |
| **Transparent metrics** | All proxy formulae disclosed; disclaimers auto-included in every response |

Every API response includes sustainability metrics - water saved, fertilizer proxy, carbon proxy, risk reduction, and a composite sustainability score - enabling data-driven crop selection that reduces resource consumption.

---

---

## Solution Architecture

```
User Request (district, season, area, scenario)
       |
       v
┌─────────────────────────────────────────┐
│   FastAPI REST API Layer                │
│   /predict/crop-plan  (POST)            │
│   /health             (GET)             │
│   /model/info         (GET)             │
└────────────┬────────────────────────────┘
             |
             v
┌─────────────────────────────────────────┐
│   Model Loader (Singleton Pattern)      │
│   - Yield Model (RandomForest)          │
│   - Price Model (RandomForest)          │
│   - Feature Configs (JSON)              │
└────────────┬────────────────────────────┘
             |
       ┌─────┴──────┐
       v            v
┌──────────────┐  ┌──────────────┐
│ Yield Model  │  │ Price Model  │
│ Prediction   │  │ Prediction   │
└──────┬───────┘  └───────┬──────┘
       |                  |
       └──────┬───────────┘
              v
┌─────────────────────────────────────────┐
│   Crop Optimizer                        │
│   - Multi-criteria Scoring              │
│   - Weighted Ranking (yield, revenue,   │
│     climate stability, soil match)      │
└────────────┬────────────────────────────┘
             |
             v
┌─────────────────────────────────────────┐
│   Sustainability Impact Engine          │
│   - Water use proxy estimation          │
│   - Fertilizer load calculation         │
│   - Carbon footprint scoring            │
│   - Climate risk reduction assessment   │
└────────────┬────────────────────────────┘
             |
             v
┌─────────────────────────────────────────┐
│   Plant Disease Detection (Optional)    │
│   - EfficientNetB0 Transfer Learning    │
│   - 28 disease classes                  │
│   - Confidence scoring                  │
└────────────┬────────────────────────────┘
             |
             v
JSON Response with Rankings + Sustainability Metrics
```

---

## System Components

### 1. **Data Pipeline** (`data/pipeline/`)

**Purpose:** End-to-end ingestion, validation, and preprocessing of 6+ data sources.

**Phases:**
- **Phase A (Audit)**: Scan data sources, detect schemas, identify gaps
- **Phase B (Conversion)**: Convert formats (NetCDF → CSV, etc.)
- **Phase C (Standardization)**: Normalize column names, units
- **Phase D (Cleaning)**: Remove outliers, handle missing values
- **Phase E (Geo)**: Merge geographic features (lat/lon, district codes)
- **Phase F (Features)**: Engineer climate, soil, and temporal features

**Key Files:**
```
data/pipeline/
├── config.py              # Central pipeline configuration
├── phase_a_audit.py       # Data source detection
├── phase_b_conversion.py  # Format conversion
├── phase_c_standardization.py
├── phase_d_cleaning.py
├── phase_e_geo.py
├── phase_f_features.py
└── utils.py
```

### 2. **Core ML Modules** (`src/`)

| Module | Purpose | Key Class |
|--------|---------|-----------|
| `data_loader.py` | Load training/inference data | `DataLoader` |
| `feature_builder.py` | Construct ML features | `FeatureBuilder` |
| `train_yield_model.py` | Train yield prediction model | — |
| `train_price_model.py` | Train price prediction model | — |
| `crop_optimizer.py` | Multi-criteria crop ranking | `CropOptimizer` |
| `revenue_engine.py` | Revenue calculation | `RevenueEngine` |
| `scenario_simulator.py` | What-if climate scenarios | `ScenarioSimulator` |
| `evaluate_models.py` | Model evaluation metrics | — |
| `sustainability_report_generator.py` | Generate sustainability reports | `SustainabilityReportGenerator` |

### 3. **Sustainability Engine** (`src/sustainability/`)

**Purpose:** Deterministic, lightweight proxy estimation for resource efficiency metrics.

| Component | Role |
|-----------|------|
| `crop_constants.py` | FAO-style agronomic proxy indices (10 major crops) |
| `impact_engine.py` | `SustainabilityImpactEngine` — computes water, fertilizer, carbon proxies |

**Compute Overhead:** < 0.01 ms per crop (pure arithmetic, no ML).

### 4. **FastAPI Application** (`cloud/api/`)

**Purpose:** Production-ready REST API with request validation and model loading.

| File | Role |
|------|------|
| `app.py` | FastAPI application with lifecycle management |
| `model_loader.py` | Singleton model loader with validation |
| `predict.py` | Prediction orchestration logic |
| `schemas.py` | Pydantic request/response validation models |

**Endpoints:**
- `POST /predict/crop-plan` — Get crop recommendations
- `GET /health` — Health check with model status
- `GET /model/info` — Model metadata
- `GET /docs` — OpenAPI documentation (Swagger UI)
- `GET /redoc` — ReDoc API documentation

### 5. **Plant Disease Detection** (`src/plant_disease_detection/`)

**Purpose:** Deep learning-based disease classification from plant leaf images.

| Component | Details |
|-----------|---------|
| Model | EfficientNetB0 (transfer learning) |
| Dataset | PlantDoc (~1000 training images) |
| Classes | 28 plant diseases |
| Accuracy | 80.65% (test set with TTA) |
| Framework | PyTorch + Torchvision |

**Key Files:**
```
src/plant_disease_detection/
├── train.py               # Model training pipeline
├── inference/
│   └── predict.py         # Inference logic
├── models/                # Pre-trained weights
└── utils/                 # Data utilities
```

### 6. **Frontend Applications**

#### **Streamlit App** (`frontend_app.py`)

- Interactive UI for crop planning
- Real-time API requests
- Sustainability metrics visualization
- Disease detection image upload
- Scenario simulation controls

#### **Next.js React App** (`frontend/`)

- Modern React 19 with TypeScript
- Tailwind CSS responsive design
- Component-based architecture
- Fast development with Next.js 15
- Framer Motion animations

---

## Key Features

| Feature | Description | Benefit |
|---------|-------------|---------|
| **Yield Prediction** | RandomForest ML model with 8 climate-soil features | Accurate production forecasting |
| **Price Forecasting** | District-level mandi price aggregation | Revenue estimation |
| **Multi-Criteria Optimization** | Weighted scoring (yield × price × climate stability × soil match) | Balanced decision-making |
| **Climate Scenarios** | What-if analysis for drought, heatwave, combined stress | Risk assessment |
| **Sustainability Scoring** | Proxy water/fertilizer/carbon metrics per crop | Resource efficiency comparison |
| **Plant Disease Detection** | EfficientNetB0 deep learning classification | Early intervention |
| **CPU-Efficient Inference** | Tree models on commodity hardware | No GPU required |
| **Edge-Deployable** | < 10 MB models, < 256 MB runtime RAM | On-device inference possible |
| **District-Level Aggregation** | 706+ districts across India | Regional coverage |
| **54+ Crops Supported** | Major crops: Rice, Wheat, Maize, Sugarcane, Cotton, etc. | Crop diversity |
| **Stateless API** | No session state, no database dependency | Horizontal scaling |
| **Full Transparency** | All proxy formulae disclosed in docs | Explainable AI |

---

## Problem Statement

Agricultural systems face compounding resource inefficiencies:

- **Water waste** - high irrigation-demand crops planted in water-scarce districts without quantitative comparison of alternatives
- **Fertilizer overuse** - blanket application rates ignore soil quality variation, increasing cost and environmental load
- **Climate exposure** - farmers lack scenario-based tools to evaluate crop resilience before committing to a season
- **Suboptimal crop selection** - decisions based on tradition rather than multi-criteria optimisation across yield, price, climate stability, and resource efficiency

These inefficiencies result in avoidable water consumption, excess chemical inputs, higher carbon-equivalent emissions, and economic losses during adverse weather.

---

## Solution

**KrishiMind SustainAI** provides:

1. **Yield Prediction** - ML models trained on historical crop data, climate features, and soil quality
2. **Price Forecasting** - District-level mandi price aggregation for revenue estimation
3. **Crop Optimization** - Multi-criteria scoring (yield x price x climate stability x soil match)
4. **Scenario Simulation** - What-if analysis for drought, warming, and combined stress conditions
5. **Sustainability Impact Scoring** - Proxy water, fertilizer, and carbon metrics for every recommendation

| Feature | Description |
|---------|-------------|
| Yield Model | RandomForest with 8 climate-soil features |
| Price Model | RandomForest on mandi aggregated data |
| Optimizer | Weighted composite scoring algorithm |
| Simulator | Predefined climate scenarios (rainfall, temperature) |
| Sustainability Engine | Proxy water/fertilizer/carbon scoring per crop |

---

## Sustainability Impact Outputs

Every API response includes per-crop sustainability metrics:

| Metric | Description |
|--------|-------------|
| `water_use_estimate` | Proxy water consumption (index-hectare-days) |
| `water_saved_vs_baseline` | % water saved vs highest-demand crop (Rice) |
| `fertilizer_proxy` | Fertilizer load index (0-1, lower = better) |
| `carbon_proxy` | Carbon footprint proxy (index-hectare units) |
| `risk_reduction_pct` | Climate risk reduction vs baseline yield |
| `sustainability_score` | Weighted composite sustainability score (0-1) |

The sustainability report (`reports/sustainability_report.json`) also auto-exports aggregate metrics:

| Output | Description |
|--------|-------------|
| `avg_water_saved_vs_baseline_pct` | Average water saved across recommended crops |
| `avg_carbon_proxy_avoided` | Average carbon proxy footprint |
| `low_input_crop_pct` | Percentage of low-input crops in recommendations |
| `avg_climate_risk_reduction_pct` | Average climate risk reduction |

---

## Sustainability Engine Description

The **SustainabilityImpactEngine** (`src/sustainability/`) enriches every crop recommendation with resource-efficiency metrics. It uses **no ML** - all computations are deterministic, based on FAO-style agronomic constants.

```
src/sustainability/
    __init__.py
    crop_constants.py   # FAO-style proxy indices for 10 major crops
    impact_engine.py    # SustainabilityImpactEngine class
```

| Formula | Expression |
|---------|------------|
| Water use | `crop_water_factor x area x season_length_days x 5` |
| Fertilizer proxy | `fertilizer_intensity x (1 - soil_quality_index)` |
| Carbon proxy | `fertilizer_score x area x 12` |
| Sustainability score | Weighted normalised combination of: water efficiency, fertilizer efficiency, climate stability, soil match |

**Constants** cover 10 major crops: Rice, Wheat, Maize, Sugarcane, Cotton, Groundnut, Soybean, Arhar/Tur, Gram, Bajra.

Total compute overhead per crop: **< 0.01 ms** (pure arithmetic, no ML invocation).

---

## Proxy Metric Disclosure

> **Sustainability metrics are proxy estimates derived from agronomic literature constants and soil indices. They are decision-support indicators, not field-measured values.**

- All constants are relative agronomic proxy indices derived from FAO-style reference literature
- These are unit-less comparative indices - not absolute physical measurements
- The `proxy_metrics: true` flag is auto-included in every API response
- The `sustainability_disclosure` text is auto-included in every response

---

## District Aggregation Disclosure

> **All predictions and sustainability scores operate at district-level granularity. No field-level, GPS-based, or grid-level geo precision is claimed.**

Outputs are suitable for regional planning and comparative crop ranking, not for individual farm prescriptions.

---

## No Retraining Statement

> **No model retraining, fine-tuning, or online learning occurs during deployment.**

Models are inference-only artifacts (`models/yield_model.pkl`, `models/price_model.pkl`). They are loaded once at startup. The sustainability scoring layer is entirely deterministic and uses no ML.

---

## No Synthetic Training Statement

> **All ML models were trained on real, publicly available datasets.**

Sources: ICRISAT crop statistics, IMD climate records, Soil Health Card data. No synthetic data was generated for model training. Where mandi price coverage is sparse, median-by-crop fallback from real data is applied.

---

## Datasets & Data Pipeline

### Data Sources

All models trained on **real, publicly available Indian agricultural datasets**:

| Dataset | Source | Records | Coverage | Purpose |
|---------|--------|---------|----------|---------|
| **Master Training Table** | ICRISAT + IMD + Soil Health Card | 343,768 | 54 crops, 706 districts, 1997-2020 | Yield model training |
| **Rainfall Features** | India Meteorological Department (IMD) | 12,784 | District-day level | Climate features |
| **Temperature Features** | IMD | 10,650 | District-day level (Tmax, Tmin) | Thermal indices |
| **Soil Data** | Soil Health Card Portal | 673 | 10 districts with micronutrients | Soil quality scoring |
| **Mandi Prices** | AGMARKNET (Agricultural Market) | Sparse | 54 commodities, district markets | Price prediction |
| **Crop Calendar** | ICAR (Indian Council of Agricultural Research) | 54 crops | Sowing/harvest windows | Seasonal alignment |
| **District Coordinates** | Government of India | 706 districts | Lat/lon centroids | Geospatial joining |

### Master Training Table Schema

**File:** `data/output/master_training_table.csv` (343,768 rows × 40 columns)

| Column Category | Examples | Type |
|-----------------|----------|------|
| **Identifiers** | id, year, state_name, district_name, crop_name | int, str |
| **Production Data** | area, production, yield_per_hectare (target) | float |
| **Soil Nutrients** | zn, fe, cu, mn, b, s, soil_quality_index | float, bool |
| **Climate Features** | rainfall_anomaly, monsoon_rainfall, heatwave_count, growing_degree_days | float, int |
| **Derived Features** | season_encoded, crop_name_encoded, district_name_encoded | categorical |

### Data Cleaning & Validation

**Missing Value Strategy:**
- Impute with district-level median
- Exclude records if > 40% missing
- Fallback to state-level aggregation

**Outlier Detection:**
- Cap continuous variables at 1st and 99th percentiles
- Flag anomalous yield values (> 100 t/ha or < 0)

**Quality Checks:**
- Schema validation via Pydantic
- Temporal continuity checks
- Geographic coverage validation

### Data Output Files

```
data/
├── cleaned_data/
│   ├── crop_yield_cleaned.csv          # Cleaned yield data
│   ├── rainfall_features.csv           # Seasonal rainfall aggregates
│   ├── temperature_features.csv        # Temperature-derived features
│   ├── temperature_seasonal_agg.csv    # Seasonal temp aggregates
│   └── soil_cleaned.csv                # Cleaned soil nutrient data
├── output/
│   └── master_training_table.csv       # Final training table
└── eda_reports/
    ├── data_profile.csv                # Data profiling summary
    ├── missingness_report.csv          # Missing value analysis
    └── summary_statistics.csv          # Statistical summary
```

---

All models trained on **real, publicly available Indian agricultural datasets**:

| Dataset | Source | Records | Description |
|---------|--------|---------|-------------|
| Master Training Table | ICRISAT + IMD | 343,768 | Crop yield with climate features |
| Rainfall Features | IMD | 12,784 | District-level seasonal rainfall |
| Temperature Features | IMD | 10,650 | Growing degree days, heatwave counts |
| Soil Data | Soil Health Cards | 673 | Micronutrient levels, quality index |

---

## Feature Engineering

### Yield Model Features (8 features)

| Feature | Type | Description |
|---------|------|-------------|
| `rainfall_anomaly` | Numeric | Deviation from normal rainfall |
| `monsoon_rainfall` | Numeric | June-September cumulative rainfall |
| `heatwave_count` | Numeric | Days exceeding heat threshold |
| `growing_degree_days` | Numeric | Accumulated thermal units |
| `soil_quality_index` | Numeric | Composite soil health score (0-1) |
| `season_encoded` | Categorical | Kharif/Rabi/Summer/etc. |
| `crop_name_encoded` | Categorical | 54 crop types |
| `district_name_encoded` | Categorical | 706 districts |

### Price Model Features (3 features)

| Feature | Type | Description |
|---------|------|-------------|
| `crop_encoded` | Categorical | Commodity type |
| `district_encoded` | Categorical | Market location |
| `month` | Numeric | Seasonality factor |

---

## Machine Learning Models

### Model Inventory

| Model | Algorithm | Purpose | Input Features | Output |
|-------|-----------|---------|-----------------|--------|
| **Yield Model** | RandomForestRegressor | Predict tonnes/hectare | 8 climate-soil features | Predicted yield (t/ha) |
| **Price Model** | RandomForestRegressor | Predict ₹/tonne | 3 features (crop, district, month) | Predicted price (₹/tonne) |
| **Disease Model** | EfficientNetB0 (CNN) | Classify 28 diseases | Leaf image (224×224 RGB) | Disease label + confidence |

### Yield Model Training

**Training Pipeline** (`src/train_yield_model.py`)

**Algorithms Evaluated:**
- RandomForest ← **Selected** (Best test R²: 0.8511)
- GradientBoosting (Test R²: 0.84)
- XGBoost (Test R²: 0.83)
- LightGBM (Test R²: 0.82)

**Training Parameters:**
```python
RandomForestRegressor(
    n_estimators=300,
    max_depth=15,
    min_samples_split=5,
    min_samples_leaf=2,
    max_features='sqrt',
    random_state=42,
    n_jobs=-1
)
```

**Input Features (8):**
1. `rainfall_anomaly` — Deviation from normal rainfall
2. `monsoon_rainfall` — June-September cumulative (mm)
3. `heatwave_count` — Days exceeding heat threshold
4. `growing_degree_days` — Accumulated thermal units
5. `soil_quality_index` — Composite soil health (0-1)
6. `season_encoded` — Kharif/Rabi/Summer/etc.
7. `crop_name_encoded` — 54 crop types
8. `district_name_encoded` — 706 districts

### Price Model Training

**Training Pipeline** (`src/train_price_model.py`)

**Algorithm:** RandomForestRegressor

**Input Features (3):**
1. `crop_encoded` — Commodity type
2. `district_encoded` — Market location
3. `month` — Seasonality factor (1-12)

**Data Strategy:**
- Real mandi prices where available (sparse)
- Median-by-crop fallback for missing districts
- No synthetic price data

---

## Model Performance Metrics

### Yield Model

| Metric | Train | Test |
|--------|-------|------|
| R-squared | 0.8899 | 0.8511 |
| RMSE | 307.21 | 358.97 |
| CV R-squared | 0.8743 +/- 0.0126 | - |

### Price Model

| Metric | Train | Test |
|--------|-------|------|
| R-squared | 0.9879 | 0.9635 |
| RMSE | 90.38 | 151.94 |
| MAE | - | 105.58 |
| CV R-squared | 0.9641 +/- 0.0078 | - |

---

## Architecture Diagram

```
User Request (district, season, area, scenario)
       |
       v
FastAPI Inference API          <-- stateless HTTP endpoint
       |
       v
Model Loader (pickle)          <-- loads .pkl once at startup
       |
       +----------+
       v          v
 Yield Model   Price Model     <-- RandomForest, CPU-only
       |          |
       +----+-----+
            v
    Crop Optimizer             <-- multi-criteria weighted scoring
            |
            v
 Sustainability Impact Engine  <-- deterministic proxy arithmetic (no ML)
            |
            v
 Decision Output + Sustainability Metrics (JSON)
```

**Key Properties**:

| Property | Detail |
|----------|--------|
| CPU-efficient tree models | O(log N) per tree - threshold comparisons only |
| Low-compute inference | Single prediction < 5 ms on commodity CPU |
| No GPU dependency | Entire pipeline runs on x86_64 or ARM64 |
| Edge-deployable | Model artifacts < 10 MB; runtime < 256 MB RAM |
| Stateless inference | No session state, no database, no external calls |
| Sustainability layer | Deterministic arithmetic; < 0.01 ms per crop |

See [docs/architecture_slide.md](docs/architecture_slide.md) for detailed slide-ready diagram.
See [docs/efficient_inference.md](docs/efficient_inference.md) for CPU-efficiency justification.

---

## How To Run Locally

Three commands - no cloud account, GPU, or external database required:

```bash
pip install -r requirements.txt                          # 1. Install
uvicorn cloud.api.app:app --host 0.0.0.0 --port 8000     # 2. Run
python scripts/final_test_matrix.py                       # 3. Test
```

Optional - generate demo output artifacts:

```bash
python scripts/generate_demo_outputs.py
```

---

## Example API Request / Response

### Request

```bash
curl -X POST http://localhost:8000/predict/crop-plan \
  -H "Content-Type: application/json" \
  -d '{"district": "Guntur", "season": "Kharif", "area": 10.0, "scenario": {"rainfall_delta": 0.0, "temp_delta": 0.0}}'
```

### Response

```json
{
  "status": "success",
  "district": "Guntur",
  "season": "Kharif",
  "area_hectares": 10.0,
  "scenario_applied": "baseline",
  "recommendations": [
    {
      "rank": 1,
      "crop": "Sugarcane",
      "composite_score": 0.963,
      "predicted_yield_tonnes_per_ha": 73.28,
      "predicted_price_inr_per_tonne": 3626,
      "expected_revenue_inr_per_ha": 265742,
      "total_revenue_inr": 2657420,
      "risk_level": "low",
      "sustainability_metrics": {
        "water_use_estimate": 15675.0,
        "water_saved_vs_baseline": 5.0,
        "fertilizer_proxy": 0.1445,
        "carbon_proxy": 17.34,
        "risk_reduction_pct": 0.0,
        "sustainability_score": 0.6814
      },
      "proxy_metrics": true
    }
  ],
  "disclaimer": "District-level aggregation. Not farm-specific advice.",
  "sustainability_disclosure": "Sustainability metrics are proxy estimates..."
}
```

### Validation Rules

| Field | Constraint |
|-------|------------|
| `district` | Required, must be valid district name |
| `season` | Required: Kharif, Rabi, Summer, Autumn, Winter, Whole Year |
| `area` | Required, must be > 0 |
| `rainfall_delta` | Optional, range: -1.0 to 1.0 |
| `temp_delta` | Optional, range: -5.0 to 10.0 deg C |

---

## Risk and Assumption Disclosures

1. **Sustainability Proxy Metrics** - Decision-support indicators, not field-measured values.
2. **Geographic Resolution** - District-level aggregation; no field-level geo precision claimed.
3. **Price Model Transparency** - Real mandi datasets with district aggregation; median-by-crop fallback where sparse.
4. **Scenario Disclaimer** - Climate scenarios are hypothetical projections showing model sensitivity, not meteorological predictions.
5. **Model Generalization** - Trained on historical data (1997-2020); performance on future unseen extremes is not guaranteed.

---

## Cloud Deployment (Optional)

Cloud deployment is **optional and generic**. The system runs fully locally. If cloud deployment is desired, any provider supporting Docker containers or serverless Python can be used. The `cloud/` directory contains adapter code for generic serverless deployment (e.g., Mangum wrapper). No specific cloud provider is required.

---

## Repository Structure

```
krishimind-ai/
    src/                    # Core ML + sustainability modules
        data_loader.py
        feature_builder.py
        revenue_engine.py
        crop_optimizer.py
        scenario_simulator.py
        sustainability_report_generator.py
        sustainability/
            crop_constants.py
            impact_engine.py
    models/                 # Trained model artifacts (inference only)
        yield_model.pkl
        price_model.pkl
    artifacts/              # Feature configs
        yield_features.json
        price_features.json
    reports/                # Evaluation + sustainability metrics
        model_metrics.json
    cloud/                  # API + optional cloud adapters
        api/                # FastAPI application
        config/             # API contract
    docker/                 # Container config
        Dockerfile
    docs/                   # Architecture + domain docs
        domain_alignment.md
        architecture_slide.md
        efficient_inference.md
    scripts/                # Demo + test utilities
        generate_demo_outputs.py
        final_test_matrix.py
    demo_outputs/           # Generated scenario outputs (JSON)
    tests/                  # Unit tests
    README.md
    LICENSE
    requirements.txt
    .gitignore
```

---

## License

MIT License - See [LICENSE](LICENSE) for details.

---

## Authors & Contributors

- **Nikita Sachan** - Core ML Architecture, Sustainability Engine, Yield & Price Models
- **Nishant Gupta** - API Development, Plant Disease Detection Integration, Model Optimization, Deployment & Infrastructure

---

## Acknowledgments

- ICRISAT for crop production data
- India Meteorological Department for climate data
- Soil Health Card Portal for soil quality data
