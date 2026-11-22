# ABOUTME: AutoMorphalyzer's rewritten measuring code, reached from this repository: one call per
# ABOUTME: vessel map, and the table saying which catalogued biomarker each of its columns answers to.

import numpy as np

from biomarkers.utils.masks import disc_mask as circle
from upstreams import automorphalyzer as upstream

#: The three maps it measures, and the structure each answers for. It measures the union as well as
#: the two classes, so the adapter forms that union itself rather than taking one as given.
CLASSES = {"binary": "vessels", "artery": "artery", "vein": "vein"}

#: The zones it measures in, as `generate_zonal_masks` builds them — and what each one *is*, which
#: is the fact that decides whether a number is comparable with anybody else's.
#:
#: *Our finding, 2026-09-21, from reading `generate_zonal_masks`:* zone **B is the annulus between
#: two and three disc radii**, which is exactly the region PVBM measures its equivalents over
#: (PVBM builds it as zone C minus zone B). Zone **C is two to five radii**.
#:
#: *Updated 2026-11-19:* that C was called "nobody else's region" until the vocabulary gained one.
#: The catalogue's `C` is Cheung et al. 2010's Extended zone, 0.5 to 2.0 disc diameters from the
#: margin, which is two to five radii from the centre (`docs/biomarkers/regions-of-interest.md`
#: §4) — this zone exactly. So both zones are catalogued, each under its own region.
ZONES = ("whole", "B", "C")
CATALOGUED_ZONES = ("B", "C")

#: What it computes over the **whole image**, and the catalogued biomarker each answers to.
#: `{side}` becomes `artery`, `vein` or `vessels`.
WHOLE: dict[str, str | None] = {
    "fractal_dimension": "density/box-counting/{side}",
    # Vessel pixels over *every* pixel of the frame, lit or not — `vessel_metrics` divides by
    # `vessels.shape[0] * vessels.shape[1]` and never sees a field of view.
    "vessel_density": "density/over-image/{side}",
    # Vessel area over skeleton length: a width weighted by how much vessel carries it.
    "average_global_calibre": "calibre/width/{side}/length-weighted",
    # Both are summed over vessels and divided by `vessel_count` in `measure.py`, so both are
    # means rather than medians.
    "tortuosity_distance": "tortuosity/hart-tau1/{side}/mean",
    "tortuosity_density": "tortuosity/grisan-density/{side}/mean",
    # *Our finding, from `measure.py`:* also a length-weighted width — `np.mean` over every
    # width sample along every vessel — differing from `average_global_calibre` by excluding
    # branch points rather than by how it weights. The vocabulary separates statistics, not
    # junction-handling, so the two cannot be told apart by name and this one stays unmapped.
    "average_local_calibre": None,
    "CRAE_Knudtson": None,
    "CRVE_Knudtson": None,
}

#: What it computes **inside a zone**, over both catalogued zones. `{side}` becomes `artery`,
#: `vein` or `vessels` and `{zone}` becomes `B` or `C`; a template naming one class outright answers
#: for that class alone — the CRAE column over the vein map is a different number, not a venular
#: equivalent.
ZONAL: dict[str, str | None] = {
    "CRAE_Knudtson": "calibre/CRE-knudtson/artery/{zone}",
    "CRVE_Knudtson": "calibre/CRE-knudtson/vein/{zone}",
    # Catalogued since the vocabulary carried a region: the same measure as the whole-image
    # column, over the annulus, pooled the same way.
    "tortuosity_distance": "tortuosity/hart-tau1/{side}/{zone}/mean",
    "tortuosity_density": "tortuosity/grisan-density/{side}/{zone}/mean",
    "average_local_calibre": None,
}

