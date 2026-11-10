# ABOUTME: The shapes a biomarker implementation is measured against, each a retina stated in microns,
# ABOUTME: and what one rendering of it is: masks, field, disc, and every value its geometry settles.

import math
from collections.abc import Callable
from dataclasses import dataclass, field
from functools import cache

import numpy as np

from . import render as rendering
from . import truth as derive
from .scene import (
    ARTERY_UM,
    DISC_CENTRED_DISC,
    DISC_RADIUS_UM,
    MACULA_CENTRED_DISC,
    VEIN_UM,
    ZONES,
    Network,
    Node,
    Scene,
    Segment,
    check_inside,
    line,
    margin,
    network,
    walk,
)
from .scene import (
    sinusoid as wave,
)

#: The grid a shape is drawn at unless asked otherwise. The frame always spans the same field of
#: view, so the side decides the scale: 2048 pixels is 6.33 µm per pixel.
SIDE = 2048

#: Most shapes are photographed macula-centred, the disc right of the frame centre.
DISC = MACULA_CENTRED_DISC

STRAIGHT_UM = 4000.0

ARC_ARTERY_RADIUS_UM = 4000.0
ARC_VEIN_RADIUS_UM = 3000.0
ARC_DEGREES = 70.0

#: An Euler spiral: curvature rising linearly from 0 to this over its length.
CLOTHOID_UM = 4000.0
CLOTHOID_END_CURVATURE = 1.0 / 1500.0

SINE_AMPLITUDE_UM = 250.0
SINE_WAVELENGTH_UM = 2000.0
SINE_CYCLES = 2.0

FORK_DEGREES = 60.0
FORK_ARM_UM = 2000.0
#: A daughter's width over its parent's under Murray's law for a symmetric fork: the cube of the
#: parent's width is the sum of the daughters' cubes.
MURRAY = 2.0 ** (-1.0 / 3.0)

TREE_DEGREES = 70.0
TREE_TRUNK_UM = 1500.0
TREE_ARM_UM = 1300.0

#: A side branch shorter than the shortest leaf several implementations keep (`RetinaConfig`'s
#: 1,000 µm among them): counted by the definition, dropped by a length filter.
SPUR_TRUNK_UM = 4500.0
SPUR_UM = 500.0
SPUR_WIDTH_UM = 60.0

CROSSING_UM = 4500.0
CROSSING_BAR_UM = 3000.0

DISJOINT_COUNT = 3
DISJOINT_UM = 2500.0
DISJOINT_SPACING_UM = 600.0

#: The deep tree: three generations of forks, each with a stub off its junction.
DEEP_DEGREES = 50.0
DEEP_ARM_UM = 720.0
DEEP_GENERATIONS = 3
DEEP_SPUR_FRACTION = 0.35

#: The Koch curve's similarity dimension: four copies at a third of the length, so `log 4 / log 3`.
#: Exact, not an integer, and within reach of a box count over a 2048-pixel frame — which an
#: ordinary vessel's dimension of 1 is not, from a bounded raster.
KOCH_DIMENSION = math.log(4.0) / math.log(3.0)
KOCH_DEPTH = 2
KOCH_REACH_UM = 4500.0
#: **The box dimension of a drawn curve is governed by how thick it is, not by how many generations
#: it has.** Thickening adds area-like scaling below the width and pulls a box count towards 2: at
#: full width it returned about 1.41 at every depth this repository tried, and half width is where
#: it lands near 1.26. Two generations, because each one the drawing cannot resolve costs a spurious
#: endpoint per merged spike and rotation stability with it.
KOCH_WIDTH_FRACTION = 0.5

#: Spokes cross both zones on a disc-centred frame (to 5.4 disc radii); on a macula-centred frame
#: the field leaves room for zone B and part of C (to 3.4).
SPOKES_PER_CLASS = 6
SPOKES_DISC_CENTRED_RADII = 5.4
SPOKES_MACULA_CENTRED_RADII = 3.4

#: What `demo_image` paints each thing. Arteries read red and veins blue, as every atlas of the
#: retina draws them; the zone edges are drawn faintly so a reader can see what crosses them.
FIELD_COLOUR = (18, 18, 22)
ARTERY_COLOUR = (214, 52, 52)
VEIN_COLOUR = (54, 92, 214)
DISC_COLOUR = (240, 198, 62)
RING_COLOUR = (72, 96, 84)
OVERLAP_COLOUR = (255, 0, 255)


