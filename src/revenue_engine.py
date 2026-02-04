"""
Revenue Engine Module
=====================
Calculates expected revenue with climate and soil risk adjustments.
Deterministic and reproducible computations.

Author: AgroPro ML Team
"""

import numpy as np
import logging
from typing import Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# ============================================================================
# CONSTANTS - Risk Penalty Thresholds
# ============================================================================

# Climate risk thresholds
RAINFALL_ANOMALY_SEVERE_THRESHOLD = -0.5  # Severe drought
RAINFALL_ANOMALY_PENALTY = 0.10  # 10% reduction

HEATWAVE_HIGH_THRESHOLD = 3  # High heatwave count
HEATWAVE_PENALTY = 0.05  # 5% reduction

# Soil quality thresholds
SOIL_QUALITY_LOW_THRESHOLD = 0.5  # Low soil quality index
SOIL_PENALTY = 0.08  # 8% reduction


@dataclass
class RevenueInput:
    """Input parameters for revenue calculation."""
    predicted_yield: float  # tonnes/hectare
    predicted_price: float  # price per tonne
    area: float = 1.0  # hectares (default 1 for per-hectare calculation)
    
    # Risk factors
    rainfall_anomaly: float = 0.0
    heatwave_count: int = 0
    soil_quality_index: float = 1.0


@dataclass
class RevenueOutput:
    """Output from revenue calculation."""
    base_revenue: float
    adjusted_revenue: float
    
    # Penalty breakdown
    climate_penalty_pct: float
    soil_penalty_pct: float
    total_penalty_pct: float
    
    # Components
    predicted_yield: float
    predicted_price: float
    area: float


class RevenueEngine:
    """
    Deterministic revenue calculation engine with risk adjustments.
    
    Revenue Formula:
        base_revenue = predicted_yield * predicted_price * area
        adjusted_revenue = base_revenue * (1 - total_penalty)
    
    Penalties:
        - Climate risk: rainfall_anomaly < -0.5 → -10%
        - Heatwave risk: heatwave_count > 3 → -5%
        - Soil risk: soil_quality_index < 0.5 → -8%
    """
    
    def __init__(
        self,
        rainfall_anomaly_threshold: float = RAINFALL_ANOMALY_SEVERE_THRESHOLD,
        rainfall_penalty: float = RAINFALL_ANOMALY_PENALTY,
        heatwave_threshold: int = HEATWAVE_HIGH_THRESHOLD,
        heatwave_penalty: float = HEATWAVE_PENALTY,
        soil_threshold: float = SOIL_QUALITY_LOW_THRESHOLD,
        soil_penalty: float = SOIL_PENALTY,
    ):
        """
        Initialize revenue engine with configurable thresholds.
        
        Args:
            rainfall_anomaly_threshold: Threshold for drought penalty
            rainfall_penalty: Penalty percentage for drought
            heatwave_threshold: Threshold for heatwave penalty
            heatwave_penalty: Penalty percentage for heatwaves
            soil_threshold: Threshold for soil quality penalty
            soil_penalty: Penalty percentage for poor soil
        """
        self.rainfall_anomaly_threshold = rainfall_anomaly_threshold
        self.rainfall_penalty = rainfall_penalty
        self.heatwave_threshold = heatwave_threshold
        self.heatwave_penalty = heatwave_penalty
        self.soil_threshold = soil_threshold
        self.soil_penalty = soil_penalty
        
        logger.info("RevenueEngine initialized with thresholds:")
        logger.info(f"  Rainfall anomaly < {rainfall_anomaly_threshold} → -{rainfall_penalty*100:.0f}%")
        logger.info(f"  Heatwave count > {heatwave_threshold} → -{heatwave_penalty*100:.0f}%")
        logger.info(f"  Soil quality < {soil_threshold} → -{soil_penalty*100:.0f}%")
    
    def calculate_climate_penalty(
        self, 
        rainfall_anomaly: float, 
        heatwave_count: int
    ) -> float:
        """
        Calculate climate-based penalty.
        
        Args:
            rainfall_anomaly: Standardized rainfall anomaly (negative = drought)
            heatwave_count: Number of heatwave events
            
        Returns:
            Total climate penalty as decimal (e.g., 0.15 = 15%)
        """
        penalty = 0.0
        
        # Drought penalty
        if rainfall_anomaly < self.rainfall_anomaly_threshold:
            penalty += self.rainfall_penalty
            logger.debug(f"Applied drought penalty: {self.rainfall_penalty*100:.0f}% "
                        f"(anomaly={rainfall_anomaly:.2f})")
        
        # Heatwave penalty
        if heatwave_count > self.heatwave_threshold:
            penalty += self.heatwave_penalty
            logger.debug(f"Applied heatwave penalty: {self.heatwave_penalty*100:.0f}% "
                        f"(count={heatwave_count})")
        
        return penalty
    
    def calculate_soil_penalty(self, soil_quality_index: float) -> float:
        """
        Calculate soil quality penalty.
        
        Args:
            soil_quality_index: Soil quality index (0-1 scale)
            
        Returns:
            Soil penalty as decimal
        """
        if soil_quality_index < self.soil_threshold:
            logger.debug(f"Applied soil penalty: {self.soil_penalty*100:.0f}% "
                        f"(index={soil_quality_index:.2f})")
            return self.soil_penalty
        return 0.0
    
    def calculate_revenue(self, inputs: RevenueInput) -> RevenueOutput:
        """
        Calculate expected revenue with risk adjustments.
        
        Args:
            inputs: RevenueInput dataclass with all parameters
            
        Returns:
            RevenueOutput with base and adjusted revenue
        """
        # Validate inputs
        if inputs.predicted_yield < 0:
            logger.warning(f"Negative yield ({inputs.predicted_yield}), clamping to 0")
            inputs.predicted_yield = 0.0
            
        if inputs.predicted_price < 0:
            logger.warning(f"Negative price ({inputs.predicted_price}), clamping to 0")
            inputs.predicted_price = 0.0
        
        # Calculate base revenue
        base_revenue = inputs.predicted_yield * inputs.predicted_price * inputs.area
        
        # Calculate penalties
        climate_penalty = self.calculate_climate_penalty(
            inputs.rainfall_anomaly, 
            inputs.heatwave_count
        )
        
        soil_penalty = self.calculate_soil_penalty(inputs.soil_quality_index)
        
        total_penalty = climate_penalty + soil_penalty
        
        # Cap total penalty at 50% to avoid extreme reductions
        total_penalty = min(total_penalty, 0.5)
        
        # Calculate adjusted revenue
        adjusted_revenue = base_revenue * (1 - total_penalty)
        
        return RevenueOutput(
            base_revenue=base_revenue,
            adjusted_revenue=adjusted_revenue,
            climate_penalty_pct=climate_penalty * 100,
            soil_penalty_pct=soil_penalty * 100,
            total_penalty_pct=total_penalty * 100,
            predicted_yield=inputs.predicted_yield,
            predicted_price=inputs.predicted_price,
            area=inputs.area,
        )
    
    def calculate(
        self,
        predicted_yield: float,
        predicted_price: float,
        area: float = 1.0,
        rainfall_anomaly: float = 0.0,
        heatwave_count: int = 0,
        soil_quality_index: float = 1.0,
    ) -> RevenueOutput:
        """
        Convenience method for revenue calculation.
        
        Args:
            predicted_yield: Predicted yield (tonnes/hectare)
            predicted_price: Predicted price (per tonne)
            area: Land area in hectares
            rainfall_anomaly: Standardized rainfall anomaly
            heatwave_count: Number of heatwave events
            soil_quality_index: Soil quality index (0-1)
            
        Returns:
            RevenueOutput with detailed breakdown
        """
        inputs = RevenueInput(
            predicted_yield=predicted_yield,
            predicted_price=predicted_price,
            area=area,
            rainfall_anomaly=rainfall_anomaly,
            heatwave_count=heatwave_count,
            soil_quality_index=soil_quality_index,
        )
        return self.calculate_revenue(inputs)


