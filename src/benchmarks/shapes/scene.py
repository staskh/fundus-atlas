# ABOUTME: A synthetic retina stated in microns: the camera, the optic disc, and each vessel class as
# ABOUTME: a network of centreline paths whose curvature and corners are known exactly.

import math
from dataclasses import dataclass, field

import numpy as np

#: The camera. A 45° fundus camera at 288 µm of retina per degree, an emmetropic eye, with the lit
#: circle inscribed in a square frame — so the frame's side spans the field of view's diameter,
#: 12,960 µm, and the scale of a rendering follows from its side alone.
FOV_DEGREES = 45.0
UM_PER_DEGREE = 288.0
FOV_DIAMETER_UM = FOV_DEGREES * UM_PER_DEGREE
FOV_RADIUS_UM = FOV_DIAMETER_UM / 2.0

#: An adult optic disc is about 1,800 µm **across**, so the radius every zone is counted in is
#: half of it — the factor-of-two trap `docs/biomarkers/calibre.md` §5 records, met here in the
#: parameter itself. Zones B and C are annuli in disc radii from the disc centre
#: (`docs/biomarkers/regions-of-interest.md`).
DISC_DIAMETER_UM = 1800.0
DISC_RADIUS_UM = DISC_DIAMETER_UM / 2.0
ZONES = {"B": (2.0, 3.0), "C": (2.0, 5.0)}

#: Where the disc sits, in µm from the frame centre (x right, y down). A macula-centred photograph
#: puts it right of centre, as a right eye's is, far enough in that zone B stays inside the field at
#: every rotation; a disc-centred photograph puts it in the middle.
MACULA_CENTRED_DISC = (2600.0, 0.0)
DISC_CENTRED_DISC = (0.0, 0.0)

#: How wide a vessel is, by class, in µm.
ARTERY_UM = 80.0
VEIN_UM = 120.0

#: How finely a path is sampled: fine enough that clipping it to a zone and integrating along it
#: are exact to well under a micron — far below anything a rendering can resolve.
SPACING_UM = 0.5


@dataclass(frozen=True)
class Path:
    """A centreline in µm (x right, y down), with the signed curvature at each sample (1/µm) and
    the signed turn concentrated at each sample (radians; non-zero only at a corner).

    Curvature is carried rather than differenced out of the points: every shape knows its own
    exactly, and differencing a sampled polyline would make the theory an approximation of the
    drawing rather than the other way round.
    """

    points: np.ndarray
    curvature: np.ndarray
    turns: np.ndarray

    @property
    def length(self) -> float:
        return float(np.hypot(*np.diff(self.points, axis=0).T).sum())

    @property
    def start_heading(self) -> float:
        dx, dy = self.points[1] - self.points[0]
        return math.atan2(dy, dx)

    @property
    def end_heading(self) -> float:
        dx, dy = self.points[-1] - self.points[-2]
        return math.atan2(dy, dx)

    @property
    def cornered(self) -> bool:
        """Whether the path turns at a point anywhere — where its curvature is infinite."""
        return bool(np.any(self.turns != 0.0))

    def __getitem__(self, index: slice) -> "Path":
        return Path(self.points[index], self.curvature[index], self.turns[index])


def walk(start, heading_degrees: float, moves) -> Path:
    """A path from `start`, heading `heading_degrees` (0 = +x, 90 = +y, down on screen), along
    `moves`: ``("straight", length)``, ``("arc", length, curvature)``,
    ``("clothoid", length, κ0, κ1)`` or ``("turn", degrees)`` — a corner. Curvature is the rate of
    change of heading with arc length, positive turning +x towards +y.

    The heading is integrated in closed form at each step's midpoint, so an arc and a clothoid are
    exact to the sampling rather than to an Euler step.
    """
    heading = math.radians(heading_degrees)
    points, curvature, turns = [np.asarray(start, dtype=float)], [0.0], [0.0]
    for move in moves:
        if move[0] == "turn":
            turns[-1] += math.radians(move[1])
            heading += math.radians(move[1])
            continue
        kind, length = move[0], move[1]
        if kind == "straight":
            k0 = k1 = 0.0
        elif kind == "arc":
            k0 = k1 = move[2]
        else:
            k0, k1 = move[2], move[3]
        steps = max(math.ceil(length / SPACING_UM), 1)
        ds = length / steps
        s = np.arange(1, steps + 1) * ds
        kappa = k0 + (k1 - k0) * s / length
        middle = s - ds / 2.0
        theta = heading + k0 * middle + (k1 - k0) * middle**2 / (2.0 * length)
        points.extend(
            points[-1] + np.cumsum(ds * np.column_stack([np.cos(theta), np.sin(theta)]), 0)
        )
        # The path's first sample takes the curvature of the move leaving it.
        if len(curvature) == 1:
            curvature[0] = k0
        curvature.extend(kappa)
        turns.extend(np.zeros(steps))
        heading += k0 * length + (k1 - k0) * length / 2.0
    return Path(np.array(points), np.array(curvature), np.array(turns))