@dataclass(frozen=True)
class Shape:
    """One rendering of one shape: what an adapter is handed, and what the answer must be.

    :param truths: every catalogued biomarker the geometry settles, by canonical name, with how it is
        known — and those it settles as having **no** value, as a `Truth` of None.
    :param um_per_px: the frame spans a fixed field of view, so this follows from the side.
    """

    name: str
    side: int
    rotation: float
    um_per_px: float
    artery: np.ndarray
    vein: np.ndarray
    fov: np.ndarray
    disc: tuple[float, float, float]
    truths: dict[str, derive.Truth]
    parameters: dict[str, float] = field(default_factory=dict)

    @property
    def theory(self) -> dict[str, float | str]:
        """The values the geometry requires, where it requires one."""
        return {key: t.value for key, t in self.truths.items() if t.value is not None}

    @property
    def undefined(self) -> list[str]:
        """The biomarkers the geometry leaves without a value: an implementation should decline."""
        return sorted(key for key, t in self.truths.items() if t.value is None)


def build(name: str, side: int = SIDE, rotation: float = 0.0) -> Shape:
    """One shape, drawn on a `side` × `side` frame turned by `rotation` degrees."""
    drawn = rendering.render(scene(name), rotation=rotation, side=side)
    return Shape(
        name=name,
        side=side,
        rotation=rotation,
        um_per_px=drawn.um_per_px,
        artery=drawn.artery,
        vein=drawn.vein,
        fov=drawn.fov,
        disc=drawn.disc,
        truths=truths(name),
        parameters=dict(scene(name).parameters),
    )


@cache
def scene(name: str) -> Scene:
    """One shape as the geometry it is, before anything is drawn."""
    if name not in SHAPES:
        raise LookupError(f"no shape named {name!r}; there are {', '.join(SHAPES)}")
    return SHAPES[name]()


@cache
def truths(name: str) -> dict[str, derive.Truth]:
    """What one shape's geometry settles. The same at every rotation and every grid, so derived
    once per shape — it is a few seconds of clipping and a grid of distances."""
    return derive.truth(scene(name))


# the shapes ------------------------------------------------------------------------------------


def straight() -> Scene:
    """One straight vessel per class, leaving the disc at right angles to each other.

    The artery runs horizontally and the vein vertically, so a measurement that walks the pixel
    lattice rather than the vessel disagrees with itself between the two once the scene is turned.
    """
    return check_inside(
        Scene(
            "straight",
            DISC,
            artery=network([line(margin(DISC, 180), 180, STRAIGHT_UM)], ARTERY_UM),
            vein=network([line(margin(DISC, 90), 90, STRAIGHT_UM)], VEIN_UM),
            parameters={"length_um": STRAIGHT_UM},
        )
    )


def arc() -> Scene:
    """A circular arc per class, one angle, two radii: τ1 = θ / (2 sin θ/2) equal for both because
    the radius cancels, and the curvature integrals not."""
    theta = math.radians(ARC_DEGREES)

    def bend(heading, radius, sign):
        return walk(margin(DISC, heading), heading, [("arc", radius * theta, sign / radius)])

    return check_inside(
        Scene(
            "arc",
            DISC,
            artery=network([bend(180, ARC_ARTERY_RADIUS_UM, 1)], ARTERY_UM),
            vein=network([bend(250, ARC_VEIN_RADIUS_UM, -1)], VEIN_UM),
            parameters={
                "artery_radius_um": ARC_ARTERY_RADIUS_UM,
                "vein_radius_um": ARC_VEIN_RADIUS_UM,
                "degrees": ARC_DEGREES,
            },
        )
    )


def clothoid() -> Scene:
    """An Euler spiral per class: curvature linear in arc length, so τ2 = κL/2 and τ3 = κ²L/3.

    The one shape whose curvature varies without changing sign, which separates a measure that
    averages curvature from one that only reads its peak or its ends.
    """
    k = CLOTHOID_END_CURVATURE

    def spiral(heading, sign):
        return walk(margin(DISC, heading), heading, [("clothoid", CLOTHOID_UM, 0.0, sign * k)])

    return check_inside(
        Scene(
            "clothoid",
            DISC,
            artery=network([spiral(180, 1)], ARTERY_UM),
            vein=network([spiral(250, -1)], VEIN_UM),
            parameters={"length_um": CLOTHOID_UM, "end_curvature_per_um": k},
        )
    )


