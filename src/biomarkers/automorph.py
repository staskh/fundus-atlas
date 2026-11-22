# ABOUTME: AutoMorph's measuring stage, reached from this repository: its M2 hand-off, its disc and
# ABOUTME: zone driver and both of its retipy copies, and the table saying what each column answers to.

import tempfile
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
from PIL import Image

from biomarkers.utils.masks import disc_mask as circle
from upstreams import automorph as upstream

#: The three maps it is asked to measure, and the structure each answers for.
CLASSES = {"binary": "vessels", "artery": "artery", "vein": "vein"}

#: The two zones its zone stage measures, as `optic_disc_centre` cuts them: **B is the annulus
#: from two to three disc radii and C from two to five**, about the disc-and-cup's centroid, with
#: the radius taken as half the larger of the disc's two bounding-box extents. Both are catalogued
#: regions (`docs/biomarkers/regions-of-interest.md`), which AutoMorphalyzer's zones are too.
ZONES = ("B", "C")

#: What `evaluate_window` returns first, in order, in both stages, and the catalogued biomarker
#: each answers to over the **whole picture**. `{side}` becomes `artery`, `vein` or `vessels`.
#:
#: These are the same six quantities AutoMorphalyzer and AutoMorphClass compute, which is what
#: makes the three comparable: both descend from this code.
COLUMNS: tuple[tuple[str, str | None], ...] = (
    ("fractal_dimension", "density/box-counting/{side}"),
    # Vessel pixels over every pixel of the frame — `vessel_density` never sees a field of view.
    ("vessel_density", "density/over-image/{side}"),
    # *Our finding, from `tortuosity_measures.py`:* `average_caliber = vessel_total_count /
    # tcurve` — vessel pixels over total curve length, which is a width weighted by how much
    # vessel carries it rather than a plain mean over vessels.
    ("average_width", "calibre/width/{side}/length-weighted"),
    # *Our finding, from the same file:* `t2` is summed over vessels and divided by
    # `vessel_count`, so it is a **mean** and not a median. AutoMorphClass, from the same
    # lineage, weights by length instead — which is why the three disagree.
    ("distance_tortuosity", "tortuosity/hart-tau1/{side}/mean"),
    # *Our finding, 2026-09-21:* **not** Hart's τ3, despite the name. `squared_curvature_tortuosity`
    # squares nothing: it accumulates discrete curvature at each sample and integrates it over the
    # sample *index* rather than over arc length. It was mapped to τ3 until the shapes disagreed by
    # five orders of magnitude, and it does not match τ2 either — its ratio to the total curvature
    # is 10.3 on the arc and 2.0 on the sinusoid, so no constant relates them. Discrete curvature
    # on a pixel skeleton is its own quantity and the catalogue has no name for it.
    ("squared_curvature_tortuosity", None),
    ("tortuosity_density", "tortuosity/grisan-density/{side}/mean"),
)

#: The same six **inside a zone**, from the zone stage's own retipy over a map already cut to the
#: annulus. `{zone}` becomes `B` or `C`.
ZONE_COLUMNS: dict[str, str | None] = {
    "fractal_dimension": "density/box-counting/{side}/{zone}",
    # *Our finding, 2026-11-22:* the vessel pixels **inside the zone** over every pixel of the
    # 912 × 912 frame, not over the zone's area — `vessel_density` divides by the window's size,
    # and the window is the whole picture with everything outside the annulus blacked out. No
    # catalogued density has that denominator, so it stays under its own name.
    "vessel_density": None,
    "average_width": "calibre/width/{side}/{zone}/length-weighted",
    "distance_tortuosity": "tortuosity/hart-tau1/{side}/{zone}/mean",
    "squared_curvature_tortuosity": None,
    "tortuosity_density": "tortuosity/grisan-density/{side}/{zone}/mean",
}

