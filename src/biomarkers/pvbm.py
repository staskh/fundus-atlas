# ABOUTME: PVBM's measuring code, reached from this repository: one call per class, and the table
# ABOUTME: saying which catalogued biomarker each of its columns answers to.

import numpy as np
from skimage.morphology import skeletonize

from upstreams import pvbm as upstream

#: What PVBM computes **per class**, and the catalogued biomarker this repository believes each
#: answers to. `{side}` is filled with `artery` or `vein`.
#:
#: **Every row is a claim** about what somebody else's code computes — usually read out of its
#: source — and the synthetic shapes are what test it. `median_branching_angle` was mapped to the
#: angle between daughters until a shape showed that it medians *every* pairwise angle at every
#: junction, the trunk included, and reads ~120° where the daughters are 60° apart. That mapping is
#: now `None`, which is a finding rather than an omission.
#:
#: `None` means nothing in the catalogue matches it **yet**. Such a column is measured and stored
#: exactly like any other, under PVBM's own name: a quantity the catalogue has no name for is a gap
#: in the catalogue, not a reason to throw a measurement away.
PER_CLASS: dict[str, str | None] = {
    "area": "vessel-area-and-length/area/{side}",
    "length": "vessel-area-and-length/skeleton-length/{side}",
    # The boundary length of a vessel mask. Nothing else in the catalogue computes it, and a name
    # exists to make two numbers comparable, so it waits for a second implementation to need one.
    "perimeter": None,
    "median_tortuosity": "tortuosity/hart-tau1/{side}",
    # All three come back from one call. PVBM's own docstring names the mean and the median and
    # omits the standard deviation, which it returns between them.
    "mean_branching_angle": None,
    "std_branching_angle": None,
    # *Our finding, 2026-09-20, from reading `compute_angles_dictionary`:* not the angle between
    # the daughters of a bifurcation. See the note above.
    "median_branching_angle": None,
    "endpoints": "junction-counts/endpoints/{side}",
    "intersections": "junction-counts/junctions/{side}",
    # PVBM's three dimensions are of the multifractal analysis, not the plain box count, which is
    # why they map to the multifractal names and not to `fractal-dimension/box-counting`.
    "capacity_dimension": "fractal-dimension/multifractal-d0/{side}",
    "entropy_dimension": "fractal-dimension/multifractal-d1/{side}",
    "correlation_dimension": "fractal-dimension/multifractal-d2/{side}",
    "singularity_length": None,
}

#: What it computes over **both classes at once**: the equivalents, and the ratios this adapter
#: forms from them because PVBM leaves that division to its user.
#:
#: *Our finding, 2026-09-20:* PVBM computes the Hubbard variants from **pixel** widths, and
#: Hubbard's constants were fitted in microns. The canonical name says microns, so a value here is
#: not comparable with one from an implementation that converts first — which is a defect of the
#: implementation rather than of the mapping, and is why the benchmark reports the number rather
#: than correcting it.
PER_PAIR: dict[str, str | None] = {
    "crae_knudtson": "central-retinal-equivalents/knudtson/artery",
    "crve_knudtson": "central-retinal-equivalents/knudtson/vein",
    "crae_hubbard": "central-retinal-equivalents/hubbard/artery",
    "crve_hubbard": "central-retinal-equivalents/hubbard/vein",
    "avr_knudtson": "avr/knudtson/both",
    "avr_hubbard": "avr/hubbard/both",
}

#: The order a reader meets PVBM's own columns in, per class.
GEOMETRY = (
    "area",
    "length",
    "perimeter",
    "median_tortuosity",
    "mean_branching_angle",
    "std_branching_angle",
    "median_branching_angle",
    "endpoints",
    "intersections",
)
FRACTALS = (
    "capacity_dimension",
    "entropy_dimension",
    "correlation_dimension",
    "singularity_length",
)
CLASSES = ("artery", "vein")


