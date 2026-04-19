# KrishiMind SustainAI — Complete Project Overview

**Last Updated**: April 19, 2026  
**Project Type**: AI-Powered Crop Planning & Resource Optimization Engine  
**Status**: Production-Ready

---

## 1. PROJECT OVERVIEW

### Purpose
KrishiMind SustainAI is a sustainable crop planning and resource optimization engine that provides district-level crop recommendations for Indian agriculture. It integrates ML models for yield and price prediction with sustainability metrics (water, fertilizer, carbon proxies) to help farmers make data-driven decisions.

### Key Features
- **Multi-criteria crop ranking**: Yield, price, revenue, climate risk, soil suitability
- **Climate scenario simulation**: Drought and heatwave impact analysis
- **Sustainability metrics**: Water efficiency, fertilizer usage, carbon footprint proxies
- **REST API**: FastAPI-based inference endpoint
- **Local-first deployment**: Fully functional locally; optionally cloud-deployable
- **District-level aggregation**: Suitable for regional planning (not farm-specific)

---

## 2. PROJECT DIRECTORY STRUCTURE

```
krishimind_sustainai/
├── src/                              # Core ML + sustainability modules
│   ├── crop_optimizer.py             # Crop ranking & scoring engine
│   ├── data_loader.py                # Data loading utilities
│   ├── evaluate_models.py            # Model evaluation scripts
│   ├── feature_builder.py            # Feature engineering
│   ├── revenue_engine.py             # Revenue calculation
│   ├── scenario_simulator.py         # Climate shock simulation
│   ├── sustainability_report_generator.py # Sustainability metrics
│   ├── train_price_model.py          # Price model training
│   ├── train_yield_model.py          # Yield model training
│   ├── sustainability/               # Sustainability engine
│   │   ├── crop_constants.py         # Agronomic constants (water, fertilizer, carbon)
│   │   └── impact_engine.py          # Proxy metric calculations
│   ├── plant_detection/              # Plant disease detection subsystem
│   │   ├── predict.py                # Disease prediction interface
│   │   ├── inference/                # Inference models & utilities
│   │   ├── model/                    # Pre-trained model artifacts
│   │   └── utils/                    # Helper utilities
│   └── plant_disease_detection/      # Alternative implementation
│       ├── app.py                    # Standalone app
│       ├── train.py                  # Training script (28 plant classes)
│       └── README.md                 # Documentation
│
├── cloud/                            # API & Cloud Adapters
│   ├── api/                          # FastAPI application
│   │   ├── app.py                    # Main FastAPI app (lifespan, endpoints)
│   │   ├── model_loader.py           # Model loading with validation
│   │   ├── predict.py                # Prediction logic
│   │   └── schemas.py                # Pydantic request/response schemas
│   ├── config/                       # Configuration
│   │   ├── api_contract.yaml         # API specification
│   │   └── aws_architecture.md       # Cloud deployment design
│   └── lambda/                       # AWS Lambda adapter
│       ├── handler.py                # Lambda handler (Mangum wrapper)
│       └── __init__.py
│
├── data/                             # Data & Processing Pipeline
│   ├── cleaned_data/                 # Cleaned datasets
│   │   ├── crop_yield_cleaned.csv
│   │   ├── rainfall_features.csv
│   │   ├── rainfall_seasonal_agg.csv
│   │   ├── soil_cleaned.csv
│   │   ├── temperature_daily_agg.csv
│   │   ├── temperature_features.csv
│   │   ├── temperature_seasonal_agg.csv
│   │   └── humidity.csv
│   ├── output/                       # Processing outputs
│   │   └── master_training_table.csv # Merged training data
│   ├── eda_reports/                  # Exploratory Data Analysis
│   │   ├── data_profile.csv          # Data profiling report
│   │   ├── missingness_report.csv    # Missing data analysis
│   │   └── summary_statistics.csv    # Statistical summary
│   ├── pipeline/                     # Data processing pipeline
│   │   ├── config.py                 # Pipeline configuration & constants
│   │   ├── phase_a_audit.py          # Data source detection & validation
│   │   ├── phase_b_conversion.py     # Format conversion (NetCDF→CSV)
│   │   ├── phase_c_standardization.py # Schema standardization
│   │   ├── phase_d_cleaning.py       # Data cleaning & outlier removal
│   │   ├── phase_e_geo.py            # Geographic resolution (gridded→district)
│   │   ├── phase_f_features.py       # Feature engineering
│   │   └── utils.py                  # Utility functions
│   ├── humadity.csv                  # Raw humidity data
│   ├── tmax_2024.csv                 # Raw max temperature data
│   └── TODO_REPLACE_GEO.csv          # Geographic mapping reference
│
├── models/                           # Pre-trained Model Artifacts
│   ├── yield_model.pkl               # Yield prediction ensemble (~5 MB)
│   ├── price_model.pkl               # Price prediction RandomForest (~3 MB)
│   └── (metadata.json)               # Model versioning (if present)
│
├── artifacts/                        # Feature Configurations
│   ├── yield_features.json           # Yield model feature schema & encodings
│   │   - feature_columns: [rainfall_anomaly, monsoon_rainfall, heatwave_count, ...]
│   │   - categorical_columns: [season, crop_name, district_name]
│   │   - label_encodings for 53+ crops, 600+ districts
│   └── price_features.json           # Price model feature schema
│       - feature_names: [crop_encoded, district_encoded, month]
│       - label_encodings for 7 crops, 5 districts
│
├── reports/                          # Model Evaluation & Metrics
│   └── model_metrics.json            # Training/test metrics, CV scores
│       - Yield model: R² ~ 0.87-0.92, RMSE < 20% mean yield
│       - Price model: R² ~ 0.96, RMSE, MAE, MAPE
│
├── demo_outputs/                     # Pre-generated API Responses
│   ├── baseline.json                 # Baseline scenario (Guntur, Kharif, 10 ha)
│   ├── drought.json                  # Drought scenario (-20% rainfall)
│   └── heatwave.json                 # Heatwave scenario (+2°C temp)
│
├── frontend/                         # Next.js React Application
│   ├── app/                          # App router directory
│   │   ├── page.tsx                  # Landing page
│   │   ├── layout.tsx                # Layout wrapper
│   │   ├── analyze/                  # Analysis page
│   │   ├── diseases/                 # Disease detection page
│   │   ├── about/                    # About page
│   │   ├── globals.css               # Global styles
│   │   └── api/                      # API routes (if any)
│   ├── components/                   # React components
│   │   ├── demo.tsx                  # Demo component
│   │   ├── sections/                 # Page sections
│   │   ├── theme/                    # Theme configuration
│   │   └── ui/                       # UI component library
│   ├── lib/                          # Utilities
│   │   └── utils.ts                  # Helper functions
│   ├── package.json                  # Dependencies & scripts
│   ├── tsconfig.json                 # TypeScript configuration
│   ├── tailwind.config.ts            # Tailwind CSS config
│   ├── next.config.ts                # Next.js config
│   ├── postcss.config.js             # PostCSS config
│   ├── components.json               # UI component definitions
│   └── next-env.d.ts                 # Type definitions
│
├── docker/                           # Container Configuration
│   ├── Dockerfile                    # Multi-stage build (Python 3.9+)
│   ├── docker-compose.yml            # Compose configuration
│   └── README.md                     # Docker usage instructions
│
├── docs/                             # Architecture & Design Documentation
│   ├── architecture_slide.md         # System architecture diagram & speaker notes
│   ├── domain_alignment.md           # Sustainability alignment & methodology
│   ├── efficient_inference.md        # CPU-efficiency justification (AMD-friendly)
│   ├── api_contract.yaml             # OpenAPI specification
│   └── aws_architecture.md           # Cloud deployment architecture
│
├── scripts/                          # Executable Utilities
│   ├── generate_demo_outputs.py      # Generate JSON responses for all scenarios
│   ├── final_test_matrix.py          # Lightweight API test suite (8 tests)
│   ├── commit_history.sh             # Git history inspection
│   └── (others)
│
├── tests/                            # Test Suite
│   ├── test_core.py                  # Core module tests
│   ├── __init__.py
│   └── (additional tests)
│
├── data_dictionary/                  # Data Metadata
│   └── data_dictionary.md            # Column definitions & data schemas
│
├── design.md                         # System Design Document (8 sections)
│   - Architecture, data pipeline, feature engineering, ML models,
│   - Decision engine, scenario simulator, deployment, local setup
│
├── requirements.md                   # Requirements Document (11 sections)
│   - Problem statement, objectives, functional/non-functional requirements,
│   - Data requirements, ML requirements, API contracts, limitations, metrics
│
├── README.md                         # Quick start & overview
├── requirements.txt                  # Python dependencies
├── run_pipeline.py                   # Data processing pipeline entry point
├── frontend_app.py                   # Frontend server (if Flask-based)
├── test_api.py                       # API testing script
├── LICENSE                           # MIT License
└── .gitignore                        # Git ignore rules
```

