# 🌾 KrishiMind AI

**Crop Planning & Resource Optimization Engine**

> AI-powered agricultural advisory system for Indian farmers, providing district-level crop recommendations, yield predictions, and revenue optimization under various climate scenarios.

---

## 📋 Table of Contents

- [Problem Statement](#problem-statement)
- [Solution](#solution)
- [Datasets](#datasets)
- [Feature Engineering](#feature-engineering)
- [Models](#models)
- [Model Metrics](#model-metrics)
- [Risk Disclosures](#risk-disclosures)
- [System Architecture](#system-architecture)
- [AWS Deployment](#aws-deployment)
- [API Usage](#api-usage)
- [Local Run Guide](#local-run-guide)
- [Build Philosophy](#build-philosophy)

---

## 🎯 Problem Statement

Indian farmers face critical challenges:
- **Unpredictable yields** due to climate variability
- **Price volatility** in agricultural markets
- **Limited access** to data-driven crop planning tools
- **No localized recommendations** based on soil and weather conditions

Traditional farming decisions rely on intuition, leading to:
- Suboptimal crop selection
- Revenue losses during adverse weather
- Inability to plan for climate scenarios

---

## 💡 Solution

**KrishiMind AI** provides:

1. **Yield Prediction** — ML models trained on historical crop data, climate features, and soil quality
2. **Price Forecasting** — District-level mandi price aggregation for revenue estimation
3. **Crop Optimization** — Multi-criteria scoring (yield × price × climate stability × soil match)
4. **Scenario Simulation** — What-if analysis for drought, warming, and combined stress conditions

### Key Capabilities

| Feature | Description |
|---------|-------------|
| Yield Model | RandomForest with 8 climate-soil features |
| Price Model | RandomForest on mandi aggregated data |
| Optimizer | Weighted composite scoring algorithm |
| Simulator | Predefined climate scenarios (±rainfall, ±temperature) |

---

## 📊 Datasets

All models trained on **real, publicly available Indian agricultural datasets**:

| Dataset | Source | Records | Description |
|---------|--------|---------|-------------|
| Master Training Table | ICRISAT + IMD | 343,768 | Crop yield with climate features |
| Rainfall Features | IMD | 12,784 | District-level seasonal rainfall |
| Temperature Features | IMD | 10,650 | Growing degree days, heatwave counts |
| Soil Data | Soil Health Cards | 673 | Micronutrient levels, quality index |

### Data Sources

- **ICRISAT** — District-level crop production statistics
- **IMD (India Meteorological Department)** — Rainfall, temperature records
- **Soil Health Card Portal** — Soil quality indicators

> ⚠️ No synthetic data generation used for model training.

---

## 🔧 Feature Engineering

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

## 🤖 Models

### Pre-Trained Models (Inference Only)

| Model | Algorithm | Purpose | Location |
|-------|-----------|---------|----------|
| Yield Model | RandomForestRegressor | Predict tonnes/hectare | `models/yield_model.pkl` |
| Price Model | RandomForestRegressor | Predict ₹/tonne | `models/price_model.pkl` |

### Model Selection Process

Four algorithms evaluated via 5-fold cross-validation:
1. RandomForest
2. GradientBoosting
3. XGBoost
4. LightGBM

**RandomForest selected** for both yield and price based on best validation R².

> 🚫 **No retraining occurs at inference time.** Models are loaded once at startup.

---

## 📈 Model Metrics

### Yield Model Performance

| Metric | Train | Test |
|--------|-------|------|
| R² | 0.8899 | 0.8511 |
| RMSE | 307.21 | 358.97 |
| CV R² | 0.8743 ± 0.0126 | — |

### Price Model Performance

| Metric | Train | Test |
|--------|-------|------|
| R² | 0.9879 | 0.9635 |
| RMSE | 90.38 | 151.94 |
| MAE | — | 105.58 |
| CV R² | 0.9641 ± 0.0078 | — |

### Feature Importance (Price Model)

| Feature | Importance |
|---------|------------|
| crop_encoded | 90.60% |
| month | 6.87% |
| district_encoded | 2.52% |

---

## ⚠️ Risk Disclosures

### 1. Geographic Resolution Limitation

> **This system provides DISTRICT-LEVEL predictions only.**
>
> No farm-level, GPS-based, or grid-level geo precision is claimed. All outputs represent district-level aggregations suitable for regional planning, not individual farm decisions.

### 2. Price Model Transparency

> **Price estimates are derived from real mandi datasets with district aggregation.**
>
> No synthetic price training data was generated. Where mandi coverage is sparse, median-by-crop fallback is applied with appropriate logging.

### 3. Scenario Simulation Disclaimer

> **Climate scenarios are hypothetical projections, not forecasts.**
>
> Scenario simulations (drought, warming) show model sensitivity to input changes. They do not represent meteorological predictions and should not be used for disaster planning.

### 4. Model Generalization

> **Models trained on historical data (1997-2020).**
>
> Performance on future unseen climate extremes or new crop varieties is not guaranteed. Regular retraining with updated data is recommended.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        KrishiMind AI                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│  │  Client  │───▶│   API    │───▶│  Models  │───▶│ Response │  │
│  │ Request  │    │ Gateway  │    │ Inference│    │   JSON   │  │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘  │
│                        │                                        │
│                        ▼                                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   Inference Pipeline                     │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────────┐ │   │
│  │  │ Feature │─▶│  Yield  │─▶│  Price  │─▶│  Optimizer  │ │   │
│  │  │ Builder │  │  Model  │  │  Model  │  │  + Revenue  │ │   │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────────┘ │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                     Data Layer                           │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────────┐ │   │
│  │  │ Models  │  │Artifacts│  │ Reports │  │   Config    │ │   │
│  │  │  .pkl   │  │  .json  │  │  .json  │  │   .yaml     │ │   │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────────┘ │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## ☁️ AWS Deployment

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         AWS Cloud                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌───────────┐     ┌───────────┐     ┌───────────────────┐    │
│   │    S3     │     │  Lambda   │     │    API Gateway    │    │
│   │  Bucket   │────▶│ Function  │◀────│    (REST API)     │    │
│   │ (models)  │     │ (Mangum)  │     │                   │    │
│   └───────────┘     └───────────┘     └───────────────────┘    │
│         │                 │                     │               │
│         ▼                 ▼                     ▼               │
│   ┌───────────┐     ┌───────────┐     ┌───────────────────┐    │
│   │ SageMaker │     │CloudWatch │     │       IAM         │    │
│   │ Endpoint  │     │   Logs    │     │ (Least Privilege) │    │
│   │  (batch)  │     │           │     │                   │    │
│   └───────────┘     └───────────┘     └───────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Service | Purpose |
|---------|---------|
| **S3** | Model artifacts, feature configs, dataset storage |
| **Lambda** | Real-time inference (FastAPI + Mangum) |
| **API Gateway** | HTTPS endpoint, request routing |
| **SageMaker** | Batch inference for bulk predictions |
| **CloudWatch** | Logging, monitoring, alerts |
| **IAM** | Role-based access, least privilege |

### Deployment Files

```
cloud/
├── api/
│   ├── app.py           # FastAPI application
│   ├── predict.py       # Inference logic
│   ├── schemas.py       # Pydantic models
│   └── model_loader.py  # Startup model loading
├── lambda/
│   └── handler.py       # Mangum adapter
├── sagemaker/
│   ├── inference.py     # SageMaker inference script
│   └── requirements.txt
└── config/
    ├── aws_architecture.md
    └── api_contract.yaml
```

---

## 🔌 API Usage

### Endpoint

```
POST /predict/crop-plan
```

### Request Schema

```json
{
  "district": "Guntur",
  "season": "Kharif",
  "area": 10.0,
  "scenario": {
    "rainfall_delta": 0.0,
    "temp_delta": 0.0
  }
}
```

### Response Schema

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
      "risk_level": "low"
    }
  ],
  "disclaimer": "District-level aggregation. Not farm-specific advice."
}
```

### Validation Rules

| Field | Constraint |
|-------|------------|
| `district` | Required, must be valid district name |
| `season` | Required, one of: Kharif, Rabi, Summer, Autumn, Winter, Whole Year |
| `area` | Required, must be > 0 |
| `rainfall_delta` | Optional, range: -1.0 to 1.0 (-100% to +100%) |
| `temp_delta` | Optional, range: -5.0 to 10.0 (°C) |

---

## 🚀 Local Run Guide

### Prerequisites

- Python 3.9+
- pip

### Installation

```bash
# Clone repository
git clone https://github.com/your-org/krishimind-ai.git
cd krishimind-ai

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Verify Models Exist

```bash
ls -la models/
# Should show: yield_model.pkl, price_model.pkl

ls -la artifacts/
# Should show: yield_features.json, price_features.json
```

### Run API Server

```bash
cd cloud/api
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### Test API

```bash
python test_api.py
```

### Run Full Pipeline (Inference Demo)

```bash
python run_pipeline.py
```

---

## 🧱 Build Philosophy

This repository follows **commit-by-commit development** to ensure:

1. **Auditability** — Every change is traceable
2. **Reproducibility** — Any commit can be checked out and run
3. **Transparency** — No magic, no hidden steps

### Commit History Progression

| Phase | Commits |
|-------|---------|
| **Data Layer** | Dataset integration, cleaning, feature engineering |
| **Model Layer** | Training, comparison, selection, serialization |
| **Service Layer** | Revenue engine, optimizer, simulator |
| **API Layer** | FastAPI, validation, error handling |
| **Cloud Layer** | Lambda adapter, SageMaker inference, Docker |
| **Quality Layer** | Tests, documentation, cleanup |

---

## 📁 Repository Structure

```
krishimind-ai/
├── src/                    # Core ML modules
│   ├── data_loader.py
│   ├── feature_builder.py
│   ├── revenue_engine.py
│   ├── crop_optimizer.py
│   └── scenario_simulator.py
├── models/                 # Trained model artifacts
│   ├── yield_model.pkl
│   └── price_model.pkl
├── artifacts/              # Feature configs
│   ├── yield_features.json
│   └── price_features.json
├── reports/                # Evaluation metrics
│   └── model_metrics.json
├── cloud/                  # AWS deployment
│   ├── api/
│   ├── lambda/
│   ├── sagemaker/
│   └── config/
├── docker/                 # Container config
│   └── Dockerfile
├── data_dictionary/        # Schema documentation
├── tests/                  # Unit tests
├── README.md
├── LICENSE
├── requirements.txt
└── .gitignore
```

---

## 📜 License

MIT License — See [LICENSE](LICENSE) for details.

---

## 👥 Authors

- **KrishiMind AI Team** — Hackathon 2026

---

## 🙏 Acknowledgments

- ICRISAT for crop production data
- India Meteorological Department for climate data
- Soil Health Card Portal for soil quality data

---

<p align="center">
  <strong>🌾 Empowering Indian Farmers with AI 🌾</strong>
</p>
