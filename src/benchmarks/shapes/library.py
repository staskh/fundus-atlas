# ABOUTME: The shapes a biomarker implementation is measured against, and the values their geometry
# ABOUTME: requires. Pure geometry and arithmetic: no implementation is called and nothing is scored.

import math
from collections.abc import Callable
from dataclasses import dataclass, field

import numpy as np

from . import geometry
from . import theory as theory_module


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
    ((moved_x, moved_y),) = geometry.turn([(x, y)], rotation, _centre(side))
    return (moved_x, moved_y, r)


def _widths(um_per_px: float, artery_um: float, vein_um: float) -> tuple[float, float]:
    """A width stated in microns, in the pixels a mask is drawn in."""
    return artery_um / um_per_px, vein_um / um_per_px


def _margin(disc: tuple[float, float, float], heading: float) -> tuple[float, float]:
    """A point on the optic disc's **margin**, at a heading measured from due right.

    Vessels leave the eye at the disc, and they leave it at its edge rather than from its centre —
    the centre is where the disc is, not where a vessel starts. Every shape here but `disjoint`
    therefore begins on this circle, which is also what the disc-anchored measurements assume when
    they walk a vessel inwards looking for where it started.
    """
    x, y, radius = disc
    angle = math.radians(heading)
    return (x + radius * math.cos(angle), y + radius * math.sin(angle))


def _outward(
    disc: tuple[float, float, float], heading: float, reach: float, samples: int = 2
) -> np.ndarray:
    """A straight vessel from the disc margin, heading away from the disc."""
    start = _margin(disc, heading)
    angle = math.radians(heading)
    along = np.linspace(0.0, reach, samples)
    return np.stack(
        [start[0] + along * math.cos(angle), start[1] + along * math.sin(angle)], axis=1
    )


def _named(values: dict[str, float], structure: str) -> dict[str, float]:
    """One curve's values, under the structure they were measured over."""
    return {f"{name}/{structure}": value for name, value in values.items()}


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


