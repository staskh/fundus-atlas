# ABOUTME: The shapes a biomarker implementation is measured against, and the values their geometry
# ABOUTME: requires. Pure geometry and arithmetic: no implementation is called and nothing is scored.

import math
from collections.abc import Callable
from dataclasses import dataclass, field

import numpy as np

from . import geometry


@dataclass(frozen=True)
class Shape:
    """One rendering of one shape: what an adapter is handed, and what the answer must be.

    :param artery: the artery class, or ``None`` where this shape draws none. A shape testing a
        measurement over the vessels as one class puts them in one mask and leaves the other
        absent, so the union an adapter forms is exactly the shape whose value is known.
    :param theory: the values this shape's geometry requires, keyed ``biomarker/variant`` after the
        catalogue in `docs/biomarkers/`, so a returned number can be compared with the right one.
    :param centreline: the curve before it was drawn, kept so a result can be re-derived without
        re-running the generator.
    """

    name: str
    side: int
    rotation: float
    artery: np.ndarray | None
    vein: np.ndarray | None
    fov: np.ndarray
    disc: tuple[float, float, float]
    theory: dict[str, float]
    parameters: dict[str, float]
    centreline: list[tuple[float, float]] = field(default_factory=list)


#: Where the disc sits, as a fraction of the frame, and how big it is. Every shape puts it in the
#: same place: the disc-anchored measurements need one, and a shape that moved it would be testing
#: the disc rather than the vessel.
DISC_AT = (0.5, 0.15)
DISC_RADIUS = 0.06

#: How finely a curve is sampled before it is drawn. The rasteriser measures distance to the
#: segments rather than to these points, so this only has to be fine enough that a segment's
#: deviation from the curve is well under a pixel.
SAMPLES = 2000


def build(name: str, side: int = 1024, rotation: float = 0.0, **parameters: float) -> Shape:
    """One shape, at one grid, at one angle."""
    if name not in SHAPES:
        raise LookupError(f"no shape named {name!r}; there are {', '.join(SHAPES)}")
    return SHAPES[name](side, rotation, **parameters)


def _disc(side: int) -> tuple[float, float, float]:
    return (DISC_AT[0] * side, DISC_AT[1] * side, DISC_RADIUS * side)


def _centre(side: int) -> tuple[float, float]:
    """Rotation is about the **frame** centre, and it turns the disc with everything else.

    Turning about the disc was the first idea and it is wrong: the disc sits near the top of the
    frame, so a vessel a third of a frame away from it sweeps a circle wide enough to leave the
    field of view, and a clipped vessel measures something other than the shape. Turning the whole
    scene keeps every distance — vessel to vessel, vessel to disc — exactly as it was, and a
    circular field of view is unchanged by the turn.
    """
    return (side / 2.0, side / 2.0)


def _turned_disc(side: int, rotation: float) -> tuple[float, float, float]:
    """Where the disc lands once the scene has been turned. Its radius does not change."""
    x, y, r = _disc(side)
    (moved_x, moved_y), = geometry.turn([(x, y)], rotation, _centre(side))
    return (moved_x, moved_y, r)


def _tube(length: float, width: float) -> float:
    """The area a vessel of constant width covers along a curve that does not cross itself.

    Exactly ``length × width`` plus a disc of that width for the two rounded ends, whatever the
    curve does in between — the two-dimensional tube formula — as long as its radius of curvature
    stays above half the width, which every shape here respects.
    """
    return length * width + math.pi * (width / 2.0) ** 2


def _fov_area(side: int) -> float:
    return math.pi * (side / 2.0) ** 2


def straight(side: int, rotation: float = 0.0, width: float = 0.02, length: float = 0.6) -> Shape:
    """A straight vessel: tortuosity exactly 1, no curvature, and a width a calibre must recover."""
    w, distance = width * side, length * side
    start = (side * 0.5 - distance / 2.0, side * 0.55)
    points = [start, (start[0] + distance, start[1])]
    drawn = geometry.turn(points, rotation, _centre(side))
    artery = geometry.draw(drawn, w, side)
    fov = geometry.field_of_view(side)
    return Shape(
        name="straight",
        side=side,
        rotation=rotation,
        artery=artery,
        vein=None,
        fov=fov,
        disc=_turned_disc(side, rotation),
        theory={
            "tortuosity/hart-tau1": 1.0,
            "tortuosity/total-curvature": 0.0,
            "curvature/constant": 0.0,
            "vessel-calibre/artery": w,
            "vessel-area-and-length/skeleton-length": distance,
            "vessel-area-and-length/area": _tube(distance, w),
            "vascular-density/over-field-of-view": _tube(distance, w) / _fov_area(side),
        },
        parameters={"width": w, "length": distance},
        centreline=drawn,
    )


