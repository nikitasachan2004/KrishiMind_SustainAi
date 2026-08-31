#!/usr/bin/env python3
"""
KrishiMind SustainAI - API Test Client
Tests the prediction endpoint locally and via pytest
"""

import json
import sys
from typing import Dict, Any, Optional
import requests
from fastapi.testclient import TestClient

from cloud.api.app import app

# Configuration
BASE_URL = "http://localhost:8000"
client = TestClient(app)


def _get_health():
    try:
        res = requests.get(f"{BASE_URL}/health", timeout=2)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    res = client.get("/health")
    return res.json()


def _post_crop_plan(payload: dict):
    try:
        res = requests.post(f"{BASE_URL}/predict/crop-plan", json=payload, timeout=5)
        return res.status_code, res.json()
    except Exception:
        pass
    res = client.post("/predict/crop-plan", json=payload)
    return res.status_code, res.json()


def test_health():
    """Test health endpoint"""
    data = _get_health()
    assert data.get("status") == "healthy"
    assert data.get("models_loaded") is True
    assert data.get("version") == "1.0.0"


def test_prediction_endpoint():
    """Test crop plan prediction for standard request"""
    payload = {
        "district": "Guntur",
        "season": "Kharif",
        "area": 10.0
    }
    status_code, data = _post_crop_plan(payload)
    assert status_code == 200
    assert data["status"] == "success"
    assert data["district"] == "Guntur"
    assert data["season"] == "Kharif"
    assert len(data["recommendations"]) > 0
    top = data["recommendations"][0]
    assert "crop" in top
    assert "composite_score" in top
    assert "predicted_yield_tonnes_per_ha" in top
    assert "expected_revenue_inr_per_ha" in top


def test_validation_errors():
    """Test input validation"""
    test_cases = [
        {"name": "Missing district", "payload": {"season": "Kharif", "area": 10}, "expect_error": True},
        {"name": "Negative area", "payload": {"district": "Guntur", "season": "Kharif", "area": -5}, "expect_error": True},
        {"name": "Invalid season", "payload": {"district": "Guntur", "season": "InvalidSeason", "area": 10}, "expect_error": True},
        {"name": "Valid minimal request", "payload": {"district": "Guntur", "season": "Kharif", "area": 1}, "expect_error": False}
    ]
    
    for test in test_cases:
        status_code, data = _post_crop_plan(test["payload"])
        is_error = status_code >= 400
        assert is_error == test["expect_error"], f"Failed test case: {test['name']}"


def test_scenario_simulation():
    """Test scenario simulation"""
    scenarios = [
        {"name": "Baseline", "rainfall": 0.0, "temp": 0.0},
        {"name": "Mild Drought", "rainfall": -0.2, "temp": 0.0},
        {"name": "Moderate Warming", "rainfall": 0.0, "temp": 2.0},
        {"name": "Combined Stress", "rainfall": -0.3, "temp": 3.0}
    ]
    
    for scenario in scenarios:
        payload = {
            "district": "Guntur",
            "season": "Kharif",
            "area": 10.0,
            "scenario": {
                "rainfall_delta": scenario["rainfall"],
                "temp_delta": scenario["temp"]
            }
        }
        status_code, data = _post_crop_plan(payload)
        assert status_code == 200
        assert len(data["recommendations"]) > 0


def test_sustainability_fields():
    """Validate that sustainability metrics are present in API responses."""
    payload = {"district": "Guntur", "season": "Kharif", "area": 10.0}
    status_code, data = _post_crop_plan(payload)
    assert status_code == 200
    assert "sustainability_disclosure" in data

    required_sus_keys = [
        "water_use_estimate",
        "water_saved_vs_baseline",
        "fertilizer_proxy",
        "carbon_proxy",
        "risk_reduction_pct",
        "sustainability_score",
    ]

    for rec in data.get("recommendations", []):
        assert "proxy_metrics" in rec
        sus = rec.get("sustainability_metrics")
        assert sus is not None
        for key in required_sus_keys:
            assert key in sus


def main():
    """Run CLI report"""
    print("\n" + "=" * 60)
    print("🌾 KRISHIMIND SUSTAINAI - API TEST SUITE")
    print("=" * 60)
    
    test_health()
    print("✓ Health Check Passed")
    
    test_prediction_endpoint()
    print("✓ Basic Prediction Passed")
    
    test_validation_errors()
    print("✓ Input Validation Passed")
    
    test_scenario_simulation()
    print("✓ Scenario Simulation Passed")
    
    test_sustainability_fields()
    print("✓ Sustainability Metrics Passed")
    
    print("\n✅ All 5 API tests passed successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
