# KrishiMind SustainAI - Sustainable Crop & Resource Optimization Engine

**AI system that reduces agricultural water use, fertilizer load, and climate risk through predictive crop planning and scenario-based resource optimization.**

> District-level crop recommendations, yield predictions, revenue optimization, and **sustainability impact scoring** under various climate scenarios.

---

## Table of Contents

- [Sustainable AI Positioning](#sustainable-ai-positioning)
- [Problem Statement](#problem-statement)
- [Solution](#solution)
- [Sustainability Impact Outputs](#sustainability-impact-outputs)
- [Sustainability Engine Description](#sustainability-engine-description)
- [Proxy Metric Disclosure](#proxy-metric-disclosure)
- [District Aggregation Disclosure](#district-aggregation-disclosure)
- [No Retraining Statement](#no-retraining-statement)
- [No Synthetic Training Statement](#no-synthetic-training-statement)
- [Datasets](#datasets)
- [Feature Engineering](#feature-engineering)
- [Models](#models)
- [Model Metrics](#model-metrics)
- [Architecture Diagram](#architecture-diagram)
- [How To Run Locally](#how-to-run-locally)
- [Example API Request / Response](#example-api-request--response)
- [Risk and Assumption Disclosures](#risk-and-assumption-disclosures)
- [Repository Structure](#repository-structure)
- [License](#license)
- [Authors](#authors)

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

## Datasets

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

## Models

### Pre-Trained Models (Inference Only)

| Model | Algorithm | Purpose | Location |
|-------|-----------|---------|----------|
| Yield Model | RandomForestRegressor | Predict tonnes/hectare | `models/yield_model.pkl` |
| Price Model | RandomForestRegressor | Predict Rs/tonne | `models/price_model.pkl` |

Four algorithms evaluated via 5-fold cross-validation: RandomForest, GradientBoosting, XGBoost, LightGBM. **RandomForest selected** for both yield and price based on best validation R-squared.

> **No retraining occurs at inference time.** Models are loaded once at startup.

---

## Model Metrics

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

## Authors

- **Nikita Sachan** - Primary Developer
- **Nishant Gupta** - Contributor

---

## Acknowledgments

- ICRISAT for crop production data
- India Meteorological Department for climate data
- Soil Health Card Portal for soil quality data