def arc(
    side: int, rotation: float = 0.0, width: float = 0.02, radius: float = 0.3, angle: float = 90.0
) -> Shape:
    """A circular arc: curvature exactly 1/r, and an arc-chord ratio in closed form.

    τ1 = θ / (2 sin(θ/2)) — arc length rθ over the chord 2r sin(θ/2), the r cancelling, so the
    ratio depends on how far the vessel bends and not at all on how large it is. An implementation
    whose τ1 changes with the radius is not computing τ1.
    """
    w, r, theta = width * side, radius * side, math.radians(angle)
    centre = (side * 0.5, side * 0.5 + r / 2.0)
    first = -theta / 2.0 - math.pi / 2.0
    angles = np.linspace(first, first + theta, SAMPLES)
    points = [(centre[0] + r * math.cos(a), centre[1] + r * math.sin(a)) for a in angles]
    drawn = geometry.turn(points, rotation, _centre(side))
    artery = geometry.draw(drawn, w, side)
    fov = geometry.field_of_view(side)
    return Shape(
        name="arc",
        side=side,
        rotation=rotation,
        artery=artery,
        vein=None,
        fov=fov,
        disc=_turned_disc(side, rotation),
        theory={
            "tortuosity/hart-tau1": theta / (2.0 * math.sin(theta / 2.0)),
            "tortuosity/total-curvature": theta,
            "tortuosity/squared-curvature": theta / r,
            "curvature/constant": 1.0 / r,
            "vessel-calibre/artery": w,
            "vessel-area-and-length/skeleton-length": r * theta,
            "vessel-area-and-length/area": _tube(r * theta, w),
            "vascular-density/over-field-of-view": _tube(r * theta, w) / _fov_area(side),
        },
        parameters={"width": w, "radius": r, "angle": angle},
        centreline=drawn,
    )


def sinusoid(
    side: int,
    rotation: float = 0.0,
    width: float = 0.02,
    amplitude: float = 0.04,
    wavelength: float = 0.25,
    cycles: float = 2.0,
) -> Shape:
    """A sine wave: arc length and the curvature integrals, by integration rather than by formula.

    Its arc length is an elliptic integral with no elementary closed form, so the theory here *is*
    the integral, evaluated finely enough that the result is exact to more places than any
    implementation will reach.
    """
    w = width * side
    a, lam = amplitude * side, wavelength * side
    span = lam * cycles
    x = np.linspace(0.0, span, SAMPLES)
    k = 2.0 * math.pi / lam
    y = a * np.sin(k * x)
    points = [(side * 0.5 - span / 2.0 + float(px), side * 0.55 + float(py)) for px, py in zip(x, y, strict=True)]
    drawn = geometry.turn(points, rotation, _centre(side))
    artery = geometry.draw(drawn, w, side)
    fov = geometry.field_of_view(side)

    fine = np.linspace(0.0, span, 200_001)
    slope = a * k * np.cos(k * fine)
    second = -a * k * k * np.sin(k * fine)
    length = float(np.trapezoid(np.sqrt(1.0 + slope**2), fine))
    curvature = np.abs(second) / (1.0 + slope**2) ** 1.5
    element = np.sqrt(1.0 + slope**2)
    return Shape(
        name="sinusoid",
        side=side,
        rotation=rotation,
        artery=artery,
        vein=None,
        fov=fov,
        disc=_turned_disc(side, rotation),
        theory={
            "tortuosity/hart-tau1": length / span,
            "tortuosity/total-curvature": float(np.trapezoid(curvature * element, fine)),
            "tortuosity/squared-curvature": float(np.trapezoid(curvature**2 * element, fine)),
            "vessel-calibre/artery": w,
            "vessel-area-and-length/skeleton-length": length,
            "vessel-area-and-length/area": _tube(length, w),
            "vascular-density/over-field-of-view": _tube(length, w) / _fov_area(side),
        },
        parameters={"width": w, "amplitude": a, "wavelength": lam, "cycles": cycles},
        centreline=drawn,
    )


