#!/usr/bin/env python3
"""
Demo Output Generator
=====================
Calls the local KrishiMind AI FastAPI endpoint with three fixed scenarios
and saves the full JSON responses under demo_outputs/.

Scenarios:
    baseline  — no climate modification
    drought   — rainfall_delta = -0.20 (−20%)
    heatwave  — temp_delta = +2.0 °C

Prerequisites:
    Server must be running:
        uvicorn cloud.api.app:app --host 0.0.0.0 --port 8000

Usage:
    python scripts/generate_demo_outputs.py
"""

import json
import sys
from pathlib import Path

import requests

# ── Configuration ────────────────────────────────────────────────
BASE_URL = "http://localhost:8000"
PREDICT_ENDPOINT = f"{BASE_URL}/predict/crop-plan"
OUTPUT_DIR = Path(__file__).parent.parent / "demo_outputs"

# Fixed request parameters (same for all scenarios)
DISTRICT = "Guntur"
SEASON = "Kharif"
AREA = 10.0

# Scenario definitions
SCENARIOS = {
    "baseline": {"rainfall_delta": 0.0, "temp_delta": 0.0},
    "drought": {"rainfall_delta": -0.20, "temp_delta": 0.0},
    "heatwave": {"rainfall_delta": 0.0, "temp_delta": 2.0},
}

# Required sustainability keys that must appear in every recommendation
REQUIRED_SUSTAINABILITY_KEYS = [
    "water_use_estimate",
    "water_saved_vs_baseline",
    "fertilizer_proxy",
    "carbon_proxy",
    "risk_reduction_pct",
    "sustainability_score",
]


def build_payload(scenario_name: str) -> dict:
    """Build the request payload for a given scenario."""
    deltas = SCENARIOS[scenario_name]
    payload = {
        "district": DISTRICT,
        "season": SEASON,
        "area": AREA,
    }
    if deltas["rainfall_delta"] != 0.0 or deltas["temp_delta"] != 0.0:
        payload["scenario"] = deltas
    return payload


def validate_response(data: dict, scenario_name: str) -> None:
    """Validate mandatory fields in the API response. Raises on failure."""
    # Top-level fields
    for field in ("status", "district", "season", "recommendations"):
        if field not in data:
            raise ValueError(f"[{scenario_name}] Missing top-level field: {field}")

    if data["status"] != "success":
        raise ValueError(f"[{scenario_name}] status is '{data['status']}', expected 'success'")

    recommendations = data["recommendations"]
    if not recommendations:
        raise ValueError(f"[{scenario_name}] Empty recommendations list")

    # Per-recommendation sustainability validation
    for rec in recommendations:
        crop = rec.get("crop", "?")
        sus = rec.get("sustainability_metrics")
        if sus is None:
            raise ValueError(
                f"[{scenario_name}] Crop '{crop}' missing 'sustainability_metrics'"
            )
        missing = [k for k in REQUIRED_SUSTAINABILITY_KEYS if k not in sus]
        if missing:
            raise ValueError(
                f"[{scenario_name}] Crop '{crop}' missing sustainability keys: {missing}"
            )


def run() -> int:
    """Generate demo outputs for all scenarios. Returns exit code."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Verify server is reachable
    try:
        health = requests.get(f"{BASE_URL}/health", timeout=5)
        if health.status_code != 200:
            print(f"Server health check failed (HTTP {health.status_code})")
            return 1
    except requests.exceptions.ConnectionError:
        print(f"Cannot connect to {BASE_URL}. Start the server first:")
        print("  uvicorn cloud.api.app:app --host 0.0.0.0 --port 8000")
        return 1

    print(f"Server reachable at {BASE_URL}\n")
    errors = 0

    for name in SCENARIOS:
        payload = build_payload(name)
        print(f"[{name}] POST {PREDICT_ENDPOINT}")
        print(f"         payload: {json.dumps(payload)}")

        response = requests.post(
            PREDICT_ENDPOINT,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )

        if response.status_code != 200:
            print(f"         FAIL — HTTP {response.status_code}: {response.text[:200]}")
            errors += 1
            continue

        data = response.json()

        try:
            validate_response(data, name)
        except ValueError as exc:
            print(f"         FAIL — {exc}")
            errors += 1
            continue

        out_path = OUTPUT_DIR / f"{name}.json"
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)

        top = data["recommendations"][0]
        sus = top["sustainability_metrics"]
        print(f"         OK   — saved to {out_path}")
        print(
            f"         top crop: {top['crop']} | "
            f"score: {top['composite_score']:.3f} | "
            f"water_saved: {sus['water_saved_vs_baseline']}% | "
            f"sustainability: {sus['sustainability_score']}"
        )
        print()

    if errors:
        print(f"\n{errors} scenario(s) failed.")
        return 1

    print("All demo outputs generated successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(run())
