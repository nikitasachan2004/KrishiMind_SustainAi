"""Main callable plant disease inference entry point."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Dict

import torch

from src.plant_detection.model.classifier import build_model, get_class_names, get_model_paths
from src.plant_detection.utils.image import load_image_tensor

_FALLBACK_RESULT: Dict[str, float | str] = {"disease": "unknown", "confidence": 0.0}


@lru_cache(maxsize=1)
def _load_predictor() -> tuple[torch.nn.Module, list[str], torch.device]:
    """Load and cache the disease model once per process."""
    model_path, classes_path = get_model_paths()
    class_names = get_class_names(classes_path)
    device = torch.device("cpu")

    model = build_model(num_classes=len(class_names), pretrained=False)
    checkpoint = torch.load(model_path, map_location=device)
    model.load_state_dict(checkpoint)
    model = model.to(device)
    model.eval()

    return model, class_names, device


def predict_disease(image_path: str) -> dict:
    """
    Input: image path
    Output: {
        "disease": str,
        "confidence": float
    }
    """
    try:
        if not image_path:
            return dict(_FALLBACK_RESULT)

        path = Path(image_path)
        if not path.exists() or not path.is_file():
            return dict(_FALLBACK_RESULT)

        model, class_names, device = _load_predictor()
        tensor = load_image_tensor(path).to(device)

        with torch.no_grad():
            logits = model(tensor)
            probabilities = torch.softmax(logits, dim=1)[0]

        confidence, predicted_index = torch.max(probabilities, dim=0)
        disease = class_names[predicted_index.item()]

        return {
            "disease": disease,
            "confidence": round(float(confidence.item()), 4),
        }
    except Exception:
        return dict(_FALLBACK_RESULT)

