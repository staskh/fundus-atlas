# ABOUTME: Resizes a native frame to a built size: photographs interpolated, masks never.
# ABOUTME: One place, so two datasets cannot disagree about what 512 means.

import numpy as np
from PIL import Image


def photograph(image: np.ndarray, size: int) -> np.ndarray:
    """Resize a photograph to ``size`` square.

    Lanczos, because a photograph is a continuous signal and the store is read by models trained
    on ordinarily resampled images.
    """
    return np.asarray(Image.fromarray(image).resize((size, size), Image.LANCZOS))


def mask(labels: np.ndarray, size: int) -> np.ndarray:
    """Resize a mask or label map to ``size`` square, without interpolation.

    Nearest neighbour is not a shortcut here: interpolating between class 1 and class 3 would
    invent class 2, and between vessel and background a half-vessel that no threshold recovers.
    """
    return np.asarray(Image.fromarray(labels).resize((size, size), Image.NEAREST))
