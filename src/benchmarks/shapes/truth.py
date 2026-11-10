# ABOUTME: Every catalogued biomarker a synthetic scene's geometry settles, by canonical name, derived
# ABOUTME: from its centrelines, widths, nodes and disc in microns — never from a rendering.

import itertools
import math
from dataclasses import dataclass
from functools import cache

import numpy as np
import shapely
from scipy.spatial import cKDTree
from shapely.geometry import LineString, MultiLineString, Point

from biomarkers import canonical

from .scene import (
    DISC_RADIUS_UM,
    FOV_DIAMETER_UM,
    FOV_RADIUS_UM,
    SPACING_UM,
    ZONES,
    Network,
    Path,
    Scene,
    merged,
)

#: The regions every biomarker is derived over: the whole field, and zones B and C.
REGIONS = ("fov", "B", "C")
STATISTICS = ("mean", "median", "std", "length-weighted")
ANGLE_STATISTICS = ("mean", "median", "std")
#: Every tortuosity measure `measures` reads off a piece; the inflection count is a total.
TORTUOSITY_MEASURES = (
    "hart-tau1",
    "hart-tau2",
    "hart-tau3",
    "hart-tau4",
    "hart-tau5",
    "hart-tau6",
    "hart-tau7",
    "spline-curvature",
    "inflection-count",
    "arc-chord-times-inflections",
    "grisan-density",
)

#: A circle drawn as a polygon of 4 × QUAD_SEGS sides: 256 puts its area within 1e-5 of π r².
QUAD_SEGS = 256
#: A tube's round ends and joins, as polygons: area within 1e-4 of the round.
TUBE_QUAD_SEGS = 32
#: How far apart two pieces of one class may be and still count as touching (µm).
TOUCH_UM = 0.01
#: The grid the distance to the nearest vessel is averaged over, and the spacing of the centreline
#: points it is measured to (µm): a point between two of them is at most half that further away.
SPARSITY_STEP_UM = 20.0
SPARSITY_SPACING_UM = 5.0

#: What Knudtson's revision multiplies each pair by, and how many vessels it keeps.
KNUDTSON = {"artery": 0.88, "vein": 0.95}
CRE_VESSELS = 6
#: Hubbard's fitted coefficients, `(a, b, c, d)` in `√(a·w₁² + b·w₂² + c·w₁·w₂ + d)`. Fitted in
#: **microns**, and the additive term is what makes that matter: it does not scale, so feeding pixel
#: widths in gives a different number rather than a rescaled one.
HUBBARD = {"artery": (0.87, 1.01, -0.22, -10.76), "vein": (0.72, 0.91, 0.0, 450.05)}

#: A photograph is disc-centred when its disc lies within this fraction of the field's diameter of
#: the frame centre, and macula-centred otherwise.
CENTRED_WITHIN = 0.1

#: How a truth is known.
KINDS = ("exact", "numerical", "asymptotic", "convention")


@dataclass(frozen=True)
class Truth:
    """One expected value and how it is known.

    - ``exact`` — a closed form, or integrated from the geometry to far below any measurement's
      error;
    - ``numerical`` — averaged on a grid of `SPARSITY_STEP_UM`;
    - ``asymptotic`` — a limit no finite raster reaches, such as a fractal dimension;
    - ``convention`` — rests on a reading of the definition the geometry alone does not settle.

    **A value of None is a biomarker the definition gives no value for here** — no piece to pool, no
    junction to take an angle at. That is not 0, and it is not "not settled": the geometry says
    there is nothing, so an implementation should return nothing too.
    """

    value: float | str | None
    kind: str = "exact"


def name(stem: str, structure: str = "", region: str = "fov", statistic: str = "") -> str:
    """`family/biomarker/structure/[region]/[statistic]`, the field of view left implicit
    (`docs/BIOMARKER-NAMES.md` §1) and every statistic spelt out."""
    parts = [stem]
    if structure:
        parts.append(structure)
    if region != "fov":
        parts.append(region)
    if statistic:
        parts.append(statistic)
    return "/".join(parts)


