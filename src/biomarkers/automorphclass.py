# ABOUTME: AutoMorphClass's feature calculation, reached from this repository: one call per vessel
# ABOUTME: map, and the table saying which catalogued biomarker each of its columns answers to.

import numpy as np

from upstreams import automorphclass as upstream

#: The three maps it is asked to measure, and the structure each answers for. It takes one map at a
#: time and knows nothing of classes, so the adapter forms the union and calls it three times.
CLASSES = {"vessels": "vessels", "artery": "artery", "vein": "vein"}

#: What `Vessel_Features` returns, and the catalogued biomarker each answers to. `{side}` becomes
#: `artery`, `vein` or `vessels`.
#:
#: Every one of its six columns maps, which is unusual and is the point of this project: it is
#: AutoMorph's measurements reimplemented, so it computes the same quantities under clearer names.
COLUMNS: dict[str, str | None] = {
    # Vessel pixels over every pixel of the frame — it never sees a field of view.
    "vessel_density": "vascular-density/over-image/{side}",
    "fractal_dimension": "fractal-dimension/box-counting/{side}",
    "average_width": "vessel-calibre/mean-width/{side}",
    "distance_tortuosity": "tortuosity/hart-tau1/{side}",
    # *Our finding, 2026-09-21:* **not** Hart's τ3, despite the name. `squared_curvature_tortuosity`
    # squares nothing: it accumulates discrete curvature at each sample and integrates it over the
    # sample *index* rather than over arc length. It was mapped to τ3 until the shapes disagreed by
    # five orders of magnitude, and it does not match τ2 either — its ratio to the total curvature
    # is 10.3 on the arc and 2.0 on the sinusoid, so no constant relates them. Discrete curvature
    # on a pixel skeleton is its own quantity and the catalogue has no name for it.
    "squared_curvature_tortuosity": None,
    "tortuosity_density": "tortuosity/grisan-density/{side}",
}

#: It computes **no central retinal equivalents and nothing zonal**: its vessel features take a
#: segmentation and no disc, so the whole family of disc-anchored measurements is absent rather
#: than wrong. That is a difference in scope from its two siblings, not a defect.
ABSENT = ("central-retinal-equivalents", "avr")


def _answers() -> dict[str, str]:
    """Answered name → the column and map behind it, as `<column>_<class>`."""
    pairs: dict[str, str] = {}
    for measured, side in CLASSES.items():
        for column, mapped in COLUMNS.items():
            own = f"{column}_{measured}"
            pairs[mapped.format(side=side) if mapped else own] = own
    return pairs


#: Answered name → the column behind it. Built once; the order is the order above.
ANSWERS = _answers()


class Automorphclass:
    """AutoMorphClass, measured as it ships.

    One call per vessel map returns its six vessel features. Its optic disc and cup features are
    not reached: they need a cup segmentation, which a biomarker adapter is not handed, and the
    cup-to-disc ratio is measured against ophthalmologists' own outlines in the disc benchmark.

    Everything is in **pixels**. It takes no scale and applies none.
    """

    slug = "automorphclass"
    needs = ("artery", "vein")
    invariant = ("rotation",)

    #: What it is handed. Its own assertion wants `H×W×1`, and it compares against 1, so a mask
    #: goes in as ones and zeros rather than as `True` and `False`.
    DTYPE = np.uint8

    #: How many pixels a vessel must have before it is traced at all. Its own default, declared
    #: here because it is a number the measurement acts on.
    MIN_PIXELS_PER_VESSEL = 15

    def __init__(self, device: str | None = None) -> None:
        self.device = "cpu"
        self.trouble: dict[str, str] = {}
        self._features = None

    def declare(self) -> dict[str, object]:
        return {
            "slug": self.slug,
            "needs": list(self.needs),
            "invariant": list(self.invariant),
            "keys": list(self.keys()),
            "names": dict(ANSWERS),
            "calls": {
                name: [f"features_{own.rsplit('_', 1)[-1]}"] for name, own in ANSWERS.items()
            },
            "min_pixels_per_vessel": self.MIN_PIXELS_PER_VESSEL,
            "absent": list(ABSENT),
            "units": {"every measurement": "px"},
            "device": self.device,
            "upstream": upstream.provenance(),
        }

    def identity(self) -> str:
        return str(upstream.COMMIT)

    def keys(self) -> tuple[str, ...]:
        return tuple(ANSWERS)

    def measure(
        self,
        artery: np.ndarray | None,
        vein: np.ndarray | None,
        fov: np.ndarray,
        disc: tuple[float, float, float],
        um_per_px: float | None,
    ) -> dict[str, float | None]:
        """Its six features per map, under catalogued names, with `None` where it could not."""
        self.trouble = {}
        computed: dict[str, float | None] = dict.fromkeys(ANSWERS.values())
        maps = {
            "artery": artery,
            "vein": vein,
            "vessels": None if artery is None and vein is None else _union(artery, vein),
        }
        for measured, mask in maps.items():
            if mask is None or not mask.any():
                continue
            try:
                found = self._loaded_features()(np.asarray(mask, dtype=self.DTYPE)[:, :, None])
            except Exception as failure:  # noqa: BLE001 — a measurement that fell over has no value
                self.trouble[f"features_{measured}"] = repr(failure)
                continue
            for column, value in found.items():
                computed[f"{column}_{measured}"] = _number(value)
        return {answered: computed.get(own) for answered, own in ANSWERS.items()}

    def _loaded_features(self):
        if self._features is None:
            self._features = upstream.features().Vessel_Features(
                min_pixels_per_vessel=self.MIN_PIXELS_PER_VESSEL
            )
        return self._features

    def release(self) -> None:
        self._features = None


def _union(artery: np.ndarray | None, vein: np.ndarray | None) -> np.ndarray:
    parts = [np.asarray(part) > 0 for part in (artery, vein) if part is not None]
    return parts[0] if len(parts) == 1 else parts[0] | parts[1]


def _number(value: object) -> float | None:
    """One finite number, or nothing. A NaN is not a measurement and is not recorded as one."""
    try:
        found = float(value)
    except (TypeError, ValueError):
        return None
    return None if not np.isfinite(found) else found


def implementation(**arguments: object) -> Automorphclass:
    return Automorphclass(**arguments)