def sinusoid() -> Scene:
    """A sine wave per class: the curvature changes sign, so it settles the inflection count and
    Grisan's density, which are zero on every curve that bends one way."""

    def sine(heading):
        start = margin(DISC, heading)
        return wave(start, heading, SINE_AMPLITUDE_UM, SINE_WAVELENGTH_UM, SINE_CYCLES)

    return check_inside(
        Scene(
            "sinusoid",
            DISC,
            artery=network([sine(180)], ARTERY_UM),
            vein=network([sine(100)], VEIN_UM),
            parameters={
                "amplitude_um": SINE_AMPLITUDE_UM,
                "wavelength_um": SINE_WAVELENGTH_UM,
                "cycles": SINE_CYCLES,
            },
        )
    )


def _fork(heading, width):
    """A trunk from the disc margin forking symmetrically into two Murray daughters."""
    trunk = line(margin(DISC, heading), heading, FORK_ARM_UM)
    nodes = {"root": Node(*trunk.points[0], root=True), "fork": Node(*trunk.points[-1])}
    segments = [Segment("root", "fork", width, trunk)]
    for index, sign in enumerate((-1, 1)):
        daughter = line(trunk.points[-1], heading + sign * FORK_DEGREES / 2, FORK_ARM_UM)
        nodes[f"tip{index}"] = Node(*daughter.points[-1])
        segments.append(Segment("fork", f"tip{index}", width * MURRAY, daughter))
    return Network(nodes, segments, {"fork": FORK_DEGREES})


def bifurcation() -> Scene:
    """A trunk splitting once per class, its daughters narrowed by Murray's law: one junction,
    three ends, the angle between the daughters exactly as drawn, and two widths to pool."""
    return check_inside(
        Scene(
            "bifurcation",
            DISC,
            artery=_fork(160, ARTERY_UM),
            vein=_fork(220, VEIN_UM),
            parameters={"degrees": FORK_DEGREES, "arm_um": FORK_ARM_UM},
        )
    )


def _tree(heading, width):
    """A trunk and two generations of symmetric forks: three junctions, four tips."""
    trunk = line(margin(DISC, heading), heading, TREE_TRUNK_UM)
    nodes = {"root": Node(*trunk.points[0], root=True), "j": Node(*trunk.points[-1])}
    segments = [Segment("root", "j", width, trunk)]
    angles = {}
    growing = [("j", heading, width)]
    for generation in range(2):
        grown = []
        for node, came, parent_width in growing:
            angles[node] = TREE_DEGREES
            for sign, which in ((-1, "a"), (1, "b")):
                child = f"{node}{which}"
                piece = line(
                    (nodes[node].x, nodes[node].y), came + sign * TREE_DEGREES / 2, TREE_ARM_UM
                )
                nodes[child] = Node(*piece.points[-1])
                segments.append(Segment(node, child, parent_width * MURRAY, piece))
                grown.append((child, came + sign * TREE_DEGREES / 2, parent_width * MURRAY))
        growing = grown if generation == 0 else []
    return Network(nodes, segments, angles)


def tree() -> Scene:
    """Two generations of forks per class: junctions and tips to count, Murray widths by
    generation, and whole vessels sharing their trunk."""
    return check_inside(
        Scene(
            "tree",
            DISC,
            artery=_tree(180, ARTERY_UM),
            vein=_tree(270, VEIN_UM),
            parameters={"degrees": TREE_DEGREES, "trunk_um": TREE_TRUNK_UM, "arm_um": TREE_ARM_UM},
        )
    )


def deep_bifurcation() -> Scene:
    """A trunk forking three generations deep, with a stub off every junction, at one width.

    What a single fork cannot show: a junction counted as a cluster of pixels, a walk that loses a
    branch, a stub too short to survive a length filter. **A stub makes a junction of four**, so
    which two of its branches are *the* daughters is a reading of the definition, and the branching
    angle is recorded as a convention here.
    """

    def grow(heading, width):
        trunk = line(margin(DISC, heading), heading, DEEP_ARM_UM)
        nodes = {"root": Node(*trunk.points[0], root=True), "n": Node(*trunk.points[-1])}
        segments = [Segment("root", "n", width, trunk)]
        angles = {}
        growing = [("n", heading)]
        for generation in range(DEEP_GENERATIONS):
            grown = []
            for node, came in growing:
                angles[node] = DEEP_DEGREES
                at = (nodes[node].x, nodes[node].y)
                for sign, which in ((-1, "a"), (1, "b")):
                    piece = line(at, came + sign * DEEP_DEGREES / 2, DEEP_ARM_UM)
                    nodes[node + which] = Node(*piece.points[-1])
                    segments.append(Segment(node, node + which, width, piece))
                    grown.append((node + which, came + sign * DEEP_DEGREES / 2))
                stub = line(at, came + 90.0, DEEP_ARM_UM * DEEP_SPUR_FRACTION)
                nodes[node + "s"] = Node(*stub.points[-1])
                segments.append(Segment(node, node + "s", width, stub))
            growing = grown if generation < DEEP_GENERATIONS - 1 else []
        return Network(nodes, segments, angles)

    return check_inside(
        Scene(
            "deep-bifurcation",
            DISC,
            artery=grow(190, ARTERY_UM),
            vein=grow(130, VEIN_UM),
            conventions=("topology/branching-angle",),
            parameters={
                "degrees": DEEP_DEGREES,
                "arm_um": DEEP_ARM_UM,
                "generations": DEEP_GENERATIONS,
                "spur_fraction": DEEP_SPUR_FRACTION,
            },
        )
    )


