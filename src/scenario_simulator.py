"""
Scenario Simulator Module
=========================
Enables what-if analysis by applying scenario overrides to climate parameters.
Supports rainfall and temperature delta simulations.

Author: AgroPro ML Team
"""

import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from copy import deepcopy

# Handle imports for both module and standalone execution
try:
    from .crop_optimizer import CropOptimizer, CropScore, get_default_candidate_crops
except ImportError:
    from crop_optimizer import CropOptimizer, CropScore, get_default_candidate_crops

logger = logging.getLogger(__name__)


@dataclass
class ScenarioConfig:
    """Configuration for a simulation scenario."""
    name: str
    description: str = ""
    
    # Climate overrides (deltas)
    rainfall_delta_percent: float = 0.0  # % change in rainfall
    temperature_delta: float = 0.0  # Absolute change in temperature (°C)
    
    # Optional direct overrides
    rainfall_anomaly_override: Optional[float] = None
    heatwave_count_override: Optional[int] = None


@dataclass
class ScenarioResult:
    """Results from a scenario simulation."""
    scenario: ScenarioConfig
    district: str
    season: str
    
    # Modified climate features
    adjusted_climate_features: Dict[str, float] = field(default_factory=dict)
    
    # Crop rankings
    crop_rankings: List[CropScore] = field(default_factory=list)
    
    # Comparison to baseline (if available)
    baseline_rankings: Optional[List[CropScore]] = None
    ranking_changes: Dict[str, int] = field(default_factory=dict)


# ============================================================================
# PREDEFINED SCENARIOS
# ============================================================================

SCENARIOS = {
    "baseline": ScenarioConfig(
        name="Baseline",
        description="Current conditions, no modifications",
    ),
    "drought_mild": ScenarioConfig(
        name="Mild Drought",
        description="-10% rainfall scenario",
        rainfall_delta_percent=-10.0,
    ),
    "drought_moderate": ScenarioConfig(
        name="Moderate Drought",
        description="-20% rainfall scenario",
        rainfall_delta_percent=-20.0,
    ),
    "drought_severe": ScenarioConfig(
        name="Severe Drought",
        description="-30% rainfall scenario",
        rainfall_delta_percent=-30.0,
    ),
    "excess_rain": ScenarioConfig(
        name="Excess Rainfall",
        description="+20% rainfall scenario",
        rainfall_delta_percent=20.0,
    ),
    "warming_mild": ScenarioConfig(
        name="Mild Warming",
        description="+1°C temperature increase",
        temperature_delta=1.0,
    ),
    "warming_moderate": ScenarioConfig(
        name="Moderate Warming",
        description="+2°C temperature increase",
        temperature_delta=2.0,
    ),
    "warming_severe": ScenarioConfig(
        name="Severe Warming",
        description="+3°C temperature increase",
        temperature_delta=3.0,
    ),
    "combined_stress": ScenarioConfig(
        name="Combined Stress",
        description="-20% rainfall + 2°C warming",
        rainfall_delta_percent=-20.0,
        temperature_delta=2.0,
    ),
}