#: The arteriovenous ratios its full run writes, `AVR_B` and `AVR_C`, which no measuring call
#: returns: `merge_results` divides the zone's artery-map CRAE by its vein-map CRVE as it writes the
#: table, and records any negative ratio as failed. *Added 2026-11-22, when an audit of its
#: `feature_measurements.csv` found them missing here.* The division is reproduced as it ships,
#: including its one quirk: when both equivalents failed, both are −1 and the ratio is a positive 1,
#: which it keeps.
RATIOS: dict[str, tuple[str, str, str]] = {
    f"AVR_{zone}": (
        f"CRAE_Knudtson@{zone}_artery",
        f"CRVE_Knudtson@{zone}_vein",
        f"calibre/AVR-knudtson/both/{zone}",
    )
    for zone in ("B", "C")
}

#: What `get_disc_metrics` returns from a disc mask, a cup mask and the vessel map, and the
#: catalogued biomarker each answers to. *Our finding, 2026-11-22, from `measure.py`:* each ratio
#: is the cup's bounding-box extent over the disc's along the image's rows or columns, an extent
#: being the last lit index minus the first. Unlike AutoMorph and AutoMorphClass it computes the
#: ratios **before** its sense checks and returns them whether or not those pass; the checks only
#: decide `macular_centred`, which is True unless the disc passes them and sits within a tenth of
#: the frame of its centre. `laterality` is a word, from which side of the cup has more vessel.
#: The cup's centre has no canonical name: it is a pixel position.
#: *Mapped 2026-11-22:* the four extents are the disc's and cup's vertical and horizontal
#: diameters, which the catalogue now names; they are returned in pixels of the frame handed
#: over and converted once by `canonical.from_pixels`, as every length here is.
#:
#: *Mapped 2026-11-22:* `macular_centred` is **three**-valued, not a yes or no — True, False, or −1
#: where `get_disc_metrics` fell over — and those are the catalogue's `macula`, `disc` and
#: `unknown`, by the same rule the shapes' ground truth uses: the disc within a tenth of the frame
#: of its centre. It is answered in the catalogue's words (`_centring`), the one value this adapter
#: re-spells; a category has no unit, so nothing is converted. One difference stays: a disc that
#: fails the sense checks reads `macula` upstream where `unknown` would be the honest answer.
DISC_COLUMNS: dict[str, str | None] = {
    "CDR_vertical": "landmarks/CDR-vertical",
    "CDR_horizontal": "landmarks/CDR-horizontal",
    "disc_height": "landmarks/disc-diameter-vertical",
    "disc_width": "landmarks/disc-diameter-horizontal",
    "cup_height": "landmarks/cup-diameter-vertical",
    "cup_width": "landmarks/cup-diameter-horizontal",
    "cup_centre_x": None,
    "cup_centre_y": None,
    "macular_centred": "landmarks/centring",
    "laterality": None,
}