def spur() -> Scene:
    """A straight artery with a 500 µm side branch at right angles halfway along: a leaf shorter
    than a typical minimal leaf length, which the definition counts and a length filter drops."""
    trunk = line(margin(DISC, 180), 180, SPUR_TRUNK_UM)
    half = len(trunk.points) // 2
    first, second = trunk[: half + 1], trunk[half:]
    side = line(tuple(first.points[-1]), 90, SPUR_UM)
    artery = Network(
        {
            "root": Node(*first.points[0], root=True),
            "j": Node(*first.points[-1]),
            "tip": Node(*second.points[-1]),
            "spur": Node(*side.points[-1]),
        },
        [
            Segment("root", "j", ARTERY_UM, first),
            Segment("j", "tip", ARTERY_UM, second),
            Segment("j", "spur", SPUR_WIDTH_UM, side),
        ],
        {"j": 90.0},
    )
    vein = network([line(margin(DISC, 90), 90, STRAIGHT_UM)], VEIN_UM)
    return check_inside(
        Scene(
            "spur",
            DISC,
            artery=artery,
            vein=vein,
            parameters={
                "trunk_um": SPUR_TRUNK_UM,
                "spur_um": SPUR_UM,
                "spur_width_um": SPUR_WIDTH_UM,
            },
        )
    )


