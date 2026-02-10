# Architecture — KrishiMind SustainAI

## Inference Pipeline Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│   User Request (district, season, area, scenario)            │
│                          │                                   │
│                          ▼                                   │
│              ┌───────────────────────┐                       │
│              │   FastAPI Inference   │   ← stateless HTTP    │
│              │        API           │      endpoint          │
│              └───────────┬───────────┘                       │
│                          │                                   │
│                          ▼                                   │
│              ┌───────────────────────┐                       │
│              │    Model Loader      │   ← loads .pkl once    │
│              │     (pickle)         │      at startup        │
│              └───────────┬───────────┘                       │
│                          │                                   │
│                ┌─────────┴─────────┐                         │
│                ▼                   ▼                          │
│   ┌──────────────────┐  ┌──────────────────┐                 │
│   │   Yield Model    │  │   Price Model    │  ← RandomForest │
│   │ (RandomForest)   │  │ (RandomForest)   │    CPU-only     │
│   └────────┬─────────┘  └────────┬─────────┘                 │
│            │                     │                            │
│            └─────────┬───────────┘                            │
│                      ▼                                        │
│         ┌────────────────────────┐                            │
│         │    Crop Optimizer      │   ← multi-criteria         │
│         │   (yield × price ×    │      weighted scoring       │
│         │  climate × soil)      │                             │
│         └────────────┬───────────┘                            │
│                      ▼                                        │
│         ┌────────────────────────┐                            │
│         │  Sustainability        │   ← deterministic          │
│         │  Impact Engine         │      proxy arithmetic      │
│         │  (water, fertilizer,  │      (no ML)                │
│         │   carbon, risk)       │                             │
│         └────────────┬───────────┘                            │
│                      ▼                                        │
│   ┌──────────────────────────────────────────┐               │
│   │  Decision Output + Sustainability Metrics │               │
│   │  (JSON response with disclosures)         │               │
│   └──────────────────────────────────────────┘               │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

## Key Architectural Properties

| Property | Detail |
|----------|--------|
| **CPU-efficient tree models** | RandomForest inference is O(log N) per tree — threshold comparisons only, no matrix multiplication |
| **Low-compute inference path** | Single prediction < 5 ms; batch of 100 districts < 200 ms on commodity CPU |
| **No GPU dependency** | Entire pipeline runs on x86_64 or ARM64 CPUs; no CUDA, ROCm, or accelerator required |
| **Edge-deployable scoring** | Model artifacts total < 10 MB; runtime memory < 256 MB including FastAPI overhead |
| **Stateless inference** | Each request is independent; no session state, no database, no external service calls |
| **Sustainability scoring layer** | Deterministic arithmetic applied post-optimisation; adds < 0.01 ms per crop; no additional model invocation |

## Speaker Notes

KrishiMind SustainAI uses a linear inference pipeline where a user request flows through model loading, parallel yield and price prediction, multi-criteria crop ranking, and a final sustainability enrichment step. The ML models are RandomForest regressors chosen specifically for CPU efficiency — they perform only threshold comparisons at inference time, avoiding the matrix operations that would require GPU acceleration. The sustainability impact engine is a pure arithmetic layer that computes proxy water, fertilizer, and carbon metrics using FAO-style crop constants and soil quality indices. This architecture is intentionally minimal: stateless, cloud-optional, and deployable on any hardware with a Python runtime. All sustainability outputs are proxy estimates with auto-included disclosures, ensuring transparency for reviewers.
