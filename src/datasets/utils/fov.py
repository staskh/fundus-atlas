# ABOUTME: Finds the circular field of view in a fundus photograph, and the mask of what is in it.
# ABOUTME: The mask is the pixels that are actually there, never a circle redrawn over them.

from dataclasses import dataclass

import numpy as np
from scipy import ndimage
from scipy.spatial import ConvexHull

#: Width of the ring, in pixels, sampled to learn what this photograph's surround looks like.
BORDER = 5

#: How far a pixel may sit from the surround's own colour, per channel, and still be surround.
#: Taken as a fraction of the photograph's 99th percentile, because exposure varies by more than an
#: order of magnitude across a screening dataset and a fixed tolerance that suits a bright
#: photograph eats into the rim of a dark one.
RELATIVE_TOLERANCE = 0.05

#: Bounds on that tolerance: loose enough for the ringing a JPEG leaves along the rim, tight enough
#: that dim retina is not mistaken for a black surround.
MIN_TOLERANCE = 4
MAX_TOLERANCE = 20

#: How much of the border ring must be one colour for there to be a surround at all. Below this,
#: retina reaches the frame's edge all the way round and there is no circle to find.
MIN_RING_SHARE = 0.4

#: A frame this full of retina has no surround worth speaking of.
FULL_FRAME = 0.98

#: What a fetcher declares when the dataset ships its own field-of-view masks.
FROM_MASK = "mask"
#: What a fetcher declares when the field has to be found in the photograph.
DETECT = "detect"
#: What a fetcher declares when there is no field to find — an archive of crops rather than
#: photographs — and the frame is to be taken as it is.
WHOLE = "whole"

#: A fitted circle must be at least this much of the region it was fitted to, and at most this
#: many times it. Outside that the fit has not found a field: a nearly straight arc admits any
#: radius, and a crop that shows only a sliver of the field edge produces exactly that.
SMALLEST_FIT = 0.5
LARGEST_FIT = 3.0


@dataclass(frozen=True)
class Circle:
    """The field of view in the photograph's own pixels."""

    cx: float
    cy: float
    r: float
    source: str


def whole(image: np.ndarray) -> Circle:
    """The frame itself, for a photograph with no field of view in it to find."""
    height, width = image.shape[:2]
    return Circle(width / 2, height / 2, max(width, height) / 2, "assumed_full_frame")


def tolerance(image: np.ndarray) -> float:
    """How close to the surround's colour a pixel must be to count as surround."""
    scale = RELATIVE_TOLERANCE * float(np.percentile(image, 99))
    return float(np.clip(scale, MIN_TOLERANCE, MAX_TOLERANCE))


def surround_colour(image: np.ndarray) -> np.ndarray | None:
    """The colour this camera painted outside the field, or `None` if it painted nothing.

    Cameras and exporters disagree about it: most write black, some write white, some a flat grey.
    What every surround has in common is that it is **one colour and it reaches the edge of the
    frame** — so that, rather than darkness, is what is looked for. A brightness test hands back
    the whole frame as field of view on a photograph whose surround happens to be white.
    """
    ring = np.concatenate(
        [
            image[:BORDER].reshape(-1, 3),
            image[-BORDER:].reshape(-1, 3),
            image[:, :BORDER].reshape(-1, 3),
            image[:, -BORDER:].reshape(-1, 3),
        ]
    ).astype(float)
    candidate = np.median(ring, axis=0)
    share = float((np.abs(ring - candidate).max(axis=1) <= tolerance(image)).mean())
    return candidate if share >= MIN_RING_SHARE else None


def mask_of(image: np.ndarray) -> np.ndarray:
    """The camera's field of view: everything but the surround.

    The field is one connected region: a burnt-in timestamp or a lens flare sitting out in the
    surround is not part of what the camera was looking at, whatever colour it is.

    A dead patch in the middle of the retina stays *inside* the mask. The mask says where the
    camera was looking, not where the photograph came out well, and a patch of no signal is still
    within the field — which is why the surround is found by reaching in from the frame's edge
    rather than by collecting every pixel that resembles it.

    :param image: an ``(h, w, 3)`` array.
    :return: ``(h, w)`` of 0 or 255.
    """
    colour = surround_colour(image)
    if colour is None:
        return np.full(image.shape[:2], 255, dtype=np.uint8)
    resembles = np.abs(image.astype(float) - colour).max(axis=2) <= tolerance(image)
    surround = _reaching_the_frame(resembles)
    if surround.mean() >= FULL_FRAME:
        # Every pixel resembles the border because the border is retina: there is no surround.
        return np.full(image.shape[:2], 255, dtype=np.uint8)
    field = _largest_component(~surround)
    return np.where(field, 255, 0).astype(np.uint8)


