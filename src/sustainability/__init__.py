"""
Sustainability Impact Layer for KrishiMind SustainAI.
Provides proxy-based resource and environmental impact estimation.
"""

from .impact_engine import SustainabilityImpactEngine
from .crop_constants import CROP_CONSTANTS

__all__ = ["SustainabilityImpactEngine", "CROP_CONSTANTS"]
