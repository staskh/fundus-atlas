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
#:
#: The offset is 0.20 of the frame rather than 0.30: the ring reaches three disc radii, and a
#: disc of clinical size leaves less room than a disc sized as a fraction of the picture did.
DISC_AT = (0.70, 0.5)

#: The optic disc's **diameter** in microns. About 1800 µm across in an adult eye, so the radius
#: every zone is counted in is half of it — the factor-of-two trap
#: `docs/biomarkers/central-retinal-equivalents.md` §5 records, met here in the parameter itself.
DISC_DIAMETER_UM = 1800.0

#: How wide a vessel is, in **microns**, by class. A retina is described in microns and a mask is
#: drawn in pixels, so these become pixels through the scale the shape is built at: the same shape
#: at 5 µm/px and at 10 µm/px is one retina photographed twice, not two retinas.
ARTERY_WIDTH_UM = 80.0
VEIN_WIDTH_UM = 120.0

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

#: What `demo_image` paints each thing. Arteries read red and veins blue, as every atlas of the
#: retina draws them; the ring the equivalents are measured over is drawn faintly so a reader can
#: see whether vessels actually cross it.
FIELD_COLOUR = (18, 18, 22)
ARTERY_COLOUR = (214, 52, 52)
VEIN_COLOUR = (54, 92, 214)
DISC_COLOUR = (240, 198, 62)
RING_COLOUR = (72, 96, 84)
OVERLAP_COLOUR = (255, 0, 255)

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


def _disc(
    side: int,
    um_per_px: float,
    disc_diameter_um: float = DISC_DIAMETER_UM,
    at: tuple[float, float] = DISC_AT,
) -> tuple[float, float, float]:
    """Where the disc is and how big it is, in pixels, from a size stated in microns."""
    return (at[0] * side, at[1] * side, disc_diameter_um / 2.0 / um_per_px)


def _needs_the_ring_inside_the_field(
    side: int, disc: tuple[float, float, float], reach: float = ZONE_B_RADII[1]
) -> None:
    """Refuse a frame too small to hold the annulus the equivalents are measured over.

    A ring that leaves the field of view is not a smaller ring, it is a truncated one: the vessels
    crossing it are cut off, so every width measured there is measured on a fragment and every
    equivalent derived from those widths describes something nobody intended. At a clinical disc
    size this is a real constraint rather than a hypothetical — three disc radii is 2700 µm, so a
    frame under about 5.5 mm across cannot hold the ring at all, however many pixels it has.
    """
    x, y, radius = disc
    offset = math.hypot(x - side / 2.0, y - side / 2.0)
    if offset + reach * radius > side / 2.0:
        raise ValueError(
            f"the ring the equivalents are measured over reaches "
            f"{offset + reach * radius:.0f} px from the centre of a {side} px frame, which is "
            f"outside its field of view: widen the frame, lower the scale, or move the disc in"
        )


def _centre(side: int) -> tuple[float, float]:
    """Rotation is about the **frame** centre, and it turns the disc with everything else.

    Turning about the disc was the first idea and it is wrong: the disc sits near the top of the
    frame, so a vessel a third of a frame away from it sweeps a circle wide enough to leave the
    field of view, and a clipped vessel measures something other than the shape. Turning the whole
    scene keeps every distance — vessel to vessel, vessel to disc — exactly as it was, and a
    circular field of view is unchanged by the turn.
    """
    return (side / 2.0, side / 2.0)


def _turned_disc(
    side: int,
    rotation: float,
    um_per_px: float,
    at: tuple[float, float] = DISC_AT,
) -> tuple[float, float, float]:
    """Where the disc lands once the scene has been turned. Its radius does not change."""
    x, y, r = _disc(side, um_per_px, at=at)
    (moved_x, moved_y), = geometry.turn([(x, y)], rotation, _centre(side))
    return (moved_x, moved_y, r)


def _widths(um_per_px: float, artery_um: float, vein_um: float) -> tuple[float, float]:
    """A width stated in microns, in the pixels a mask is drawn in."""
    return artery_um / um_per_px, vein_um / um_per_px


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

