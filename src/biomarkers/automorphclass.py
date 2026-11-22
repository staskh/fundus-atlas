# ABOUTME: AutoMorphClass's feature calculation, reached from this repository: one call per vessel
# ABOUTME: map, and the table saying which catalogued biomarker each of its columns answers to.

import numpy as np

from biomarkers.utils.masks import disc_mask
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
    "vessel_density": "density/over-image/{side}",
    "fractal_dimension": "density/box-counting/{side}",
    # `np.sum(Z) / np.sum(Z_skeleton)`: area over skeleton length, a length-weighted width.
    "average_width": "calibre/width/{side}/length-weighted",
    # *Our finding, from `_tortuosity_per_window`:* `len_weighted=True` is its default, so each
    # vessel contributes in proportion to its own curve length. AutoMorph and AutoMorphalyzer
    # divide by the vessel count instead, which makes these **different statistics of the same
    # measurement** and is part of why the three disagree on one picture.
    "distance_tortuosity": "tortuosity/hart-tau1/{side}/length-weighted",
    # *Our finding, 2026-09-21:* **not** Hart's τ3, despite the name. `squared_curvature_tortuosity`
    # squares nothing: it accumulates discrete curvature at each sample and integrates it over the
    # sample *index* rather than over arc length. It was mapped to τ3 until the shapes disagreed by
    # five orders of magnitude, and it does not match τ2 either — its ratio to the total curvature
    # is 10.3 on the arc and 2.0 on the sinusoid, so no constant relates them. Discrete curvature
    # on a pixel skeleton is its own quantity and the catalogue has no name for it.
    "squared_curvature_tortuosity": None,
    "tortuosity_density": "tortuosity/grisan-density/{side}/length-weighted",
}

#: What `Optic_Disc_Cup_Features` returns from a disc mask and a cup mask, and the catalogued
#: biomarker each answers to. *Our finding, 2026-11-22, from `optic_cup_features`:* each ratio is
#: the cup's bounding-box extent over the disc's along the image's rows or columns, an extent being
#: the last lit index minus the first — one pixel short of the number of pixels spanned. The four
#: extents are pixel sizes, which no canonical name holds.
#:
#: It answers **-1 for every column** when its sense checks fail (a disc wider than a third of the
#: frame, a cup centred outside the disc's box, a cup not smaller than the disc). That is how it
#: says it declined, so the adapter reads -1 as no answer and records why, rather than storing -1
#: as a cup-to-disc ratio.
DISC_COLUMNS: dict[str, str | None] = {
    "cdr_vertical": "landmarks/CDR-vertical",
    "cdr_horizontal": "landmarks/CDR-horizontal",
    "disc_width": None,
    "disc_height": None,
    "cup_width": None,
    "cup_height": None,
}

#: The zones its full pipeline measures, as `AutoMorphModel.define_zones` cuts them about the disc's
#: centroid, the radius being half the larger of its two bounding-box extents. *Our finding,
#: 2026-11-19, from `main.py`:* **zone B is two to three disc radii**, the catalogue's B, but its
#: **zone C is three to five** — a ring outside B rather than the catalogue's two-to-five, so its
#: zone-C columns stay under its own names. *Measured here since 2026-11-22*, when an audit found
#: these 36 columns of its run missing from this adapter.
ZONES: dict[str, str | None] = {"ZoneB": "B", "ZoneC": None}

#: The same six inside a catalogued zone. Vessel density there is the zone's vessel pixels over the
#: whole frame, a denominator no catalogued density has.
ZONE_COLUMNS: dict[str, str | None] = {
    "vessel_density": None,
    "fractal_dimension": "density/box-counting/{side}/{zone}",
    "average_width": "calibre/width/{side}/{zone}/length-weighted",
    "distance_tortuosity": "tortuosity/hart-tau1/{side}/{zone}/length-weighted",
    "squared_curvature_tortuosity": None,
    "tortuosity_density": "tortuosity/grisan-density/{side}/{zone}/length-weighted",
}

#: It computes **no central retinal equivalents**: `main.py` ends `# todo: add calibre features`.
ABSENT = (
    "calibre/CRE-knudtson",
    "calibre/CRE-hubbard",
    "calibre/AVR-knudtson",
    "calibre/AVR-hubbard",
)

#: The prefixes `forward` gives each map's features, against this adapter's names for the maps.
PREFIXES = {"Vessel": "vessels", "Artery": "artery", "Vein": "vein"}

