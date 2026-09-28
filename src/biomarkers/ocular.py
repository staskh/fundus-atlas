# ABOUTME: OCULAR's measuring code, reached from this repository: PVBM's geometry as this project
# ABOUTME: modified it, and the table saying which catalogued biomarker each returned value answers to.

import numpy as np
from skimage.morphology import skeletonize

from upstreams import ocular as upstream

#: The classes it is asked about, one call each — the same two PVBM is asked about, because the two
#: are measured side by side and the question is what OCULAR's changes did to PVBM's numbers.
CLASSES = ("artery", "vein")

#: What `compute_geomVBMs` returns, **in order**, and the catalogued biomarker each answers to.
#: `{side}` becomes `artery` or `vein`.
#:
#: The list is positional — it returns a bare list — so the order here is the contract, and a
#: change to it upstream would be silent. It is taken from the `return` statement itself rather
#: than from any documentation.
COLUMNS: tuple[tuple[str, str | None], ...] = (
    ("area", "vessel-area-and-length/area/{side}"),
    # Total arc over total chord: one ratio for the whole map, rather than a ratio per vessel.
    # `tortuosity/hart-tau1` is the per-vessel ratio, so this is a different aggregation of the
    # same idea and the catalogue has no name separating them.
    ("pooled_tortuosity", None),
    # The median of the per-vessel arc-over-chord ratios — the same quantity PVBM's
    # `median_tortuosity` reports, which is what makes the two comparable.
    ("median_tortuosity", "tortuosity/hart-tau1/{side}"),
    # Arc-weighted mean of the same ratios. A third aggregation; see above.
    ("length_weighted_tortuosity", None),
    ("length", "vessel-area-and-length/skeleton-length/{side}"),
    # *Our finding, carried over from PVBM:* not the angle between a bifurcation's daughters. It is
    # the median of every pairwise angle at every particular point, the trunk included, and OCULAR
    # inherits the function that computes it.
    ("median_branching_angle", None),
    # Where the walk began, which need not be one per connected component.
    ("start_points", None),
    # *Our finding, 2026-09-26:* **withdrawn**, for the same reason as PVBM's. OCULAR is a fork of
    # `GeometryAnalysis`, which walks each tree from the optic disc and calls the origin a *start
    # point*, so `endpoints` counts the free ends **excluding** that one: a straight vessel reads 1
    # where the geometry requires 2, and `endpoints + start_points` is what answers the catalogued
    # question. Kept under OCULAR's own name rather than summed into a number it never returned.
    ("endpoints", None),
    ("intersections", "junction-counts/junctions/{side}"),
)

#: OCULAR computes **no central retinal equivalents**. Its copy of PVBM's `CREVBMs` keeps that
#: class's graph machinery and replaces the measuring method with one that returns geometry only,
#: so the whole family is absent rather than wrong.
ABSENT = ("central-retinal-equivalents", "avr")


def _answers() -> dict[str, str]:
    """Answered name → the returned value behind it, as `<column>_<class>`."""
    pairs: dict[str, str] = {}
    for side in CLASSES:
        for column, mapped in COLUMNS:
            own = f"{column}_{side}"
            pairs[mapped.format(side=side) if mapped else own] = own
    return pairs


#: Answered name → the value behind it. Built once; the order is the order above.
ANSWERS = _answers()

#: Each column under **its own name**, against the catalogued biomarker it answers to — or `None`
#: where the catalogue has no name for it yet. The evidence a run writes is keyed by the
#: implementation's own names, because that is what its authors call these numbers and what a
#: reader checking against their documentation will look for; translating to a catalogued name is
#: a claim, and a claim belongs in the analysis that relies on it rather than baked into the
#: measurement.
CANONICAL: dict[str, str | None] = {
    own: (answered if "/" in answered else None) for answered, own in ANSWERS.items()
}