---

## 3. CONFIGURATION FILES & ARCHITECTURE

### Key Configuration Files

| File | Purpose | Contents |
|------|---------|----------|
| [design.md](design.md) | System design & architecture | ML pipeline, feature engineering, decision logic, simulator design |
| [requirements.md](requirements.md) | Functional & non-functional specs | Problem statement, objectives, FR/NFR, data requirements, ML specs |
| [README.md](README.md) | Quick start guide | 3-line setup, example request/response, deployment instructions |
| [data_dictionary.md](data_dictionary/data_dictionary.md) | Data schema documentation | Column definitions, data types, expected ranges |
| [architecture_slide.md](docs/architecture_slide.md) | Architecture visualization | System diagram, key properties, speaker notes |
| [domain_alignment.md](docs/domain_alignment.md) | Sustainability methodology | Proxy metrics, disclosure, no synthetic data, deterministic scoring |
| [efficient_inference.md](docs/efficient_inference.md) | CPU-efficiency details | Why tree models, no GPU, edge deployment readiness |
| [api_contract.yaml](cloud/config/api_contract.yaml) | OpenAPI specification | Request/response schemas, endpoints, status codes |

### Data Pipeline Phases

| Phase | Module | Purpose | Input | Output |
|-------|--------|---------|-------|--------|
| **A** | phase_a_audit.py | Data source discovery & validation | Raw data files | Data availability report |
| **B** | phase_b_conversion.py | Format standardization | NetCDF/GRD/CSV files | Unified CSV format |
| **C** | phase_c_standardization.py | Schema consistency | Heterogeneous CSVs | Standardized columns, data types, names |
| **D** | phase_d_cleaning.py | Quality assurance | Raw data with issues | Cleaned, validated datasets |
| **E** | phase_e_geo.py | Geographic aggregation | Gridded climate data | District-level aggregates |
| **F** | phase_f_features.py | Feature engineering | Aggregated data | Derived features (seasonal, anomaly, GDD) |

