# ABOUTME: AutoMorphalyzer's rewritten measuring code, reached from this repository: one call per
# ABOUTME: vessel map, and the table saying which catalogued biomarker each of its columns answers to.

import numpy as np

from upstreams import automorphalyzer as upstream

#: The three maps it measures, and the structure each answers for. It measures the union as well as
#: the two classes, so the adapter forms that union itself rather than taking one as given.
CLASSES = {"binary": "vessels", "artery": "artery", "vein": "vein"}

#: The zones it measures in, as `generate_zonal_masks` builds them — and what each one *is*, which
#: is the fact that decides whether a number is comparable with anybody else's.
#:
#: *Our finding, 2026-09-21, from reading `generate_zonal_masks`:* zone **B is the annulus between
#: two and three disc radii**, which is exactly the region PVBM measures its equivalents over
#: (PVBM builds it as zone C minus zone B). Zone **C is two to five radii**, which is nobody
#: else's region. So a value from B is comparable and a value from C is not, whatever they share a
#: name with.
ZONES = ("whole", "B", "C")
COMPARABLE_ZONE = "B"

#: What it computes over the **whole image**, and the catalogued biomarker each answers to.
#: `{side}` becomes `artery`, `vein` or `vessels`.
WHOLE: dict[str, str | None] = {
    "fractal_dimension": "fractal-dimension/box-counting/{side}",
    # Vessel pixels over *every* pixel of the frame, lit or not — `vessel_metrics` divides by
    # `vessels.shape[0] * vessels.shape[1]` and never sees a field of view.
    "vessel_density": "vascular-density/over-image/{side}",
    # Vessel area over skeleton length: a mean width by construction.
    "average_global_calibre": "vessel-calibre/mean-width/{side}",
    "tortuosity_distance": "tortuosity/hart-tau1/{side}",
    "tortuosity_density": "tortuosity/grisan-density/{side}",
    # The mean of per-vessel widths rather than area over skeleton. A different aggregation of the
    # same idea, and the catalogue has no name separating the two yet.
    "average_local_calibre": None,
    "CRAE_Knudtson": None,
    "CRVE_Knudtson": None,
}

#: What it computes **inside a zone**. Only zone B is catalogued, for the reason above; the same
#: column measured over zone C keeps its own name and is stored beside it.
ZONAL: dict[str, str | None] = {
    "CRAE_Knudtson": "central-retinal-equivalents/knudtson/artery",
    "CRVE_Knudtson": "central-retinal-equivalents/knudtson/vein",
    "tortuosity_distance": None,
    "tortuosity_density": None,
    "average_local_calibre": None,
}

#: What it signals when a measurement could not be made. It is a sentinel rather than a value, and
#: is turned into no answer here rather than averaged into somebody's table as a negative calibre.
FAILED = -1


def _answers() -> dict[str, str]:
    """Answered name → the column and zone behind it, as `<column>@<zone>_<class>`.

    A name carrying a `/` is a catalogued biomarker and a name without one is AutoMorphalyzer's
    own, kept because the catalogue cannot name that quantity or that region yet.
    """
    pairs: dict[str, str] = {}
    for measured, side in CLASSES.items():
        for column, mapped in WHOLE.items():
            own = f"{column}@whole_{measured}"
            pairs[mapped.format(side=side) if mapped else own] = own
        for zone in ("B", "C"):
            for column, mapped in ZONAL.items():
                own = f"{column}@{zone}_{measured}"
                catalogued = (
                    mapped
                    and zone == COMPARABLE_ZONE
                    and side in (mapped.split("/")[-1], "vessels")
                )
                # An equivalent is named for the class it measures, so the artery column only
                # answers for arteries; the same column over the vein map is a different number.
                if catalogued and mapped.split("/")[-1] == side:
                    pairs[mapped] = own
                else:
                    pairs[own] = own
    return pairs


#: Answered name → the column behind it. Built once; the order is the order above.
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


