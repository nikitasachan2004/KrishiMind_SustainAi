#!/usr/bin/env python3
"""
KrishiMind AI - API Test Client
Tests the prediction endpoint locally
"""

import json
import sys
import requests
from typing import Dict, Any, Optional


# Configuration
BASE_URL = "http://localhost:8000"


def test_health() -> bool:
    """Test health endpoint"""
    print("\n" + "=" * 60)
    print("TEST: Health Check")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Service Status: {data.get('status')}")
            print(f"✓ Models Loaded: {data.get('models_loaded')}")
            print(f"✓ Version: {data.get('version')}")
            return data.get('models_loaded', False)
        else:
            print(f"✗ Health check failed: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("✗ Connection failed. Is the server running?")
        print(f"  Expected server at: {BASE_URL}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_prediction(
    district: str,
    season: str,
    area: float,
    rainfall_delta: float = 0.0,
    temp_delta: float = 0.0
) -> Optional[Dict[str, Any]]:
    """Test crop plan prediction"""
    print("\n" + "=" * 60)
    print(f"TEST: Crop Prediction - {district} / {season}")
    print("=" * 60)
    
    # Build request
    payload = {
        "district": district,
        "season": season,
        "area": area
    }
    
    if rainfall_delta != 0 or temp_delta != 0:
        payload["scenario"] = {
            "rainfall_delta": rainfall_delta,
            "temp_delta": temp_delta
        }
    
    print(f"Request: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/predict/crop-plan",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Validate required fields
            required_fields = ['status', 'district', 'season', 'recommendations']
            missing = [f for f in required_fields if f not in data]
            
            if missing:
                print(f"✗ Missing fields: {missing}")
                return None
            
            print(f"✓ Status: {data['status']}")
            print(f"✓ District: {data['district']}")
            print(f"✓ Season: {data['season']}")
            print(f"✓ Area: {data['area_hectares']} ha")
            print(f"✓ Scenario: {data['scenario_applied']}")
            
            print(f"\n📊 Top Recommendations:")
            print("-" * 50)
            
            for rec in data['recommendations'][:3]:
                print(f"  {rec['rank']}. {rec['crop']}")
                print(f"     Score: {rec['composite_score']:.3f}")
                print(f"     Yield: {rec['predicted_yield_tonnes_per_ha']} t/ha")
                print(f"     Revenue: ₹{rec['expected_revenue_inr_per_ha']:,.0f}/ha")
                print(f"     Risk: {rec['risk_level']}")
                print()
            
            print(f"⚠️  {data.get('disclaimer', '')}")
            
            return data
        else:
            print(f"✗ Request failed: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("✗ Connection failed. Is the server running?")
        return None
    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def test_validation_errors() -> bool:
    """Test input validation"""
    print("\n" + "=" * 60)
    print("TEST: Input Validation")
    print("=" * 60)
    
    test_cases = [
        {
            "name": "Missing district",
            "payload": {"season": "Kharif", "area": 10},
            "expect_error": True
        },
        {
            "name": "Negative area",
            "payload": {"district": "Guntur", "season": "Kharif", "area": -5},
            "expect_error": True
        },
        {
            "name": "Invalid season",
            "payload": {"district": "Guntur", "season": "InvalidSeason", "area": 10},
            "expect_error": True
        },
        {
            "name": "Valid minimal request",
            "payload": {"district": "Guntur", "season": "Kharif", "area": 1},
            "expect_error": False
        }
    ]
    
    all_passed = True
    
    for test in test_cases:
        try:
            response = requests.post(
                f"{BASE_URL}/predict/crop-plan",
                json=test["payload"],
                timeout=10
            )
            
            is_error = response.status_code >= 400
            
            if is_error == test["expect_error"]:
                status = "✓ PASS"
            else:
                status = "✗ FAIL"
                all_passed = False
            
            print(f"{status}: {test['name']} (Status: {response.status_code})")
            
        except Exception as e:
            print(f"✗ FAIL: {test['name']} - {e}")
            all_passed = False
    
    return all_passed


def test_scenario_simulation() -> bool:
    """Test scenario simulation"""
    print("\n" + "=" * 60)
    print("TEST: Scenario Simulation")
    print("=" * 60)
    
    scenarios = [
        {"name": "Baseline", "rainfall": 0.0, "temp": 0.0},
        {"name": "Mild Drought", "rainfall": -0.2, "temp": 0.0},
        {"name": "Moderate Warming", "rainfall": 0.0, "temp": 2.0},
        {"name": "Combined Stress", "rainfall": -0.3, "temp": 3.0}
    ]
    
    results = []
    
    for scenario in scenarios:
        result = test_prediction(
            district="Guntur",
            season="Kharif",
            area=10.0,
            rainfall_delta=scenario["rainfall"],
            temp_delta=scenario["temp"]
        )
        
        if result:
            top_crop = result['recommendations'][0]['crop']
            top_score = result['recommendations'][0]['composite_score']
            results.append({
                "scenario": scenario["name"],
                "top_crop": top_crop,
                "score": top_score
            })
    
    if results:
        print("\n📈 Scenario Comparison:")
        print("-" * 40)
        for r in results:
            print(f"  {r['scenario']}: {r['top_crop']} (Score: {r['score']:.3f})")
        return True
    
    return False


def test_sustainability_fields() -> bool:
    """Validate that sustainability metrics are present in API responses."""
    print("\n" + "=" * 60)
    print("TEST: Sustainability Metrics")
    print("=" * 60)

    payload = {"district": "Guntur", "season": "Kharif", "area": 10.0}

    try:
        response = requests.post(
            f"{BASE_URL}/predict/crop-plan",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )

        if response.status_code != 200:
            print(f"✗ Non-200 response: {response.status_code}")
            return False

        data = response.json()

        # Check top-level disclosure field
        if "sustainability_disclosure" not in data:
            print("✗ Missing top-level 'sustainability_disclosure'")
            return False
        print("✓ sustainability_disclosure present")

        # Validate each recommendation
        required_sus_keys = [
            "water_use_estimate",
            "water_saved_vs_baseline",
            "fertilizer_proxy",
            "carbon_proxy",
            "risk_reduction_pct",
            "sustainability_score",
        ]

        all_ok = True
        for rec in data.get("recommendations", []):
            crop = rec.get("crop", "?")

            # proxy_metrics flag
            if "proxy_metrics" not in rec:
                print(f"✗ {crop}: missing 'proxy_metrics' flag")
                all_ok = False
                continue

            sus = rec.get("sustainability_metrics")
            if sus is None:
                print(f"✗ {crop}: missing 'sustainability_metrics' block")
                all_ok = False
                continue

            missing = [k for k in required_sus_keys if k not in sus]
            if missing:
                print(f"✗ {crop}: missing sustainability keys: {missing}")
                all_ok = False
            else:
                print(
                    f"✓ {crop}: sustainability_score={sus['sustainability_score']:.4f}, "
                    f"water_saved={sus['water_saved_vs_baseline']:.1f}%, "
                    f"carbon_proxy={sus['carbon_proxy']:.2f}"
                )

        return all_ok

    except requests.exceptions.ConnectionError:
        print("✗ Connection failed. Is the server running?")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("🌾 KRISHIMIND AI - API TEST SUITE")
    print("=" * 60)
    print(f"Target: {BASE_URL}")
    
    # Test sequence
    tests_passed = 0
    tests_total = 5
    
    # 1. Health check
    if test_health():
        tests_passed += 1
    else:
        print("\n⚠️  Server not ready. Start with: uvicorn cloud.api.app:app --reload")
        sys.exit(1)
    
    # 2. Basic prediction
    if test_prediction("Guntur", "Kharif", 10.0):
        tests_passed += 1
    
    # 3. Validation
    if test_validation_errors():
        tests_passed += 1
    
    # 4. Scenarios
    if test_scenario_simulation():
        tests_passed += 1
    
    # 5. Sustainability fields
    if test_sustainability_fields():
        tests_passed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Tests Passed: {tests_passed}/{tests_total}")
    
    if tests_passed == tests_total:
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