---

## 4. PYTHON MODULES — CORE ML & SUSTAINABILITY

### src/ Core Modules

| Module | Purpose | Key Classes/Functions |
|--------|---------|----------------------|
| **crop_optimizer.py** | Multi-criteria crop ranking | `CropOptimizer`, `optimize()`, `CropScore` (dataclass) |
| **data_loader.py** | Data loading utilities | `DataLoader`, load climate/soil/yield/price data |
| **feature_builder.py** | Feature construction | `FeatureBuilder`, construct features for ML models |
| **revenue_engine.py** | Revenue calculation | Calculate yield × price = revenue per hectare |
| **scenario_simulator.py** | Climate shock simulation | `ScenarioSimulator`, simulate drought/heatwave |
| **sustainability_report_generator.py** | Sustainability metrics | Generate proxy sustainability scores |
| **train_yield_model.py** | Yield model training | Ensemble (RF + GBM + XGBoost) training pipeline |
| **train_price_model.py** | Price model training | LightGBM price prediction training |
| **evaluate_models.py** | Model evaluation | Compute metrics (R², RMSE, MAE, MAPE, F1) |

### src/sustainability/ — Sustainability Engine

| Module | Purpose | Deterministic Calculations |
|--------|---------|---------------------------|
| **crop_constants.py** | Agronomic constants | Water factor, fertilizer intensity, carbon equivalent by crop |
| **impact_engine.py** | Proxy metrics | Water saved %, fertilizer proxy (0-1), carbon proxy, risk reduction % |

