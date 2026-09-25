# ABOUTME: What a drawn shape's geometry requires, derived from its centreline rather than from the
# ABOUTME: pixels it was drawn as: every catalogued quantity a curve settles, in closed form or by integration.

import math

import numpy as np

#: How finely a curve is integrated. Far finer than it is sampled for drawing, because an integral
#: evaluated here is the value an implementation is judged against and must be exact to more places
#: than any of them will reach.
STEPS = 200_001


def arc_and_chord(points: np.ndarray) -> tuple[float, float]:
    """The distance travelled along a curve, and the straight line between its ends."""
    steps = np.diff(points, axis=0)
    return float(np.hypot(steps[:, 0], steps[:, 1]).sum()), float(math.dist(points[0], points[-1]))


def integrals(points: np.ndarray, curvature: np.ndarray) -> tuple[float, float]:
    """`∫κ ds` and `∫κ² ds`, integrated along the curve.

    Curvature is passed in rather than differenced out of the points: every shape here knows its
    own curvature exactly — zero for a straight segment, `1/r` for a circular arc, a formula for a
    sine wave — and differencing a sampled polyline would make the *theory* an approximation of the
    drawing rather than the other way round.
    """
    steps = np.hypot(*np.diff(points, axis=0).T)
    middle = (curvature[:-1] + curvature[1:]) / 2.0
    return float(np.abs(middle) @ steps), float((middle**2) @ steps)


def inflections(curvature: np.ndarray) -> int:
    """How many times the curvature changes sign — where the curve stops bending one way."""
    turning = np.sign(curvature[np.abs(curvature) > 1e-12])
    return int(np.count_nonzero(np.diff(turning))) if turning.size else 0


def grisan(points: np.ndarray, curvature: np.ndarray) -> float:
    """Grisan's tortuosity density: `((n−1)/n) · (1/L_c) · Σ (arc/chord − 1)` over turn curves.

    The curve is cut wherever its curvature changes sign — the paper's *turn curves* — and each
    piece contributes how far its own arc exceeds its own chord. A straight vessel has one piece
    that contributes nothing, so its density is 0, and a curve that bends one way throughout is the
    same: the measure is about *changing* direction rather than about being bent.
    """
    total, _ = arc_and_chord(points)
    sign = np.sign(curvature)
    cuts = [0, *(int(i) + 1 for i in np.nonzero(np.diff(sign[sign != 0]))[0]), len(points) - 1]
    cuts = sorted(set(cuts))
    pieces = [points[a : b + 1] for a, b in zip(cuts[:-1], cuts[1:], strict=True) if b > a]
    n = len(pieces)
    if n < 2 or not total:
        return 0.0
    excess = sum(arc / chord - 1.0 for arc, chord in map(arc_and_chord, pieces) if chord)
    return (n - 1) / n * excess / total


def tube(length: float, width: float) -> float:
    """The area a vessel of constant width covers along a curve that does not cross itself."""
    return length * width + math.pi * (width / 2.0) ** 2


def curve(points: np.ndarray, curvature: np.ndarray) -> dict[str, float]:
    """Every catalogued quantity one curve settles, by the name's own definition.

    Returned without a structure, which the caller appends — the same curve drawn as an artery and
    as a vein settles the same numbers.
    """
    arc, chord = arc_and_chord(points)
    total_curvature, total_squared = integrals(points, curvature)
    turns = inflections(curvature)
    return {
        "tortuosity/hart-tau1": arc / chord if chord else math.nan,
        "tortuosity/hart-tau2": total_curvature,
        "tortuosity/hart-tau3": total_squared,
        "tortuosity/hart-tau4": total_curvature / arc if arc else math.nan,
        "tortuosity/hart-tau5": total_squared / arc if arc else math.nan,
        "tortuosity/hart-tau6": total_curvature / chord if chord else math.nan,
        "tortuosity/hart-tau7": total_squared / chord if chord else math.nan,
        # Mean curvature along the curve. A *fitted* spline is an implementation's own choice of
        # smoothing, and on an exact curve the thing it is fitting to is this.
        "tortuosity/spline-mean-curvature": total_curvature / arc if arc else math.nan,
        "tortuosity/inflection-count": float(turns),
        "tortuosity/arc-chord-times-inflections": (arc / chord if chord else math.nan) * turns,
        "tortuosity/grisan-density": grisan(points, curvature),
        "vessel-area-and-length/skeleton-length": arc,
    }


def straight_curvature(points: np.ndarray) -> np.ndarray:
    """Zero, exactly, for every sample of a polyline made of straight pieces."""
    return np.zeros(len(points))


#: How coarsely the distance field is evaluated, and how finely a centreline is walked for it.
#: Sparsity is a distance of hundreds of pixels, so a grid of a few pixels and a few hundred
#: segments settle it to well under a per cent — and the cost is the product of the two, which is
#: why neither is the sampling used for drawing or for integrating.
SPARSITY_GRID = 256
SPARSITY_STEPS = 400


def sparsity(
    centrelines: list[np.ndarray],
    widths: list[float],
    side: int,
    fraction: float = 1.0,
    grid: int = SPARSITY_GRID,
) -> tuple[float, float]:
    """How far the retina is from a vessel: the mean of that distance, and the largest.

    Measured from the **centrelines** rather than from a drawn mask, on a grid fine enough that the
    answer is stable — the same numerical evaluation the sinusoid's arc length is. Distance is to
    the vessel's edge, so a point inside a vessel is zero away from one, and only the lit circle
    counts because the dark corners of the frame are not retina.
    """
    step = side / grid
    axis = (np.arange(grid) + 0.5) * step
    x, y = np.meshgrid(axis, axis)
    inside = (x - side / 2.0) ** 2 + (y - side / 2.0) ** 2 <= (fraction * side / 2.0) ** 2
    nearest = np.full(x.shape, np.inf)
    for points, width in zip(centrelines, widths, strict=True):
        step = max(1, len(points) // SPARSITY_STEPS)
        walked = np.vstack([points[::step], points[-1:]])
        for start, end in zip(walked[:-1], walked[1:], strict=True):
            nearest = np.minimum(nearest, _to_segment(start, end, x, y) - width / 2.0)
    nearest = np.maximum(nearest[inside], 0.0)
    return float(nearest.mean()), float(nearest.max())


def _to_segment(start, end, x, y) -> np.ndarray:
    """Distance from every point to one line segment, clamped at its ends."""
    dx, dy = end[0] - start[0], end[1] - start[1]
    squared = dx * dx + dy * dy
    if squared == 0.0:
        return np.hypot(x - start[0], y - start[1])
    along = np.clip(((x - start[0]) * dx + (y - start[1]) * dy) / squared, 0.0, 1.0)
    return np.hypot(x - (start[0] + along * dx), y - (start[1] + along * dy))