def _shared(
    wa: float, wv: float, length_a: float, length_v: float, area_a: float, area_v: float, side: int
) -> dict[str, float]:
    """What every family pins in the same way, now that every family draws both classes.

    Two calibres and the ratio between them, a length and an area per class, and what those come
    to over the union — so an implementation reporting per class and one reporting over the
    vessels as a whole are each compared against the value that applies to them.
    """
    return {
        "vessel-calibre/mean-width/artery": wa,
        "vessel-calibre/mean-width/vein": wv,
        "avr/ratio-of-calibres/both": wa / wv,
        "vessel-area-and-length/skeleton-length/artery": length_a,
        "vessel-area-and-length/skeleton-length/vein": length_v,
        "vessel-area-and-length/skeleton-length/vessels": length_a + length_v,
        "vessel-area-and-length/area/artery": area_a,
        "vessel-area-and-length/area/vein": area_v,
        "vessel-area-and-length/area/vessels": area_a + area_v,
        "vascular-density/over-field-of-view/vessels": (area_a + area_v) / _fov_area(side),
    }


def straight(
    side: int,
    rotation: float = 0.0,
    um_per_px: float = UM_PER_PX,
    artery_um: float = ARTERY_WIDTH_UM,
    vein_um: float = VEIN_WIDTH_UM,
    length: float = 0.6,
) -> Shape:
    """A straight artery beside a straight vein: tortuosity exactly 1, and two widths to recover."""
    wa, wv = _widths(um_per_px, artery_um, vein_um)
    distance = length * side
    x0 = side * 0.5 - distance / 2.0
    lines = {
        "artery": [(x0, side * 0.44), (x0 + distance, side * 0.44)],
        "vein": [(x0, side * 0.60), (x0 + distance, side * 0.60)],
    }
    turned = {name: geometry.turn(part, rotation, _centre(side)) for name, part in lines.items()}
    return Shape(
        name="straight",
        side=side,
        rotation=rotation,
        um_per_px=um_per_px,
        artery=geometry.draw(turned["artery"], wa, side),
        vein=geometry.draw(turned["vein"], wv, side),
        fov=geometry.field_of_view(side),
        disc=_turned_disc(side, rotation, um_per_px),
        theory={
            **_shared(wa, wv, distance, distance, _tube(distance, wa), _tube(distance, wv), side),
            "tortuosity/hart-tau1/artery": 1.0,
            "tortuosity/hart-tau1/vein": 1.0,
            "tortuosity/hart-tau2/artery": 0.0,
            "tortuosity/hart-tau2/vein": 0.0,
            "tortuosity/hart-tau3/artery": 0.0,
            "tortuosity/hart-tau3/vein": 0.0,
            "tortuosity/hart-tau4/artery": 0.0,
            "tortuosity/hart-tau4/vein": 0.0,
            "tortuosity/hart-tau5/artery": 0.0,
            "tortuosity/hart-tau5/vein": 0.0,
            "junction-counts/junctions/vessels": 0.0,
            "junction-counts/components/vessels": 2.0,
            "junction-counts/endpoints/vessels": 4.0,
            "junction-counts/endpoints/artery": 2.0,
            "junction-counts/endpoints/vein": 2.0,
        },
        parameters={"artery_width": wa, "vein_width": wv, "length": distance},
        centreline=turned["artery"],
    )