def truth(scene: Scene) -> dict[str, Truth]:
    """Every catalogued biomarker `scene` settles, by canonical name.

    Per class, over the vessels as one class (`vessels`), and for the ratios of the two (`both`).
    Every value is the same at every rotation: the scene is turned about the centre of a circular
    field, which carries every distance with it.

    **The cup-to-disc ratios are not here.** They are read from a disc and a cup *mask*, and the
    benchmark hands an implementation the disc as a circle and no cup at all, so a truth for them
    would be a question no implementation is given the means to answer.

    :raises LookupError: if a name derived for an artery or a vein is not in the vocabulary — a
        typo must not reach the committed ground truth. A union name the vocabulary does not carry is
        simply left out: not every biomarker is defined over both classes at once.
    """
    classes = scene.classes()
    union = merged(classes["artery"], classes["vein"])
    # Where the two classes touch, the union is one tree where the two were two, and its topology
    # depends on how an implementation reads a crossing of two classes.
    touching = bool(_tubes(classes["artery"]).intersects(_tubes(classes["vein"])))
    found: dict[str, Truth] = {}
    for vessel, net in (*classes.items(), ("vessels", union)):
        for region in REGIONS:
            derived = {
                **_density(scene, vessel, net, region),
                **_calibre(scene, vessel, net, region),
                **_tortuosity(vessel, net, scene, region),
                **_topology(scene, vessel, net, region),
            }
            if vessel == "vessels":
                derived = {
                    key: Truth(t.value, "convention" if touching else t.kind)
                    for key, t in derived.items()
                    if _catalogued(key)
                }
            found.update(derived)
    for region in REGIONS:
        found.update(_ratios(scene, region))
    found.update(_landmarks(scene))
    for key in found:
        canonical.check(key)
    return {
        key: Truth(t.value, "convention") if key.startswith(tuple(scene.conventions)) else t
        for key, t in found.items()
    }


@cache
def _catalogued(key: str) -> bool:
    try:
        canonical.check(key)
    except LookupError:
        return False
    return True


# regions ---------------------------------------------------------------------------------------


def inside(points: np.ndarray, scene: Scene, region: str) -> np.ndarray:
    """Which (x, y) µm points lie in the region: the field of view, or an annulus of disc radii
    from the disc centre within it, closed at both edges."""
    points = np.atleast_2d(points)
    within = np.hypot(*points.T) <= FOV_RADIUS_UM
    if region == "fov":
        return within
    inner, outer = ZONES[region]
    away = np.hypot(points[:, 0] - scene.disc[0], points[:, 1] - scene.disc[1])
    return within & (away >= inner * DISC_RADIUS_UM) & (away <= outer * DISC_RADIUS_UM)


def region_polygon(scene: Scene, region: str):
    fov = Point(0.0, 0.0).buffer(FOV_RADIUS_UM, quad_segs=QUAD_SEGS)
    if region == "fov":
        return fov
    inner, outer = ZONES[region]
    centre = Point(*scene.disc)
    ring = centre.buffer(outer * DISC_RADIUS_UM, quad_segs=QUAD_SEGS).difference(
        centre.buffer(inner * DISC_RADIUS_UM, quad_segs=QUAD_SEGS)
    )
    return ring.intersection(fov)


def _tubes(net: Network):
    """The class as drawn: each segment's centreline swept by a disc of its width."""
    return shapely.union_all(
        [
            LineString(s.path.points).buffer(s.width / 2.0, quad_segs=TUBE_QUAD_SEGS)
            for s in net.segments
        ]
    )


def _lines(net: Network, segments=None):
    return MultiLineString([s.path.points for s in (segments or net.segments)])


def _pieces(geometry) -> list:
    """The connected pieces of a set of lines: lines within TOUCH_UM of each other are one."""
    if geometry.is_empty:
        return []
    grown = shapely.union_all([geometry.buffer(TOUCH_UM)])
    return list(getattr(grown, "geoms", [grown]))


