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
    :param um_per_px: the scale the shape was built with. A synthetic shape has no camera, so this
        is a stated convention — but it has to be stated, because Hubbard's equivalents carry
        additive constants fitted in microns and mean nothing without one.
    :param centreline: the curve before it was drawn, kept so a result can be re-derived without
        re-running the generator.
    """

    name: str
    side: int
    rotation: float
    um_per_px: float
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
#:
#: It sits to the **right** of centre, where a fundus camera puts it, and far enough in that the
#: ring the central retinal equivalents are measured over — out to three disc radii — stays inside
#: the field of view at every rotation: 0.30 from the centre plus 0.18 of ring is 0.48, and the
#: field has radius 0.5.
DISC_AT = (0.80, 0.5)
DISC_RADIUS = 0.06

#: The annulus the central retinal equivalents are measured in, in **disc radii** from the disc
#: centre. PVBM builds it as zone C minus zone B — filled circles at 2 and 3 disc radii — and the
#: classical convention states the same region in disc *diameters*, which is the factor-of-two trap
#: `docs/biomarkers/central-retinal-equivalents.md` §5 records.
ZONE_B_RADII = (2.0, 3.0)

#: What Knudtson's revision multiplies each pair by, and how many vessels it keeps.
KNUDTSON = {"artery": 0.88, "vein": 0.95}
KNUDTSON_VESSELS = 6

#: Hubbard's fitted coefficients, `(a, b, c, d)` in `√(a·w₁² + b·w₂² + c·w₁·w₂ + d)`. They were
#: fitted in **microns**, and the additive term is what makes that matter: it does not scale, so
#: feeding pixel widths in gives a different number rather than a rescaled one.
HUBBARD = {"artery": (0.87, 1.01, -0.22, -10.76), "vein": (0.72, 0.91, 0.0, 450.05)}

#: Microns per pixel where a shape is not told otherwise. A synthetic shape has no camera, so this
#: is a stated convention rather than a measurement — but a scale has to be stated, because
#: Hubbard's equivalents are meaningless without one.
UM_PER_PX = 10.0

#: How finely a curve is sampled before it is drawn. The rasteriser measures distance to the
#: segments rather than to these points, so this only has to be fine enough that a segment's
#: deviation from the curve is well under a pixel.
SAMPLES = 2000


def build(
    name: str,
    side: int = 1024,
    rotation: float = 0.0,
    um_per_px: float = UM_PER_PX,
    **parameters: float,
) -> Shape:
    """One shape, at one grid, at one angle, at one scale.

    :param um_per_px: microns per pixel. It changes no geometry — a shape is the same shape at any
        scale — but it decides what the scale-dependent theory says, which is Hubbard's equivalents
        and nothing else here.
    """
    if name not in SHAPES:
        raise LookupError(f"no shape named {name!r}; there are {', '.join(SHAPES)}")
    return SHAPES[name](side, rotation, um_per_px, **parameters)


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


def _combine(widths: list[float], pair: Callable[[float, float], float]) -> float:
    """The recursion both equivalents share: pair the widest with the narrowest, repeat.

    Knudtson's revision fixed the vessels used at the six largest and the pairing at widest with
    narrowest; the same iteration is applied to Hubbard's combination here, which is what the
    implementations in this catalogue do. Hubbard's own paper is less explicit about the order,
    so that is an assumption rather than a reading — and one the synthetic shapes make harmless,
    since every vessel of a class shares a width and every order gives the same answer.
    """
    remaining = sorted(widths, reverse=True)[:KNUDTSON_VESSELS]
    while len(remaining) > 1:
        remaining.sort(reverse=True)
        combined = []
        left, right = 0, len(remaining) - 1
        while left < right:
            combined.append(pair(remaining[left], remaining[right]))
            left += 1
            right -= 1
        if left == right:
            combined.append(remaining[left])
        remaining = combined
    return remaining[0]


def hubbard(widths_um: list[float], structure: str) -> float:
    """The Hubbard equivalent, **in microns**, of vessel widths given in microns.

    `√(a·w₁² + b·w₂² + c·w₁w₂ + d)` per pair, with the coefficients Hubbard et al. 1999 fitted.
    The additive constant is the reason the unit is stated twice: −10.76 for arterioles and
    +450.05 for venules do not scale with the image, so this variant is **not** scale-free and a
    value computed on pixel widths is a different quantity rather than one awaiting conversion.

    Undefined for a single vessel: the formula combines two, and there is nothing to combine one
    with. A shape offering one vessel per class therefore carries no Hubbard theory — which is
    itself worth testing, since an implementation must decline rather than invent a second vessel.
    """
    if len(widths_um) < 2:
        raise ValueError("Hubbard's equivalent combines a pair; one vessel cannot make one")
    a, b, c, d = HUBBARD[structure]
    return _combine(
        widths_um,
        lambda w1, w2: math.sqrt(max(a * w1 * w1 + b * w2 * w2 + c * w1 * w2 + d, 0.0)),
    )


def knudtson(widths: list[float], structure: str) -> float:
    """The Knudtson equivalent of a set of vessel widths: CRAE on arteries, CRVE on veins.

    The recursion of Knudtson et al. 2003: take the six largest vessels, pair the widest with the
    narrowest, the next widest with the next narrowest, and combine each pair as
    ``k·√(w₁² + w₂²)`` — ``k`` being 0.88 for arterioles and 0.95 for venules. Repeat on the
    results until one number is left; where a round has an odd count, the middle vessel passes
    through untouched.

    Being purely multiplicative it is scale-free, so it can be computed on pixel widths and
    converted afterwards — which is the property Hubbard's fitted constants do not have.

    **Every vessel here is the same width**, which is deliberate: then every pairing order gives
    the same answer, so a shape built this way tests the formula and the ring rather than an
    implementation's sorting convention. A shape with unequal widths would test the convention and
    have no single correct answer to test it against.
    """
    constant = KNUDTSON[structure]
    return _combine(widths, lambda w1, w2: constant * math.hypot(w1, w2))


def straight(
    side: int,
    rotation: float = 0.0,
    um_per_px: float = UM_PER_PX,
    width: float = 0.02,
    length: float = 0.6,
) -> Shape:
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
        um_per_px=um_per_px,
        artery=artery,
        vein=None,
        fov=fov,
        disc=_turned_disc(side, rotation),
        theory={
            "tortuosity/hart-tau1/artery": 1.0,
            "tortuosity/hart-tau2/artery": 0.0,
            "tortuosity/hart-tau3/artery": 0.0,
            "tortuosity/hart-tau4/artery": 0.0,
            "tortuosity/hart-tau5/artery": 0.0,
            "vessel-calibre/mean-width/artery": w,
            "vessel-area-and-length/skeleton-length/artery": distance,
            "vessel-area-and-length/area/artery": _tube(distance, w),
            "vascular-density/over-field-of-view/vessels": _tube(distance, w) / _fov_area(side),
            "junction-counts/junctions/vessels": 0.0,
            "junction-counts/components/vessels": 1.0,
            "junction-counts/endpoints/vessels": 2.0,
        },
        parameters={"width": w, "length": distance},
        centreline=drawn,
    )


def arc(
    side: int,
    rotation: float = 0.0,
    um_per_px: float = UM_PER_PX, width: float = 0.02, radius: float = 0.3, angle: float = 90.0
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
        um_per_px=um_per_px,
        artery=artery,
        vein=None,
        fov=fov,
        disc=_turned_disc(side, rotation),
        theory={
            "tortuosity/hart-tau1/artery": theta / (2.0 * math.sin(theta / 2.0)),
            "tortuosity/hart-tau2/artery": theta,
            "tortuosity/hart-tau3/artery": theta / r,
            # Hart's compositional pair, and the reason he preferred them: both depend on the
            # radius alone, so measuring more of the same arc does not change them, while τ2 and
            # τ3 grow with however much of it happened to be traced.
            "tortuosity/hart-tau4/artery": 1.0 / r,
            "tortuosity/hart-tau5/artery": 1.0 / (r * r),
            "vessel-calibre/mean-width/artery": w,
            "vessel-area-and-length/skeleton-length/artery": r * theta,
            "vessel-area-and-length/area/artery": _tube(r * theta, w),
            "vascular-density/over-field-of-view/vessels": _tube(r * theta, w) / _fov_area(side),
        },
        parameters={"width": w, "radius": r, "angle": angle},
        centreline=drawn,
    )


def sinusoid(
    side: int,
    rotation: float = 0.0,
    um_per_px: float = UM_PER_PX,
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
    total_curvature = float(np.trapezoid(curvature * element, fine))
    total_squared = float(np.trapezoid(curvature**2 * element, fine))
    return Shape(
        name="sinusoid",
        side=side,
        rotation=rotation,
        um_per_px=um_per_px,
        artery=artery,
        vein=None,
        fov=fov,
        disc=_turned_disc(side, rotation),
        theory={
            "tortuosity/hart-tau1/artery": length / span,
            "tortuosity/hart-tau2/artery": total_curvature,
            "tortuosity/hart-tau3/artery": total_squared,
            "tortuosity/hart-tau4/artery": total_curvature / length,
            "tortuosity/hart-tau5/artery": total_squared / length,
            "vessel-calibre/mean-width/artery": w,
            "vessel-area-and-length/skeleton-length/artery": length,
            "vessel-area-and-length/area/artery": _tube(length, w),
            "vascular-density/over-field-of-view/vessels": _tube(length, w) / _fov_area(side),
        },
        parameters={"width": w, "amplitude": a, "wavelength": lam, "cycles": cycles},
        centreline=drawn,
    )


def bifurcation(
    side: int,
    rotation: float = 0.0,
    um_per_px: float = UM_PER_PX, width: float = 0.02, angle: float = 60.0, arm: float = 0.25
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
        um_per_px=um_per_px,
        artery=artery,
        vein=None,
        fov=fov,
        disc=_turned_disc(side, rotation),
        theory={
            "bifurcation-angle/between-daughters/artery": float(angle),
            "junction-counts/junctions/vessels": 1.0,
            "junction-counts/endpoints/vessels": 3.0,
            "junction-counts/components/vessels": 1.0,
            "vessel-calibre/mean-width/artery": w,
            "vessel-area-and-length/skeleton-length/artery": 3.0 * reach,
        },
        parameters={"width": w, "angle": angle, "arm": reach},
        centreline=turned[0],
    )


def disjoint(
    side: int,
    rotation: float = 0.0,
    um_per_px: float = UM_PER_PX, width: float = 0.02, segments: float = 4, length: float = 0.4
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
        um_per_px=um_per_px,
        artery=artery,
        vein=None,
        fov=fov,
        disc=_turned_disc(side, rotation),
        theory={
            "junction-counts/junctions/vessels": 0.0,
            "junction-counts/endpoints/vessels": 2.0 * count,
            "junction-counts/components/vessels": float(count),
            "vessel-calibre/mean-width/artery": w,
            "tortuosity/hart-tau1/artery": 1.0,
            "vessel-area-and-length/skeleton-length/artery": count * distance,
            "vessel-area-and-length/area/artery": count * _tube(distance, w),
            "vascular-density/over-field-of-view/vessels": (
                count * _tube(distance, w) / _fov_area(side)
            ),
        },
        parameters={"width": w, "segments": float(count), "length": distance},
    )


def artery_vein_pair(
    side: int,
    rotation: float = 0.0,
    um_per_px: float = UM_PER_PX,
    artery_width: float = 0.018,
    vein_width: float = 0.024,
    length: float = 0.5,
) -> Shape:
    """One artery beside one vein, of known widths: the ratio is exactly the ratio of the widths.

    The only shape here that draws both classes without touching the disc, and what it tests is a
    ratio of two calibres — **not** a central retinal equivalent. Those are measured over a ring
    around the disc, and two vessels that never cross that ring cannot produce one; an
    implementation that returns a CRAE here is measuring something it was not given, which is a
    finding rather than a value. The shape that does test the equivalents is `disc-spokes`.
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
        um_per_px=um_per_px,
        artery=artery,
        vein=vein,
        fov=fov,
        disc=_turned_disc(side, rotation),
        theory={
            "avr/ratio-of-calibres/both": wa / wv,
            # One artery and one vein cross the ring, which is a degenerate but legitimate case:
            # Knudtson's recursion returns a lone vessel's own width untouched. Hubbard's combines
            # a pair and so has no value here at all — an implementation must decline rather than
            # invent a second vessel, and this is the shape that asks it to.
            "central-retinal-equivalents/knudtson/artery": knudtson([wa], "artery"),
            "central-retinal-equivalents/knudtson/vein": knudtson([wv], "vein"),
            "avr/knudtson/both": knudtson([wa], "artery") / knudtson([wv], "vein"),
            "vessel-calibre/mean-width/artery": wa,
            "vessel-calibre/mean-width/vein": wv,
            "tortuosity/hart-tau1/artery": 1.0,
            "tortuosity/hart-tau1/vein": 1.0,
            "vessel-area-and-length/skeleton-length/artery": distance,
            "vessel-area-and-length/skeleton-length/vein": distance,
            "vascular-density/over-field-of-view/vessels": (
                _tube(distance, wa) + _tube(distance, wv)
            ) / _fov_area(side),
        },
        parameters={"artery_width": wa, "vein_width": wv, "length": distance},
    )