#: The central retinal equivalents, which only the zone stage computes: `evaluate_window` there
#: returns all four on every map, and the zone drivers keep the **arterial ones from the artery map
#: and the venular ones from the vein map** and discard the rest. The ratios are the drivers' own
#: arithmetic, `Data4stage2['AVR_Hubbard'] = CRAE_Hubbard / CRVE_Hubbard`, done here the same way.
#: Each is under AutoMorph's own name, with the zone suffix its merged CSV gives it.
#:
#: *Our finding, 2026-11-22, from `tortuosity_measures.py` in the zone stage:* Hubbard's formula
#: there carries its micron constants (−10.76 for arteries, +450.05 for veins), applied to widths
#: already multiplied by the image's `Scale_resolution` — so it is right when that scale is in
#: microns, which is how AutoMorph's own run writes it and how this adapter writes it.
EQUIVALENTS: dict[str, tuple[str, int, str]] = {
    # own name: (the map it is read from, its index in what `evaluate_window` returns, canonical)
    "CRAE_Hubbard": ("artery", 9, "calibre/CRE-hubbard/artery/{zone}"),
    "CRVE_Hubbard": ("vein", 10, "calibre/CRE-hubbard/vein/{zone}"),
    "CRAE_Knudtson": ("artery", 11, "calibre/CRE-knudtson/artery/{zone}"),
    "CRVE_Knudtson": ("vein", 12, "calibre/CRE-knudtson/vein/{zone}"),
}
RATIOS: dict[str, tuple[str, str, str]] = {
    "AVR_Hubbard": ("CRAE_Hubbard", "CRVE_Hubbard", "calibre/AVR-hubbard/both/{zone}"),
    "AVR_Knudtson": ("CRAE_Knudtson", "CRVE_Knudtson", "calibre/AVR-knudtson/both/{zone}"),
}

#: What `optic_disc_centre` writes into `Disc_cup_results.csv`, under its own column names. Each
#: ratio is the cup's bounding-box extent over the disc's along one image axis, an extent being the
#: last lit index minus the first, on the disc and cup resized to 912 — the formula AutoMorphClass
#: kept. Its sense checks (a disc under a third of the frame, the cup's centre inside the disc's
#: box, the cup smaller both ways) decide whether **any** of this, the zones included, is written:
#: where they fail, every column is −1 and no zone is cut.
#: *Mapped 2026-11-22:* the four extents are the disc's and cup's vertical and horizontal
#: diameters, which the catalogue now names; they are returned in pixels of the frame handed
#: over and converted once by `canonical.from_pixels`, as every length here is.
DISC_COLUMNS: dict[str, str | None] = {
    "Disc_height": "landmarks/disc-diameter-vertical",
    "Disc_width": "landmarks/disc-diameter-horizontal",
    "Cup_height": "landmarks/cup-diameter-vertical",
    "Cup_width": "landmarks/cup-diameter-horizontal",
    "CDR_vertical": "landmarks/CDR-vertical",
    "CDR_horizontal": "landmarks/CDR-horizontal",
}

#: The columns AutoMorph multiplies by the image's scale, and so returns in microns. The adapter
#: hands back pixels of the frame it was given, as every adapter here does, by dividing by the
#: scale it was handed; `canonical.from_pixels` then converts them once, for everybody.
IN_MICRONS = ("average_width", "CRAE_", "CRVE_", "Disc_", "Cup_")

#: Hubbard's equivalents need widths in microns, because its constants are. Without a scale there
#: are none, and neither is the ratio of the two.
NEEDS_MICRONS = ("CRAE_Hubbard", "CRVE_Hubbard", "AVR_Hubbard")

#: What it signals when a measurement could not be made, in every column of every driver.
FAILED = -1


def _zone_suffix(zone: str) -> str:
    return f"_zone_{zone.lower()}"