def arc(
    side: int,
    rotation: float = 0.0,
    um_per_px: float = UM_PER_PX,
    artery_um: float = ARTERY_WIDTH_UM,
    vein_um: float = VEIN_WIDTH_UM,
    radius: float = 0.30,
    separation: float = 0.06,
    angle: float = 90.0,
) -> Shape:
    """Two concentric circular arcs: curvature exactly 1/r, and an arc-chord ratio in closed form.

    τ1 = θ / (2 sin(θ/2)) — arc length rθ over the chord 2r sin(θ/2), the r cancelling, so the
    ratio depends on how far the vessel bends and not at all on how large it is. An implementation
    whose τ1 changes with the radius is not computing τ1 — and the two classes here share an angle
    and differ in radius, so τ1 must come back the same for both while τ3, τ4 and τ5 must not.

    The vein runs **inside** the artery rather than outside it, because outside would put it
    through the edge of the field of view.
    """
    wa, wv = _widths(um_per_px, artery_um, vein_um)
    ra, rv, theta = radius * side, (radius - separation) * side, math.radians(angle)
    centre = (side * 0.5, side * 0.5 + ra / 2.0)
    first = -theta / 2.0 - math.pi / 2.0
    angles = np.linspace(first, first + theta, SAMPLES)
    turned = {}
    for name, r in (("artery", ra), ("vein", rv)):
        points = [(centre[0] + r * math.cos(a), centre[1] + r * math.sin(a)) for a in angles]
        turned[name] = geometry.turn(points, rotation, _centre(side))
    tau1 = theta / (2.0 * math.sin(theta / 2.0))
    return Shape(
        name="arc",
        side=side,
        rotation=rotation,
        um_per_px=um_per_px,
        artery=geometry.draw(turned["artery"], wa, side),
        vein=geometry.draw(turned["vein"], wv, side),
        fov=geometry.field_of_view(side),
        disc=_turned_disc(side, rotation, um_per_px),
        theory={
            **_shared(
                wa, wv, ra * theta, rv * theta,
                _tube(ra * theta, wa), _tube(rv * theta, wv), side,
            ),
            "tortuosity/hart-tau1/artery": tau1,
            "tortuosity/hart-tau1/vein": tau1,
            "tortuosity/hart-tau2/artery": theta,
            "tortuosity/hart-tau2/vein": theta,
            "tortuosity/hart-tau3/artery": theta / ra,
            "tortuosity/hart-tau3/vein": theta / rv,
            # Hart's compositional pair, and the reason he preferred them: both depend on the
            # radius alone, so measuring more of the same arc does not change them, while τ2 and
            # τ3 grow with however much of it happened to be traced.
            "tortuosity/hart-tau4/artery": 1.0 / ra,
            "tortuosity/hart-tau4/vein": 1.0 / rv,
            "tortuosity/hart-tau5/artery": 1.0 / (ra * ra),
            "tortuosity/hart-tau5/vein": 1.0 / (rv * rv),
            "junction-counts/junctions/vessels": 0.0,
            "junction-counts/components/vessels": 2.0,
            "junction-counts/endpoints/vessels": 4.0,
        },
        parameters={
            "artery_width": wa, "vein_width": wv,
            "artery_radius": ra, "vein_radius": rv, "angle": angle,
        },
        centreline=turned["artery"],
    )


def _sinusoid_measures(a: float, lam: float, span: float) -> tuple[float, float, float]:
    """Arc length and the two curvature integrals of one sine wave, by integration.

    Its arc length is an elliptic integral with no elementary closed form, so the theory here *is*
    the integral, evaluated finely enough that the result is exact to more places than any
    implementation will reach.
    """
    fine = np.linspace(0.0, span, 200_001)
    k = 2.0 * math.pi / lam
    slope = a * k * np.cos(k * fine)
    second = -a * k * k * np.sin(k * fine)
    element = np.sqrt(1.0 + slope**2)
    curvature = np.abs(second) / (1.0 + slope**2) ** 1.5
    return (
        float(np.trapezoid(element, fine)),
        float(np.trapezoid(curvature * element, fine)),
        float(np.trapezoid(curvature**2 * element, fine)),
    )