def disc_spokes(
    side: int,
    rotation: float = 0.0,
    um_per_px: float = UM_PER_PX,
    artery_width: float = 0.012,
    vein_width: float = 0.016,
    vessels: float = 6,
) -> Shape:
    """Vessels radiating from the optic disc, crossing the ring the equivalents are measured over.

    Six arteries and six veins of constant width, each running from the disc margin out past three
    disc radii, so every one of them crosses the annulus between two and three radii that PVBM
    builds as zone C minus zone B. That is what a central retinal equivalent needs and what no
    other shape here provides: an implementation measuring in the right ring finds twelve vessels
    of two known widths, and one measuring somewhere else finds nothing or finds them twice.

    All the arteries share a width and all the veins share theirs, so the Knudtson recursion gives
    the same number whatever order an implementation pairs them in — the shape tests the formula
    and the region rather than a sorting convention.

    The two classes alternate around the disc, twelve spokes evenly spaced, so neither class is
    bunched on one side where a half-ring or a temporal-only convention would miss it.
    """
    count = int(vessels)
    wa, wv = artery_width * side, vein_width * side
    x, y, radius = _disc(side)
    inner, outer = radius * 1.0, radius * (ZONE_B_RADII[1] + 0.4)
    artery = np.zeros((side, side), dtype=bool)
    vein = np.zeros((side, side), dtype=bool)
    for index in range(2 * count):
        heading = 2.0 * math.pi * index / (2 * count)
        spoke = [
            (x + inner * math.cos(heading), y + inner * math.sin(heading)),
            (x + outer * math.cos(heading), y + outer * math.sin(heading)),
        ]
        turned = geometry.turn(spoke, rotation, _centre(side))
        if index % 2 == 0:
            artery |= geometry.draw(turned, wa, side)
        else:
            vein |= geometry.draw(turned, wv, side)
    crae = knudtson([wa] * count, "artery")
    crve = knudtson([wv] * count, "vein")
    # Hubbard's constants were fitted in microns, so its widths go in as microns and its answer
    # comes out in microns. That is the one place the scale a shape was built with changes what
    # the theory says.
    crae_um = hubbard([wa * um_per_px] * count, "artery")
    crve_um = hubbard([wv * um_per_px] * count, "vein")
    length = outer - inner
    return Shape(
        name="disc-spokes",
        side=side,
        rotation=rotation,
        um_per_px=um_per_px,
        artery=artery,
        vein=vein,
        fov=geometry.field_of_view(side),
        disc=_turned_disc(side, rotation),
        theory={
            "central-retinal-equivalents/knudtson/artery": crae,
            "central-retinal-equivalents/knudtson/vein": crve,
            "avr/knudtson/both": crae / crve,
            "central-retinal-equivalents/hubbard/artery": crae_um,
            "central-retinal-equivalents/hubbard/vein": crve_um,
            "avr/hubbard/both": crae_um / crve_um,
            "avr/ratio-of-calibres/both": wa / wv,
            "vessel-calibre/mean-width/artery": wa,
            "vessel-calibre/mean-width/vein": wv,
            "tortuosity/hart-tau1/artery": 1.0,
            "tortuosity/hart-tau1/vein": 1.0,
            "junction-counts/components/vessels": float(2 * count),
            "junction-counts/junctions/vessels": 0.0,
            "vessel-area-and-length/skeleton-length/artery": count * length,
            "vessel-area-and-length/skeleton-length/vein": count * length,
        },
        parameters={
            "artery_width": wa,
            "vein_width": wv,
            "vessels_per_class": float(count),
            "disc_radius": radius,
            "inner_radius_in_disc_radii": inner / radius,
            "outer_radius_in_disc_radii": outer / radius,
        },
    )


#: Every shape, by the name that appears in `results/biomarker-synthetic/<model>/<shape>.csv`.
SHAPES: dict[str, Callable[..., Shape]] = {
    "straight": straight,
    "arc": arc,
    "sinusoid": sinusoid,
    "bifurcation": bifurcation,
    "disjoint": disjoint,
    "artery-vein-pair": artery_vein_pair,
    "disc-spokes": disc_spokes,
}