#: The columns that are lengths, measured on its 912 × 912 maps and scaled here to pixels of the
#: frame handed over. The rest are ratios, counts or dimensions and need nothing.
LENGTHS = ("average_width", "disc_width", "disc_height", "cup_width", "cup_height")


def _zone_suffix(zone: str) -> str:
    return "_zone_" + zone[-1].lower()


def _answers() -> dict[str, str]:
    """Answered name → its own column: `<column>_<class>` over the whole picture,
    `<column>_<class>_zone_<b|c>` inside a zone, and the disc and cup columns under their own
    names, since they measure no vessel class."""
    pairs: dict[str, str] = {}
    for measured, side in CLASSES.items():
        for column, mapped in COLUMNS.items():
            own = f"{column}_{measured}"
            pairs[mapped.format(side=side) if mapped else own] = own
    for zone, catalogued in ZONES.items():
        for measured, side in CLASSES.items():
            for column, mapped in ZONE_COLUMNS.items():
                own = f"{column}_{measured}{_zone_suffix(zone)}"
                named = mapped and catalogued
                pairs[mapped.format(side=side, zone=catalogued) if named else own] = own
    for column, mapped in DISC_COLUMNS.items():
        pairs[mapped or column] = column
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


#: For each column with no canonical name, the nearest one and what keeps it from being that name.
#: Rendered into the project page's list of every column it writes (`python -m biomarkers.pages`).
#: A close name is a pointer for a reader, never a mapping: nothing is compared against it, and a
#: column moves into the naming table above only when the shapes can test it. Patterns are matched
#: against the whole of the column's own name; a column no rule matches has nothing near.
CLOSEST = (
    (
        r"average_width_(?P<side>vessels|artery|vein)_zone_c",
        "calibre/width/{side}/C/length-weighted",
        "its zone C is 3 to 5 disc radii; the catalogue's C is 2 to 5",
    ),
    (
        r"distance_tortuosity_(?P<side>vessels|artery|vein)_zone_c",
        "tortuosity/hart-tau1/{side}/C/length-weighted",
        "its zone C is 3 to 5 disc radii; the catalogue's C is 2 to 5",
    ),
    (
        r"tortuosity_density_(?P<side>vessels|artery|vein)_zone_c",
        "tortuosity/grisan-density/{side}/C/length-weighted",
        "its zone C is 3 to 5 disc radii; the catalogue's C is 2 to 5",
    ),
    (
        r"fractal_dimension_(?P<side>vessels|artery|vein)_zone_c",
        "density/box-counting/{side}/C",
        "its zone C is 3 to 5 disc radii; the catalogue's C is 2 to 5",
    ),
    (
        r"vessel_density_(?P<side>vessels|artery|vein)_zone_(?P<zone>[bc])",
        "density/over-image/{side}/{zone}",
        "the zone's vessel pixels over every pixel of the 912 × 912 frame, not over the zone",
    ),
    (
        r"squared_curvature_tortuosity_(?P<side>vessels|artery|vein)",
        "tortuosity/hart-tau3/{side}/length-weighted",
        (
            "named for Hart's τ3, the integral of squared curvature; it integrates curvature over the "
            "sample index instead, and is out by orders of magnitude on the shapes"
        ),
    ),
    (
        r"squared_curvature_tortuosity_(?P<side>vessels|artery|vein)_zone_(?P<zone>[bc])",
        "tortuosity/hart-tau3/{side}/{zone}/length-weighted",
        "as the whole-picture column, inside its zone {zone}",
    ),
    (
        r"(disc|cup)_(height|width)",
        None,
        "a bounding-box extent; the catalogue has no disc or cup size",
    ),
)
CLOSEST_WORDS = {
    "side": {"vessels": "vessels", "artery": "artery", "vein": "vein"},
    "zone": {"b": "B", "c": "C"},
}


