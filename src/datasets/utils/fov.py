# ABOUTME: Finds the circular field of view in a fundus photograph, and the mask of what is in it.
# ABOUTME: The mask is the pixels that are actually there, never a circle redrawn over them.

from dataclasses import dataclass

import numpy as np
from scipy import ndimage

#: Where the surround ends and the retina begins, as a fraction of the photograph's own 99th
#: percentile. Relative rather than fixed because exposure varies by more than an order of
#: magnitude across a screening dataset: a fixed line that suits a bright photograph cuts into a
#: dark one, cropping away retina that is there and shrinking the field to what happened to be
#: well lit.
RELATIVE_DARK = 0.05

#: A floor for the line, so JPEG noise in a near-black surround is not read as retina.
MIN_DARK = 4

#: A frame this full of retina has no surround to find, so there is no circle to fit.
FULL_FRAME = 0.98

#: What a fetcher declares when the dataset ships its own field-of-view masks.
FROM_MASK = "mask"
#: What a fetcher declares when the field has to be found in the photograph.
DETECT = "detect"


@dataclass(frozen=True)
class Circle:
    """The field of view in the photograph's own pixels."""

    cx: float
    cy: float
    r: float
    source: str


def dark_level(image: np.ndarray) -> float:
    """The intensity below which this particular photograph is surround rather than retina."""
    return max(MIN_DARK, RELATIVE_DARK * float(np.percentile(image.max(axis=2), 99)))


def mask_of(image: np.ndarray, dark: float | None = None) -> np.ndarray:
    """The photograph's own footprint: which pixels hold retina rather than surround.

    Holes are left in. A dead patch inside the field is a fact about the photograph, and a mask
    that fills it in would claim the crop transported something it did not.

    :param image: an ``(h, w, 3)`` array.
    :param dark: the line to use, or `None` to take it from the photograph itself.
    :return: ``(h, w)`` of 0 or 255.
    """
    level = dark_level(image) if dark is None else dark
    return np.where(image.max(axis=2) > level, 255, 0).astype(np.uint8)


def detect(image: np.ndarray, dark: float | None = None) -> Circle:
    """Find the field of view, fitting a circle to the edge the camera actually left behind.

    The fit deliberately ignores every boundary pixel lying on the frame edge: where the circle
    runs off the sensor — which is the usual case, and why so many fundus photographs are taller
    than they are wide — the cut edge is the sensor's, not the camera's, and including it would
    shrink the circle to the crop somebody else already made.

    :param image: an ``(h, w, 3)`` array.
    :return: the circle, with ``source`` recording how it was arrived at.
    """
    height, width = image.shape[:2]
    footprint = mask_of(image, dark) > 0
    if footprint.mean() >= FULL_FRAME:
        return Circle(width / 2, height / 2, max(width, height) / 2, "assumed_full_frame")

    field = _largest_component(ndimage.binary_fill_holes(footprint))
    edge = field & ~ndimage.binary_erosion(field)
    edge[0, :] = edge[-1, :] = False
    edge[:, 0] = edge[:, -1] = False
    ys, xs = np.nonzero(edge)
    if len(xs) < 3:
        return Circle(width / 2, height / 2, max(width, height) / 2, "assumed_full_frame")
    return _fit_circle(xs.astype(float), ys.astype(float))


def _largest_component(mask: np.ndarray) -> np.ndarray:
    """Drop specks — a lens flare, a burnt-in timestamp — that are not the field."""
    labels, count = ndimage.label(mask)
    if count <= 1:
        return mask
    sizes = ndimage.sum_labels(mask, labels, index=range(1, count + 1))
    return labels == (int(np.argmax(sizes)) + 1)


def _fit_circle(xs: np.ndarray, ys: np.ndarray) -> Circle:
    """Least-squares circle through the visible arc (Kasa's linearisation)."""
    a = np.column_stack([xs, ys, np.ones_like(xs)])
    b = xs**2 + ys**2
    (u, v, w), *_ = np.linalg.lstsq(a, b, rcond=None)
    cx, cy = u / 2, v / 2
    return Circle(float(cx), float(cy), float(np.sqrt(w + cx**2 + cy**2)), "detected")
