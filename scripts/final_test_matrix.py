#!/usr/bin/env python3
"""
Final Test Matrix
=================
Lightweight validation suite for KrishiMind SustainAI.
Runs against the local FastAPI server and prints a pass/fail table.

No external test frameworks required — uses only requests + stdlib.

Prerequisites:
    uvicorn cloud.api.app:app --host 0.0.0.0 --port 8000

Usage:
    python scripts/final_test_matrix.py
"""

import json
import sys

import requests

BASE_URL = "http://localhost:8000"

# Shared request payload
PAYLOAD_BASELINE = {"district": "Guntur", "season": "Kharif", "area": 10.0}
PAYLOAD_DROUGHT = {
    "district": "Guntur",
    "season": "Kharif",
    "area": 10.0,
    "scenario": {"rainfall_delta": -0.20, "temp_delta": 0.0},
}

REQUIRED_SUS_KEYS = [
    "water_use_estimate",
    "water_saved_vs_baseline",
    "fertilizer_proxy",
    "carbon_proxy",
    "risk_reduction_pct",
    "sustainability_score",
]

# ── Test result collector ────────────────────────────────────────
results = []


def record(name: str, passed: bool, detail: str = "") -> None:
    """Register a test result."""
    results.append({"name": name, "passed": passed, "detail": detail})


# ── Individual tests ─────────────────────────────────────────────

def test_server_reachable() -> None:
    """T1: API startup reachable."""
    try:
        r = requests.get(f"{BASE_URL}/", timeout=5)
        record("T1 Server reachable", r.status_code == 200, f"HTTP {r.status_code}")
    except requests.exceptions.ConnectionError:
        record("T1 Server reachable", False, "Connection refused")


def test_health_healthy() -> None:
    """T2: /health returns healthy."""
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        data = r.json()
        ok = data.get("status") == "healthy" and data.get("models_loaded") is True
        record("T2 Health healthy", ok, f"status={data.get('status')}")
    except Exception as exc:
        record("T2 Health healthy", False, str(exc))


def test_predict_200() -> None:
    """T3: /predict/crop-plan returns 200."""
    try:
        r = requests.post(
            f"{BASE_URL}/predict/crop-plan", json=PAYLOAD_BASELINE, timeout=30
        )
        record("T3 Predict 200", r.status_code == 200, f"HTTP {r.status_code}")
    except Exception as exc:
        record("T3 Predict 200", False, str(exc))


def test_scenario_changes_output() -> None:
    """T4: Scenario delta changes output values."""
    try:
        r_base = requests.post(
            f"{BASE_URL}/predict/crop-plan", json=PAYLOAD_BASELINE, timeout=30
        ).json()
        r_drought = requests.post(
            f"{BASE_URL}/predict/crop-plan", json=PAYLOAD_DROUGHT, timeout=30
        ).json()

        base_scores = [
            r["composite_score"] for r in r_base.get("recommendations", [])
        ]
        drought_scores = [
            r["composite_score"] for r in r_drought.get("recommendations", [])
        ]
        changed = base_scores != drought_scores
        record("T4 Scenario changes output", changed, "scores differ" if changed else "identical")
    except Exception as exc:
        record("T4 Scenario changes output", False, str(exc))


def test_sustainability_keys_exist() -> None:
    """T5: sustainability_metrics keys exist in every crop result."""
    try:
        r = requests.post(
            f"{BASE_URL}/predict/crop-plan", json=PAYLOAD_BASELINE, timeout=30
        ).json()
        all_ok = True
        detail_parts = []
        for rec in r.get("recommendations", []):
            sus = rec.get("sustainability_metrics")
            if sus is None:
                all_ok = False
                detail_parts.append(f"{rec.get('crop','?')}: missing block")
                continue
            missing = [k for k in REQUIRED_SUS_KEYS if k not in sus]
            if missing:
                all_ok = False
                detail_parts.append(f"{rec.get('crop','?')}: {missing}")
        detail = "; ".join(detail_parts) if detail_parts else "all keys present"
        record("T5 Sustainability keys", all_ok, detail)
    except Exception as exc:
        record("T5 Sustainability keys", False, str(exc))


