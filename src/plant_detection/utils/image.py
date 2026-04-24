"""Image preprocessing utilities for plant disease inference."""

from __future__ import annotations

from pathlib import Path

from PIL import Image
from torchvision import transforms

_IMAGE_SIZE = 224
_IMAGENET_MEAN = [0.485, 0.456, 0.406]
_IMAGENET_STD = [0.229, 0.224, 0.225]

_TRANSFORMS = transforms.Compose(
    [
        transforms.Resize((_IMAGE_SIZE, _IMAGE_SIZE), interpolation=transforms.InterpolationMode.BILINEAR),
        transforms.ToTensor(),
        transforms.Normalize(mean=_IMAGENET_MEAN, std=_IMAGENET_STD),
    ]
)


def load_image_tensor(image_path: Path):
    """Load an image path into a model-ready tensor."""
    with Image.open(image_path) as image:
        if image.mode == "RGBA":
            rgb_image = Image.new("RGB", image.size, (255, 255, 255))
            rgb_image.paste(image, mask=image.split()[3])
            image = rgb_image
        elif image.mode != "RGB":
            image = image.convert("RGB")

        tensor = _TRANSFORMS(image)

    return tensor.unsqueeze(0)