class Ocular:
    """OCULAR's geometry, run as it ships.

    Its `utils/GeometricalVBMs.py` is a modified copy of **PVBM's `GeometryAnalysis.GeometricalVBMs`**
    — 343 of its 486 lines are identical, and it carries the same five methods — and it imports
    PVBM's tortuosity, perimeter and branching-angle helpers at runtime. So this adapter measures
    PVBM's code as OCULAR changed it, which is exactly the comparison the two pages are for.

    *Corrected 2026-09-26: this said `CREVBMs`, which is the class OCULAR's **equivalents** file
    forks. The geometry file forks the geometry class, and it forks the current one rather than the
    deprecated `GeometricalAnalysis`.*

    Everything is in **pixels**; no scale is taken and none is applied.
    """

    slug = "ocular"
    needs = ("artery", "vein", "disc")
    invariant = ("rotation",)

    #: What the masks are handed over as. **Not uint8**, for the reason recorded against PVBM: this
    #: code writes pixel coordinates into arrays derived from its input, and an 8-bit array
    #: overflows on a frame wide enough for a coordinate to pass 255.
    DTYPE = np.float64

    #: Which traversal OCULAR is asked for. *Our finding, 2026-09-22:* this argument selects only
    #: the tree-drawing walk, and its own default is `'recursive'`. The topology walk is iterative
    #: unconditionally, and subgraph extraction is recursive unconditionally — `extract_subgraphs`
    #: accepts the same argument and never reads it. Left at OCULAR's default, because a benchmark
    #: of fixed code measures the fix rather than the option.
    TRAVERSAL = "recursive"

    def __init__(self, device: str | None = None) -> None:
        self.device = "cpu"
        self.trouble: dict[str, str] = {}
        self._geometry = None

    def declare(self) -> dict[str, object]:
        return {
            "slug": self.slug,
            # Its catalogue page is not named after its slug: the project is OCULARNet, of which
            # OCULAR is the released collection and model together. Everything that links to a page
            # asks the adapter rather than assuming the two names match.
            "page": "ocularnet",
            "needs": list(self.needs),
            "invariant": list(self.invariant),
            "keys": list(self.keys()),
            "names": dict(CANONICAL),
            "calls": {own: [f"geometry_{own.rsplit('_', 1)[-1]}"] for own in CANONICAL},
            "traversal": self.TRAVERSAL,
            "absent": list(ABSENT),
            "units": {"every measurement": "px"},
            "device": self.device,
            "upstream": upstream.provenance(),
        }

    def identity(self) -> str:
        return str(upstream.provenance()["commit"])

    def keys(self) -> tuple[str, ...]:
        return tuple(CANONICAL)

    def measure(
        self,
        artery: np.ndarray | None,
        vein: np.ndarray | None,
        fov: np.ndarray,
        disc: tuple[float, float, float],
        um_per_px: float | None,
    ) -> dict[str, float | None]:
        """Its nine measurements per class, under catalogued names where one applies."""
        self.trouble = {}
        computed: dict[str, float | None] = dict.fromkeys(ANSWERS.values())
        x, y, radius = (float(value) for value in disc)
        for side, mask in (("artery", artery), ("vein", vein)):
            if mask is None or not mask.any():
                continue
            try:
                found = self._one_class(mask, x, y, radius)
            except Exception as failure:  # noqa: BLE001 — a measurement that fell over has no value
                self.trouble[f"geometry_{side}"] = repr(failure)
                continue
            for (column, _mapped), value in zip(COLUMNS, found, strict=False):
                computed[f"{column}_{side}"] = _number(value)
        return {own: computed.get(own) for own in CANONICAL}

    def _one_class(self, mask: np.ndarray, x: float, y: float, radius: float):
        """One class, measured by OCULAR's own call. The skeleton is an input it does not make."""
        binary = np.asarray(mask, dtype=self.DTYPE)
        spine = skeletonize(np.asarray(mask) > 0).astype(self.DTYPE)
        measured, _visualisations = self._loaded()().compute_geomVBMs(
            blood_vessel=binary,
            skeleton=spine,
            xc=int(round(x)),
            yc=int(round(y)),
            radius=int(round(radius)),
            iterative_or_recursive=self.TRAVERSAL,
        )
        return measured

    def _loaded(self):
        if self._geometry is None:
            self._geometry = upstream.geometry()
        return self._geometry

    def release(self) -> None:
        self._geometry = None


def _number(value: object) -> float | None:
    try:
        found = float(value)
    except (TypeError, ValueError):
        return None
    return None if not np.isfinite(found) else found


def implementation(**arguments: object) -> Ocular:
    return Ocular(**arguments)