def bifurcation(
    side: int, rotation: float = 0.0, width: float = 0.02, angle: float = 60.0, arm: float = 0.25
) -> Shape:
    """A parent vessel splitting into two daughters at a known angle.

    Symmetric, so the angle between the daughters is exactly what was asked for and neither
    daughter is the trunk. One junction, three ends.
    """
    w, reach = width * side, arm * side
    apex = (side * 0.5, side * 0.45)
    half = math.radians(angle) / 2.0
    trunk = [(apex[0], apex[1] - reach), apex]
    left = [apex, (apex[0] - reach * math.sin(half), apex[1] + reach * math.cos(half))]
    right = [apex, (apex[0] + reach * math.sin(half), apex[1] + reach * math.cos(half))]
    fov = geometry.field_of_view(side)
    turned = [geometry.turn(part, rotation, _centre(side)) for part in (trunk, left, right)]
    artery = np.zeros((side, side), dtype=bool)
    for part in turned:
        artery |= geometry.draw(part, w, side)
    return Shape(
        name="bifurcation",
        side=side,
        rotation=rotation,
        artery=artery,
        vein=None,
        fov=fov,
        disc=_turned_disc(side, rotation),
        theory={
            "bifurcation-angle/between-daughters": float(angle),
            "junction-counts/junctions": 1.0,
            "junction-counts/endpoints": 3.0,
            "junction-counts/components": 1.0,
            "vessel-calibre/artery": w,
            "vessel-area-and-length/skeleton-length": 3.0 * reach,
        },
        parameters={"width": w, "angle": angle, "arm": reach},
        centreline=turned[0],
    )


def disjoint(
    side: int, rotation: float = 0.0, width: float = 0.02, segments: float = 4, length: float = 0.4
) -> Shape:
    """Parallel vessels that never meet: no junctions, and as many components as there are lines.

    A skeletoniser that joins them, or a junction counter that finds a crossing where two vessels
    merely pass near one another, says so here and nowhere else.
    """
    w, distance, count = width * side, length * side, int(segments)
    fov = geometry.field_of_view(side)
    artery = np.zeros((side, side), dtype=bool)
    spacing = side * 0.12
    first = side * 0.5 - spacing * (count - 1) / 2.0
    for index in range(count):
        y = first + index * spacing
        part = [(side * 0.5 - distance / 2.0, y), (side * 0.5 + distance / 2.0, y)]
        artery |= geometry.draw(geometry.turn(part, rotation, _centre(side)), w, side)
    return Shape(
        name="disjoint",
        side=side,
        rotation=rotation,
        artery=artery,
        vein=None,
        fov=fov,
        disc=_turned_disc(side, rotation),
        theory={
            "junction-counts/junctions": 0.0,
            "junction-counts/endpoints": 2.0 * count,
            "junction-counts/components": float(count),
            "vessel-calibre/artery": w,
            "vessel-area-and-length/skeleton-length": count * distance,
            "vessel-area-and-length/area": count * _tube(distance, w),
            "vascular-density/over-field-of-view": count * _tube(distance, w) / _fov_area(side),
        },
        parameters={"width": w, "segments": float(count), "length": distance},
    )


def artery_vein_pair(
    side: int,
    rotation: float = 0.0,
    artery_width: float = 0.018,
    vein_width: float = 0.024,
    length: float = 0.5,
) -> Shape:
    """One artery beside one vein, of known widths: the ratio is exactly the ratio of the widths.

    The only shape here that draws both classes, and the only one that can test a measurement
    which is a ratio of the two. It separates an implementation that divides two calibres from one
    that divides two central retinal equivalents computed over a ring, since on parallel vessels of
    constant width those two are the same number and on a real eye they are not.
    """
    wa, wv, distance = artery_width * side, vein_width * side, length * side
    fov = geometry.field_of_view(side)
    x0, x1 = side * 0.5 - distance / 2.0, side * 0.5 + distance / 2.0
    above = [(x0, side * 0.45), (x1, side * 0.45)]
    below = [(x0, side * 0.62), (x1, side * 0.62)]
    artery = geometry.draw(geometry.turn(above, rotation, _centre(side)), wa, side)
    vein = geometry.draw(geometry.turn(below, rotation, _centre(side)), wv, side)
    return Shape(
        name="artery-vein-pair",
        side=side,
        rotation=rotation,
        artery=artery,
        vein=vein,
        fov=fov,
        disc=_turned_disc(side, rotation),
        theory={
            "avr/ratio-of-calibres": wa / wv,
            "vessel-calibre/artery": wa,
            "vessel-calibre/vein": wv,
            "central-retinal-equivalents/crae": wa,
            "central-retinal-equivalents/crve": wv,
            "tortuosity/hart-tau1": 1.0,
            "vessel-area-and-length/skeleton-length": 2.0 * distance,
            "vascular-density/over-field-of-view": (
                _tube(distance, wa) + _tube(distance, wv)
            ) / _fov_area(side),
        },
        parameters={"artery_width": wa, "vein_width": wv, "length": distance},
    )


#: Every shape, by the name that appears in `results/biomarker-synthetic/<model>/<shape>.csv`.
SHAPES: dict[str, Callable[..., Shape]] = {
    "straight": straight,
    "arc": arc,
    "sinusoid": sinusoid,
    "bifurcation": bifurcation,
    "disjoint": disjoint,
    "artery-vein-pair": artery_vein_pair,
}
