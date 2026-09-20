# ABOUTME: Turning a continuous centreline into a mask, and turning it about a point — the two
# ABOUTME: operations every synthetic shape rests on. Pure geometry: no implementation, no scoring.

import numpy as np

#: How much of the frame the field of view fills. A fundus photograph is a lit circle in a dark
#: square, and a measurement taken over "the image" means something different from one taken over
#: the retina, so every shape carries the region it was measured in.
FIELD = 1.0


def draw(points: list[tuple[float, float]], width: float, side: int) -> np.ndarray:
    """Rasterise a centreline of the given width onto a ``side``×``side`` grid.

    A pixel belongs to the vessel when its **centre** lies within half a width of the centreline,
    measured as the true distance to the line segments rather than to their sampled points — so
    the width is exact along the whole length, including inside a corner, and does not depend on
    how finely the caller sampled the curve.

    :param points: the centreline, in pixel coordinates as ``(x, y)``, at this ``side``.
    :param width: the vessel's full width in pixels, so the mask reaches ``width / 2`` either side.
    """
    grid = np.arange(side, dtype=np.float64) + 0.5
    x, y = np.meshgrid(grid, grid)
    nearest = _distance(np.asarray(points, dtype=np.float64), x, y, width / 2.0)
    return nearest <= width / 2.0


def turn(
    points: list[tuple[float, float]], degrees: float, about: tuple[float, float]
) -> list[tuple[float, float]]:
    """Rotate a centreline about a point, **before** it is drawn.

    Turning the picture instead would resample it, and resampling a structure a few pixels wide
    destroys it: rescaling one dataset's tracing in this repository turned 19 connected components
    into 309. Rotating the geometry and drawing again leaves the grid as the only difference
    between one angle and another, which is the difference the benchmark is asking about.
    """
    angle = np.deg2rad(degrees)
    cos, sin = np.cos(angle), np.sin(angle)
    ox, oy = about
    moved = []
    for px, py in points:
        dx, dy = px - ox, py - oy
        moved.append((ox + dx * cos - dy * sin, oy + dx * sin + dy * cos))
    return moved


def field_of_view(side: int, fraction: float = FIELD) -> np.ndarray:
    """The lit circle a fundus camera produces, inscribed in the frame."""
    grid = np.arange(side, dtype=np.float64) + 0.5
    x, y = np.meshgrid(grid, grid)
    centre = side / 2.0
    return (x - centre) ** 2 + (y - centre) ** 2 <= (fraction * side / 2.0) ** 2


def _distance(points: np.ndarray, x: np.ndarray, y: np.ndarray, reach: float) -> np.ndarray:
    """Distance from every pixel centre to the nearest point **on** the polyline.

    Segment by segment, because the distance to a sampled point is not the distance to the curve:
    sampling a straight line every ten pixels and measuring to the samples would scallop its edge.

    Each segment is measured only inside its own bounding box, grown by ``reach``. Outside that box
    no pixel can be within ``reach`` of the segment, so the answer is identical and the work is a
    few thousand pixels rather than four million — which matters because a sampled curve has two
    thousand segments, and measuring each against the whole grid is eight billion distances for one
    sinusoid.
    """
    nearest = np.full(x.shape, np.inf)
    if len(points) == 1:
        return np.hypot(x - points[0, 0], y - points[0, 1])
    side = x.shape[0]
    for start, end in zip(points[:-1], points[1:], strict=True):
        left = max(int(min(start[0], end[0]) - reach) - 1, 0)
        right = min(int(max(start[0], end[0]) + reach) + 2, side)
        top = max(int(min(start[1], end[1]) - reach) - 1, 0)
        bottom = min(int(max(start[1], end[1]) + reach) + 2, side)
        if left >= right or top >= bottom:
            continue
        window = (slice(top, bottom), slice(left, right))
        nearest[window] = np.minimum(
            nearest[window], _to_segment(start, end, x[window], y[window])
        )
    return nearest


def _to_segment(
    start: np.ndarray, end: np.ndarray, x: np.ndarray, y: np.ndarray
) -> np.ndarray:
    """Distance from every pixel centre to one line segment, clamped at its ends."""
    dx, dy = end[0] - start[0], end[1] - start[1]
    squared = dx * dx + dy * dy
    if squared == 0.0:
        return np.hypot(x - start[0], y - start[1])
    along = ((x - start[0]) * dx + (y - start[1]) * dy) / squared
    along = np.clip(along, 0.0, 1.0)
    return np.hypot(x - (start[0] + along * dx), y - (start[1] + along * dy))