### src/plant_detection/ — Disease Detection

| Component | Purpose | Framework |
|-----------|---------|-----------|
| **predict.py** | Disease classification API | PyTorch model inference |
| **inference/** | Model utilities | Image preprocessing, model loading |
| **model/** | Pre-trained weights | EfficientNet-B0 (28 plant classes) |
| **utils/** | Helpers | Image transforms, label encoding |

---

## 5. CLOUD API — FastAPI APPLICATION

### cloud/api/app.py — Main Application

**Architecture**: Lifespan-managed FastAPI with startup model loading

**Endpoints**:
- `GET /` — Root info
- `GET /health` — Health check (models_loaded, version)
- `POST /predict/crop-plan` — Main recommendation endpoint
- `GET /model/info` — Model metadata

**Request Schema** (`CropPlanRequest`):
```json
{
  "district": "string (required)",
  "season": "Kharif|Rabi|Summer|... (enum)",
  "area": "float (hectares, > 0)",
  "scenario": {
    "rainfall_delta": "float (-1.0 to 1.0)",
    "temp_delta": "float (-5.0 to 10.0)"
  },
  "image_path": "string (optional, plant disease detection)"
}
```

**Response Schema** (`CropPlanResponse`):
```json
{
  "status": "success",
  "district": "...",
  "season": "...",
  "area_hectares": 10.0,
  "scenario_applied": "baseline|mild_drought|moderate_warming|...",
  "recommendations": [
    {
      "rank": 1,
      "crop": "Sugarcane",
      "composite_score": 0.963,
      "predicted_yield_tonnes_per_ha": 73.28,
      "predicted_price_inr_per_tonne": 3626,
      "expected_revenue_inr_per_ha": 265742,
      "total_revenue_inr": 2657420,
      "risk_level": "low|medium|high",
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
  "plant_disease": {
    "disease": "Apple Scab Leaf",
    "confidence": 0.95
  },
  "disclaimer": "District-level aggregation. Not farm-specific advice.",
  "sustainability_disclosure": "..."
}
```

### cloud/api/model_loader.py — Singleton Model Management

**Design**: Lazy load at startup, singleton pattern

**Models Loaded**:
1. Yield model: RandomForest ensemble (3 sub-models) → `models/yield_model.pkl`
2. Price model: RandomForest regressor → `models/price_model.pkl`
3. Yield features: Schema & encodings → `artifacts/yield_features.json`
4. Price features: Schema & encodings → `artifacts/price_features.json`

**Validation**:
- File existence checks
- Non-empty file validation
- JSON schema validation for feature configs
- Type inference (RF/XGBoost/etc.)

**Errors**: Raises `ModelLoadError` → API fails fast at startup

### cloud/api/schemas.py — Pydantic Models

**Request Models**:
- `CropPlanRequest` — Main prediction request
- `ScenarioInput` — Climate shock parameters
- `SeasonEnum` — Kharif/Rabi/Summer/Autumn/Winter/Whole Year

**Response Models**:
- `CropPlanResponse` — Main response
- `CropRecommendation` — Per-crop ranking
- `SustainabilityMetrics` — Proxy metrics
- `PlantDiseasePrediction` — Disease classification
- `HealthResponse` — Health check response
- `ErrorResponse` — Error reporting

---

## 6. MACHINE LEARNING MODELS

### Yield Prediction Model

**Type**: Ensemble (Weighted Average)
- 30% RandomForest Regressor (100 trees)
- 30% Gradient Boosting Regressor (100 estimators)
- 40% XGBoost Regressor (100 estimators)

**Input Features** (15-20):
- Climate: rainfall_mean, rainfall_anomaly, monsoon_rainfall, avg_temp, heatwave_count, GDD
- Soil: nitrogen, phosphorus, potassium, pH, organic_carbon, soil_quality_index
- Temporal: year, season_encoded, crop_encoded, district_encoded

**Output**: Yield (quintals/hectare)

**Performance**:
- CV R²: 0.87-0.92
- Test RMSE: < 20% of mean yield
- Artifact: `models/yield_model.pkl`

### Price Prediction Model

**Type**: RandomForest Regressor
- 100 trees
- Hyperparameters: learning_rate=0.05, num_leaves=31, max_depth=7

**Input Features** (3):
- crop_encoded
- district_encoded
- month

**Output**: Price (₹/quintal)

**Performance**:
- CV R²: 0.964 ± 0.0078
- Test RMSE: 151.94 INR/quintal
- Test MAE: 105.58 INR/quintal
- Artifact: `models/price_model.pkl`

### Feature Encoding

**Yield Features** (`artifacts/yield_features.json`):
- 53 crops + "Other Cereals", "Other Pulses"
- 600+ districts across India
- 6 seasons (Kharif, Rabi, Summer, Autumn, Winter, Whole Year)

**Price Features** (`artifacts/price_features.json`):
- 7 crops (Cotton, Groundnut, Maize, Rice, Soybean, Sugarcane, Wheat)
- 5 districts (Guntur, Karimnagar, Krishna, Nizamabad, Warangal)

---

## 7. FRONTEND — NEXT.JS REACT APPLICATION

### Structure

```
frontend/
├── app/                      # App Router (Next.js 13+)
│   ├── page.tsx             # Landing/home page
│   ├── layout.tsx           # Root layout
│   ├── globals.css          # Global styles (Tailwind)
│   ├── analyze/             # /analyze — crop analysis page
│   ├── diseases/            # /diseases — plant disease detection
│   ├── about/               # /about — project info
│   └── api/                 # Optional server routes
│
├── components/              # Reusable React components
│   ├── demo.tsx            # Demo component
│   ├── sections/           # Full-width page sections
│   ├── theme/              # Theme provider & config
│   └── ui/                 # Shadcn/UI components (buttons, cards, etc.)
│
├── lib/
│   └── utils.ts            # TypeScript utilities
│
├── Configuration Files
│   ├── package.json        # Dependencies (Next.js, React, Tailwind)
│   ├── tsconfig.json       # TypeScript config
│   ├── tailwind.config.ts  # Tailwind CSS theme
│   ├── next.config.ts      # Next.js settings
│   └── postcss.config.js   # PostCSS plugins
```

### Pages
- **Landing** (`/`) — Project overview, hero section
- **Analyze** (`/analyze`) — Crop recommendation form & results
- **Diseases** (`/diseases`) — Plant disease detection with image upload
- **About** (`/about`) — Project background & team

### Styling
- Tailwind CSS for utility-first styling
- Responsive design (mobile-first)
- Dark mode support (theme config)

---

## 8. PLANT DISEASE DETECTION SUBSYSTEM

### Structure

```
src/plant_disease_detection/
├── train.py               # Training script (28 classes)
├── app.py                 # Standalone Streamlit/Flask app
├── PlantDoc_Colab.ipynb   # Colab training notebook
├── model/                 # Pre-trained EfficientNet-B0
├── inference/             # Inference utilities
└── utils/                 # Image preprocessing, augmentation

Key Training Config:
- Model: EfficientNet-B0 (224×224 images)
- Classes: 28 plant disease types (PlantDoc dataset)
- Batch Size: 32
- Epochs Phase 1: 10, Phase 2: 20
- Data Augmentation: RandomCrop, HorizontalFlip, ColorJitter, RandomRotation
- Mixed Precision: Optional (FP16)
```

### Integration with Main API
- Disease predictions returned in `CropPlanResponse.plant_disease` if `image_path` provided
- Returns: `{"disease": "Apple Scab Leaf", "confidence": 0.95}`

---

## 9. DATA FILES & PIPELINE

### Cleaned Datasets (data/cleaned_data/)

| File | Rows | Columns | Description |
|------|------|---------|-------------|
| **crop_yield_cleaned.csv** | 100k+ | year, district, crop, season, yield | Historical crop yield records |
| **rainfall_features.csv** | 1M+ | region_key, year, season, rainfall_mean, monsoon_rainfall | Aggregated rainfall by district/season |
| **temperature_daily_agg.csv** | 500k+ | region_key, year, season, avg_temp, heatwave_count, gdd | Temperature aggregates |
| **temperature_features.csv** | 500k+ | region_key, year, season, avg_temp_mean, gdd, heatwave_count | Temperature-derived features |
| **temperature_seasonal_agg.csv** | 100k+ | region_key, year, season, avg_temp, std, min, max | Seasonal temperature statistics |
| **soil_cleaned.csv** | 700+ | district, zn, fe, cu, mn, b, s, ph, oc, soil_quality_index | Soil nutrients by district |
| **rainfall_seasonal_agg.csv** | 100k+ | district, year, season, seasonal_rainfall, rainy_days | Seasonal rainfall aggregates |

### EDA Reports (data/eda_reports/)

| Report | Purpose |
|--------|---------|
| **data_profile.csv** | Data profiling (missing %, dtypes, cardinality) |
| **missingness_report.csv** | Missing value analysis by column & dataset |
| **summary_statistics.csv** | Min, max, mean, std for numeric columns |

### Feature Engineering Outputs (data/output/)

| File | Purpose |
|------|---------|
| **master_training_table.csv** | Merged clean data for model training (yield, price, soil, climate) |

### Raw Data (data/)

| File | Source | Format | Purpose |
|------|--------|--------|---------|
| **humadity.csv** | IMD | CSV | Humidity observations by station/date |
| **tmax_2024.csv** | IMD | CSV | Max temperature observations |
| **TODO_REPLACE_GEO.csv** | Reference | CSV | Geographic mapping (lat/lon → district) |

---

## 10. MODELS & ARTIFACTS

### Pre-trained Model Artifacts (models/)

```
models/
├── yield_model.pkl       # ~5 MB, RandomForest ensemble
│                        # Load: joblib.load(path)
│                        # Predict: model.predict(feature_matrix) → array
│
└── price_model.pkl       # ~3 MB, RandomForest regressor
                         # Load: joblib.load(path)
                         # Predict: model.predict(feature_matrix) → array
```

### Feature Configurations (artifacts/)

```
artifacts/
├── yield_features.json
│   ├── feature_columns: [list of 8 input features]
│   ├── categorical_columns: [season, crop_name, district_name]
│   ├── numeric_columns: [rainfall, temp, GDD, soil_quality_index]
│   ├── feature_stats: {fill_value, missing_count} for each feature
│   └── label_encodings: {season: [list], crop_name: [53 crops], district_name: [600+ districts]}
│
└── price_features.json
    ├── feature_names: [crop_encoded, district_encoded, month]
    ├── metrics: {model_name, CV R², test R², RMSE, MAE, feature_importance}
    └── label_encodings: {crop: [7], district: [5]}
```

### Evaluation Metrics (reports/model_metrics.json)

```json
{
  "yield_model": {
    "cv_r2": 0.89,
    "test_rmse": 1.8,
    "test_mae": 1.2
  },
  "price_model": {
    "cv_r2": 0.964,
    "test_rmse": 151.94,
    "test_mape": 0.23
  }
}
```

---

## 11. EXECUTABLE SCRIPTS

### scripts/

| Script | Purpose | Run Command |
|--------|---------|-------------|
| **generate_demo_outputs.py** | Generate JSON outputs for 3 scenarios (baseline, drought, heatwave) | `python scripts/generate_demo_outputs.py` |
| **final_test_matrix.py** | Lightweight test suite (8 tests: server, health, predict, scenario, sustainability keys, no negatives, risk range, proxy flag) | `python scripts/final_test_matrix.py` |
| **commit_history.sh** | Git history inspection | `bash scripts/commit_history.sh` |

### Root-level Scripts

| Script | Purpose | Run Command |
|--------|---------|-------------|
| **run_pipeline.py** | Execute data processing pipeline (all 6 phases) | `python run_pipeline.py` |
| **test_api.py** | Manual API testing | `python test_api.py` |
| **frontend_app.py** | Frontend server (if present) | `python frontend_app.py` |

---

## 12. DOCKER & DEPLOYMENT

### Dockerfile

**Multi-stage build**:
1. **Builder stage**: Install dependencies, compile packages
2. **Runtime stage**: Copy only necessary artifacts (~512 MB image)

**Configuration**:
- Base image: `python:3.9-slim`
- Entrypoint: `uvicorn cloud.api.app:app --host 0.0.0.0 --port 8000`
- Exposed port: 8000
- Environment: Path adjustments for model/artifact discovery

### docker-compose.yml

```yaml
services:
  krishimind:
    build: ./docker
    ports:
      - "8000:8000"
    environment:
      - MODEL_PATH=/app/models
      - ARTIFACT_PATH=/app/artifacts
    volumes:
      - ./models:/app/models:ro
      - ./artifacts:/app/artifacts:ro
```

### Local Deployment

**3-command setup**:
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run FastAPI server
uvicorn cloud.api.app:app --host 0.0.0.0 --port 8000

# 3. Test endpoints
python scripts/final_test_matrix.py
```

### Optional: Cloud Deployment

**Supported platforms**:
- AWS Lambda (via `cloud/lambda/handler.py` + Mangum wrapper)
- Google Cloud Run (containerized)
- Azure Container Instances (Docker)
- Any Kubernetes cluster

**No cloud-specific dependencies**: Works on any Python 3.9+ runtime

---

## 13. TESTS & VALIDATION

### Test Suite (tests/)

| Test File | Purpose | Coverage |
|-----------|---------|----------|
| **test_core.py** | Core module tests | Data loader, feature builder, crop optimizer |

### Integration Tests (scripts/final_test_matrix.py)

**8 Test Cases**:
1. **T1: Server Reachable** — HTTP 200 on root endpoint
2. **T2: Health Healthy** — Health check returns `{"status": "healthy", "models_loaded": true}`
3. **T3: Predict 200** — `/predict/crop-plan` returns HTTP 200
4. **T4: Scenario Changes Output** — Drought scenario produces different scores than baseline
5. **T5: Sustainability Keys** — Every crop has all 6 sustainability metrics
6. **T6: No Negative Values** — No negative values in score/water/fertilizer/carbon
7. **T7: Risk Reduction Range** — Risk reduction in [-100, 100] range
8. **T8: Proxy Flag Present** — Every recommendation has `proxy_metrics=true`

### Demo Outputs

**3 Pre-generated scenarios** (demo_outputs/):
- **baseline.json** — Normal conditions (Guntur, Kharif, 10 ha)
- **drought.json** — 20% rainfall reduction
- **heatwave.json** — +2°C temperature increase

Each includes top-5 crop recommendations with sustainability metrics.

---

## 14. REQUIREMENTS & DEPENDENCIES

### Python Dependencies (requirements.txt)

**Key packages**:
- **FastAPI** — API framework
- **Pydantic** — Request/response validation
- **Joblib** — Model serialization
- **Pandas, NumPy** — Data processing
- **Scikit-learn** — ML models
- **XGBoost, LightGBM** — Gradient boosting
- **PyTorch, EfficientNet** — Plant disease detection
- **Uvicorn** — ASGI server
- **Mangum** — Lambda adapter
- **Scipy** — Scientific computing

### Node.js Dependencies (frontend/package.json)

**Key packages**:
- **Next.js 14+** — React framework
- **React 18+** — UI library
- **Tailwind CSS** — Styling
- **TypeScript** — Type safety
- **Shadcn/UI** — Component library

---

## 15. KEY FEATURES & CAPABILITIES

### Inference Pipeline

**Single prediction latency**: < 5 ms per request (CPU-only)

**Batch scoring**: 100 district-season combinations < 200 ms

**Memory footprint**: < 256 MB (models + FastAPI + overhead)

### Model Capabilities

| Capability | Supported | Details |
|-----------|-----------|---------|
| Yield prediction | ✓ | 50+ crops, 600+ districts |
| Price forecasting | ✓ | 7 major crops, 5 key districts |
| Climate risk scoring | ✓ | Drought, heatwave, combined stress |
| Scenario simulation | ✓ | Rainfall ±%, temperature ±°C |
| Sustainability metrics | ✓ | Water, fertilizer, carbon proxies |
| Plant disease detection | ✓ | 28 plant disease classes |

### Sustainability Scoring

**Proxy metrics** (deterministic, no ML):
- **Water saved vs baseline** (%) — Relative to highest-demand crop
- **Fertilizer proxy** (0-1) — Adjusted for soil quality
- **Carbon proxy** (index units) — Derived from fertilizer intensity
- **Risk reduction** (%) — Yield robustness under stress
- **Sustainability score** (0-1) — Weighted composite

**Methodology**: 
- Uses FAO-style agronomic constants
- No synthetic data
- All disclosure included in API response

---

## 16. DOCUMENTATION

### Main Documentation Files

| File | Purpose |
|------|---------|
| [README.md](README.md) | Quick start (3 commands), example request/response, architecture link |
| [design.md](design.md) | Detailed system design (8 sections, 460+ lines) |
| [requirements.md](requirements.md) | Comprehensive requirements (11 sections, 306+ lines) |
| [data_dictionary.md](data_dictionary/data_dictionary.md) | Data schema & definitions |
| [architecture_slide.md](docs/architecture_slide.md) | Visual architecture + speaker notes |
| [domain_alignment.md](docs/domain_alignment.md) | Sustainability methodology & transparency |
| [efficient_inference.md](docs/efficient_inference.md) | CPU-friendly design & edge deployment |

### Inline Documentation

- **Docstrings**: All classes/functions have docstrings
- **Type hints**: Full type annotations throughout codebase
- **Comments**: Implementation details where non-obvious
- **Error messages**: Descriptive error handling with context

---

## 17. PROJECT STATISTICS

### Codebase Metrics

| Metric | Value |
|--------|-------|
| Python files | 40+ |
| TypeScript/React files | 15+ |
| Total lines of code | ~10,000+ |
| Model artifacts | 2 (.pkl files) |
| Feature configs | 2 (.json files) |
| Data files | 10+ (CSVs) |
| Documentation | 5+ files (MD) |

### Data Scale

| Dataset | Size | Rows | Time Period |
|---------|------|------|-------------|
| Crop yield history | 50 MB+ | 100,000+ | 1997-2020 |
| Climate data | 500 MB+ | 1,000,000+ | Daily observations |
| Soil data | 5 MB+ | 700+ | District-level |
| Mandi prices | 20 MB+ | 50,000+ | Historical prices |

### Model Scale

| Model | Size | Type | Parameters |
|-------|------|------|-------------|
| Yield ensemble | 5 MB | RF+GBM+XGBoost | ~100k trees total |
| Price model | 3 MB | RandomForest | ~100 trees |
| Disease detection | 100 MB | EfficientNet-B0 | 5.3M parameters |

---

## 18. QUICK START

### Development Setup

```bash
# 1. Clone & enter directory
cd KrishiMind_SustainAi

# 2. Create Python environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start API server
uvicorn cloud.api.app:app --host 0.0.0.0 --port 8000

# 5. In another terminal, run tests
python scripts/final_test_matrix.py

# 6. Generate demo outputs
python scripts/generate_demo_outputs.py
```

### API Usage

**Example request**:
```bash
curl -X POST http://localhost:8000/predict/crop-plan \
  -H "Content-Type: application/json" \
  -d '{
    "district": "Guntur",
    "season": "Kharif",
    "area": 10.0,
    "scenario": {"rainfall_delta": 0.0, "temp_delta": 0.0}
  }'
```

**Response**: Top-5 crop recommendations with sustainability metrics (see demo_outputs/)

### Frontend

```bash
cd frontend
npm install
npm run dev
# Navigate to http://localhost:3000
```

---

## 19. KNOWN LIMITATIONS

1. **District-level only** — No field-level precision
2. **Proxy metrics** — Sustainability indicators, not field-measured
3. **Historical training** — May not predict unprecedented events
4. **Limited crop/district coverage** — 50+ crops, 600+ districts; not all combinations
5. **Market volatility** — Price predictions subject to sudden shocks
6. **No online learning** — Models are static (inference-only)

---

## 20. FUTURE ENHANCEMENTS

1. Add satellite imagery for field-level analysis
2. Implement online learning for model updates
3. Expand to pest/disease risk prediction
4. Integrate IoT sensors for real-time monitoring
5. Develop mobile app for farmer accessibility
6. Add insurance integration
7. Multi-language support (Hindi, Telugu, etc.)
8. Crop-specific recommendations (variety selection)

---

**End of Summary**

For more details, refer to:
- **Architecture**: [design.md](design.md)
- **Requirements**: [requirements.md](requirements.md)
- **Quick Start**: [README.md](README.md)