def detect(image: np.ndarray) -> Circle:
    """Find the field of view, fitting a circle to the edge the camera actually left behind.

    Two things the fit deliberately ignores, each for the same reason — a point that is not on the
    camera's circle must not be allowed to pull the circle towards it:

    - **Boundary pixels on the frame edge.** Where the circle runs off the sensor — the usual case,
      and why so many fundus photographs are taller than they are wide — the cut edge is the
      sensor's, not the camera's, and fitting to it would shrink the field to the crop somebody
      else already made.
    - **Everything but the outline's convex hull.** A dim sector, a ragged rim or a shadow at the
      edge takes a bite out of the mask, and the edge pixels along that bite sit well inside the
      true field. The hull spans such a bite instead of following it in.

    :param image: an ``(h, w, 3)`` array.
    :return: the circle, with ``source`` recording how it was arrived at.
    """
    height, width = image.shape[:2]
    whole_frame = Circle(width / 2, height / 2, max(width, height) / 2, "assumed_full_frame")

    field = mask_of(image) > 0
    if field.mean() >= FULL_FRAME:
        return whole_frame

    field = _largest_component(ndimage.binary_fill_holes(field))
    edge = field & ~ndimage.binary_erosion(field)
    ys, xs = np.nonzero(edge)
    rim = _on_the_cameras_circle(np.column_stack([xs, ys]).astype(float), height, width)
    if len(rim) < 3:
        return whole_frame
    circle = _fit_circle(rim[:, 0], rim[:, 1])
    return circle if _plausible(circle, field) else whole_frame


def _plausible(circle: Circle, field: np.ndarray) -> bool:
    """Whether a fitted circle could be the field the mask shows.

    The check is against the region fitted to rather than against the frame, because a photograph
    with wide margins has a small field and that is not an error. What is an error is a circle far
    smaller or far larger than the thing it was fitted to.
    """
    ys, xs = np.nonzero(field)
    if not len(xs):
        return False
    across = max(xs.max() - xs.min(), ys.max() - ys.min()) + 1
    return SMALLEST_FIT * across <= 2 * circle.r <= LARGEST_FIT * across


def _reaching_the_frame(resembles: np.ndarray) -> np.ndarray:
    """The parts of a surround-coloured region that touch the frame's edge.

    Connectivity is what separates surround from a patch inside the retina: the two can be the
    same colour, but only one of them runs off the edge of the photograph.
    """
    labels, count = ndimage.label(resembles)
    if count == 0:
        return resembles
    border = np.concatenate([labels[0], labels[-1], labels[:, 0], labels[:, -1]])
    return np.isin(labels, np.unique(border[border > 0]))


def _largest_component(mask: np.ndarray) -> np.ndarray:
    """Drop specks — a lens flare, a burnt-in timestamp — that are not the field."""
    labels, count = ndimage.label(mask)
    if count <= 1:
        return mask
    sizes = ndimage.sum_labels(mask, labels, index=range(1, count + 1))
    return labels == (int(np.argmax(sizes)) + 1)


def _on_the_cameras_circle(points: np.ndarray, height: int, width: int) -> np.ndarray:
    """The outline points that can be trusted to lie on the camera's circle.

    The convex hull of the footprint, less the corners where the circle leaves the sensor.
    """
    if len(points) < 3:
        return points
    hull = points[ConvexHull(points).vertices]
    inside_frame = (
        (hull[:, 0] > 0) & (hull[:, 0] < width - 1) & (hull[:, 1] > 0) & (hull[:, 1] < height - 1)
    )
    return hull[inside_frame]


def _fit_circle(xs: np.ndarray, ys: np.ndarray) -> Circle:
    """Least-squares circle through the visible arc (Kasa's linearisation)."""
    a = np.column_stack([xs, ys, np.ones_like(xs)])
    b = xs**2 + ys**2
    (u, v, w), *_ = np.linalg.lstsq(a, b, rcond=None)
    cx, cy = u / 2, v / 2
    return Circle(float(cx), float(cy), float(np.sqrt(w + cx**2 + cy**2)), "detected")