def _clip(path: Path, scene: Scene, region: str) -> list[Path]:
    """A path cut to its runs inside the region, each with at least two samples."""
    keep = inside(path.points, scene, region)
    runs, start = [], None
    for index, flag in enumerate([*keep, False]):
        if flag and start is None:
            start = index
        elif not flag and start is not None:
            if index - start >= 2:
                runs.append(path[start:index])
            start = None
    return runs


def _undefined(stem: str, vessel: str, region: str, statistics=()) -> dict[str, Truth]:
    """A biomarker the geometry leaves undefined, under each statistic it would carry."""
    if not statistics:
        return {name(stem, vessel, region): Truth(None)}
    return {name(stem, vessel, region, s): Truth(None) for s in statistics}


def _pooled(values, lengths, statistics) -> dict[str, float]:
    values = np.asarray(values, dtype=float)
    # Values equal to rounding have no spread; np.std would report ~1e-16 of float noise, which
    # the analysis would then take as the biomarker's own size.
    equal = np.ptp(values) <= 1e-12 * max(1.0, float(np.abs(values).max()))
    out = {
        "mean": float(values.mean()),
        "median": float(np.median(values)),
        "std": 0.0 if equal else float(values.std()),
    }
    if lengths is not None:
        out["length-weighted"] = float(values @ lengths / lengths.sum())
    return {s: out[s] for s in statistics}


# whole vessels ---------------------------------------------------------------------------------


def _reversed(path: Path) -> Path:
    """The same path walked the other way: its curvature and turns change sign."""
    return Path(path.points[::-1], -path.curvature[::-1], -path.turns[::-1])


def _joined(first: Path, second: Path) -> Path:
    """Two paths meeting at a point, with the change of heading there as a corner."""
    turn = (second.start_heading - first.end_heading + math.pi) % (2 * math.pi) - math.pi
    corner = first.turns[-1] + turn + second.turns[0]
    return Path(
        np.vstack([first.points, second.points[1:]]),
        np.concatenate([first.curvature, second.curvature[1:]]),
        np.concatenate([first.turns[:-1], [corner], second.turns[1:]]),
    )


def vessels(net: Network) -> list[Path]:
    """Every root-to-tip path through the network — a whole vessel — one per tip a root reaches.

    A `vessel-` biomarker is measured over these rather than over segments between junctions, so a
    whole vessel through a fork turns at the fork, by the angle between trunk and daughter.
    """
    found = []

    def grow(node, path, used):
        onward = [s for s in net.segments if id(s) not in used and node in (s.start, s.end)]
        if not onward:
            found.append(path)
            return
        for s in onward:
            piece = s.path if s.start == node else _reversed(s.path)
            other = s.end if s.start == node else s.start
            grow(other, piece if path is None else _joined(path, piece), used | {id(s)})

    for node_id, node in net.nodes.items():
        if node.root:
            grow(node_id, None, set())
    return [p for p in found if p is not None]


# tortuosity ------------------------------------------------------------------------------------


def measures(path: Path) -> dict[str, float | None]:
    """Every tortuosity measure of one piece, by its definition in `docs/biomarkers/tortuosity.md`.

    None where the definition does not reach: the squared curvature at a corner is infinite, and
    Grisan's turn curves and a fitted spline are undefined across one.
    """
    steps = np.hypot(*np.diff(path.points, axis=0).T)
    arc = float(steps.sum())
    chord = float(np.hypot(*(path.points[-1] - path.points[0])))
    middle = (path.curvature[:-1] + path.curvature[1:]) / 2.0
    total = float(np.abs(middle) @ steps + np.abs(path.turns).sum())
    squared = None if path.cornered else float((middle**2) @ steps)
    turning = _turning(path, middle * steps)
    inflections = float(np.count_nonzero(np.diff(np.sign(turning))))
    tau1 = arc / chord
    return {
        "hart-tau1": tau1,
        "hart-tau2": total,
        "hart-tau3": squared,
        "hart-tau4": total / arc,
        "hart-tau5": None if squared is None else squared / arc,
        "hart-tau6": total / chord,
        "hart-tau7": None if squared is None else squared / chord,
        "spline-curvature": None if path.cornered else total / arc,
        "inflection-count": inflections,
        "arc-chord-times-inflections": tau1 * inflections,
        "grisan-density": None if path.cornered else _grisan(path, middle * steps, arc),
    }