def line(start, heading_degrees: float, length: float) -> Path:
    return walk(start, heading_degrees, [("straight", length)])


def sinusoid(start, heading_degrees: float, amplitude: float, wavelength: float, cycles: float):
    """``amplitude · sin(2πu / wavelength)`` across a baseline along `heading_degrees`, over
    `cycles` wavelengths. Its curvature ``y″ / (1 + y′²)^1.5`` is exact; its arc length is an
    elliptic integral with no elementary closed form, so the value the truth uses *is* the sum."""
    span = wavelength * cycles
    slope = 2.0 * math.pi * amplitude / wavelength
    u = np.linspace(0.0, span, math.ceil(span * math.hypot(1.0, slope) / SPACING_UM) + 1)
    k = 2.0 * math.pi / wavelength
    across = amplitude * np.sin(k * u)
    first, second = amplitude * k * np.cos(k * u), -amplitude * k * k * np.sin(k * u)
    angle = math.radians(heading_degrees)
    c, s = math.cos(angle), math.sin(angle)
    points = np.column_stack([start[0] + u * c - across * s, start[1] + u * s + across * c])
    return Path(points, second / (1.0 + first**2) ** 1.5, np.zeros(len(u)))


def margin(disc, heading_degrees: float) -> tuple[float, float]:
    """The point on the optic disc's margin at `heading_degrees` from its centre.

    Vessels leave the eye at the disc's edge rather than from its centre, so every shape but the
    orphaned one begins on this circle — which is also what a disc-anchored measurement assumes when
    it walks a vessel inwards looking for where it started.
    """
    angle = math.radians(heading_degrees)
    return (disc[0] + DISC_RADIUS_UM * math.cos(angle), disc[1] + DISC_RADIUS_UM * math.sin(angle))


@dataclass(frozen=True)
class Node:
    x: float
    y: float
    root: bool = False


@dataclass(frozen=True)
class Segment:
    """One edge of a network: a path from node `start` to node `end`, of constant width (µm)."""

    start: str
    end: str
    width: float
    path: Path


@dataclass(frozen=True)
class Network:
    """One vessel class: nodes by id, segments between them, and the angle between the two
    daughters at each junction (degrees), stated by the shape that built the fork."""

    nodes: dict[str, Node]
    segments: list[Segment]
    angles: dict[str, float] = field(default_factory=dict)

    def degree(self, node: str) -> int:
        return sum((s.start == node) + (s.end == node) for s in self.segments)


def network(paths: list[Path], width: float, rooted: bool = True) -> Network:
    """Unbranched vessels, one segment each, each starting at a root when `rooted` (on the disc)."""
    nodes, segments = {}, []
    for index, path in enumerate(paths):
        start, end = f"{index}s", f"{index}e"
        nodes[start] = Node(*path.points[0], root=rooted)
        nodes[end] = Node(*path.points[-1])
        segments.append(Segment(start, end, width, path))
    return Network(nodes, segments)


def merged(*networks: Network) -> Network:
    """Several networks as one, their node ids kept apart — the vessels measured as a single class.

    It is the union an adapter forms when an implementation measures arteries and veins together,
    so a truth derived on it describes the same vessels that union shows.
    """
    nodes: dict[str, Node] = {}
    segments: list[Segment] = []
    angles: dict[str, float] = {}
    for index, net in enumerate(networks):
        nodes.update({f"{index}:{key}": node for key, node in net.nodes.items()})
        segments += [
            Segment(f"{index}:{s.start}", f"{index}:{s.end}", s.width, s.path) for s in net.segments
        ]
        angles.update({f"{index}:{key}": angle for key, angle in net.angles.items()})
    return Network(nodes, segments, angles)


@dataclass(frozen=True)
class Scene:
    """A retina: the disc centre (µm from the frame centre), each class, the box-counting dimension
    its vessels tend to (1 for smooth curves), and the name prefixes whose truth rests on a reading
    of the definition rather than on the geometry alone."""

    name: str
    disc: tuple[float, float]
    artery: Network
    vein: Network
    dimension: float = 1.0
    conventions: tuple[str, ...] = ()
    parameters: dict[str, float] = field(default_factory=dict)

    def classes(self) -> dict[str, Network]:
        return {"artery": self.artery, "vein": self.vein}


def check_inside(scene: Scene) -> Scene:
    """Refuse a scene with a vessel reaching the edge of the field of view.

    A truncated vessel is not a shorter vessel, it is a different shape: everything measured on it is
    measured on a fragment, and the truth derived beside it would describe something nobody drew.
    """
    for vessel, net in scene.classes().items():
        for segment in net.segments:
            reach = np.hypot(*segment.path.points.T).max() + segment.width / 2.0
            if reach > FOV_RADIUS_UM:
                raise ValueError(
                    f"{scene.name}: an {vessel} reaches {reach:.0f} µm from the centre, outside "
                    f"the field of view ({FOV_RADIUS_UM:.0f} µm)"
                )
    return scene