class ScenarioSimulator:
    """
    What-if scenario simulator for crop planning.
    
    Allows testing different climate scenarios and their impact on
    crop recommendations and expected revenues.
    """
    
    def __init__(self, optimizer: Optional[CropOptimizer] = None):
        """
        Initialize scenario simulator.
        
        Args:
            optimizer: CropOptimizer instance (creates new one if not provided)
        """
        self.optimizer = optimizer or CropOptimizer()
        
        if optimizer is None:
            self.optimizer.load_models()
        
        logger.info("ScenarioSimulator initialized")
    
    def apply_scenario(
        self,
        base_climate: Dict[str, float],
        scenario: ScenarioConfig,
    ) -> Dict[str, float]:
        """
        Apply scenario modifications to climate features.
        
        Args:
            base_climate: Base climate feature dictionary
            scenario: Scenario configuration with deltas
            
        Returns:
            Modified climate features
        """
        adjusted = deepcopy(base_climate)
        
        # Apply rainfall delta
        if scenario.rainfall_delta_percent != 0:
            pct_change = scenario.rainfall_delta_percent / 100.0
            
            for key in ["rainfall_mean", "monsoon_rainfall", "seasonal_rainfall"]:
                if key in adjusted:
                    adjusted[key] = adjusted[key] * (1 + pct_change)
            
            # Adjust rainfall anomaly based on delta
            current_anomaly = adjusted.get("rainfall_anomaly", 0)
            # -20% rainfall roughly corresponds to -0.5 anomaly shift
            anomaly_shift = scenario.rainfall_delta_percent / 40.0
            adjusted["rainfall_anomaly"] = current_anomaly + anomaly_shift
            
            logger.info(f"Applied rainfall delta: {scenario.rainfall_delta_percent:+.0f}%")
        
        # Apply temperature delta
        if scenario.temperature_delta != 0:
            for key in ["avg_temp_mean", "avg_temp_max", "avg_temp_min"]:
                if key in adjusted:
                    adjusted[key] = adjusted[key] + scenario.temperature_delta
            
            # Adjust growing degree days
            if "growing_degree_days" in adjusted:
                adjusted["growing_degree_days"] += scenario.temperature_delta
            
            # Increase heatwave likelihood with warming
            if scenario.temperature_delta > 1.5:
                current_heatwaves = adjusted.get("heatwave_count", 0)
                additional = int(scenario.temperature_delta)
                adjusted["heatwave_count"] = current_heatwaves + additional
            
            logger.info(f"Applied temperature delta: {scenario.temperature_delta:+.1f}°C")
        
        # Apply direct overrides if specified
        if scenario.rainfall_anomaly_override is not None:
            adjusted["rainfall_anomaly"] = scenario.rainfall_anomaly_override
        
        if scenario.heatwave_count_override is not None:
            adjusted["heatwave_count"] = scenario.heatwave_count_override
        
        return adjusted
    
    def simulate(
        self,
        district: str,
        season: str,
        base_climate: Dict[str, float],
        soil_features: Dict[str, float],
        scenario: ScenarioConfig,
        candidate_crops: Optional[List[str]] = None,
        top_n: int = 5,
        baseline: Optional[List[CropScore]] = None,
    ) -> ScenarioResult:
        """
        Run a scenario simulation.
        
        Args:
            district: District name
            season: Season name
            base_climate: Base climate features
            soil_features: Soil features
            scenario: Scenario configuration
            candidate_crops: List of crops to evaluate
            top_n: Number of top crops to return
            baseline: Baseline rankings for comparison
            
        Returns:
            ScenarioResult with modified rankings
        """
        logger.info("=" * 60)
        logger.info(f"Running scenario: {scenario.name}")
        logger.info(f"  {scenario.description}")
        logger.info("=" * 60)
        
        crops = candidate_crops or get_default_candidate_crops()
        
        # Apply scenario modifications
        adjusted_climate = self.apply_scenario(base_climate, scenario)
        
        # Run optimization with adjusted features
        rankings = self.optimizer.optimize(
            district=district,
            season=season,
            candidate_crops=crops,
            climate_features=adjusted_climate,
            soil_features=soil_features,
            top_n=top_n,
        )
        
        # Calculate ranking changes if baseline provided
        ranking_changes = {}
        if baseline:
            baseline_order = {s.crop_name: i for i, s in enumerate(baseline)}
            for i, score in enumerate(rankings):
                if score.crop_name in baseline_order:
                    change = baseline_order[score.crop_name] - i
                    ranking_changes[score.crop_name] = change
        
        return ScenarioResult(
            scenario=scenario,
            district=district,
            season=season,
            adjusted_climate_features=adjusted_climate,
            crop_rankings=rankings,
            baseline_rankings=baseline,
            ranking_changes=ranking_changes,
        )
    
    def run_multiple_scenarios(
        self,
        district: str,
        season: str,
        base_climate: Dict[str, float],
        soil_features: Dict[str, float],
        scenario_names: Optional[List[str]] = None,
        candidate_crops: Optional[List[str]] = None,
        top_n: int = 5,
    ) -> Dict[str, ScenarioResult]:
        """
        Run multiple scenarios and compare results.
        
        Args:
            district: District name
            season: Season name
            base_climate: Base climate features
            soil_features: Soil features
            scenario_names: List of scenario names to run (default: all)
            candidate_crops: List of crops to evaluate
            top_n: Number of top crops per scenario
            
        Returns:
            Dictionary mapping scenario names to results
        """
        scenarios_to_run = scenario_names or list(SCENARIOS.keys())
        results = {}
        
        # Run baseline first
        baseline_result = None
        if "baseline" in scenarios_to_run:
            baseline_result = self.simulate(
                district, season, base_climate, soil_features,
                SCENARIOS["baseline"], candidate_crops, top_n
            )
            results["baseline"] = baseline_result
            scenarios_to_run = [s for s in scenarios_to_run if s != "baseline"]
        
        # Run other scenarios with comparison to baseline
        baseline_rankings = baseline_result.crop_rankings if baseline_result else None
        
        for scenario_name in scenarios_to_run:
            if scenario_name not in SCENARIOS:
                logger.warning(f"Unknown scenario: {scenario_name}")
                continue
            
            result = self.simulate(
                district, season, base_climate, soil_features,
                SCENARIOS[scenario_name], candidate_crops, top_n,
                baseline=baseline_rankings
            )
            results[scenario_name] = result
        
        return results
    
    def compare_scenarios(
        self,
        results: Dict[str, ScenarioResult],
    ) -> pd.DataFrame:
        """
        Create comparison table across scenarios.
        
        Args:
            results: Dictionary of scenario results
            
        Returns:
            DataFrame comparing top crops across scenarios
        """
        rows = []
        
        for scenario_name, result in results.items():
            for rank, score in enumerate(result.crop_rankings, 1):
                rows.append({
                    "scenario": scenario_name,
                    "rank": rank,
                    "crop": score.crop_name,
                    "composite_score": score.composite_score,
                    "predicted_yield": score.predicted_yield,
                    "predicted_revenue": score.predicted_revenue,
                    "climate_stability": score.climate_stability_score,
                })
        
        df = pd.DataFrame(rows)
        return df
    
    def format_scenario_report(
        self,
        result: ScenarioResult,
    ) -> str:
        """
        Format a scenario result as a readable report.
        
        Args:
            result: ScenarioResult to format
            
        Returns:
            Formatted string report
        """
        lines = [
            "=" * 60,
            f"SCENARIO: {result.scenario.name}",
            f"Description: {result.scenario.description}",
            f"District: {result.district}",
            f"Season: {result.season}",
            "=" * 60,
            "",
            "Climate Adjustments:",
        ]
        
        if result.scenario.rainfall_delta_percent != 0:
            lines.append(f"  Rainfall: {result.scenario.rainfall_delta_percent:+.0f}%")
        if result.scenario.temperature_delta != 0:
            lines.append(f"  Temperature: {result.scenario.temperature_delta:+.1f}°C")
        
        lines.extend([
            "",
            "TOP CROP RECOMMENDATIONS:",
            "-" * 40,
        ])
        
        for i, score in enumerate(result.crop_rankings, 1):
            change_str = ""
            if result.ranking_changes and score.crop_name in result.ranking_changes:
                change = result.ranking_changes[score.crop_name]
                if change > 0:
                    change_str = f" (↑{change})"
                elif change < 0:
                    change_str = f" (↓{abs(change)})"
            
            lines.extend([
                f"\n{i}. {score.crop_name}{change_str}",
                f"   Score: {score.composite_score:.3f}",
                f"   Yield: {score.predicted_yield:.2f} t/ha",
                f"   Revenue: ₹{score.predicted_revenue:,.0f}/ha",
            ])
        
        return "\n".join(lines)