class Automorphalyzer:
    """AutoMorphalyzer, measured as it ships.

    One call per vessel map computes everything it computes for that map — its global metrics over
    the whole image and its tortuosity, calibre and equivalents inside each zone — which is why the
    adapter is per implementation rather than per biomarker.

    Everything is in **pixels**. Its authors state plainly that the pipeline assumes no knowledge
    of the physical resolution and measures at a fixed working size, so no scale is passed on here
    and none is applied.
    """

    slug = "automorphalyzer"
    needs = ("artery", "vein", "disc")
    invariant = ("rotation",)

    #: What the masks are handed over as. `vessel_metrics` casts to `uint8` itself, and the tracer
    #: wants something it can multiply, so this is what its own driver hands it.
    DTYPE = np.uint8

    def __init__(self, device: str | None = None) -> None:
        self.device = "cpu"
        #: What went wrong during the last call, by where, so a run can record it rather than
        #: leaving an empty cell that could mean anything.
        self.trouble: dict[str, str] = {}
        self._measure = None
        self._coordinates = None
        self._zones = None

    def declare(self) -> dict[str, object]:
        return {
            "slug": self.slug,
            "needs": list(self.needs),
            "invariant": list(self.invariant),
            "keys": list(self.keys()),
            "names": dict(CANONICAL),
            "calls": {own: [f"measure_{own.rsplit('_', 1)[-1]}"] for own in CANONICAL},
            "zones": {"B": "2 to 3 disc radii", "C": "2 to 5 disc radii", "whole": "the frame"},
            "units": {"every measurement": "px"},
            "device": self.device,
            "upstream": upstream.provenance(),
        }

    def identity(self) -> str:
        """What pins the code that will run. It carries no weights of its own for this work."""
        return str(upstream.COMMIT)

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
        """Everything it computes, under catalogued names, with `None` where it could not."""
        self.trouble = {}
        computed: dict[str, float | None] = dict.fromkeys(ANSWERS.values())
        x, y, radius = (float(value) for value in disc)
        side = (artery if artery is not None else vein).shape[0]
        disc_mask = self._disc_mask(side, x, y, radius)
        maps = {
            "artery": artery,
            "vein": vein,
            # The union is formed here rather than taken as given, which is the same derivation the
            # artery/vein benchmark applies to every model.
            "binary": None if artery is None and vein is None else _union(artery, vein),
        }
        for measured, mask in maps.items():
            if mask is None or not mask.any():
                continue
            computed.update(self._one_map(mask, measured, disc_mask, (x, y), radius, side))
        return {own: computed.get(own) for own in CANONICAL}

    def _one_map(self, mask, measured, disc_mask, centre, radius, side):
        """One vessel map, measured in every zone, under the column names it uses itself."""
        found: dict[str, float | None] = {}
        binary = np.asarray(mask, dtype=self.DTYPE)
        try:
            zones = self._loaded_zones().generate_zonal_masks((side, side), radius, centre)
            traced = self._loaded_coordinates().generate_vessel_skeleton(
                binary, disc_mask, centre, min_length=10
            )
            measured_zones = self._loaded_measure().vessel_metrics(
                binary, traced, zones, vessel_type=measured
            )
        except Exception as failure:  # noqa: BLE001 — a measurement that fell over has no value
            self.trouble[f"measure_{measured}"] = repr(failure)
            return found
        for zone, values in measured_zones.items():
            for column, value in values.items():
                found[f"{column}@{zone}_{measured}"] = _number(value)
        return found

    @staticmethod
    def _disc_mask(side: int, x: float, y: float, radius: float) -> np.ndarray:
        """The disc as a filled circle. Its tracer wants a mask, not a centre and a radius."""
        grid = np.arange(side, dtype=np.float64) + 0.5
        px, py = np.meshgrid(grid, grid)
        return (px - x) ** 2 + (py - y) ** 2 <= radius * radius

    def _loaded_measure(self):
        if self._measure is None:
            self._measure = upstream.measure()
        return self._measure

    def _loaded_coordinates(self):
        if self._coordinates is None:
            self._coordinates = upstream.coordinates()
        return self._coordinates

    def _loaded_zones(self):
        if self._zones is None:
            self._zones = upstream.zones()
        return self._zones

    def release(self) -> None:
        self._measure = self._coordinates = self._zones = None


def _union(artery: np.ndarray | None, vein: np.ndarray | None) -> np.ndarray:
    parts = [np.asarray(part) > 0 for part in (artery, vein) if part is not None]
    return parts[0] if len(parts) == 1 else parts[0] | parts[1]


def _number(value: object) -> float | None:
    """One finite number, or nothing. Its −1 sentinel is not a measurement and is not kept as one."""
    try:
        found = float(value)
    except (TypeError, ValueError):
        return None
    if not np.isfinite(found) or found == FAILED:
        return None
    return found


def implementation(**arguments: object) -> Automorphalyzer:
    return Automorphalyzer(**arguments)
