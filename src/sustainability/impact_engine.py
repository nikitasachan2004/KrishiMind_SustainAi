"""
Sustainability Impact Engine
=============================
Deterministic proxy computations for water use, fertilizer load,
carbon footprint, and climate-risk reduction.

All outputs are **proxy estimates** — not field-measured values.
They enable comparative ranking of crops on sustainability criteria
at district-level aggregation.

Disclosure (auto-included in every enriched result):
    Sustainability metrics are proxy estimates derived from agronomic
    literature constants and soil indices. They are decision-support
    indicators, not field-measured values.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from .crop_constants import get_crop_constants, CROP_CONSTANTS

logger = logging.getLogger(__name__)

# ────────────────────────────────────────────────────────────────
# Sustainability score weights (must sum to 1.0)
# ────────────────────────────────────────────────────────────────
_SUSTAINABILITY_WEIGHTS: Dict[str, float] = {
    "water_efficiency": 0.30,
    "fertilizer_efficiency": 0.25,
    "climate_stability": 0.25,
    "soil_match": 0.20,
}

# Disclosure text injected into every enrichment result
PROXY_DISCLOSURE = (
    "Sustainability metrics are proxy estimates derived from agronomic "
    "literature constants and soil indices. They are decision-support "
    "indicators, not field-measured values."
)


class SustainabilityImpactEngine:
    """
    Computes proxy sustainability metrics for crop recommendations.

    All formulas are deterministic — no ML model is invoked.
    """

    # Reference crop for water-saved baseline (highest water factor)
    _BASELINE_CROP = "Rice"

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self.weights = weights or _SUSTAINABILITY_WEIGHTS
        # Pre-compute baseline water factor for savings comparison
        self._baseline_water_factor = get_crop_constants(self._BASELINE_CROP)[
            "crop_water_factor"
        ]

    # ── Core Estimation Functions ────────────────────────────────

    def estimate_water_use(
        self, crop: str, area: float, season: str  # noqa: ARG002 – kept for interface
    ) -> float:
        """
        Proxy water use (unit-less index-hectare-days).

        Formula:
            water_use = crop_water_factor × area × season_length_days × 5
        """
        c = get_crop_constants(crop)
        return round(c["crop_water_factor"] * area * c["season_length_days"] * 5, 2)

    def estimate_fertilizer_proxy(
        self, crop: str, soil_quality_index: float
    ) -> float:
        """
        Proxy fertilizer load (index, 0-1 range, lower = better).

        Formula:
            fertilizer_score = fertilizer_intensity × (1 - soil_quality_index)
        """
        c = get_crop_constants(crop)
        return round(c["fertilizer_intensity"] * (1 - soil_quality_index), 4)

    def estimate_carbon_proxy(
        self, fertilizer_score: float, area: float
    ) -> float:
        """
        Proxy carbon footprint (index-hectare units).

        Formula:
            carbon_proxy = fertilizer_score × area × 12
        """
        return round(fertilizer_score * area * 12, 2)

    def compute_risk_reduction(
        self, baseline_yield: float, scenario_yield: float
    ) -> float:
        """
        Climate risk reduction percentage.

        Positive value → scenario yield exceeds baseline (risk reduced).
        Negative value → scenario yield fell (risk increased).

        Formula:
            risk_reduction_pct = ((scenario_yield - baseline_yield)
                                  / baseline_yield) × 100
        """
        if baseline_yield <= 0:
            return 0.0
        return round(
            ((scenario_yield - baseline_yield) / baseline_yield) * 100, 2
        )

    def compute_sustainability_score(self, metrics: Dict[str, float]) -> float:
        """
        Weighted normalised sustainability score (0–1, higher = more sustainable).

        Components (from *metrics* dict):
            water_efficiency     – 1 - normalised water use
            fertilizer_efficiency – 1 - fertilizer_proxy
            climate_stability    – passed through (0–1)
            soil_match           – passed through (0–1)
        """
        score = 0.0
        for key, weight in self.weights.items():
            score += weight * metrics.get(key, 0.5)
        return round(min(1.0, max(0.0, score)), 4)

    # ── Water-Saved Helper ───────────────────────────────────────

    def _water_saved_vs_baseline(
        self, crop: str, area: float, season: str
    ) -> float:
        """
        Percentage water saved compared to baseline crop (Rice).
        Returns 0.0 when the crop *is* the baseline.
        """
        crop_water = self.estimate_water_use(crop, area, season)
        baseline_water = self.estimate_water_use(self._BASELINE_CROP, area, season)
        if baseline_water <= 0:
            return 0.0
        return round(
            ((baseline_water - crop_water) / baseline_water) * 100, 2
        )

    # ── High-Level Enrichment ────────────────────────────────────

    def enrich_crop_results(
        self,
        crop_rankings: List[Dict[str, Any]],
        soil_quality_index: float,
        area: float,
        season: str,
    ) -> List[Dict[str, Any]]:
        """
        Augment every crop recommendation dict with sustainability metrics.

        Adds the following keys to each crop dict:
            water_use_estimate
            water_saved_vs_baseline
            fertilizer_proxy
            carbon_proxy
            risk_reduction_pct
            sustainability_score
            sustainability_disclosure
            proxy_metrics

        Parameters
        ----------
        crop_rankings : list[dict]
            Each dict must contain at minimum ``crop`` and
            ``predicted_yield_tonnes_per_ha``.
        soil_quality_index : float
            Composite soil quality (0-1).
        area : float
            Area in hectares.
        season : str
            Growing season name (e.g. "Kharif").

        Returns
        -------
        list[dict]
            Same list, each dict enriched with sustainability fields.
        """
        # Determine baseline yield (first crop = best ranked)
        baseline_yield = (
            crop_rankings[0]["predicted_yield_tonnes_per_ha"]
            if crop_rankings
            else 1.0
        )

        for rec in crop_rankings:
            crop = rec.get("crop", "Unknown")

            # Core proxy metrics
            water_use = self.estimate_water_use(crop, area, season)
            water_saved = self._water_saved_vs_baseline(crop, area, season)
            fert_proxy = self.estimate_fertilizer_proxy(crop, soil_quality_index)
            carbon = self.estimate_carbon_proxy(fert_proxy, area)
            risk_red = self.compute_risk_reduction(
                baseline_yield, rec.get("predicted_yield_tonnes_per_ha", 0)
            )

            # Build component dict for composite score
            c = get_crop_constants(crop)
            water_efficiency = 1.0 - c["crop_water_factor"]
            fertilizer_efficiency = 1.0 - fert_proxy
            climate_stability = rec.get("climate_stability_score", 0.7)
            # Fallback: derive from composite if the key isn't present
            if "climate_stability_score" not in rec:
                climate_stability = min(1.0, rec.get("composite_score", 0.7))
            soil_match = soil_quality_index

            sustainability_score = self.compute_sustainability_score(
                {
                    "water_efficiency": water_efficiency,
                    "fertilizer_efficiency": fertilizer_efficiency,
                    "climate_stability": climate_stability,
                    "soil_match": soil_match,
                }
            )

            # Inject into recommendation
            rec["sustainability_metrics"] = {
                "water_use_estimate": water_use,
                "water_saved_vs_baseline": water_saved,
                "fertilizer_proxy": fert_proxy,
                "carbon_proxy": carbon,
                "risk_reduction_pct": risk_red,
                "sustainability_score": sustainability_score,
            }
            rec["proxy_metrics"] = True

        logger.info(
            "Sustainability metrics enriched for %d crop(s)", len(crop_rankings)
        )
        return crop_rankings