def sinusoid(
    side: int,
    rotation: float = 0.0,
    um_per_px: float = UM_PER_PX,
    artery_um: float = ARTERY_WIDTH_UM,
    vein_um: float = VEIN_WIDTH_UM,
    amplitude: float = 0.04,
    wavelength: float = 0.25,
    cycles: float = 2.0,
) -> Shape:
    """Two sine waves, one per class: arc length and the curvature integrals by integration."""
    wa, wv = _widths(um_per_px, artery_um, vein_um)
    a, lam = amplitude * side, wavelength * side
    span = lam * cycles
    x = np.linspace(0.0, span, SAMPLES)
    y = a * np.sin(2.0 * math.pi / lam * x)
    turned = {}
    for name, baseline in (("artery", 0.42), ("vein", 0.62)):
        points = [
            (side * 0.5 - span / 2.0 + float(px), side * baseline + float(py))
            for px, py in zip(x, y, strict=True)
        ]
        turned[name] = geometry.turn(points, rotation, _centre(side))
    length, total_curvature, total_squared = _sinusoid_measures(a, lam, span)
    return Shape(
        name="sinusoid",
        side=side,
        rotation=rotation,
        um_per_px=um_per_px,
        artery=geometry.draw(turned["artery"], wa, side),
        vein=geometry.draw(turned["vein"], wv, side),
        fov=geometry.field_of_view(side),
        disc=_turned_disc(side, rotation, um_per_px),
        theory={
            **_shared(
                wa, wv, length, length, _tube(length, wa), _tube(length, wv), side,
            ),
            # The two classes trace the same curve, so every shape-only quantity is the same for
            # both and only the widths tell them apart.
            "tortuosity/hart-tau1/artery": length / span,
            "tortuosity/hart-tau1/vein": length / span,
            "tortuosity/hart-tau2/artery": total_curvature,
            "tortuosity/hart-tau2/vein": total_curvature,
            "tortuosity/hart-tau3/artery": total_squared,
            "tortuosity/hart-tau3/vein": total_squared,
            "tortuosity/hart-tau4/artery": total_curvature / length,
            "tortuosity/hart-tau4/vein": total_curvature / length,
            "tortuosity/hart-tau5/artery": total_squared / length,
            "tortuosity/hart-tau5/vein": total_squared / length,
            "junction-counts/junctions/vessels": 0.0,
            "junction-counts/components/vessels": 2.0,
            "junction-counts/endpoints/vessels": 4.0,
        },
        parameters={
            "artery_width": wa, "vein_width": wv,
            "amplitude": a, "wavelength": lam, "cycles": cycles,
        },
        centreline=turned["artery"],
    )


def _wye(apex: tuple[float, float], reach: float, angle: float) -> list[list[tuple[float, float]]]:
    """A trunk and two daughters meeting at one point, symmetric about the vertical."""
    half = math.radians(angle) / 2.0
    return [
        [(apex[0], apex[1] - reach), apex],
        [apex, (apex[0] - reach * math.sin(half), apex[1] + reach * math.cos(half))],
        [apex, (apex[0] + reach * math.sin(half), apex[1] + reach * math.cos(half))],
    ]


def bifurcation(
    side: int,
    rotation: float = 0.0,
    um_per_px: float = UM_PER_PX,
    artery_um: float = ARTERY_WIDTH_UM,
    vein_um: float = VEIN_WIDTH_UM,
    angle: float = 60.0,
    arm: float = 0.18,
) -> Shape:
    """An arterial Y beside a venous one, each splitting at a known angle.

    Symmetric, so the angle between the daughters is exactly what was asked for and neither
    daughter is the trunk. One junction and three ends per class; side by side rather than one
    above the other, because stacking them would make the two Ys overlap.
    """
    wa, wv = _widths(um_per_px, artery_um, vein_um)
    reach = arm * side
    drawn = {}
    for name, (width, at_x) in (("artery", (wa, 0.32)), ("vein", (wv, 0.68))):
        mask = np.zeros((side, side), dtype=bool)
        for part in _wye((side * at_x, side * 0.42), reach, angle):
            mask |= geometry.draw(geometry.turn(part, rotation, _centre(side)), width, side)
        drawn[name] = mask
    return Shape(
        name="bifurcation",
        side=side,
        rotation=rotation,
        um_per_px=um_per_px,
        artery=drawn["artery"],
        vein=drawn["vein"],
        fov=geometry.field_of_view(side),
        disc=_turned_disc(side, rotation, um_per_px),
        theory={
            # A junction's own pixels are counted in neither arm's length, so the area of a Y is
            # not three tubes added up; the length is, and only the length is promised here.
            "vessel-calibre/mean-width/artery": wa,
            "vessel-calibre/mean-width/vein": wv,
            "avr/ratio-of-calibres/both": wa / wv,
            "vessel-area-and-length/skeleton-length/artery": 3.0 * reach,
            "vessel-area-and-length/skeleton-length/vein": 3.0 * reach,
            "vessel-area-and-length/skeleton-length/vessels": 6.0 * reach,
            "bifurcation-angle/between-daughters/artery": float(angle),
            "bifurcation-angle/between-daughters/vein": float(angle),
            "junction-counts/junctions/artery": 1.0,
            "junction-counts/junctions/vein": 1.0,
            "junction-counts/junctions/vessels": 2.0,
            "junction-counts/endpoints/artery": 3.0,
            "junction-counts/endpoints/vein": 3.0,
            "junction-counts/endpoints/vessels": 6.0,
            "junction-counts/components/vessels": 2.0,
        },
        parameters={"artery_width": wa, "vein_width": wv, "angle": angle, "arm": reach},
    )


