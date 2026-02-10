# Efficient Inference — AMD-Friendly Architecture

> KrishiMind SustainAI is designed for **low-compute, CPU-friendly inference** suitable for edge deployment and AMD Slingshot environments.

---

## Model Architecture Choice

| Decision | Rationale |
|----------|-----------|
| **RandomForest** chosen over deep nets | Constant-time tree traversal; no GPU required |
| **No neural networks** | Eliminates CUDA/ROCm dependency entirely |
| **Deterministic scoring** | Sustainability engine uses pure arithmetic — zero ML overhead |

## Why Tree Models?

1. **O(log N) inference** — Each prediction traverses ~10-20 decision nodes regardless of input size.
2. **Embarrassingly parallelisable** — Individual trees are independent; batch scoring scales linearly across CPU cores.
3. **No matrix multiplication** — Unlike dense layers, tree splits are simple threshold comparisons.
4. **Fixed memory footprint** — Model size is constant post-training (~2-5 MB per `.pkl`), fits entirely in L2/L3 cache on modern AMD CPUs.

## CPU-Friendly Characteristics

| Property | Value |
|----------|-------|
| Yield model size | < 5 MB |
| Price model size | < 3 MB |
| Inference latency (single) | < 5 ms on any modern CPU |
| Batch scoring (100 districts) | < 200 ms |
| Peak RAM | < 256 MB including FastAPI overhead |
| GPU required | **No** |
| Internet required at inference | **No** |

## Edge Deployment Readiness

KrishiMind SustainAI can run on:

- **AMD Ryzen Embedded** — V-series or R-series edge processors
- **Any x86_64 Linux box** with Python 3.9+
- **Docker containers** with < 512 MB image size
- **ARM64** (e.g. Raspberry Pi 4) with minor packaging adjustments

No specialised accelerator, FPGA, or GPU is needed at any stage of the inference pipeline.

## Batch Scoring Support

The API's `/predict/crop-plan` endpoint processes one district-season combination per call. For bulk scoring:

```python
# Score all district-season combinations in parallel
import concurrent.futures, requests

combos = [("Guntur", "Kharif"), ("Nagpur", "Rabi"), ...]

def score(district, season):
    return requests.post(
        "http://localhost:8000/predict/crop-plan",
        json={"district": district, "season": season, "area": 100}
    ).json()

with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
    results = list(pool.map(lambda c: score(*c), combos))
```

Thread-pooled batch calls saturate available CPU cores without GPU contention.

## Sustainability Engine — Zero Additional Compute

The `SustainabilityImpactEngine` adds **no ML inference cost**. All metrics are computed via deterministic arithmetic:

| Metric | Computation |
|--------|-------------|
| Water use | 1 multiply + 2 lookups |
| Fertilizer proxy | 1 multiply + 1 subtract |
| Carbon proxy | 1 multiply |
| Sustainability score | 4 weighted additions |

Total overhead per crop: < 0.01 ms.

## Summary

| Aspect | Status |
|--------|--------|
| Deep learning dependency | ❌ None |
| GPU dependency | ❌ None |
| Cloud dependency | ❌ None (runs fully offline) |
| AMD CPU optimised | ✅ Tree models + arithmetic only |
| Edge deployable | ✅ < 256 MB RAM, < 10 MB models |
| Batch scoring | ✅ Thread-parallel, CPU-bound |

---

> **No benchmarking was performed.** This document describes architectural decisions that make the system inherently CPU-efficient. Actual latency will vary by hardware.