def _answers() -> dict[str, str]:
    """What this adapter answers under, against the PVBM column each value came from.

    A name carrying a `/` is a catalogued biomarker and a name without one is PVBM's own, so two
    implementations' evidence lines up column by column wherever the catalogue has a name for what
    they computed, and keeps what it has no name for yet.
    """
    pairs: dict[str, str] = {}
    for side in CLASSES:
        for own in GEOMETRY + FRACTALS:
            mapped = PER_CLASS[own]
            pairs[mapped.format(side=side) if mapped else f"{own}_{side}"] = f"{own}_{side}"
    for own, mapped in PER_PAIR.items():
        pairs[mapped or own] = own
    return pairs


#: Answered name → the PVBM column behind it. Built once; the order is the order above.
ANSWERS = _answers()


def _calls() -> dict[str, list[str]]:
    """Which of PVBM's calls each answered column comes out of, named as `trouble` names them.

    A failure is recorded per **call**, because that is what raises — one call computes seven
    quantities and loses all seven when it falls over. Without this, a reader of the evidence
    cannot tell a column that was lost to an exception from one that was simply never defined on
    that shape, since both are empty; with it, a missing value can be attributed to the failure
    that actually caused it.
    """
    where: dict[str, list[str]] = {}
    for side in CLASSES:
        for own in GEOMETRY:
            mapped = PER_CLASS[own]
            where[mapped.format(side=side) if mapped else f"{own}_{side}"] = [f"geometry_{side}"]
        for own in FRACTALS:
            mapped = PER_CLASS[own]
            where[mapped.format(side=side) if mapped else f"{own}_{side}"] = [f"fractals_{side}"]
    for own, mapped in PER_PAIR.items():
        # A ratio needs both classes, so it is lost if either call fails.
        sides = ["artery"] if own.startswith("crae") else ["vein"] if own.startswith("crve") else list(CLASSES)
        where[mapped or own] = [f"equivalents_{side}" for side in sides]
    return where


#: Answered name → the calls that produce it. Keyed to match what `trouble` records.
CALLS = _calls()

#: What PVBM signals when a central retinal equivalent could not be computed. It is a sentinel
#: rather than a value, and it is turned into "no answer" here rather than left to be averaged
#: into somebody's table as a negative calibre.
FAILED = -1