def disjoint(
    side: int,
    rotation: float = 0.0,
    um_per_px: float = UM_PER_PX,
    artery_um: float = ARTERY_WIDTH_UM,
    vein_um: float = VEIN_WIDTH_UM,
    segments: float = 4,
    length: float = 0.4,
) -> Shape:
    """Parallel vessels that never meet, alternating class: no junctions, and as many components
    as there are lines.

    A skeletoniser that joins them, or a junction counter that finds a crossing where two vessels
    merely pass near one another, says so here and nowhere else. Alternating the classes means a
    vessel of each kind has a vessel of the other kind as its neighbour, which is where a
    classifier that leaks between them shows it.
    """
    wa, wv = _widths(um_per_px, artery_um, vein_um)
    distance, count = length * side, int(segments)
    spacing = side * 0.09
    drawn = {"artery": np.zeros((side, side), dtype=bool), "vein": np.zeros((side, side), dtype=bool)}
    first = side * 0.5 - spacing * (2 * count - 1) / 2.0
    for index in range(2 * count):
        y = first + index * spacing
        part = [(side * 0.5 - distance / 2.0, y), (side * 0.5 + distance / 2.0, y)]
        turned = geometry.turn(part, rotation, _centre(side))
        name = "artery" if index % 2 == 0 else "vein"
        drawn[name] |= geometry.draw(turned, wa if name == "artery" else wv, side)
    return Shape(
        name="disjoint",
        side=side,
        rotation=rotation,
        um_per_px=um_per_px,
        artery=drawn["artery"],
        vein=drawn["vein"],
        fov=geometry.field_of_view(side),
        disc=_turned_disc(side, rotation, um_per_px),
        theory={
            **_shared(
                wa, wv, count * distance, count * distance,
                count * _tube(distance, wa), count * _tube(distance, wv), side,
            ),
            "tortuosity/hart-tau1/artery": 1.0,
            "tortuosity/hart-tau1/vein": 1.0,
            "junction-counts/junctions/vessels": 0.0,
            "junction-counts/endpoints/artery": 2.0 * count,
            "junction-counts/endpoints/vein": 2.0 * count,
            "junction-counts/endpoints/vessels": 4.0 * count,
            "junction-counts/components/artery": float(count),
            "junction-counts/components/vein": float(count),
            "junction-counts/components/vessels": float(2 * count),
        },
        parameters={
            "artery_width": wa, "vein_width": wv,
            "segments_per_class": float(count), "length": distance,
        },
    )