#: Where the structure sits in a catalogued name, so a mapping that names one class outright can
#: be told from one that answers for whichever class it was computed on.
_STRUCTURE = 2

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
                if not mapped or zone not in CATALOGUED_ZONES:
                    pairs[own] = own
                    continue
                # An equivalent is named for the class it measures, so the artery column only
                # answers for arteries; the same column over the vein map is a different number.
                wants = mapped.split("/")[_STRUCTURE]
                if wants != "{side}" and wants != side:
                    pairs[own] = own
                else:
                    pairs[mapped.format(side=side, zone=zone)] = own
    for own, (_, _, mapped) in RATIOS.items():
        pairs[mapped] = own
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
        r"average_local_calibre@whole_(?P<side>binary|artery|vein)",
        "calibre/width/{side}/length-weighted",
        (
            "a mean over every width sample along every vessel, branch points left out; "
            "`average_global_calibre` is the column named this"
        ),
    ),
    (
        r"average_local_calibre@(?P<zone>B|C)_(?P<side>binary|artery|vein)",
        "calibre/width/{side}/{zone}/length-weighted",
        "a mean over every width sample along every vessel in the zone, branch points left out",
    ),
    (
        r"CRAE_Knudtson@whole_(?P<side>binary|artery|vein)",
        "calibre/CRE-knudtson/artery/B",
        "computed over the whole frame on the {side} map; an equivalent is defined in a zone",
    ),
    (
        r"CRVE_Knudtson@whole_(?P<side>binary|artery|vein)",
        "calibre/CRE-knudtson/vein/B",
        "computed over the whole frame on the {side} map; an equivalent is defined in a zone",
    ),
    (
        r"CRAE_Knudtson@(?P<zone>B|C)_(?P<side>binary|vein)",
        "calibre/CRE-knudtson/artery/{zone}",
        "Knudtson's arterial pairing applied to the {side} map, which upstream drops from its table",
    ),
    (
        r"CRVE_Knudtson@(?P<zone>B|C)_(?P<side>binary|artery)",
        "calibre/CRE-knudtson/vein/{zone}",
        "Knudtson's venular pairing applied to the {side} map, which upstream drops from its table",
    ),
    (
        r"cup_centre_[xy]",
        None,
        "a pixel position; the catalogue has no position for the cup",
    ),
    (
        r"laterality",
        None,
        "which eye, a word, inferred from where the vessels are; no canonical name",
    ),
)
CLOSEST_WORDS = {
    "side": {"binary": "vessels", "artery": "artery", "vein": "vein"},
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
        self._returned: dict[str, object] = {}

    def declare(self) -> dict[str, object]:
        return {
            "slug": self.slug,
            "needs": list(self.needs),
            "invariant": list(self.invariant),
            "keys": list(self.keys()),
            "names": dict(CANONICAL),
            "calls": {
                own: [
                    "disc_and_cup"
                    if own in DISC_COLUMNS
                    else "merge_results"
                    if own in RATIOS
                    else f"measure_{own.rsplit('_', 1)[-1]}"
                ]
                for own in CANONICAL
            },
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
        cup: np.ndarray | None = None,
    ) -> dict[str, float | None]:
        """Everything it computes, under catalogued names, with `None` where it could not."""
        self.trouble = {}
        self._returned: dict[str, object] = {}
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
        for own, (top, bottom, _) in RATIOS.items():
            computed[own] = _ratio(self._returned.get(top), self._returned.get(bottom))
        if cup is not None and maps["binary"] is not None:
            computed.update(self._disc_and_cup(disc_mask, cup, maps["binary"]))
        return {own: computed.get(own) for own in CANONICAL}

    def _disc_and_cup(self, disc_mask, cup, vessels) -> dict[str, float | str | None]:
        """Its disc metrics, as its own driver calls them: disc, cup, and the union of the vessels."""
        try:
            found = self._loaded_measure().get_disc_metrics(
                np.asarray(disc_mask, dtype=self.DTYPE),
                np.asarray(cup, dtype=self.DTYPE),
                np.asarray(vessels, dtype=self.DTYPE),
            )
        except Exception as failure:  # noqa: BLE001 — a measurement that fell over has no value
            self.trouble["disc_and_cup"] = repr(failure)
            return {}
        kept: dict[str, float | str | None] = {}
        for column in DISC_COLUMNS:
            value = found.get(column)
            if column == "macular_centred":
                kept[column] = _centring(value)
                continue
            kept[column] = value if isinstance(value, str) else _number(value)
        return kept

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
                # What it returned, sentinel and all, for the ratios `merge_results` derives.
                self._returned[f"{column}@{zone}_{measured}"] = value
        return found

    @staticmethod
    def _disc_mask(side: int, x: float, y: float, radius: float) -> np.ndarray:
        """The disc as a filled circle. Its tracer wants a mask, not a centre and a radius."""
        return circle(side, x, y, radius)

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


def _ratio(artery: object, vein: object) -> float | None:
    """`merge_results`'s ratio: CRAE over CRVE as returned, and no ratio where that is negative."""
    try:
        found = float(artery) / float(vein)
    except (TypeError, ValueError, ZeroDivisionError):
        return None
    return found if np.isfinite(found) and found >= 0 else None


def _centring(value: object) -> str:
    """`macular_centred` in the catalogue's words. The −1 sentinel is checked first: it is truthy,
    and True compares equal to 1, so a yes-or-no test alone would read a failure as `macula`."""
    if value is None or (not isinstance(value, (bool, np.bool_)) and value == FAILED):
        return "unknown"
    return "macula" if bool(value) else "disc"


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
