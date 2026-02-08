# Domain Alignment — Sustainable AI

## 1. Problem Statement

Agricultural systems in India face compounding resource inefficiencies:

- **Water waste** — crops with high irrigation demand are planted in water-scarce districts without quantitative comparison of alternatives.
- **Fertilizer overuse** — blanket application rates ignore soil quality variation, increasing input cost and environmental load.
- **Climate exposure** — farmers lack scenario-based tools to evaluate crop resilience under drought or heat-stress conditions before committing to a season.
- **Suboptimal crop selection** — decisions are made on tradition or single-variable heuristics rather than multi-criteria optimisation across yield, price, climate stability, and resource efficiency.

These inefficiencies result in avoidable water consumption, excess chemical inputs, higher carbon-equivalent emissions from fertilizer production, and economic losses during adverse weather events.

## 2. System Overview

**KrishiMind AI** is a predictive crop planning and resource optimisation engine that:

1. Predicts district-level **yield** (tonnes/ha) and **market price** (₹/tonne) using pre-trained RandomForest models.
2. Ranks candidate crops via a **multi-criteria composite score** (yield, revenue, climate stability, soil match).
3. Simulates **climate scenarios** (drought, heatwave, combined stress) to evaluate crop resilience.
4. Enriches every recommendation with **sustainability impact metrics** — water use, fertilizer proxy, carbon proxy, and risk reduction — through a deterministic scoring layer.

No model retraining occurs at inference time. All ML artifacts are serialised and loaded once at startup.

## 3. Sustainability Impact Mapping

Every API response includes the following sustainability metrics per crop recommendation:

| Metric | What It Measures | How It Supports Sustainability |
|--------|-----------------|-------------------------------|
| `water_saved_vs_baseline` | Percentage reduction in proxy water demand vs highest-demand crop (Rice) | Enables selection of water-efficient crops in scarce regions |
| `fertilizer_proxy` | Relative fertilizer load adjusted for soil quality (0–1, lower = better) | Identifies low-input crops that reduce chemical dependency |
| `carbon_proxy` | Carbon-equivalent footprint proxy derived from fertilizer intensity and area | Quantifies emission-reduction potential of crop switching |
| `risk_reduction_pct` | Yield change under scenario vs baseline, as percentage | Measures climate resilience gained by choosing scenario-robust crops |
| `sustainability_score` | Weighted composite of water efficiency, fertilizer efficiency, climate stability, and soil match (0–1) | Single decision-support index for ranking crops on resource efficiency |

## 4. Methodology Disclosure

### 4.1 Proxy Constants

Sustainability metrics are computed using **relative agronomic proxy constants** (crop water factor, fertilizer intensity, season length) derived from FAO-style reference literature. These are unit-less comparative indices — not absolute physical measurements.

### 4.2 District-Level Aggregation

All predictions and sustainability scores operate at **district-level granularity**. No field-level, GPS-based, or grid-level geo precision is claimed. Outputs are suitable for regional planning and comparative crop ranking, not for individual farm prescriptions.

### 4.3 No Synthetic Training Data

All ML models were trained on real, publicly available datasets (ICRISAT crop statistics, IMD climate records, Soil Health Card data). No synthetic data was generated for model training. Where mandi price coverage is sparse, median-by-crop fallback from real data is applied.

### 4.4 No Model Retraining in This Phase

Models are inference-only artifacts (`models/yield_model.pkl`, `models/price_model.pkl`). No retraining, fine-tuning, or online learning occurs during deployment. The sustainability scoring layer is entirely deterministic and uses no ML.

### 4.5 Sustainability Metrics Are Proxy Estimates

> Sustainability metrics are proxy estimates derived from agronomic literature constants and soil indices. They are decision-support indicators, not field-measured values.

This disclosure is auto-included in every API response (`sustainability_disclosure` field) and in the sustainability report JSON.

## 5. Value Statement

KrishiMind AI enables data-driven crop selection that quantifiably reduces water consumption, fertilizer dependency, and carbon-equivalent emissions while improving climate resilience — using CPU-efficient ML inference deployable at the edge without cloud or GPU requirements.