class Automorphclass:
    """AutoMorphClass, run through its own pipeline's `forward`.

    `AutoMorphModel.forward` is what its full run calls: it resizes every mask to 912 × 912 with
    nearest neighbour, measures the disc and cup, cuts zones B and C from the disc, measures the six
    vessel features on nine maps — the vessels, the arteries and the veins, whole and in each zone —
    and sets every zone column to −1 where the disc failed its sense checks. Handed all three masks,
    it runs none of its three segmentation networks, so the module is made without its constructor,
    which would load their weights for nothing; the two feature calculators are set exactly as the
    constructor sets them. *Changed 2026-11-22:* until then the six features were called directly on
    the full-size map, and its zones were not measured at all.

    Lengths come back in 912-pixels and are scaled to pixels of the frame handed over (`LENGTHS`).
    """

    slug = "automorphclass"
    needs = ("artery", "vein")
    invariant = ("rotation",)

    #: The size `forward` resizes every mask to (`_resize_to_920`, which resizes to 912).
    WORKING_SIZE = 912

    def __init__(self, device: str | None = None) -> None:
        self.device = "cpu"
        self.trouble: dict[str, str] = {}
        self._model = None

    def declare(self) -> dict[str, object]:
        return {
            "slug": self.slug,
            "needs": list(self.needs),
            "invariant": list(self.invariant),
            "keys": list(self.keys()),
            "names": dict(CANONICAL),
            "calls": {own: ["AutoMorphModel.forward"] for own in CANONICAL},
            "zones": {"B": "2 to 3 disc radii", "C": "3 to 5 disc radii"},
            "working_size": self.WORKING_SIZE,
            "absent": list(ABSENT),
            "units": {
                "lengths": "px of the frame handed over, scaled from its 912 × 912 maps",
                "everything else": "as returned",
            },
            "device": self.device,
            "upstream": upstream.provenance(),
        }

    def identity(self) -> str:
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
        cup: np.ndarray | None = None,
    ) -> dict[str, float | None]:
        """Everything its pipeline writes for one picture, under its own names."""
        import torch

        self.trouble = {}
        computed: dict[str, float | None] = dict.fromkeys(CANONICAL)
        given = {"artery": artery, "vein": vein}
        present = {name for name, mask in given.items() if mask is not None and np.any(mask)}
        if not present:
            return computed
        shape = next(np.asarray(m).shape for m in given.values() if m is not None)
        blank = np.zeros(shape, dtype=bool)
        artery_ = np.asarray(artery) > 0 if artery is not None else blank
        vein_ = np.asarray(vein) > 0 if vein is not None else blank
        hollow = np.asarray(cup) > 0 if cup is not None else blank
        whole_disc = disc_mask(shape[1], *(float(value) for value in disc))[: shape[0]]

        def tensor(*planes: np.ndarray):
            return torch.from_numpy(np.stack(planes).astype(np.float32))[None]

        try:
            found = self._loaded_model()(
                torch.zeros((1, 3, *shape)),
                vessel_masks=tensor(artery_ | vein_),
                optic_disc_masks=tensor(whole_disc, hollow),
                artery_vein_masks=tensor(artery_, vein_),
            )
        except Exception as failure:  # noqa: BLE001 — a measurement that fell over has no value
            self.trouble["forward"] = repr(failure)
            return computed

        scale = shape[1] / self.WORKING_SIZE
        disc_values = {column: _number(found[column]) for column in DISC_COLUMNS if column in found}
        declined = all(value == -1 for value in disc_values.values())
        if declined:
            self.trouble["disc_and_cup"] = "answered -1 everywhere: its sense checks declined"
        for key, value in found.items():
            number = _number(value)
            own = self._own(key)
            if own is None or own not in computed:
                continue
            if number is None or (number == -1 and (declined or "_zone_" in own)):
                continue
            if own.startswith(LENGTHS):
                number *= scale
            computed[own] = number
        for name in ("artery", "vein"):
            if name not in present:
                for own in computed:
                    if own.endswith(f"_{name}") or f"_{name}_zone_" in own:
                        computed[own] = None
        return computed

    @staticmethod
    def _own(key: str) -> str | None:
        """`ZoneB_Artery_average_width` → `average_width_artery_zone_b`; disc columns as they are."""
        if key in DISC_COLUMNS:
            return key
        zone = None
        if key.startswith(tuple(ZONES)):
            zone, _, key = key.partition("_")
        prefix, _, column = key.partition("_")
        if prefix not in PREFIXES:
            return None
        return f"{column}_{PREFIXES[prefix]}" + (_zone_suffix(zone) if zone else "")

    def _loaded_model(self):
        if self._model is None:
            import torch

            main = upstream.main()
            features = upstream.features()
            model = main.AutoMorphModel.__new__(main.AutoMorphModel)
            torch.nn.Module.__init__(model)
            model.include_zones = True
            model.include_artery_vein = True
            model.include_optic_disc = True
            model.optic_disc_cup_feature_calculator = features.AutoMorphNumpyWrapper(
                features.Optic_Disc_Cup_Features(), num_channels=2, return_masks=True
            )
            model.vessel_feature_calculator = features.AutoMorphNumpyWrapper(
                features.Vessel_Features(), num_channels=1
            )
            model.return_as_tensor = False
            model.savemask_path = None
            model.eval()
            self._model = model
        return self._model

    def release(self) -> None:
        self._model = None


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
