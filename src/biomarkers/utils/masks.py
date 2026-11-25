# ABOUTME: The masks an adapter draws for itself from what it is handed: the optic disc as a filled
# ABOUTME: circle, at the pixel-centre convention the disc is handed over in.

import numpy as np


def disc_mask(side: int, x: float, y: float, radius: float) -> np.ndarray:
    """The disc `(x, y, radius)` as a filled circle on a `side` × `side` frame.

    **Pixel `i`'s centre is at `i`**, the convention the disc is handed over in, so this is the
    circle the synthetic store draws as its disc mask rather than one half a pixel off it.
    """
    grid = np.arange(side, dtype=np.float64)
    px, py = np.meshgrid(grid, grid)
    return (px - x) ** 2 + (py - y) ** 2 <= radius * radius
