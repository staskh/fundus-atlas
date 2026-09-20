# ABOUTME: PVBM's measuring code, reached from this repository: one call per class, answering with
# ABOUTME: PVBM's own column names and never renaming, converting or repairing anything.

import numpy as np
from skimage.morphology import skeletonize

from upstreams import pvbm as upstream

#: Every column this adapter can return, in the order a reader meets them. They are PVBM's names,
#: not this repository's: the translation lives in `naming.py`, reviewed on its own, because it is
#: a claim about what somebody's code computes.
GEOMETRY = (
    "area",
    "length",
    "perimeter",
    "median_tortuosity",
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
EQUIVALENTS = ("crae_knudtson", "crve_knudtson", "crae_hubbard", "crve_hubbard")
RATIOS = ("avr_knudtson", "avr_hubbard")

#: What PVBM signals when a central retinal equivalent could not be computed. It is a sentinel
#: rather than a value, and it is turned into "no answer" here rather than left to be averaged
#: into somebody's table as a negative calibre.
FAILED = -1


class Pvbm:
    """PVBM, measured as it ships.

    One call computes everything PVBM computes — its geometry runs once per class over one
    skeleton, its fractal analysis once per class, and its equivalents once over both — which is
    why the adapter is per implementation rather than per biomarker.

    Two of its habits are reproduced rather than corrected. Its areas and lengths are in pixels,
    which it says plainly; and its Hubbard equivalents carry constants fitted in microns, so they
    are computed on micron widths here and returned in microns, while its Knudtson equivalents are
    scale-free and returned in pixels. A benchmark of fixed code measures the fix.
    """

    slug = "pvbm"
    needs = ("artery", "vein", "disc")
    invariant = ("rotation",)

    def __init__(self, device: str | None = None) -> None:
        self.device = "cpu"
        self._geometry = None
        self._fractals = None
        self._equivalents = None

    def declare(self) -> dict[str, object]:
        return {
            "slug": self.slug,
            "needs": list(self.needs),
            "invariant": list(self.invariant),
            "keys": list(self.keys()),
            "units": {
                "area": "px²",
                "length": "px",
                "crae_knudtson": "px",
                "crae_hubbard": "µm",
                "median_branching_angle": "degrees",
            },
            "device": self.device,
            "upstream": upstream.provenance(),
        }

    def identity(self) -> str:
        """What pins the code that will run. PVBM carries no weights of its own for this work."""
        return str(upstream.COMMIT)

    def keys(self) -> tuple[str, ...]:
        """Every column, whatever it was handed — so a table has one shape across every shape."""
        per_class = tuple(f"{name}_{side}" for side in ("artery", "vein") for name in GEOMETRY + FRACTALS)
        return per_class + EQUIVALENTS + RATIOS

    def measure(
        self,
        artery: np.ndarray | None,
        vein: np.ndarray | None,
        fov: np.ndarray,
        disc: tuple[float, float, float],
        um_per_px: float | None,
    ) -> dict[str, float | None]:
        """Everything PVBM computes, under PVBM's own names, with `None` where it could not."""
        answers: dict[str, float | None] = dict.fromkeys(self.keys())
        for side, mask in (("artery", artery), ("vein", vein)):
            if mask is None or not mask.any():
                continue
            answers.update(self._per_class(mask, side))
        answers.update(self._per_pair(artery, vein, disc, um_per_px))
        return answers

    def _per_class(self, mask: np.ndarray, side: str) -> dict[str, float | None]:
        """The measurements PVBM takes over one class at a time."""
        found: dict[str, float | None] = {}
        binary = np.asarray(mask, dtype=np.uint8)
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
            spine = skeletonize(binary > 0).astype(np.uint8)
            found[f"area_{side}"] = float(geometry.area(binary))
            median_tortuosity, length, _chord, _arc, _connections = geometry.compute_tortuosity_length(
                spine
            )
            found[f"median_tortuosity_{side}"] = _number(median_tortuosity)
            found[f"length_{side}"] = _number(length)
            endpoints, intersections, _ends, _inters = geometry.compute_particular_points(spine)
            found[f"endpoints_{side}"] = _number(endpoints)
            found[f"intersections_{side}"] = _number(intersections)
            _mean, _spread, median_angle, _angles, _centroid = geometry.compute_branching_angles(spine)
            found[f"median_branching_angle_{side}"] = _number(median_angle)
        except Exception:  # noqa: BLE001 — a measurement that fell over is one that has no value
            pass
        try:
            spectrum = self._loaded_fractals().compute_multifractals(binary.copy())
            for name, value in zip(FRACTALS, spectrum, strict=False):
                found[f"{name}_{side}"] = _number(value)
        except Exception:  # noqa: BLE001
            pass
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
            except Exception:  # noqa: BLE001
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
        binary = np.asarray(mask, dtype=np.uint8)
        spine = skeletonize(binary > 0).astype(np.uint8)
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