def test_no_negative_sustainability() -> None:
    """T6: No negative values in core sustainability metrics (score, water_use, fertilizer, carbon)."""
    try:
        r = requests.post(
            f"{BASE_URL}/predict/crop-plan", json=PAYLOAD_BASELINE, timeout=30
        ).json()
        negatives = []
        check_keys = ["sustainability_score", "water_use_estimate", "fertilizer_proxy", "carbon_proxy"]
        for rec in r.get("recommendations", []):
            sus = rec.get("sustainability_metrics", {})
            for k in check_keys:
                v = sus.get(k, 0)
                if v < 0:
                    negatives.append(f"{rec.get('crop','?')}.{k}={v}")
        ok = len(negatives) == 0
        detail = "none negative" if ok else "; ".join(negatives)
        record("T6 Sustainability >= 0", ok, detail)
    except Exception as exc:
        record("T6 Sustainability >= 0", False, str(exc))


def test_risk_reduction_in_range() -> None:
    """T7: risk_reduction_pct in valid range."""
    try:
        r = requests.post(
            f"{BASE_URL}/predict/crop-plan", json=PAYLOAD_BASELINE, timeout=30
        ).json()
        out_of_range = []
        for rec in r.get("recommendations", []):
            sus = rec.get("sustainability_metrics", {})
            rr = sus.get("risk_reduction_pct", 0)
            if not (-100 <= rr <= 100):
                out_of_range.append(f"{rec.get('crop','?')}={rr}")
        ok = len(out_of_range) == 0
        detail = "all in range" if ok else "; ".join(out_of_range)
        record("T7 Risk reduction range", ok, detail)
    except Exception as exc:
        record("T7 Risk reduction range", False, str(exc))


def test_proxy_metrics_flag() -> None:
    """T8: proxy_metrics flag present in every recommendation."""
    try:
        r = requests.post(
            f"{BASE_URL}/predict/crop-plan", json=PAYLOAD_BASELINE, timeout=30
        ).json()
        missing = []
        for rec in r.get("recommendations", []):
            if "proxy_metrics" not in rec:
                missing.append(rec.get("crop", "?"))
        ok = len(missing) == 0
        detail = "all have flag" if ok else f"missing in: {missing}"
        record("T8 proxy_metrics flag", ok, detail)
    except Exception as exc:
        record("T8 proxy_metrics flag", False, str(exc))


# ── Runner ───────────────────────────────────────────────────────

def print_results() -> None:
    """Print pass/fail table."""
    print()
    print("=" * 72)
    print("KRISHIMIND SUSTAINAI — FINAL TEST MATRIX")
    print("=" * 72)
    print(f"{'Test':<35} {'Result':<8} {'Detail'}")
    print("-" * 72)
    for r in results:
        status = "PASS" if r["passed"] else "FAIL"
        marker = "\u2713" if r["passed"] else "\u2717"
        print(f"{marker} {r['name']:<33} {status:<8} {r['detail']}")
    print("-" * 72)
    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    print(f"Total: {passed}/{total} passed")
    if passed == total:
        print("\nAll tests passed.")
    else:
        print(f"\n{total - passed} test(s) failed.")
    print()


def main() -> int:
    test_server_reachable()
    # Abort early if server unreachable
    if not results[0]["passed"]:
        print_results()
        print("Server not reachable. Start with:")
        print("  uvicorn cloud.api.app:app --host 0.0.0.0 --port 8000")
        return 1

    test_health_healthy()
    test_predict_200()
    test_scenario_changes_output()
    test_sustainability_keys_exist()
    test_no_negative_sustainability()
    test_risk_reduction_in_range()
    test_proxy_metrics_flag()

    print_results()

    failed = sum(1 for r in results if not r["passed"])
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
