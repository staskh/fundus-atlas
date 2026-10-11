# ABOUTME: Resizes the crop to the size a model asks for, when it is read: photographs interpolated,
# ABOUTME: masks never. One place, so two readers cannot disagree about what 512 means.

from pathlib import Path

import numpy as np
from PIL import Image

from . import paths


def photograph(image: np.ndarray, size: int) -> np.ndarray:
    """Resize a photograph to ``size`` square.

    Lanczos, because a photograph is a continuous signal and the store is read by models trained
    on ordinarily resampled images.
    """
    return np.asarray(Image.fromarray(image).resize((size, size), Image.LANCZOS))


def read_photograph(store: Path, key: str, size: int) -> np.ndarray:
    """One photograph of a store, read from its crop and resized to ``size`` square, as RGB."""
    with Image.open(paths.layer(store, "images") / f"{key}.png") as image:
        return photograph(np.asarray(image.convert("RGB")), size)


def mask(labels: np.ndarray, size: int) -> np.ndarray:
    """Resize a mask or label map to ``size`` square, without interpolation.

    Nearest neighbour is not a shortcut here: interpolating between class 1 and class 3 would
    invent class 2, and between vessel and background a half-vessel that no threshold recovers.
    """
    return np.asarray(Image.fromarray(labels).resize((size, size), Image.NEAREST))