def run_demo_simulation():
    """Run a demonstration scenario simulation."""
    logger.info("Running demo scenario simulation...")
    
    simulator = ScenarioSimulator()
    
    # Base conditions
    base_climate = {
        "rainfall_mean": 120,
        "rainfall_anomaly": 0.0,
        "monsoon_rainfall": 850,
        "avg_temp_mean": 28,
        "heatwave_count": 1,
        "growing_degree_days": 16,
    }
    
    soil_features = {
        "soil_quality_index": 0.85,
    }
    
    # Run key scenarios
    scenarios_to_run = ["baseline", "drought_moderate", "warming_moderate", "combined_stress"]
    
    results = simulator.run_multiple_scenarios(
        district="Guntur",
        season="Kharif",
        base_climate=base_climate,
        soil_features=soil_features,
        scenario_names=scenarios_to_run,
        top_n=5,
    )
    
    # Print reports
    for name, result in results.items():
        print("\n" + simulator.format_scenario_report(result))
    
    # Create comparison
    comparison_df = simulator.compare_scenarios(results)
    print("\n" + "=" * 60)
    print("SCENARIO COMPARISON (Top 3 crops)")
    print("=" * 60)
    
    pivot = comparison_df[comparison_df["rank"] <= 3].pivot_table(
        index="crop",
        columns="scenario",
        values="composite_score",
        aggfunc="first"
    ).round(3)
    
    print(pivot.to_string())
    
    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_demo_simulation()