def _answers() -> dict[str, str]:
    """Answered name → its own column name.

    A name carrying a `/` is a catalogued biomarker and a name without one is AutoMorph's own, kept
    because the catalogue cannot name that quantity yet.
    """
    pairs: dict[str, str] = {}
    for measured, side in CLASSES.items():
        for column, mapped in COLUMNS:
            own = f"{column}_{measured}"
            pairs[mapped.format(side=side) if mapped else own] = own
    for zone in ZONES:
        for measured, side in CLASSES.items():
            for column, mapped in ZONE_COLUMNS.items():
                own = f"{column}_{measured}{_zone_suffix(zone)}"
                pairs[mapped.format(side=side, zone=zone) if mapped else own] = own
        for own, (_, _, mapped) in EQUIVALENTS.items():
            pairs[mapped.format(zone=zone)] = own + _zone_suffix(zone)
        for own, (_, _, mapped) in RATIOS.items():
            pairs[mapped.format(zone=zone)] = own + _zone_suffix(zone)
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
        r"squared_curvature_tortuosity_(?P<side>binary|artery|vein)",
        "tortuosity/hart-tau3/{side}/mean",
        (
            "named for Hart's τ3, the integral of squared curvature; it integrates curvature over the "
            "sample index instead, and is out by orders of magnitude on the shapes"
        ),
    ),
    (
        r"squared_curvature_tortuosity_(?P<side>binary|artery|vein)_zone_(?P<zone>[bc])",
        "tortuosity/hart-tau3/{side}/{zone}/mean",
        "as the whole-picture column, inside zone {zone}",
    ),
    (
        r"vessel_density_(?P<side>binary|artery|vein)_zone_(?P<zone>[bc])",
        "density/over-image/{side}/{zone}",
        "the zone's vessel pixels over every pixel of the 912 × 912 frame, not over the zone",
    ),
)
CLOSEST_WORDS = {
    "side": {"binary": "vessels", "artery": "artery", "vein": "vein"},
    "zone": {"b": "B", "c": "C"},
}