def _turning(path: Path, per_step: np.ndarray) -> np.ndarray:
    """The signed turn of each step and corner in walking order, zeros left out."""
    sequence = np.zeros(2 * len(per_step) + 1)
    sequence[0::2] = path.turns
    sequence[1::2] = per_step
    return sequence[np.abs(sequence) > 1e-12]


def _grisan(path: Path, per_step: np.ndarray, arc: float) -> float:
    """Grisan's density, ``((n − 1) / n) · Σ (Lᵢ / cᵢ − 1) / L`` over the n turn curves, cut where
    the curvature changes sign; 0 for a curve that turns one way only (n = 1)."""
    signs = np.sign(per_step)
    cuts = [0]
    last = 0.0
    for index, sign in enumerate(signs):
        if sign and last and sign != last:
            cuts.append(index)
        last = sign or last
    cuts.append(len(path.points) - 1)
    n = len(cuts) - 1
    if n < 2:
        return 0.0
    excess = 0.0
    for a, b in itertools.pairwise(cuts):
        piece = path.points[a : b + 1]
        length = float(np.hypot(*np.diff(piece, axis=0).T).sum())
        excess += length / float(np.hypot(*(piece[-1] - piece[0]))) - 1.0
    return (n - 1) / n * excess / arc


def _tortuosity(vessel: str, net: Network, scene: Scene, region: str) -> dict[str, Truth]:
    found = {}
    forms = {"": [s.path for s in net.segments], "vessel-": vessels(net)}
    for prefix, paths in forms.items():
        pieces = [run for path in paths for run in _clip(path, scene, region)]
        pieces = [p for p in pieces if np.hypot(*(p.points[-1] - p.points[0])) > 0]
        # Nothing to pool: every measure is undefined, the inflection count too.
        if not pieces:
            for measure in TORTUOSITY_MEASURES:
                count = measure == "inflection-count"
                stem = f"tortuosity/{prefix}{measure}"
                found.update(_undefined(stem, vessel, region, () if count else STATISTICS))
            continue
        values = [measures(p) for p in pieces]
        lengths = np.array([p.length for p in pieces])
        for measure in values[0]:
            column = [v[measure] for v in values]
            # Infinite somewhere — a corner's squared curvature — is not undefined: left out.
            if any(v is None for v in column):
                continue
            stem = f"tortuosity/{prefix}{measure}"
            if measure == "inflection-count":
                found[name(stem, vessel, region)] = Truth(float(sum(column)))
                continue
            for statistic, value in _pooled(column, lengths, STATISTICS).items():
                found[name(stem, vessel, region, statistic)] = Truth(value)
    return found


# calibre ---------------------------------------------------------------------------------------


def _width_pieces(scene: Scene, net: Network, region: str):
    return [(s.width, run.length) for s in net.segments for run in _clip(s.path, scene, region)]


def _calibre(scene: Scene, vessel: str, net: Network, region: str) -> dict[str, Truth]:
    pieces = _width_pieces(scene, net, region)
    if pieces:
        widths, lengths = np.array(pieces).T
        found = {
            name("calibre/width", vessel, region, statistic): Truth(value)
            for statistic, value in _pooled(widths, lengths, STATISTICS).items()
        }
    else:
        found = _undefined("calibre/width", vessel, region, STATISTICS)
    # The equivalents are defined per class, in a zone.
    if region == "fov" or vessel not in KNUDTSON:
        return found
    crossing = crossing_widths(scene, net, region)
    if not crossing:
        for formula in ("knudtson", "hubbard"):
            found.update(_undefined(f"calibre/CRE-{formula}", vessel, region))
        return found
    # Both formulas combine pairs: a single vessel passed through is a reading of them.
    kind = "exact" if len(crossing) >= 2 else "convention"
    found[name("calibre/CRE-knudtson", vessel, region)] = Truth(knudtson(crossing, vessel), kind)
    found[name("calibre/CRE-hubbard", vessel, region)] = Truth(hubbard(crossing, vessel), kind)
    return found