def artery_vein_pair(
    side: int,
    rotation: float = 0.0,
    um_per_px: float = UM_PER_PX,
    artery_um: float = ARTERY_WIDTH_UM,
    vein_um: float = VEIN_WIDTH_UM,
    length: float = 0.5,
) -> Shape:
    """One artery beside one vein, of known widths: the ratio is exactly the ratio of the widths.

    What this tests is a ratio of two calibres and the degenerate case of the equivalents: one
    vessel per class crosses the ring, and Knudtson's recursion returns a lone vessel's own width
    untouched while Hubbard's has nothing to combine it with.
    """
    wa, wv = _widths(um_per_px, artery_um, vein_um)
    distance = length * side
    x0, x1 = side * 0.5 - distance / 2.0, side * 0.5 + distance / 2.0
    above = geometry.turn([(x0, side * 0.45), (x1, side * 0.45)], rotation, _centre(side))
    below = geometry.turn([(x0, side * 0.62), (x1, side * 0.62)], rotation, _centre(side))
    return Shape(
        name="artery-vein-pair",
        side=side,
        rotation=rotation,
        um_per_px=um_per_px,
        artery=geometry.draw(above, wa, side),
        vein=geometry.draw(below, wv, side),
        fov=geometry.field_of_view(side),
        disc=_turned_disc(side, rotation, um_per_px),
        theory={
            **_shared(wa, wv, distance, distance, _tube(distance, wa), _tube(distance, wv), side),
            # One artery and one vein cross the ring, which is a degenerate but legitimate case:
            # Knudtson's recursion returns a lone vessel's own width untouched. Hubbard's combines
            # a pair and so has no value here at all — an implementation must decline rather than
            # invent a second vessel, and this is the shape that asks it to.
            "central-retinal-equivalents/knudtson/artery": knudtson([wa], "artery"),
            "central-retinal-equivalents/knudtson/vein": knudtson([wv], "vein"),
            "avr/knudtson/both": knudtson([wa], "artery") / knudtson([wv], "vein"),
            "tortuosity/hart-tau1/artery": 1.0,
            "tortuosity/hart-tau1/vein": 1.0,
            "junction-counts/junctions/vessels": 0.0,
            "junction-counts/components/vessels": 2.0,
            "junction-counts/endpoints/vessels": 4.0,
        },
        parameters={"artery_width": wa, "vein_width": wv, "length": distance},
    )