class Automorph:
    """AutoMorph's measuring stage, run as its `run.sh` runs it.

    AutoMorph is a pipeline of scripts that pass files to each other, so each call lays out the
    tree those scripts read and write — `Results/M0`, `Results/M2`, `Results/M3` — in a temporary
    directory, and runs the steps after segmentation on it in their order:

    1. **The M2 hand-off.** `filter_frag` from each M2 stage, as shipped: the artery/vein one reads
       a colour map (red artery, blue vein, green where both), resizes it to 912 × 912 with nearest
       neighbour, drops specks under 30 pixels and skeletonises; the vessel one does the same to a
       912 × 912 vessel map. The adapter stands in for the networks only: it writes the masks it was
       handed where their predictions would be, the vessel map being the union of the two classes
       resized to 912 the same way.
    2. **The disc, the cup and the zones.** `optic_disc_centre` from the disc stage, as shipped,
       reads the disc-and-cup map (red the rim, blue the cup), measures both, decides whether the
       picture is disc- or macula-centred, removes the skeleton's branch points, and writes the
       maps cut to zones B and C.
    3. **The measuring.** The whole-picture stage's retipy over the M2 maps, and the zone stage's own
       retipy over the zone maps, each called as its driver calls it.

    *Changed 2026-11-22.* Until then this adapter wrote the mask it was handed at full size with a
    scale of 1, and let retipy resample it to 912 bicubically. That is not what AutoMorph measures —
    its M2 stage hands M3 a binary 912 map — and it returned widths in 912-pixels that the
    benchmark then read as pixels of the full frame, 2.25 times too small. It also measured with
    `evaluate_window`'s default thresholds rather than the `retipy.config` every driver reads.

    The scale written into `crop_info.csv` is **microns per 912-pixel**, which is what AutoMorph's
    own run writes there, so the widths, the equivalents and the disc sizes come back in microns and
    Hubbard's micron constants apply to microns. Those columns are divided by `um_per_px` on the way
    out (`IN_MICRONS`), into pixels of the frame handed over.
    """

    slug = "automorph"
    needs = ("artery", "vein")
    invariant = ("rotation",)

    #: The size AutoMorph's M2 stage hands every map to M3 at, and the window its drivers measure.
    WORKING_SIZE = 912

    #: The name each rendering is written under; any name works, as long as it is the same one in
    #: every folder and in `crop_info.csv`.
    NAME = "image.png"

    def __init__(self, device: str | None = None) -> None:
        self.device = "cpu"
        self.trouble: dict[str, str] = {}
        self._loaded: dict | None = None
        # Read once: reading it reaches the checkout, and that runs `git`, which has no business
        # inside every measurement — four runs side by side once collided on it.
        self._thresholds: dict | None = None

    def declare(self) -> dict[str, object]:
        config = self._config()
        return {
            "slug": self.slug,
            "needs": list(self.needs),
            "invariant": list(self.invariant),
            "keys": list(self.keys()),
            "names": dict(CANONICAL),
            "calls": {own: [_call(own)] for own in CANONICAL},
            "min_pixels_per_vessel": config["pixels_per_window"],
            "sampling_size": config["sampling_size"],
            "r2_threshold": config["r_2_threshold"],
            "working_size": self.WORKING_SIZE,
            "units": {
                "widths, equivalents, disc and cup sizes": "px of the frame handed over",
                "everything else": "as returned, measured on the 912 × 912 map",
            },
            "device": self.device,
            "upstream": upstream.CODE.provenance(),
        }

    def identity(self) -> str:
        return str(upstream.CODE.commit)

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
        """Everything AutoMorph's run writes for one picture, under its own names."""
        self.trouble = {}
        computed: dict[str, float | None] = dict.fromkeys(CANONICAL)
        given = {"artery": artery, "vein": vein}
        present = {name for name, mask in given.items() if mask is not None and np.any(mask)}
        if not present:
            return computed
        shape = next(np.asarray(m).shape for m in given.values() if m is not None)
        side = shape[1]
        # Microns per 912-pixel, as AutoMorph's run writes it; without a scale, pixels of the frame
        # handed over per 912-pixel, so that the lengths still come back in those pixels.
        scale = (um_per_px or 1.0) * side / self.WORKING_SIZE
        blank = np.zeros(shape, dtype=bool)
        artery_ = np.asarray(artery) > 0 if artery is not None else blank
        vein_ = np.asarray(vein) > 0 if vein is not None else blank
        maps = [
            name for name in ("binary", "artery", "vein") if name == "binary" or name in present
        ]

        with tempfile.TemporaryDirectory(prefix="automorph-") as where:
            data = Path(where)
            results = data / "Results"
            self._hand_off(results, artery_, vein_, disc, cup, scale, shape)
            centring = self._disc_and_zones(data, results, computed)
            for measured in maps:
                self._whole(results, measured, computed)
            if centring is not None:
                for zone in ZONES:
                    for measured in maps:
                        self._zone(results, centring, zone, measured, computed)

        for zone in ZONES:
            suffix = _zone_suffix(zone)
            for own, (top, bottom, _) in RATIOS.items():
                a, v = computed.get(top + suffix), computed.get(bottom + suffix)
                computed[own + suffix] = a / v if a is not None and v else None
        for own in list(computed):
            if computed[own] is None:
                continue
            if um_per_px is None and own.startswith(NEEDS_MICRONS):
                computed[own] = None
            elif um_per_px is not None and own.startswith(IN_MICRONS):
                computed[own] = computed[own] / um_per_px
        return {own: computed.get(own) for own in CANONICAL}

    # -- the steps -------------------------------------------------------------------------------

    def _hand_off(self, results, artery, vein, disc, cup, scale, shape) -> None:
        """Lay out what segmentation would have left, and run the M2 stages' `filter_frag`."""
        av = results / "M2" / "artery_vein"
        vessels = results / "M2" / "binary_vessel"
        discs = results / "M2" / "optic_disc_cup" / "resized"
        for folder in (
            results / "M0",
            av / "raw",
            av / "resized",
            vessels / "resize_binary",
            discs,
        ):
            folder.mkdir(parents=True, exist_ok=True)
        (results / "M0" / "crop_info.csv").write_text(
            f"Name,Scale_resolution\n{self.NAME},{scale!r}\n"
        )

        # The artery/vein network's prediction, as its stage saves it: red artery, blue vein, green
        # where the two cross. `filter_frag` reads it with `skimage.io` (RGB) and takes red or green
        # as artery and blue or green as vein.
        colour = np.zeros((*shape, 3), dtype=np.uint8)
        colour[..., 0] = (artery & ~vein) * 255
        colour[..., 1] = (artery & vein) * 255
        colour[..., 2] = (vein & ~artery) * 255
        for folder in ("raw", "resized"):
            Image.fromarray(colour).save(av / folder / self.NAME)

        # The vessel network's prediction, at the 912 its stage hands on; resized as the
        # artery/vein stage resizes its own.
        union = (artery | vein).astype(np.uint8) * 255
        small = cv2.resize(union, (self.WORKING_SIZE,) * 2, interpolation=cv2.INTER_NEAREST)
        Image.fromarray(small).save(vessels / "resize_binary" / self.NAME)

        # The disc-and-cup network's prediction, as `cv2.imwrite` saves it: channel 2 the rim, the
        # disc's class without the cup, and channel 0 the cup.
        x, y, radius = disc
        whole = circle(shape[1], x, y, radius)[: shape[0]]
        hollow = np.asarray(cup) > 0 if cup is not None else np.zeros(shape, dtype=bool)
        picture = np.zeros((*shape, 3), dtype=np.uint8)
        picture[..., 2] = (whole & ~hollow) * 255
        picture[..., 0] = hollow * 255
        cv2.imwrite(str(discs / self.NAME), picture)

        steps = self._steps()
        steps["av"]["filter_frag"](data_path=f"{av}/")
        steps["vessel"]["filter_frag"](f"{vessels}/")

    def _disc_and_zones(self, data, results, computed) -> str | None:
        """Run `optic_disc_centre`; record the disc columns, and say which zone folders it wrote."""
        driver = self._steps()["disc"]
        driver["AUTOMORPH_DATA"] = str(data)
        try:
            driver["optic_disc_centre"](
                f"{results}/M2/optic_disc_cup/resized/",
                f"{results}/M2/binary_vessel/",
                f"{results}/M2/artery_vein/",
            )
        except Exception as failure:  # noqa: BLE001 — a driver that fell over wrote nothing
            self.trouble["optic_disc_centre"] = repr(failure)
            return None
        for centring in ("Disc_centred", "Macular_centred"):
            table = pd.read_csv(results / "M3" / centring / "Disc_cup_results.csv")
            row = table[table["Name"] == self.NAME]
            if row.empty:
                continue
            for column in DISC_COLUMNS:
                computed[column] = _number(row[column].iloc[0])
            # The zones are written only where the disc passed the checks; the folder names say
            # which kind of picture the driver decided this was.
            return "disc" if centring == "Disc_centred" else "macula"
        return None

    def _whole(self, results, measured, computed) -> None:
        """The whole-picture stage, as `create_datasets_disc_centred.py` calls it."""
        folder = "binary_vessel" if measured == "binary" else "artery_vein"
        stem = "binary" if measured == "binary" else f"{measured}_binary"
        skeleton = results / "M2" / folder / f"{stem}_skeleton" / self.NAME
        store = results / "M2" / folder / f"{stem}_process"
        measures, retina = self._steps()["whole"]
        try:
            values = self._evaluate(measures, retina, skeleton, store)
        except Exception as failure:  # noqa: BLE001 — a measurement that fell over has no value
            self.trouble[f"evaluate_{measured}"] = repr(failure)
            return
        for (column, _), value in zip(COLUMNS, values, strict=False):
            computed[f"{column}_{measured}"] = _number(value)

    def _zone(self, results, centring, zone, measured, computed) -> None:
        """The zone stage, as `create_datasets_{disc,macular}_centred_{B,C}.py` call it."""
        folder = "binary_vessel" if measured == "binary" else "artery_vein"
        prefix = (
            f"Zone_{zone}_disc_centred_" if centring == "disc" else f"macular_Zone_{zone}_centred_"
        )
        skeleton = results / "M2" / folder / f"{prefix}{measured}_skeleton" / self.NAME
        store = results / "M2" / folder / f"{prefix}{measured}_process"
        if not skeleton.exists():
            return
        measures, retina = self._steps()["zone"]
        suffix = _zone_suffix(zone)
        try:
            values = self._evaluate(measures, retina, skeleton, store)
        except Exception as failure:  # noqa: BLE001 — the driver writes −1 for all of it
            self.trouble[f"evaluate_{measured}{suffix}"] = repr(failure)
            return
        for column, value in zip(ZONE_COLUMNS, values, strict=False):
            computed[f"{column}_{measured}{suffix}"] = _number(value)
        for own, (kept_from, index, _) in EQUIVALENTS.items():
            if kept_from == measured:
                computed[own + suffix] = _number(values[index])

    def _evaluate(self, measures, retina, skeleton: Path, store: Path) -> tuple:
        config = self._config()
        picture = retina.Retina(None, str(skeleton), store_path=str(store))
        window = retina.Window(picture, self.WORKING_SIZE, min_pixels=config["pixels_per_window"])
        return measures.evaluate_window(
            window,
            config["pixels_per_window"],
            config["sampling_size"],
            config["r_2_threshold"],
            store_path=f"{store}/",
        )

    # -- loading ---------------------------------------------------------------------------------

    def _steps(self) -> dict:
        if self._loaded is None:
            self._loaded = {
                "av": upstream.driver(upstream.AV_STAGE, "test_outside.py", ("filter_frag",)),
                "vessel": upstream.driver(
                    upstream.VESSEL_STAGE, "test_outside_integrated.py", ("filter_frag",)
                ),
                "disc": upstream.driver(
                    upstream.DISC_STAGE,
                    "generate_av_results.py",
                    ("intersection", "optic_disc_centre"),
                ),
                "whole": upstream.measurements(),
                "zone": upstream.zone_measurements(),
            }
        return self._loaded

    def _config(self) -> dict[str, float]:
        """The thresholds every driver reads from its stage's `resources/retipy.config`.

        `run.sh` changes into each stage's `retipy` folder before running its drivers, whose
        `--configuration` defaults to that file; both stages ship the same one.
        """
        if self._thresholds is None:
            self._thresholds = upstream.retipy_config()
        return self._thresholds

    def release(self) -> None:
        self._loaded = None


def _call(own: str) -> str:
    """Which of AutoMorph's steps writes a column."""
    if own in DISC_COLUMNS:
        return "M2_lwnet_disc_cup/generate_av_results.py:optic_disc_centre"
    if own.startswith(tuple(RATIOS)):
        return "M3_feature_zone/retipy/create_datasets_*_centred_*.py: CRAE / CRVE"
    if "_zone_" in own:
        return "M3_feature_zone/retipy/retipy/tortuosity_measures.py:evaluate_window"
    return "M3_feature_whole_pic/retipy/retipy/tortuosity_measures.py:evaluate_window"


def _number(value: object) -> float | None:
    try:
        found = float(value)
    except (TypeError, ValueError):
        return None
    if not np.isfinite(found) or found == FAILED:
        return None
    return found


def implementation(**arguments: object) -> Automorph:
    return Automorph(**arguments)
