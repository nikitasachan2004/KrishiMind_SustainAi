"""
Sustainability Report Generator
================================
Produces a JSON summary of sustainability impact metrics from
a batch of crop recommendations.

Output: reports/sustainability_report.json

Usage:
    python -m src.sustainability_report_generator
    # or import and call generate_sustainability_report(recommendations)
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

# Handle imports for both module and standalone execution
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.sustainability.impact_engine import SustainabilityImpactEngine, PROXY_DISCLOSURE
from src.sustainability.crop_constants import CROP_CONSTANTS

logger = logging.getLogger(__name__)

REPORTS_DIR = Path(__file__).parent.parent / "reports"


def generate_sustainability_report(
    recommendations: List[Dict[str, Any]],
    district: str = "aggregate",
    season: str = "all",
    area: float = 10.0,
    soil_quality_index: float = 0.83,
) -> Dict[str, Any]:
    """
    Generate a sustainability summary report from enriched recommendations.

    Parameters
    ----------
    recommendations : list[dict]
        Crop recommendation dicts (must already contain sustainability_metrics,
        or will be enriched in-place).
    district : str
        District context label.
    season : str
        Season context label.
    area : float
        Area in hectares.
    soil_quality_index : float
        Soil quality (0-1).

    Returns
    -------
    dict  — report payload (also written to reports/sustainability_report.json).
    """
    engine = SustainabilityImpactEngine()

    # Enrich if not already done
    if recommendations and "sustainability_metrics" not in recommendations[0]:
        engine.enrich_crop_results(recommendations, soil_quality_index, area, season)

    # Collect metrics
    water_saved_list: List[float] = []
    carbon_proxy_list: List[float] = []
    fert_proxy_list: List[float] = []
    risk_reduction_list: List[float] = []
    sustainability_scores: List[float] = []
    low_input_count = 0

    for rec in recommendations:
        sus = rec.get("sustainability_metrics", {})
        water_saved_list.append(sus.get("water_saved_vs_baseline", 0.0))
        carbon_proxy_list.append(sus.get("carbon_proxy", 0.0))
        fert_proxy_list.append(sus.get("fertilizer_proxy", 0.0))
        risk_reduction_list.append(sus.get("risk_reduction_pct", 0.0))
        sustainability_scores.append(sus.get("sustainability_score", 0.0))

        # Low-input crop: fertilizer_proxy < 0.15 AND water_factor ≤ 0.45
        crop = rec.get("crop", "")
        constants = CROP_CONSTANTS.get(crop, {})
        if (
            sus.get("fertilizer_proxy", 1.0) < 0.15
            and constants.get("crop_water_factor", 1.0) <= 0.45
        ):
            low_input_count += 1

    n = max(len(recommendations), 1)

    def safe_avg(lst: List[float]) -> float:
        return round(sum(lst) / max(len(lst), 1), 4)

    low_input_pct = round((low_input_count / n) * 100, 2)

    report: Dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "district": district,
        "season": season,
        "area_hectares": area,
        "num_crops_evaluated": n,
        "avg_water_saved_vs_baseline_pct": safe_avg(water_saved_list),
        "avg_carbon_proxy_avoided": safe_avg(carbon_proxy_list),
        "low_input_crop_pct": low_input_pct,
        "avg_climate_risk_reduction_pct": safe_avg(risk_reduction_list),
        "avg_sustainability_score": safe_avg(sustainability_scores),
        "avg_fertilizer_proxy": safe_avg(fert_proxy_list),
        "disclosure": PROXY_DISCLOSURE,
        "proxy_metrics": True,
        "district_level_aggregation": True,
    }

    # Write to disk
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = REPORTS_DIR / "sustainability_report.json"
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)

    logger.info("Sustainability report written to %s", out_path)
    return report


# ── CLI entry point ──────────────────────────────────────────────
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Build a demo set of recommendations for default crops
    from cloud.api.predict import CropPredictor  # type: ignore

    predictor = CropPredictor()
    recs_schema = predictor.optimize(
        district="Guntur", season="Kharif", area=10.0
    )
    # Convert schema objects to dicts
    recs = [r.model_dump() for r in recs_schema]

    report = generate_sustainability_report(
        recommendations=recs,
        district="Guntur",
        season="Kharif",
        area=10.0,
    )

    print(json.dumps(report, indent=2))
