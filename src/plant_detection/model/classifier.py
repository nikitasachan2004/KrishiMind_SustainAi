"""Plant disease model construction and asset access."""

from __future__ import annotations

import json
from pathlib import Path

import timm
import torch.nn as nn


def get_model_paths() -> tuple[Path, Path]:
    """Resolve shared model assets from the existing disease module."""
    project_root = Path(__file__).resolve().parents[3]
    model_dir = project_root / "src" / "plant_disease_detection" / "models"
    return model_dir / "model.pt", model_dir / "classes.json"


def get_class_names(classes_path: Path) -> list[str]:
    """Load disease class names from JSON."""
    with classes_path.open("r", encoding="utf-8") as handle:
        classes = json.load(handle)

    if isinstance(classes, dict):
        return [classes[str(index)] for index in range(len(classes))]

    return list(classes)


class PlantDiseaseClassifier(nn.Module):
    """EfficientNetB0 backbone with the trained classification head."""

    def __init__(self, num_classes: int, pretrained: bool = False):
        super().__init__()
        self.backbone = timm.create_model(
            "efficientnet_b0",
            pretrained=pretrained,
            num_classes=0,
            global_pool="avg",
        )
        feature_dim = self.backbone.num_features
        self.head = nn.Sequential(
            nn.BatchNorm1d(feature_dim),
            nn.Dropout(0.3),
            nn.Linear(feature_dim, 256),
            nn.SiLU(),
            nn.BatchNorm1d(256),
            nn.Dropout(0.15),
            nn.Linear(256, num_classes),
        )

    def forward(self, inputs):
        features = self.backbone(inputs)
        return self.head(features)


def build_model(num_classes: int, pretrained: bool = False) -> PlantDiseaseClassifier:
    """Build the trained classifier architecture."""
    return PlantDiseaseClassifier(num_classes=num_classes, pretrained=pretrained)