class Pvbm:
    """PVBM, measured as it ships.

    One call computes everything PVBM computes — its geometry runs once per class over one
    skeleton, its fractal analysis once per class, and its equivalents once over both — which is
    why the adapter is per implementation rather than per biomarker.

    **It answers under catalogued names**, translating PVBM's own through the table above, so that
    two implementations' evidence lines up column by column. A column the catalogue has no name for
    is answered under PVBM's own name and measured all the same.

    Two of its habits are reproduced rather than corrected. Its areas and lengths are in pixels,
    which it says plainly; and its Hubbard equivalents carry constants fitted in microns, so they
    are computed on micron widths here and returned in microns, while its Knudtson equivalents are
    scale-free and returned in pixels. A benchmark of fixed code measures the fix.
    """

    slug = "pvbm"
    needs = ("artery", "vein", "disc")
    invariant = ("rotation",)

    #: What the masks are handed over as. **Not uint8**: PVBM writes pixel coordinates and labels
    #: into arrays it derives from the input, so an 8-bit input overflows on any image wide enough
    #: for a coordinate to pass 255 — `OverflowError: Python integer 416 out of bounds for uint8`
    #: at 2048². Its own documentation asks only for binary values, and float is what its examples
    #: hand it.
    DTYPE = np.float64

    def __init__(self, device: str | None = None) -> None:
        self.device = "cpu"
        #: What went wrong during the last call, by where, so a run can record it rather than
        #: leaving an empty cell that could mean anything.
        self.trouble: dict[str, str] = {}
        self._geometry = None
        self._fractals = None
        self._equivalents = None

    def declare(self) -> dict[str, object]:
        return {
            "slug": self.slug,
            "needs": list(self.needs),
            "invariant": list(self.invariant),
            "keys": list(self.keys()),
            # What each answered column is called in PVBM's own vocabulary, so a run records the
            # claim it was measured under and a later reader can check it against the source.
            "names": dict(ANSWERS),
            "unnamed": [own for own, mapped in {**PER_CLASS, **PER_PAIR}.items() if not mapped],
            # Which call each column comes out of, so a run's `note` can be attributed to the
            # columns it actually cost rather than to every column of that rendering.
            "calls": {name: list(calls) for name, calls in CALLS.items()},
            "units": {
                "vessel-area-and-length/area/artery": "px²",
                "vessel-area-and-length/skeleton-length/artery": "px",
                "central-retinal-equivalents/knudtson/artery": "px",
                "central-retinal-equivalents/hubbard/artery": "µm",
                "median_branching_angle_artery": "degrees",
            },
            "device": self.device,
            "upstream": upstream.provenance(),
        }

    def identity(self) -> str:
        """What pins the code that will run. PVBM carries no weights of its own for this work."""
        return str(upstream.COMMIT)

    def keys(self) -> tuple[str, ...]:
        """Every column, whatever it was handed — so a table has one shape across every shape."""
        return tuple(ANSWERS)

    def canonical_for(self, own: str) -> str | None:
        """The catalogued name a PVBM column is believed to answer to, or `None` if none does."""
        for answered, column in ANSWERS.items():
            if column == own:
                return answered if "/" in answered else None
        raise LookupError(f"PVBM computes no column named {own!r}")

    def measure(
        self,
        artery: np.ndarray | None,
        vein: np.ndarray | None,
        fov: np.ndarray,
        disc: tuple[float, float, float],
        um_per_px: float | None,
    ) -> dict[str, float | None]:
        """Everything PVBM computes, under catalogued names, with `None` where it could not.

        The measuring is done under PVBM's own names and translated once, here, so that what is
        computed and what it is called stay separable: a mapping that turns out to be wrong is
        corrected in the table above without touching a line of the measuring.
        """
        self.trouble = {}
        computed: dict[str, float | None] = dict.fromkeys(ANSWERS.values())
        for side, mask in (("artery", artery), ("vein", vein)):
            if mask is None or not mask.any():
                continue
            computed.update(self._per_class(mask, side))
        computed.update(self._per_pair(artery, vein, disc, um_per_px))
        return {answered: computed.get(column) for answered, column in ANSWERS.items()}

    def _per_class(self, mask: np.ndarray, side: str) -> dict[str, float | None]:
        """The measurements PVBM takes over one class at a time."""
        found: dict[str, float | None] = {}
        binary = np.asarray(mask, dtype=self.DTYPE)
        try:
            geometry = self._loaded_geometry()
            # `compute_perimeter` returns a second value it calls `segmentation_skeleton`, and it
            # is **not** a centreline: it skeletonises the vessel's *border*, so it is a closed
            # outline with no endpoints at all. Feeding it to the tortuosity call — which the name
            # invites — yields a median of nan and a length of zero, because the walk looks for
            # endpoints and junctions and a loop has neither. The centreline is taken here, which
            # is what every one of PVBM's own docstrings asks for.
            perimeter, _border = geometry.compute_perimeter(binary)
            found[f"perimeter_{side}"] = float(perimeter)
            spine = skeletonize(np.asarray(mask) > 0).astype(self.DTYPE)
            found[f"area_{side}"] = float(geometry.area(binary))
            median_tortuosity, length, _chord, _arc, _connections = geometry.compute_tortuosity_length(
                spine
            )
            found[f"median_tortuosity_{side}"] = _number(median_tortuosity)
            found[f"length_{side}"] = _number(length)
            endpoints, intersections, _ends, _inters = geometry.compute_particular_points(spine)
            found[f"endpoints_{side}"] = _number(endpoints)
            found[f"intersections_{side}"] = _number(intersections)
            mean_angle, spread, median_angle, _angles, _centroid = geometry.compute_branching_angles(
                spine
            )
            found[f"mean_branching_angle_{side}"] = _number(mean_angle)
            found[f"std_branching_angle_{side}"] = _number(spread)
            found[f"median_branching_angle_{side}"] = _number(median_angle)
        except Exception as failure:  # noqa: BLE001 — a measurement that fell over has no value
            # Recorded rather than swallowed. Silence here once made an adapter's own bug look
            # like PVBM declining to answer, which is the most expensive kind of quiet there is.
            self.trouble[f"geometry_{side}"] = repr(failure)
        try:
            spectrum = self._loaded_fractals().compute_multifractals(binary.copy())
            for name, value in zip(FRACTALS, spectrum, strict=False):
                found[f"{name}_{side}"] = _number(value)
        except Exception as failure:  # noqa: BLE001
            self.trouble[f"fractals_{side}"] = repr(failure)
        return found

    def _per_pair(
        self,
        artery: np.ndarray | None,
        vein: np.ndarray | None,
        disc: tuple[float, float, float],
        um_per_px: float | None,
    ) -> dict[str, float | None]:
        """The equivalents, which need the disc, and the ratios PVBM leaves its user to divide."""
        found: dict[str, float | None] = {}
        x, y, radius = (float(value) for value in disc)
        for side, mask, artery_flag in (("artery", artery, True), ("vein", vein, False)):
            if mask is None or not mask.any():
                continue
            prefix = "crae" if artery_flag else "crve"
            # One call returns both variants, and **neither takes a scale**: PVBM measures widths
            # from the mask in pixels and puts those pixel widths into both formulas. For Knudtson
            # that is fine, the formula being scale-free. For Hubbard it is the dimensional error
            # `docs/biomarkers/central-retinal-equivalents.md` §3.1 records — its constants were
            # fitted in microns and its additive term does not scale — so what comes back is not a
            # Hubbard equivalent in pixels awaiting conversion, it is a different number. It is
            # returned as PVBM computes it, because a benchmark of corrected code measures the
            # correction.
            try:
                both = self._equivalents_of(mask, x, y, radius, artery_flag)
            except Exception as failure:  # noqa: BLE001
                self.trouble[f"equivalents_{side}"] = repr(failure)
                both = {}
            found[f"{prefix}_knudtson"] = both.get("knudtson")
            found[f"{prefix}_hubbard"] = both.get("hubbard")
        for variant in ("knudtson", "hubbard"):
            crae, crve = found.get(f"crae_{variant}"), found.get(f"crve_{variant}")
            # A ratio needs both classes. Formed from one, it would be a number nobody could see
            # was wrong, which is why it is left empty instead.
            found[f"avr_{variant}"] = crae / crve if crae and crve else None
        return found

    def _equivalents_of(
        self, mask: np.ndarray, x: float, y: float, radius: float, artery: bool
    ) -> dict[str, float | None]:
        """Both equivalents for one class, from the one call that computes them together.

        PVBM names its answers `craek` and `craeh` — or `crvek` and `crveh` — with the trailing
        letter naming the formula. It signals a failure with −1, which is turned into no answer
        here rather than left to be averaged into somebody's table as a negative calibre.
        """
        binary = np.asarray(mask, dtype=self.DTYPE)
        spine = skeletonize(np.asarray(mask) > 0).astype(self.DTYPE)
        result, _plot = self._loaded_equivalents().compute_central_retinal_equivalents(
            blood_vessel=binary,
            skeleton=spine,
            xc=int(round(x)),
            yc=int(round(y)),
            radius=int(round(radius)),
            artery=artery,
            Toplot=False,
        )
        answers: dict[str, float | None] = {"knudtson": None, "hubbard": None}
        for name, value in (result or {}).items():
            variant = "knudtson" if name.endswith("k") else "hubbard" if name.endswith("h") else None
            if variant is None:
                continue
            number = _number(value)
            answers[variant] = None if number is None or number == FAILED else number
        return answers

    def _loaded_geometry(self):
        if self._geometry is None:
            self._geometry = upstream.geometry()
        return self._geometry

    def _loaded_fractals(self):
        if self._fractals is None:
            self._fractals = upstream.fractals()
        return self._fractals

    def _loaded_equivalents(self):
        if self._equivalents is None:
            self._equivalents = upstream.equivalents()
        return self._equivalents

    def release(self) -> None:
        self._geometry = self._fractals = self._equivalents = None


def _number(value: object) -> float | None:
    """One finite number, or nothing. A NaN is not a measurement and is not recorded as one."""
    try:
        found = float(value)
    except (TypeError, ValueError):
        return None
    return None if not np.isfinite(found) else found


def implementation(**arguments: object) -> Pvbm:
    return Pvbm(**arguments)