def crossing_widths(scene: Scene, net: Network, region: str) -> list[float]:
    """The vessels crossing a zone: each connected piece of the class inside it, at the width of
    its widest segment there."""
    zone = region_polygon(scene, region)
    pieces = _pieces(_lines(net).intersection(zone))
    widths = []
    for piece in pieces:
        touching = [s.width for s in net.segments if LineString(s.path.points).intersects(piece)]
        widths.append(max(touching))
    return sorted(widths, reverse=True)


def _combine(widths, pair) -> float:
    """Knudtson's recursion: the six widest, widest paired with narrowest, the middle one of an odd
    count passed through, repeated until one is left.

    Hubbard's own paper is less explicit about the order; the same iteration is applied to his
    combination, which is what the implementations in this catalogue do.
    """
    remaining = sorted(widths, reverse=True)[:CRE_VESSELS]
    while len(remaining) > 1:
        remaining.sort(reverse=True)
        combined = [pair(remaining[i], remaining[-1 - i]) for i in range(len(remaining) // 2)]
        if len(remaining) % 2:
            combined.append(remaining[len(remaining) // 2])
        remaining = combined
    return remaining[0]


def knudtson(widths: list[float], vessel: str) -> float:
    """Knudtson et al. 2003: pairs combined as ``k·√(w₁² + w₂²)``, k 0.88 for arterioles and 0.95
    for venules. Purely multiplicative, so scale-free."""
    k = KNUDTSON[vessel]
    return _combine(widths, lambda a, b: k * math.hypot(a, b))


def hubbard(widths: list[float], vessel: str) -> float:
    """Hubbard et al. 1999, **in microns**, of widths in microns. Its additive constants do not
    scale with the image, so a value computed on pixel widths is a different quantity rather than
    one awaiting conversion."""
    a, b, c, d = HUBBARD[vessel]
    return _combine(widths, lambda w1, w2: math.sqrt(a * w1 * w1 + b * w2 * w2 + c * w1 * w2 + d))


def _ratios(scene: Scene, region: str) -> dict[str, Truth]:
    """Artery over vein: the mean segment widths, and in a zone the two equivalents; None where
    either class has nothing to measure."""
    means = {}
    for vessel, net in scene.classes().items():
        pieces = _width_pieces(scene, net, region)
        if pieces:
            means[vessel] = float(np.mean([w for w, _ in pieces]))
    found = {name("calibre/AVR-ratio", "both", region): Truth(None)}
    if len(means) == 2:
        found[name("calibre/AVR-ratio", "both", region)] = Truth(means["artery"] / means["vein"])
    if region == "fov":
        return found
    crossing = {v: crossing_widths(scene, n, region) for v, n in scene.classes().items()}
    if not (crossing["artery"] and crossing["vein"]):
        for formula in ("knudtson", "hubbard"):
            found.update(_undefined(f"calibre/AVR-{formula}", "both", region))
        return found
    kind = "exact" if min(map(len, crossing.values())) >= 2 else "convention"
    found[name("calibre/AVR-knudtson", "both", region)] = Truth(
        knudtson(crossing["artery"], "artery") / knudtson(crossing["vein"], "vein"), kind
    )
    found[name("calibre/AVR-hubbard", "both", region)] = Truth(
        hubbard(crossing["artery"], "artery") / hubbard(crossing["vein"], "vein"), kind
    )
    return found


# density ---------------------------------------------------------------------------------------


def _density(scene: Scene, vessel: str, net: Network, region: str) -> dict[str, Truth]:
    zone = region_polygon(scene, region)
    drawn = _tubes(net)
    area = drawn.intersection(zone).area
    lines = _lines(net)
    rooted = [
        piece
        for piece in _pieces(lines)
        if any(n.root and piece.intersects(Point(n.x, n.y)) for n in net.nodes.values())
    ]
    rooted_length = sum(lines.intersection(piece).intersection(zone).length for piece in rooted)
    found = {
        name("density/area", vessel, region): Truth(area),
        name("density/skeleton-length", vessel, region): Truth(lines.intersection(zone).length),
        name("density/skeleton-length-rooted", vessel, region): Truth(rooted_length),
        name("density/over-fov", vessel, region): Truth(area / zone.area),
    }
    mean, furthest = sparsity(scene, net, region)
    found[name("density/sparsity", vessel, region, "mean")] = Truth(mean, "numerical")
    found[name("density/sparsity", vessel, region, "max")] = Truth(furthest, "numerical")
    if region == "fov":
        # The whole frame, lit or not, which is what dividing by `height × width` measures.
        found[name("density/over-image", vessel)] = Truth(drawn.area / FOV_DIAMETER_UM**2)
    # A curve cut to a zone keeps its dimension, and a monofractal's spectrum is one number. No
    # vessel in the region: no mass to count, so no dimension.
    for stem in ("box-counting", "multifractal-d0", "multifractal-d1", "multifractal-d2"):
        if area > 0:
            found[name(f"density/{stem}", vessel, region)] = Truth(scene.dimension, "asymptotic")
        else:
            found.update(_undefined(f"density/{stem}", vessel, region))
    return found


def sparsity(scene: Scene, net: Network, region: str) -> tuple[float, float]:
    """The distance from each point of the region to the nearest vessel edge (0 on a vessel), on a
    grid of SPARSITY_STEP_UM: its mean and its largest value. A tube's edge is half its width from
    its centreline, so the distance to it is the distance to the centreline less that."""
    axis = np.arange(-FOV_RADIUS_UM + SPARSITY_STEP_UM / 2, FOV_RADIUS_UM, SPARSITY_STEP_UM)
    x, y = np.meshgrid(axis, axis)
    grid = np.column_stack([x.ravel(), y.ravel()])
    grid = grid[inside(grid, scene, region)]
    nearest = np.full(len(grid), np.inf)
    every = max(int(SPARSITY_SPACING_UM / SPACING_UM), 1)
    for s in net.segments:
        points = np.vstack([s.path.points[::every], s.path.points[-1:]])
        distance, _ = cKDTree(points).query(grid, workers=-1)
        nearest = np.minimum(nearest, distance - s.width / 2.0)
    nearest = np.maximum(nearest, 0.0)
    return float(nearest.mean()), float(nearest.max())


# topology --------------------------------------------------------------------------------------


def _topology(scene: Scene, vessel: str, net: Network, region: str) -> dict[str, Truth]:
    def within(node_id):
        node = net.nodes[node_id]
        return bool(inside(np.array([[node.x, node.y]]), scene, region)[0])

    junctions = [n for n in net.nodes if net.degree(n) >= 3 and within(n)]
    endpoints = [n for n in net.nodes if net.degree(n) == 1 and within(n)]
    zone = region_polygon(scene, region)
    found = {
        name("topology/junctions", vessel, region): Truth(float(len(junctions))),
        name("topology/endpoints", vessel, region): Truth(float(len(endpoints))),
        name("topology/components", vessel, region): Truth(
            float(len(_pieces(_lines(net).intersection(zone))))
        ),
    }
    angles = [angle for node, angle in net.angles.items() if within(node)]
    if not angles:
        found.update(_undefined("topology/branching-angle", vessel, region, ANGLE_STATISTICS))
        return found
    for statistic, value in _pooled(angles, None, ANGLE_STATISTICS).items():
        found[name("topology/branching-angle", vessel, region, statistic)] = Truth(value)
    return found


# landmarks -------------------------------------------------------------------------------------


def _landmarks(scene: Scene) -> dict[str, Truth]:
    """The photograph's centring, from where its disc sits in the frame."""
    offset = math.hypot(*scene.disc)
    centred = offset < CENTRED_WITHIN * FOV_DIAMETER_UM
    return {"landmarks/centring": Truth("disc" if centred else "macula")}