def crossing() -> Scene:
    """An artery from the disc crossed at right angles by an artery that never reaches it: two
    vessels over one another, not a junction. The counts that rest on that reading are conventions."""
    rooted = line(margin(DISC, 180), 180, CROSSING_UM)
    x = rooted.points[len(rooted.points) // 2][0]
    bar = line((x, -CROSSING_BAR_UM / 2), 90, CROSSING_BAR_UM)
    artery = Network(
        {
            "root": Node(*rooted.points[0], root=True),
            "tip": Node(*rooted.points[-1]),
            "bar0": Node(*bar.points[0]),
            "bar1": Node(*bar.points[-1]),
        },
        [Segment("root", "tip", ARTERY_UM, rooted), Segment("bar0", "bar1", ARTERY_UM, bar)],
    )
    vein = network([line(margin(DISC, 90), 90, STRAIGHT_UM)], VEIN_UM)
    conventions = (
        "topology/",
        "tortuosity/vessel-",
        "density/skeleton-length-rooted",
        "calibre/CRE-",
        "calibre/AVR-knudtson",
        "calibre/AVR-hubbard",
    )
    return check_inside(
        Scene(
            "crossing",
            DISC,
            artery=artery,
            vein=vein,
            conventions=conventions,
            parameters={"length_um": CROSSING_UM, "bar_um": CROSSING_BAR_UM},
        )
    )


def disjoint() -> Scene:
    """Parallel vessels that never reach the disc, alternating class: orphans only.

    It shows whether a measurement quietly requires a vessel to reach the disc before counting it —
    a restriction some implementations impose and none announce.
    """
    paths = {"artery": [], "vein": []}
    first = -DISJOINT_SPACING_UM * (2 * DISJOINT_COUNT - 1) / 2
    for index in range(2 * DISJOINT_COUNT):
        y = first + index * DISJOINT_SPACING_UM
        paths["artery" if index % 2 == 0 else "vein"].append(line((-4500.0, y), 0, DISJOINT_UM))
    return check_inside(
        Scene(
            "disjoint",
            DISC,
            artery=network(paths["artery"], ARTERY_UM, rooted=False),
            vein=network(paths["vein"], VEIN_UM, rooted=False),
            parameters={
                "per_class": DISJOINT_COUNT,
                "length_um": DISJOINT_UM,
                "spacing_um": DISJOINT_SPACING_UM,
            },
        )
    )


def koch_moves(reach: float, depth: int) -> list:
    """A Koch curve as moves: every piece replaced by four a third as long, turning 60°, −120°,
    60° between them."""
    turns = [0.0]
    for _ in range(depth):
        turns = [t for turn in turns for t in (turn, 60.0, -120.0, 60.0)]
    piece = reach / 3**depth
    moves = []
    for turn in turns:
        if turn:
            moves.append(("turn", turn))
        moves.append(("straight", piece))
    return moves


def koch() -> Scene:
    """A Koch curve per class, at half the usual width: box-counting dimension log 4 / log 3, and an
    arc over chord of (4/3) per generation."""
    moves = koch_moves(KOCH_REACH_UM, KOCH_DEPTH)
    return check_inside(
        Scene(
            "koch",
            DISC,
            artery=network([walk(margin(DISC, 180), 180, moves)], ARTERY_UM * KOCH_WIDTH_FRACTION),
            vein=network([walk(margin(DISC, 100), 100, moves)], VEIN_UM * KOCH_WIDTH_FRACTION),
            dimension=KOCH_DIMENSION,
            parameters={"reach_um": KOCH_REACH_UM, "depth": KOCH_DEPTH},
        )
    )


def _spokes(label: str, disc, radii: float) -> Scene:
    """Straight vessels radiating from the disc margin, alternating class every 30°.

    Every vessel of a class shares a width, so Knudtson's recursion gives the same number whatever
    order an implementation pairs them in — the shape tests the formula and the zone rather than a
    sorting convention.
    """
    reach = (radii - 1.0) * DISC_RADIUS_UM
    paths = {"artery": [], "vein": []}
    for index in range(2 * SPOKES_PER_CLASS):
        heading = 360.0 * index / (2 * SPOKES_PER_CLASS)
        paths["artery" if index % 2 == 0 else "vein"].append(
            line(margin(disc, heading), heading, reach)
        )
    return check_inside(
        Scene(
            label,
            disc,
            artery=network(paths["artery"], ARTERY_UM),
            vein=network(paths["vein"], VEIN_UM),
            parameters={"per_class": SPOKES_PER_CLASS, "reach_disc_radii": radii},
        )
    )


def spokes_disc_centred() -> Scene:
    """The spokes with the disc in the middle of the frame, crossing zones B and C entirely."""
    return _spokes("spokes-disc-centred", DISC_CENTRED_DISC, SPOKES_DISC_CENTRED_RADII)


def spokes_macula_centred() -> Scene:
    """The same eye framed macula-centred. Every value of zone B is the same as on the disc-centred
    framing; a measurement that differs between the two is reading the framing, not the eye."""
    return _spokes("spokes-macula-centred", MACULA_CENTRED_DISC, SPOKES_MACULA_CENTRED_RADII)


def demo_image(shape, rings: bool = True) -> np.ndarray:
    """One picture of a rendering for a person to look at, as `H×W×3` 8-bit colour.

    Nothing measures this. A rendering read back from a store carries the same four things — masks,
    field and disc — so one can be passed here in place of a shape that was just built.
    """
    side = shape.side
    picture = np.zeros((side, side, 3), dtype=np.uint8)
    picture[shape.fov] = FIELD_COLOUR
    if rings:
        x, y, radius = shape.disc
        grid = np.arange(side, dtype=np.float64)
        px, py = np.meshgrid(grid, grid)
        away = np.hypot(px - x, py - y) / radius
        for at in (1.0, *ZONES["B"], ZONES["C"][1]):
            edge = np.abs(away - at) < (1.5 / radius)
            picture[edge & shape.fov] = DISC_COLOUR if at == 1.0 else RING_COLOUR
    picture[shape.artery] = ARTERY_COLOUR
    picture[shape.vein] = VEIN_COLOUR
    picture[shape.artery & shape.vein] = OVERLAP_COLOUR
    return picture


#: Every shape, by the name its images and its rows are keyed on.
SHAPES: dict[str, Callable[[], Scene]] = {
    "straight": straight,
    "arc": arc,
    "clothoid": clothoid,
    "sinusoid": sinusoid,
    "bifurcation": bifurcation,
    "tree": tree,
    "deep-bifurcation": deep_bifurcation,
    "spur": spur,
    "crossing": crossing,
    "disjoint": disjoint,
    "koch": koch,
    "spokes-macula-centred": spokes_macula_centred,
    "spokes-disc-centred": spokes_disc_centred,
}