def _coarse(points: np.ndarray) -> list[tuple[float, float]]:
    """A curve thinned to about `SAMPLES` points, keeping its last one.

    Drawing and integrating want different samplings: a rasteriser needs only enough points
    that a segment strays well under a pixel from the curve; an integral wants as many as it
    can get. Using one sampling for both makes one of them wrong or slow.
    """
    step = max(1, len(points) // SAMPLES)
    thinned = [tuple(p) for p in points[::step]]
    if thinned[-1] != tuple(points[-1]):
        thinned.append(tuple(points[-1]))
    return thinned


def _needs_the_vessels_inside_the_field(side: int, parts: list[np.ndarray]) -> None:
    """Refuse a frame too small to hold the vessels it was asked to draw.

    Every shape here leaves the optic disc, and a disc of clinical size takes up a large part of a
    small frame — so a vessel of a given length can run off the edge, and a clipped vessel measures
    something other than the shape. It is the same refusal the ring gets, for the same reason: a
    truncated drawing is not a smaller drawing.
    """
    limit = side / 2.0
    for points in parts:
        away = np.hypot(points[:, 0] - limit, points[:, 1] - limit).max()
        if away > limit:
            raise ValueError(
                f"a vessel reaches {away:.0f} px from the centre of a {side} px frame, which is "
                f"outside its field of view: widen the frame, lower the scale, or shorten it"
            )


def _compose(
    name: str,
    side: int,
    rotation: float,
    um_per_px: float,
    at: tuple[float, float],
    artery: list[tuple[np.ndarray, np.ndarray]],
    vein: list[tuple[np.ndarray, np.ndarray]],
    wa: float,
    wv: float,
    counts: dict[str, float],
    extra: dict[str, float] | None = None,
    curved: bool = True,
    parameters: dict[str, float] | None = None,
) -> Shape:
    """One shape, from the centrelines of each class: drawn once, and its values derived once.

    Every part is a `(points, curvature)` pair in unrotated coordinates. The parts of one class are
    identical in everything but position wherever a shape can manage it, because then no
    aggregation — a median, a mean, a length-weighted mean — can disagree about the answer, and the
    shape tests the formula rather than somebody's choice of average.

    :param curved: whether the curvature integrals are defined. A vessel made of straight pieces
        has zero curvature everywhere it is defined and corners where it is not, so a shape whose
        vessels turn at a corner pins arc-over-chord and leaves the integrals alone rather than
        claiming a zero no implementation can return.
    """
    centre = _centre(side)
    _needs_the_vessels_inside_the_field(side, [points for points, _ in artery + vein])
    drawn: dict[str, np.ndarray] = {}
    turned: dict[str, list[np.ndarray]] = {}
    for structure, parts, width in (("artery", artery, wa), ("vein", vein, wv)):
        mask = np.zeros((side, side), dtype=bool)
        turned[structure] = []
        for points, _curvature in parts:
            moved = np.asarray(geometry.turn([tuple(p) for p in points], rotation, centre))
            turned[structure].append(moved)
            # Drawn from a coarse sample and integrated from the fine one: a rasteriser measuring
            # distance to each segment needs only enough points that a segment strays well
            # under a pixel, while handing it the integration sample means walking two
            # hundred thousand segments per vessel.
            mask |= geometry.draw(_coarse(moved), width, side)
        drawn[structure] = mask

    theory: dict[str, float] = {}
    for structure, parts, width in (("artery", artery, wa), ("vein", vein, wv)):
        values = [theory_module.curve(points, curvature) for points, curvature in parts]
        length = sum(value["vessel-area-and-length/skeleton-length"] for value in values)
        area = sum(
            theory_module.tube(value["vessel-area-and-length/skeleton-length"], width)
            for value in values
        )
        theory.update(
            _named(
                {
                    "vessel-calibre/mean-width": width,
                    # Every vessel of a class shares a width, so the median is the mean.
                    "vessel-calibre/median-width": width,
                    "vessel-area-and-length/skeleton-length": length,
                    "vessel-area-and-length/area": area,
                },
                structure,
            )
        )
        # A quantity every part agrees on is the shape's; one they disagree about is an aggregation
        # question the shape cannot answer, and is left out rather than guessed at.
        shared_names = set(values[0]) - {"vessel-area-and-length/skeleton-length"}
        if not curved:
            shared_names = {n for n in shared_names if n in {"tortuosity/hart-tau1"}}
        for quantity in sorted(shared_names):
            found = {round(value[quantity], 9) for value in values}
            if len(found) == 1 and math.isfinite(next(iter(found))):
                theory[f"{quantity}/{structure}"] = values[0][quantity]

    both_areas = (
        theory["vessel-area-and-length/area/artery"] + theory["vessel-area-and-length/area/vein"]
    )
    theory.update(
        {
            "vessel-area-and-length/skeleton-length/vessels": (
                theory["vessel-area-and-length/skeleton-length/artery"]
                + theory["vessel-area-and-length/skeleton-length/vein"]
            ),
            "vessel-area-and-length/area/vessels": both_areas,
            "vascular-density/over-field-of-view/vessels": both_areas / _fov_area(side),
            # The whole frame, lit or not, which is what an implementation dividing by
            # `height × width` is measuring.
            "vascular-density/over-image/vessels": both_areas / float(side * side),
            "avr/ratio-of-calibres/both": wa / wv,
        }
    )
    theory.update(counts)
    if extra:
        theory.update(extra)

    # How far the retina is from a vessel, over both classes together and over each alone.
    #
    # Measured on the **unrotated** centrelines. Turning the scene about the centre of a circular
    # field turns the whole distance field with it, so this quantity cannot depend on the angle —
    # but evaluating it on a grid can, by a hair, because the samples fall differently. Computing
    # it once, before the turn, keeps the theory identical at every angle, which is exactly what
    # every shape here promises and what the shapes notebook asserts.
    everything = [(np.asarray(points), wa) for points, _ in artery] + [
        (np.asarray(points), wv) for points, _ in vein
    ]
    for structure, parts in (
        ("artery", [(np.asarray(points), wa) for points, _ in artery]),
        ("vein", [(np.asarray(points), wv) for points, _ in vein]),
        ("vessels", everything),
    ):
        mean, furthest = theory_module.sparsity(
            [np.asarray(_coarse(points)) for points, _ in parts],
            [width for _, width in parts],
            side,
        )
        theory[f"sparsity/mean-distance/{structure}"] = mean
        theory[f"sparsity/max-distance/{structure}"] = furthest

    return Shape(
        name=name,
        side=side,
        rotation=rotation,
        um_per_px=um_per_px,
        artery=drawn["artery"],
        vein=drawn["vein"],
        fov=geometry.field_of_view(side),
        disc=_turned_disc(side, rotation, um_per_px, at=at),
        theory=theory,
        parameters={"artery_width": wa, "vein_width": wv, **(parameters or {})},
        centreline=[tuple(p) for p in turned["artery"][0]],
    )


def straight(
    side: int,
    rotation: float = 0.0,
    um_per_px: float = UM_PER_PX,
    artery_um: float = ARTERY_WIDTH_UM,
    vein_um: float = VEIN_WIDTH_UM,
    length: float = 0.30,
) -> Shape:
    """One straight vessel per class, leaving the optic disc at right angles to each other.

    The artery runs horizontally and the vein vertically, so that a measurement which walks the
    pixel lattice rather than the vessel disagrees with itself between the two: a digital line at
    0° and one at 90° are both exact, and one at 30° is not. Both are exactly as tortuous as a
    straight line, which is to say exactly 1.
    """
    wa, wv = _widths(um_per_px, artery_um, vein_um)
    disc = _disc(side, um_per_px)
    reach = length * side
    return _compose(
        "straight",
        side,
        rotation,
        um_per_px,
        DISC_AT,
        artery=[(_outward(disc, 180.0, reach), np.zeros(2))],
        vein=[(_outward(disc, 90.0, reach), np.zeros(2))],
        wa=wa,
        wv=wv,
        counts={
            "junction-counts/junctions/artery": 0.0,
            "junction-counts/junctions/vein": 0.0,
            "junction-counts/junctions/vessels": 0.0,
            "junction-counts/endpoints/artery": 2.0,
            "junction-counts/endpoints/vein": 2.0,
            "junction-counts/endpoints/vessels": 4.0,
            "junction-counts/components/artery": 1.0,
            "junction-counts/components/vein": 1.0,
            "junction-counts/components/vessels": 2.0,
        },
    )


def arc(
    side: int,
    rotation: float = 0.0,
    um_per_px: float = UM_PER_PX,
    artery_um: float = ARTERY_WIDTH_UM,
    vein_um: float = VEIN_WIDTH_UM,
    radius: float = 0.22,
    angle: float = 90.0,
) -> Shape:
    """A circular arc per class, each leaving the disc margin and bending away from it.

    Curvature is exactly `1/r` everywhere, so every one of Hart's measures has a closed form and
    the arc-over-chord ratio `θ / (2 sin(θ/2))` does not depend on how large the arc is. The two
    classes bend by the same angle about different radii, so τ1 must come back equal for both and
    the curvature integrals must not.
    """
    wa, wv = _widths(um_per_px, artery_um, vein_um)
    disc = _disc(side, um_per_px)
    theta = math.radians(angle)
    # The vein bends more tightly than the artery, so the two share an angle and differ in radius —
    # which is what makes τ1 come back equal for both while the curvature integrals do not.
    ra, rv = radius * side, radius * 0.75 * side
    parts = {}
    for structure, heading, r in (("artery", 180.0, ra), ("vein", 250.0, rv)):
        start = _margin(disc, heading)
        # Turning left off the margin, so the arc curves into the frame rather than across it.
        away = math.radians(heading)
        centre = (start[0] - r * math.sin(away), start[1] + r * math.cos(away))
        first = math.atan2(start[1] - centre[1], start[0] - centre[0])
        sweep = np.linspace(first, first + theta, theory_module.STEPS)
        points = np.stack([centre[0] + r * np.cos(sweep), centre[1] + r * np.sin(sweep)], axis=1)
        parts[structure] = [(points, np.full(len(sweep), 1.0 / r))]
    return _compose(
        "arc",
        side,
        rotation,
        um_per_px,
        DISC_AT,
        artery=parts["artery"],
        vein=parts["vein"],
        wa=wa,
        wv=wv,
        parameters={"artery_radius": ra, "vein_radius": rv, "angle": angle},
        counts={
            "junction-counts/junctions/vessels": 0.0,
            "junction-counts/endpoints/artery": 2.0,
            "junction-counts/endpoints/vein": 2.0,
            "junction-counts/endpoints/vessels": 4.0,
            "junction-counts/components/vessels": 2.0,
        },
    )


def sinusoid(
    side: int,
    rotation: float = 0.0,
    um_per_px: float = UM_PER_PX,
    artery_um: float = ARTERY_WIDTH_UM,
    vein_um: float = VEIN_WIDTH_UM,
    amplitude: float = 0.035,
    wavelength: float = 0.16,
    cycles: float = 1.5,
) -> Shape:
    """A sine wave per class, leaving the disc margin and waving away from it.

    Its arc length is an elliptic integral with no elementary closed form, so the value here *is*
    the integral. It is the only shape whose curvature changes sign, which makes it the one that
    settles the inflection count and Grisan's density — both of which are zero everywhere else.
    """
    wa, wv = _widths(um_per_px, artery_um, vein_um)
    disc = _disc(side, um_per_px)
    a, lam = amplitude * side, wavelength * side
    span = lam * cycles
    parts = {}
    for structure, heading in (("artery", 180.0), ("vein", 100.0)):
        start = _margin(disc, heading)
        away = math.radians(heading)
        along = np.linspace(0.0, span, theory_module.STEPS)
        k = 2.0 * math.pi / lam
        across = a * np.sin(k * along)
        # Waving about the outward heading rather than about the x axis, so it leaves the disc.
        points = np.stack(
            [
                start[0] + along * math.cos(away) - across * math.sin(away),
                start[1] + along * math.sin(away) + across * math.cos(away),
            ],
            axis=1,
        )
        slope = a * k * np.cos(k * along)
        second = -a * k * k * np.sin(k * along)
        curvature = second / (1.0 + slope**2) ** 1.5
        parts[structure] = [(points, curvature)]
    return _compose(
        "sinusoid",
        side,
        rotation,
        um_per_px,
        DISC_AT,
        artery=parts["artery"],
        vein=parts["vein"],
        wa=wa,
        wv=wv,
        parameters={"amplitude": a, "wavelength": lam, "cycles": cycles, "span": span},
        counts={
            "junction-counts/junctions/vessels": 0.0,
            "junction-counts/endpoints/artery": 2.0,
            "junction-counts/endpoints/vein": 2.0,
            "junction-counts/endpoints/vessels": 4.0,
            "junction-counts/components/vessels": 2.0,
        },
    )


def _fork(start, heading: float, reach: float, angle: float):
    """Two straight daughters leaving one point, symmetric about the heading they came in on."""
    return [
        _line(start, heading - angle / 2.0, reach),
        _line(start, heading + angle / 2.0, reach),
    ]


def _line(start, heading: float, reach: float) -> np.ndarray:
    angle = math.radians(heading)
    return np.array(
        [start, (start[0] + reach * math.cos(angle), start[1] + reach * math.sin(angle))]
    )


def bifurcation(
    side: int,
    rotation: float = 0.0,
    um_per_px: float = UM_PER_PX,
    artery_um: float = ARTERY_WIDTH_UM,
    vein_um: float = VEIN_WIDTH_UM,
    angle: float = 60.0,
    arm: float = 0.13,
) -> Shape:
    """A trunk leaving the disc and splitting once, per class.

    Symmetric, so the angle between the daughters is exactly what was asked for and neither
    daughter is the trunk. Every piece is straight, so each is exactly as tortuous as a straight
    line whatever an implementation averages over.
    """
    wa, wv = _widths(um_per_px, artery_um, vein_um)
    disc = _disc(side, um_per_px)
    reach = arm * side
    parts = {}
    for structure, heading in (("artery", 180.0), ("vein", 120.0)):
        trunk = _outward(disc, heading, reach)
        parts[structure] = [
            (trunk, np.zeros(2)),
            *((piece, np.zeros(2)) for piece in _fork(trunk[-1], heading, reach, angle)),
        ]
    return _compose(
        "bifurcation",
        side,
        rotation,
        um_per_px,
        DISC_AT,
        artery=parts["artery"],
        vein=parts["vein"],
        wa=wa,
        wv=wv,
        curved=False,
        parameters={"angle": float(angle), "arm": reach},
        counts={
            "bifurcation-angle/between-daughters/artery": float(angle),
            "bifurcation-angle/between-daughters/vein": float(angle),
            "junction-counts/junctions/artery": 1.0,
            "junction-counts/junctions/vein": 1.0,
            "junction-counts/junctions/vessels": 2.0,
            "junction-counts/endpoints/artery": 3.0,
            "junction-counts/endpoints/vein": 3.0,
            "junction-counts/endpoints/vessels": 6.0,
            "junction-counts/components/artery": 1.0,
            "junction-counts/components/vein": 1.0,
            "junction-counts/components/vessels": 2.0,
        },
    )


def deep_bifurcation(
    side: int,
    rotation: float = 0.0,
    um_per_px: float = UM_PER_PX,
    artery_um: float = ARTERY_WIDTH_UM,
    vein_um: float = VEIN_WIDTH_UM,
    angle: float = 50.0,
    arm: float = 0.07,
    generations: float = 3,
    spur: float = 0.35,
) -> Shape:
    """A tree: a trunk from the disc, forking repeatedly, with short spurs along the way.

    This is the shape that exercises what a single fork cannot. A real vasculature is a tree, and
    the things that go wrong on one — a junction counted as a cluster of pixels, a walk that loses
    a branch, a spur too short to survive a length filter — need more than one generation to show.
    Some daughters fork again and some end; each fork also carries a **spur**, a stub a third the
    length of its siblings, because a filter that discards short segments will silently change the
    count and nothing else here would notice.

    Every piece is straight, so the tortuosity of each is exactly 1 whatever an implementation
    averages over, and what the shape settles is the counting.
    """
    wa, wv = _widths(um_per_px, artery_um, vein_um)
    disc = _disc(side, um_per_px)
    reach = arm * side
    depth = int(generations)
    parts: dict[str, list[tuple[np.ndarray, np.ndarray]]] = {}
    tally = {"pieces": 0, "junctions": 0, "ends": 0}
    for structure, heading in (("artery", 190.0), ("vein", 130.0)):
        pieces: list[np.ndarray] = []
        trunk = _outward(disc, heading, reach)
        pieces.append(trunk)
        growing = [(trunk[-1], heading)]
        for generation in range(depth):
            nxt = []
            for tip, came in growing:
                daughters = _fork(tip, came, reach, angle)
                pieces.extend(daughters)
                # A stub off the same junction: short enough that a length filter may drop it.
                pieces.append(_line(tip, came + 90.0, reach * spur))
                if generation < depth - 1:
                    nxt.append((daughters[0][-1], came - angle / 2.0))
                    nxt.append((daughters[1][-1], came + angle / 2.0))
            growing = nxt
        parts[structure] = [(piece, np.zeros(2)) for piece in pieces]
        forks = sum(2**generation for generation in range(depth))
        tally = {
            # One junction per fork, and the spur meets the vessel at that same point.
            "junctions": float(forks),
            # Every free end: the trunk's start, each spur's tip, and each final daughter.
            "ends": float(1 + forks + 2**depth),
            "pieces": float(len(pieces)),
        }
    return _compose(
        "deep-bifurcation",
        side,
        rotation,
        um_per_px,
        DISC_AT,
        artery=parts["artery"],
        vein=parts["vein"],
        wa=wa,
        wv=wv,
        curved=False,
        counts={
            "bifurcation-angle/between-daughters/artery": float(angle),
            "bifurcation-angle/between-daughters/vein": float(angle),
            "junction-counts/junctions/artery": tally["junctions"],
            "junction-counts/junctions/vein": tally["junctions"],
            "junction-counts/junctions/vessels": 2.0 * tally["junctions"],
            "junction-counts/endpoints/artery": tally["ends"],
            "junction-counts/endpoints/vein": tally["ends"],
            "junction-counts/endpoints/vessels": 2.0 * tally["ends"],
            "junction-counts/components/artery": 1.0,
            "junction-counts/components/vein": 1.0,
            "junction-counts/components/vessels": 2.0,
        },
    )


def disjoint(
    side: int,
    rotation: float = 0.0,
    um_per_px: float = UM_PER_PX,
    artery_um: float = ARTERY_WIDTH_UM,
    vein_um: float = VEIN_WIDTH_UM,
    segments: float = 4,
    length: float = 0.34,
) -> Shape:
    """Parallel vessels that never meet, alternating class — and the one shape not on the disc.

    Every other shape here leaves the optic disc, because vessels do. This one deliberately does
    not: it is what shows whether a measurement quietly requires a vessel to reach the disc before
    it will count it, which is a restriction some implementations impose and none announce.
    """
    wa, wv = _widths(um_per_px, artery_um, vein_um)
    distance, count = length * side, int(segments)
    spacing = side * 0.075
    first = side * 0.5 - spacing * (2 * count - 1) / 2.0
    parts: dict[str, list[tuple[np.ndarray, np.ndarray]]] = {"artery": [], "vein": []}
    for index in range(2 * count):
        y = first + index * spacing
        line = np.array([(side * 0.32 - distance / 2.0, y), (side * 0.32 + distance / 2.0, y)])
        parts["artery" if index % 2 == 0 else "vein"].append((line, np.zeros(2)))
    return _compose(
        "disjoint",
        side,
        rotation,
        um_per_px,
        DISC_AT,
        artery=parts["artery"],
        vein=parts["vein"],
        wa=wa,
        wv=wv,
        curved=False,
        counts={
            "junction-counts/junctions/artery": 0.0,
            "junction-counts/junctions/vein": 0.0,
            "junction-counts/junctions/vessels": 0.0,
            "junction-counts/endpoints/artery": 2.0 * count,
            "junction-counts/endpoints/vein": 2.0 * count,
            "junction-counts/endpoints/vessels": 4.0 * count,
            "junction-counts/components/artery": float(count),
            "junction-counts/components/vein": float(count),
            "junction-counts/components/vessels": float(2 * count),
        },
    )


#: The Koch curve's similarity dimension: four copies at a third of the length, so `log 4 / log 3`.
#: It is exact, it is not an integer, and it is a value a box count over a finite raster can
#: plausibly reach — which an ordinary vessel's dimension of 1 is not.
KOCH_DIMENSION = math.log(4.0) / math.log(3.0)

#: How wide the Koch curve's vessels are drawn, as a fraction of every other shape's width.
#:
#: **The box dimension of a drawn curve is governed by how thick the vessel is, not by how many
#: generations it has.** Thickening adds area-like scaling at every box size below the width, which
#: pulls the estimate towards 2 from underneath: at full width a box count over this frame returns
#: about 1.41 whatever the depth, and it only falls to the 1.2619 the geometry requires as the
#: vessel narrows. Half width is where it lands — 1.28 measured against 1.2619 — and 40 µm is an
#: ordinary arteriole rather than an invention.
KOCH_WIDTH_FRACTION = 0.5

#: How many times the finest generation must exceed the vessel width before the curve is considered
#: to be in the image at all.
#:
#: Three is a proxy rather than a threshold anybody derived, and it is set from what was measured
#: across depths and widths on a 2048 px frame. Well above it — at six times, which is where this
#: shape now sits — the drawn arc-to-chord ratio and box dimension both land within a few percent
#: of the geometry, the skeleton carries four to six endpoints against the two a clean curve has,
#: and turning the picture moves the ratio by about 1%. Below one, which is where four generations
#: at full width sat, the arc-to-chord ratio collapses by 31%, the box dimension rises to 1.51, and
#: the skeleton sprouts a dozen endpoints out of merged spikes.
#:
#: Deeper is not better once this is understood. A curve is only worth the generations it can carry,
#: and each one it cannot costs endpoints, rotation stability and nothing gained in dimension.
KOCH_RESOLVABLE = 3.0


def _koch(start, heading: float, reach: float, depth: int) -> np.ndarray:
    """One Koch curve, as a polyline: each segment replaced by four a third as long."""
    points = [np.array(start, dtype=float), np.array(_line(start, heading, reach)[-1], dtype=float)]
    for _ in range(depth):
        grown = [points[0]]
        for a, b in zip(points[:-1], points[1:], strict=True):
            step = (b - a) / 3.0
            turn = math.radians(60.0)
            rotated = np.array(
                [
                    step[0] * math.cos(turn) - step[1] * math.sin(turn),
                    step[0] * math.sin(turn) + step[1] * math.cos(turn),
                ]
            )
            grown.extend([a + step, a + step + rotated, a + 2 * step, b])
        points = grown
    return np.array(points)


def _needs_the_koch_inside_its_own_width(base: float, depth: int, widest: float) -> None:
    """Refuse a Koch curve whose finest generation is narrower than the vessel drawn along it.

    This is the fractal equivalent of the two refusals above, and it is the one that is easy to
    miss, because nothing about the picture looks truncated: the curve is entirely inside the
    frame, it simply is not the curve that was asked for. Where a generation is finer than the
    brush, the spikes merge into the stroke, and the image carries a shallower Koch curve than the
    ground truth derived beside it — which charges every implementation with an error none of them
    can avoid, and is exactly what this shape exists to prevent.

    It is a guard rather than a proof: clearing it does not make a drawing faithful, it only rules
    out the way this one went wrong. `KOCH_RESOLVABLE` says what the ratio was chosen from.
    """
    finest = base / 3.0**depth
    if finest < KOCH_RESOLVABLE * widest:
        raise ValueError(
            f"a Koch curve of {depth} generations over {base:.0f} px has a finest generation of "
            f"{finest:.1f} px, which a {widest:.1f} px vessel paints over: it needs to be at least "
            f"{KOCH_RESOLVABLE:.0f}× the width. Use fewer generations, a longer reach, or a "
            f"narrower vessel."
        )


def koch(
    side: int,
    rotation: float = 0.0,
    um_per_px: float = UM_PER_PX,
    artery_um: float = ARTERY_WIDTH_UM,
    vein_um: float = VEIN_WIDTH_UM,
    reach: float = 0.34,
    depth: float = 2,
) -> Shape:
    """A Koch curve per class, leaving the disc margin: the shape with a known fractal dimension.

    Every other shape here is a union of smooth curves, whose box-counting dimension is exactly 1 —
    a value no estimator returns from a bounded pixel image, so pinning it would charge every
    implementation with an error none of them can avoid. A Koch curve's dimension is `log 4 / log 3`
    ≈ 1.2619: not an integer, exactly known, and within reach of a box count over the range of
    scales a 2048-pixel frame offers.

    It is also self-similar rather than merely fractal, which is why the same number answers for
    the capacity, information and correlation dimensions: a monofractal's spectrum is a point.

    **Two generations, at half the usual vessel width.** The curve leaves the disc and must stay
    inside the field, so its span is fixed at about 700 px; each further generation divides the
    finest detail by three while the vessel width stays put. At four generations that detail was
    8.6 px under a 24 px vein — the brush wider than what it was painting — and the drawing carried
    an arc-to-chord ratio of 2.18 against a derived 3.16, with a box dimension of 1.51 against
    1.2619. Neither number was in the image, so neither was a fair question to ask, and all six
    implementations duly returned about 1.3 for a ratio of 3.16.

    Two things decide the parameters, and only one of them is what you would guess. The **box
    dimension** is set by the vessel width rather than the depth, because thickening adds area-like
    scaling below the width: at full width a box count returns about 1.41 at every depth tried, and
    only narrowing brings it down. The **arc-to-chord ratio** is what depth buys, but each
    generation the drawing cannot resolve costs a spurious endpoint per merged spike — four
    generations leave the skeleton with about 60 endpoints where the curve has 2, and three leave
    about 20 — and costs rotation stability with it.

    So: the fewest generations that still make the curve self-similar over a useful range of
    scales, at the width where the dimension lands. Two generations and half width gives 1.84
    against a derived 1.78, a box dimension of 1.28 against 1.2619, four to six endpoints, and
    about 1% movement when the picture is turned.
    """
    wa, wv = _widths(um_per_px, artery_um * KOCH_WIDTH_FRACTION, vein_um * KOCH_WIDTH_FRACTION)
    _needs_the_koch_inside_its_own_width(reach * side, int(depth), max(wa, wv))
    disc = _disc(side, um_per_px)
    generations = int(depth)
    parts = {}
    for structure, heading in (("artery", 180.0), ("vein", 110.0)):
        curve = _koch(_margin(disc, heading), heading, reach * side, generations)
        parts[structure] = [(curve, np.zeros(len(curve)))]
    fractal = {
        f"fractal-dimension/{variant}/{structure}": KOCH_DIMENSION
        for variant in ("box-counting", "multifractal-d0", "multifractal-d1", "multifractal-d2")
        for structure in ("artery", "vein", "vessels")
    }
    return _compose(
        "koch",
        side,
        rotation,
        um_per_px,
        DISC_AT,
        artery=parts["artery"],
        vein=parts["vein"],
        wa=wa,
        wv=wv,
        curved=False,
        counts={
            "junction-counts/junctions/vessels": 0.0,
            "junction-counts/endpoints/artery": 2.0,
            "junction-counts/endpoints/vein": 2.0,
            "junction-counts/endpoints/vessels": 4.0,
            "junction-counts/components/vessels": 2.0,
        },
        extra=fractal,
    )


def _spokes(
    name: str, at: tuple[float, float], side, rotation, um_per_px, artery_um, vein_um, vessels
):
    """Vessels radiating from the disc margin, crossing the ring the equivalents are measured over.

    Six per class of constant width, each running from the margin out past three disc radii, so
    every one crosses the annulus between two and three radii. All the arteries share a width and
    all the veins share theirs, so Knudtson's recursion gives the same number whatever order an
    implementation pairs them in — the shape tests the formula and the region rather than a sorting
    convention.
    """
    count = int(vessels)
    wa, wv = _widths(um_per_px, artery_um, vein_um)
    disc = _disc(side, um_per_px, at=at)
    _needs_the_ring_inside_the_field(side, disc)
    reach = disc[2] * (ZONE_B_RADII[1] + 0.2 - 1.0)
    parts: dict[str, list[tuple[np.ndarray, np.ndarray]]] = {"artery": [], "vein": []}
    for index in range(2 * count):
        heading = 360.0 * index / (2 * count)
        line = _outward(disc, heading, reach)
        parts["artery" if index % 2 == 0 else "vein"].append((line, np.zeros(2)))
    crae, crve = knudtson([wa] * count, "artery"), knudtson([wv] * count, "vein")
    crae_um = hubbard([wa * um_per_px] * count, "artery")
    crve_um = hubbard([wv * um_per_px] * count, "vein")
    return _compose(
        name,
        side,
        rotation,
        um_per_px,
        at,
        artery=parts["artery"],
        vein=parts["vein"],
        wa=wa,
        wv=wv,
        curved=False,
        counts={
            "junction-counts/junctions/vessels": 0.0,
            "junction-counts/endpoints/artery": 2.0 * count,
            "junction-counts/endpoints/vein": 2.0 * count,
            "junction-counts/endpoints/vessels": 4.0 * count,
            "junction-counts/components/artery": float(count),
            "junction-counts/components/vein": float(count),
            "junction-counts/components/vessels": float(2 * count),
        },
        extra={
            "central-retinal-equivalents/knudtson/artery": crae,
            "central-retinal-equivalents/knudtson/vein": crve,
            "central-retinal-equivalents/hubbard/artery": crae_um,
            "central-retinal-equivalents/hubbard/vein": crve_um,
            "avr/knudtson/both": crae / crve,
            "avr/hubbard/both": crae_um / crve_um,
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
    """The spokes as a macula-centred photograph frames them: the disc off to one side."""
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
    """The same retina photographed with the disc in the middle of the frame.

    Every disc-anchored measurement should return the same number on both, so a difference between
    them is a measurement reading the framing rather than the eye.
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
        picture[shape.artery & shape.vein] = OVERLAP_COLOUR
    return picture


#: Every shape, by the name its images and its rows are keyed on.
SHAPES: dict[str, Callable[..., Shape]] = {
    "straight": straight,
    "arc": arc,
    "sinusoid": sinusoid,
    "bifurcation": bifurcation,
    "deep-bifurcation": deep_bifurcation,
    "disjoint": disjoint,
    "koch": koch,
    "spokes-macula-centred": spokes_macula_centred,
    "spokes-disc-centred": spokes_disc_centred,
}