def compute_expected_revenue(
    predicted_yield: float,
    predicted_price: float,
    area: float = 1.0,
    rainfall_anomaly: float = 0.0,
    heatwave_count: int = 0,
    soil_quality_index: float = 1.0,
) -> Dict[str, float]:
    """
    Simple function interface for revenue calculation.
    
    Args:
        predicted_yield: Predicted yield (tonnes/hectare)
        predicted_price: Predicted price (per tonne)
        area: Land area in hectares
        rainfall_anomaly: Standardized rainfall anomaly
        heatwave_count: Number of heatwave events
        soil_quality_index: Soil quality index (0-1)
        
    Returns:
        Dictionary with revenue breakdown
    """
    engine = RevenueEngine()
    output = engine.calculate(
        predicted_yield=predicted_yield,
        predicted_price=predicted_price,
        area=area,
        rainfall_anomaly=rainfall_anomaly,
        heatwave_count=heatwave_count,
        soil_quality_index=soil_quality_index,
    )
    
    return {
        "base_revenue": output.base_revenue,
        "adjusted_revenue": output.adjusted_revenue,
        "climate_penalty_pct": output.climate_penalty_pct,
        "soil_penalty_pct": output.soil_penalty_pct,
        "total_penalty_pct": output.total_penalty_pct,
    }


if __name__ == "__main__":
    # Test revenue engine
    logging.basicConfig(level=logging.INFO)
    
    engine = RevenueEngine()
    
    # Test case 1: Normal conditions
    print("\n" + "=" * 50)
    print("Test 1: Normal conditions")
    output = engine.calculate(
        predicted_yield=2.5,
        predicted_price=2000,
        area=1.0,
        rainfall_anomaly=0.0,
        heatwave_count=1,
        soil_quality_index=0.8,
    )
    print(f"Base revenue: ₹{output.base_revenue:,.2f}")
    print(f"Adjusted revenue: ₹{output.adjusted_revenue:,.2f}")
    print(f"Total penalty: {output.total_penalty_pct:.1f}%")
    
    # Test case 2: Drought conditions
    print("\n" + "=" * 50)
    print("Test 2: Drought conditions")
    output = engine.calculate(
        predicted_yield=2.5,
        predicted_price=2000,
        area=1.0,
        rainfall_anomaly=-0.7,  # Severe drought
        heatwave_count=1,
        soil_quality_index=0.8,
    )
    print(f"Base revenue: ₹{output.base_revenue:,.2f}")
    print(f"Adjusted revenue: ₹{output.adjusted_revenue:,.2f}")
    print(f"Climate penalty: {output.climate_penalty_pct:.1f}%")
    
    # Test case 3: Multiple risk factors
    print("\n" + "=" * 50)
    print("Test 3: Multiple risk factors")
    output = engine.calculate(
        predicted_yield=2.5,
        predicted_price=2000,
        area=1.0,
        rainfall_anomaly=-0.6,  # Drought
        heatwave_count=5,  # High heatwaves
        soil_quality_index=0.3,  # Poor soil
    )
    print(f"Base revenue: ₹{output.base_revenue:,.2f}")
    print(f"Adjusted revenue: ₹{output.adjusted_revenue:,.2f}")
    print(f"Climate penalty: {output.climate_penalty_pct:.1f}%")
    print(f"Soil penalty: {output.soil_penalty_pct:.1f}%")
    print(f"Total penalty: {output.total_penalty_pct:.1f}%")