def _spokes(
    name: str,
    at: tuple[float, float],
    side: int,
    rotation: float,
    um_per_px: float,
    artery_um: float,
    vein_um: float,
    vessels: float,
) -> Shape:
    """Vessels radiating from the optic disc, crossing the ring the equivalents are measured over.

    Six arteries and six veins of constant width, each running from the disc margin out past three
    disc radii, so every one of them crosses the annulus between two and three radii that PVBM
    builds as zone C minus zone B. That is what a central retinal equivalent needs: an
    implementation measuring in the right ring finds twelve vessels of two known widths, and one
    measuring somewhere else finds nothing or finds them twice.

    All the arteries share a width and all the veins share theirs, so the Knudtson recursion gives
    the same number whatever order an implementation pairs them in — the shape tests the formula
    and the region rather than a sorting convention.

    The two classes alternate around the disc, twelve spokes evenly spaced, so neither class is
    bunched on one side where a half-ring or a temporal-only convention would miss it.
    """
    count = int(vessels)
    wa, wv = _widths(um_per_px, artery_um, vein_um)
    x, y, radius = _disc(side, um_per_px, at=at)
    _needs_the_ring_inside_the_field(side, (x, y, radius))
    # Out to a little past the ring's outer edge, so a spoke crosses the whole annulus rather
    # than stopping inside it — and no further, because the field of view has an edge.
    inner, outer = radius, radius * (ZONE_B_RADII[1] + 0.2)
    drawn = {"artery": np.zeros((side, side), dtype=bool), "vein": np.zeros((side, side), dtype=bool)}
    for index in range(2 * count):
        heading = 2.0 * math.pi * index / (2 * count)
        spoke = [
            (x + inner * math.cos(heading), y + inner * math.sin(heading)),
            (x + outer * math.cos(heading), y + outer * math.sin(heading)),
        ]
        turned = geometry.turn(spoke, rotation, _centre(side))
        which = "artery" if index % 2 == 0 else "vein"
        drawn[which] |= geometry.draw(turned, wa if which == "artery" else wv, side)
    crae = knudtson([wa] * count, "artery")
    crve = knudtson([wv] * count, "vein")
    # Hubbard's constants were fitted in microns, so its widths go in as microns and its answer
    # comes out in microns. That is the one place the scale a shape was built with changes what
    # the theory says.
    crae_um = hubbard([wa * um_per_px] * count, "artery")
    crve_um = hubbard([wv * um_per_px] * count, "vein")
    length = outer - inner
    return Shape(
        name=name,
        side=side,
        rotation=rotation,
        um_per_px=um_per_px,
        artery=drawn["artery"],
        vein=drawn["vein"],
        fov=geometry.field_of_view(side),
        disc=_turned_disc(side, rotation, um_per_px, at=at),
        theory={
            **_shared(
                wa, wv, count * length, count * length,
                count * _tube(length, wa), count * _tube(length, wv), side,
            ),
            "central-retinal-equivalents/knudtson/artery": crae,
            "central-retinal-equivalents/knudtson/vein": crve,
            "avr/knudtson/both": crae / crve,
            "central-retinal-equivalents/hubbard/artery": crae_um,
            "central-retinal-equivalents/hubbard/vein": crve_um,
            "avr/hubbard/both": crae_um / crve_um,
            "tortuosity/hart-tau1/artery": 1.0,
            "tortuosity/hart-tau1/vein": 1.0,
            "junction-counts/components/artery": float(count),
            "junction-counts/components/vein": float(count),
            "junction-counts/components/vessels": float(2 * count),
            "junction-counts/junctions/vessels": 0.0,
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


def spokes_macula_centred(
    side: int,
    rotation: float = 0.0,
    um_per_px: float = UM_PER_PX,
    artery_um: float = ARTERY_WIDTH_UM,
    vein_um: float = VEIN_WIDTH_UM,
    vessels: float = 6,
) -> Shape:
    """The spokes as a macula-centred photograph frames them: the disc off to one side.

    This is how most fundus photography is taken — the macula in the middle, the disc nasal to it —
    and it is the harder of the two for a measurement anchored on the disc, because the ring runs
    towards the edge of the field where a photograph is dimmest and a segmentation weakest.
    """
    return _spokes(
        "spokes-macula-centred", DISC_AT, side, rotation, um_per_px, artery_um, vein_um, vessels
    )


def spokes_disc_centred(
    side: int,
    rotation: float = 0.0,
    um_per_px: float = UM_PER_PX,
    artery_um: float = ARTERY_WIDTH_UM,
    vein_um: float = VEIN_WIDTH_UM,
    vessels: float = 6,
) -> Shape:
    """The spokes as a disc-centred photograph frames them: the disc in the middle of the frame.

    The same retina and the same vessels as `spokes-macula-centred`, photographed the other way,
    so the two differ in nothing but where the disc sits. Every disc-anchored measurement should
    therefore return the same number on both — and a difference between them is a measurement
    reading the framing rather than the eye.
    """
    return _spokes(
        "spokes-disc-centred", (0.5, 0.5), side, rotation, um_per_px, artery_um, vein_um, vessels
    )


def demo_image(shape: Shape, rings: bool = True) -> np.ndarray:
    """One picture of a rendering for a person to look at, as `H×W×3` 8-bit colour.

    Nothing measures this: the masks are what an implementation is handed, and this is so a reader
    can see at a glance which class is which, where the disc is, and whether the ring the
    equivalents are measured over actually has vessels crossing it.

    A rendering read back from a store carries the same four things — its masks, its field and its
    disc — so one can be passed here in place of a shape that was just built.
    """
    side = shape.side
    picture = np.zeros((side, side, 3), dtype=np.uint8)
    picture[shape.fov] = FIELD_COLOUR
    if rings:
        x, y, radius = shape.disc
        grid = np.arange(side, dtype=np.float64) + 0.5
        px, py = np.meshgrid(grid, grid)
        away = np.hypot(px - x, py - y) / radius
        for at in (*ZONE_B_RADII, 1.0):
            edge = np.abs(away - at) < (1.5 / radius)
            picture[edge & shape.fov] = DISC_COLOUR if at == 1.0 else RING_COLOUR
    if shape.artery is not None:
        picture[shape.artery] = ARTERY_COLOUR
    if shape.vein is not None:
        picture[shape.vein] = VEIN_COLOUR
    if shape.artery is not None and shape.vein is not None:
        # Where the two classes claim the same pixel. It should never happen in a synthetic shape,
        # so it is coloured to be noticed rather than blended away.
        picture[shape.artery & shape.vein] = OVERLAP_COLOUR
    return picture


#: Every shape, by the name its images and its rows are keyed on.
SHAPES: dict[str, Callable[..., Shape]] = {
    "straight": straight,
    "arc": arc,
    "sinusoid": sinusoid,
    "bifurcation": bifurcation,
    "disjoint": disjoint,
    "artery-vein-pair": artery_vein_pair,
    "spokes-macula-centred": spokes_macula_centred,
    "spokes-disc-centred": spokes_disc_centred,
}
