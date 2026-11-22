# ABOUTME: What each implementation's own columns claim to compute, for the columns the catalogue
# ABOUTME: cannot name, and the value each claim requires on every stored rendering.

"""The ground truth an implementation is held to **by its own description**.

`ground_truth.csv` holds what the geometry requires of every *catalogued* biomarker. That covers
every column an adapter maps onto the vocabulary, and nothing else. The columns that map to no
canonical name are measured and stored all the same, and without this module none of them could be
checked: PVBM's tortuosity index, a start-point count, AutoMorph's squared-curvature tortuosity.

Each entry here reads one such column **the way its authors describe it**, by its name, its
docstring, or the paper it cites, and says what that description requires of a shape. There are two
kinds:

- **A claim the vocabulary already names.** AutoMorph's `squared_curvature_tortuosity` cites Hart's
  paper and is called squared curvature, so it claims Hart's τ3, though the adapter withdrew that
  mapping because the shapes contradict it. Its truth is τ3's. Checking it against the claim shows
  how far what the code *does* is from what it *says*, which is the comparison `CLAUDE.md` §1 asks
  every page to make.
- **A claim the vocabulary does not name.** PVBM's tortuosity index is total arc over total chord.
  Its truth is derived here, from the scene, by the same geometry `truth.py` uses.

A claim the shapes cannot settle is listed too, with the reason, so that a reader can see it was
considered rather than missed.

Every value is in **the catalogue's units**: microns for a length, plain numbers for a ratio, a
count or an angle. A column measured in pixels is converted with `power`, the claim's dimension in
length, exactly as `canonical.from_pixels` converts a catalogued one.

None of this changes what a run measures. A run never reads a ground truth, so this table can be
corrected without measuring anything again.
"""

import csv
import math
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import shapely
from shapely.geometry import Point

from . import library, store
from .scene import DISC_DIAMETER_UM, FOV_DIAMETER_UM, FOV_RADIUS_UM, Scene, merged
from .truth import CENTRED_WITHIN, QUAD_SEGS, Truth, _tubes, cup_ratios

#: The file the claimed values are written to, beside `ground_truth.csv`, and its kinds.
VALUES = "ground_truth_claimed.csv"
KINDS = "ground_truth_claimed_kind.csv"

#: VascX's circle: 1.1667 disc diameters from the disc centre (`crcl_multiplier_1p16666666667`).
VASCX_CIRCLE_UM = (7.0 / 6.0) * DISC_DIAMETER_UM


@dataclass(frozen=True)
class Claim:
    """One column, read the way its authors describe it.

    :param slug: the implementation.
    :param column: the column, exactly as the evidence names it (without `said_`).
    :param claims: what it says it computes, in words.
    :param source: where it says so.
    :param canonical: the catalogued name whose truth the claim is, where the vocabulary has one.
    :param derive: otherwise, the claimed value of a rendering: `(scene, row) -> Truth`, where
        `row` is the rendering's manifest row.
    :param power: the claim's dimension in length (1 a length, 0 a ratio, count or angle), which
        is how a pixel answer is converted before it is compared.
    :param unsettled: why the shapes cannot settle the claim, when they cannot.
    """

    slug: str
    column: str
    claims: str
    source: str
    canonical: str | None = None
    derive: Callable[[Scene, dict], Truth] | None = None
    power: int = 0
    unsettled: str = ""

    @property
    def label(self) -> str:
        """How the claimed truth is keyed: implementation, then its own column."""
        return f"{self.slug}:{self.column}"


# derivations -----------------------------------------------------------------------------------


def _class(scene: Scene, side: str):
    """One class's network, or the two as one for an implementation's all-vessel map."""
    if side == "vessels":
        return merged(scene.artery, scene.vein)
    return scene.classes()[side]


def _start_points(side: str) -> Callable[[Scene, dict], Truth]:
    """How many vessels leave the disc: one walk starts at each, so one start point each."""

    def derive(scene: Scene, row: dict) -> Truth:
        net = _class(scene, side)
        return Truth(float(sum(node.root for node in net.nodes.values())))

    return derive


def _ratio_of_sums(side: str) -> Callable[[Scene, dict], Truth]:
    """Total arc over total chord, over every segment between two nodes of the network.

    A segment here is what PVBM's walk measures between two singular points of the skeleton —
    an end, a junction or a start point — so its arc is the centreline's length and its chord the
    straight line between its two ends.
    """

    def derive(scene: Scene, row: dict) -> Truth:
        net = _class(scene, side)
        arcs = [float(segment.path.length) for segment in net.segments]
        chords = [
            math.dist(segment.path.points[0], segment.path.points[-1]) for segment in net.segments
        ]
        if not arcs or sum(chords) == 0:
            return Truth(None)
        return Truth(sum(arcs) / sum(chords))

    return derive


def _density_in_vascx_circle(side: str) -> Callable[[Scene, dict], Truth]:
    """Vessel area inside VascX's disc-centred circle, over the circle's area in the field."""

    def derive(scene: Scene, row: dict) -> Truth:
        fov = Point(0.0, 0.0).buffer(FOV_RADIUS_UM, quad_segs=QUAD_SEGS)
        circle = Point(*scene.disc).buffer(VASCX_CIRCLE_UM, quad_segs=QUAD_SEGS).intersection(fov)
        drawn = _tubes(_class(scene, side))
        return Truth(float(shapely.area(drawn.intersection(circle)) / circle.area), "numerical")

    return derive


def _zone_over_frame(side: str, inner: float, outer: float) -> Callable[[Scene, dict], Truth]:
    """Vessel area inside an annulus of `inner` to `outer` disc radii about the disc's centre, over
    the area of the whole square frame — the denominator AutoMorph's `vessel_density` divides a
    zone's vessel pixels by. The frame spans the field of view's diameter."""

    def derive(scene: Scene, row: dict) -> Truth:
        radius = DISC_DIAMETER_UM / 2.0
        centre = Point(*scene.disc)
        ring = centre.buffer(outer * radius, quad_segs=QUAD_SEGS).difference(
            centre.buffer(inner * radius, quad_segs=QUAD_SEGS)
        )
        drawn = _tubes(_class(scene, side))
        return Truth(
            float(shapely.area(drawn.intersection(ring)) / FOV_DIAMETER_UM**2), "numerical"
        )

    return derive


def _disc_diameter(scene: Scene, row: dict) -> Truth:
    """A circle is as tall as it is wide, at every angle."""
    return Truth(DISC_DIAMETER_UM)


def _cup_extent(along: str) -> Callable[[Scene, dict], Truth]:
    """The turned cup's extent along the image's rows or columns, in microns."""

    def derive(scene: Scene, row: dict) -> Truth:
        ratio = cup_ratios(scene, float(row["rotation"]))[f"landmarks/CDR-{along}"].value
        return Truth(ratio * DISC_DIAMETER_UM)

    return derive


def _cup_centre(axis: str) -> Callable[[Scene, dict], Truth]:
    """Where the cup's centre is, in microns from the centre of the frame's first pixel.

    The cup sits on the disc's centre, which the manifest records in pixels at the pixel-centre
    convention; times the scale, that is the position an implementation's pixel answer converts to.
    """

    def derive(scene: Scene, row: dict) -> Truth:
        return Truth(float(row[f"disc_c{axis}"]) * float(row["um_per_px"]))

    return derive


def _macular_centred(scene: Scene, row: dict) -> Truth:
    """1 for a photograph centred on the macula, 0 for one centred on the disc."""
    centred = math.hypot(*scene.disc) < CENTRED_WITHIN * FOV_DIAMETER_UM
    return Truth(0.0 if centred else 1.0)


# the claims ------------------------------------------------------------------------------------

_HART = "Hart et al. 1999, cited in retipy's `squared_curvature_tortuosity` docstring"
_FOVEA = "it needs a fovea, and the synthetic shapes place none"
_RING_3_TO_5 = (
    "its zone C is 3 to 5 disc radii, a ring the stored ground truth does not cover; the "
    "catalogue's zone C is 2 to 5"
)


def _automorph_family() -> list[Claim]:
    found = []
    for slug, maps, statistic in (
        ("automorph", {"artery": "artery", "vein": "vein", "binary": "vessels"}, "mean"),
        (
            "automorphclass",
            {"artery": "artery", "vein": "vein", "vessels": "vessels"},
            "length-weighted",
        ),
    ):
        for own, side in maps.items():
            found.append(
                Claim(
                    slug,
                    f"squared_curvature_tortuosity_{own}",
                    "Hart's squared-curvature tortuosity, ∫κ² ds, pooled as its sibling columns are",
                    _HART,
                    canonical=f"tortuosity/hart-tau3/{side}/{statistic}",
                    power=-1,
                )
            )
    # *Added 2026-11-22*, when the AutoMorph and AutoMorphClass adapters first reached their zones.
    for slug, maps, statistic, zones in (
        (
            "automorph",
            {"artery": "artery", "vein": "vein", "binary": "vessels"},
            "mean",
            {"b": ("/B", 2.0, 3.0), "c": ("/C", 2.0, 5.0)},
        ),
        (
            "automorphclass",
            {"artery": "artery", "vein": "vein", "vessels": "vessels"},
            "length-weighted",
            {"b": ("/B", 2.0, 3.0), "c": (None, 3.0, 5.0)},
        ),
    ):
        source = (
            "AutoMorph's zone-stage `evaluate_window`"
            if slug == "automorph"
            else "AutoMorphClass's `Vessel_Features` over `define_zones`"
        )
        for own, side in maps.items():
            for zone, (region, inner, outer) in zones.items():
                found.append(
                    Claim(
                        slug,
                        f"squared_curvature_tortuosity_{own}_zone_{zone}",
                        "Hart's squared-curvature tortuosity, ∫κ² ds, inside the zone",
                        _HART,
                        canonical=(
                            f"tortuosity/hart-tau3/{side}{region}/{statistic}" if region else None
                        ),
                        power=-1,
                        unsettled="" if region else _RING_3_TO_5,
                    )
                )
                found.append(
                    Claim(
                        slug,
                        f"vessel_density_{own}_zone_{zone}",
                        f"the zone's vessel pixels over every pixel of the frame, the zone being "
                        f"{inner:g} to {outer:g} disc radii",
                        source,
                        derive=_zone_over_frame(side, inner, outer),
                    )
                )
                if slug == "automorphclass" and zone == "c":
                    for column, says in (
                        ("fractal_dimension", "the box-counting dimension, inside the zone"),
                        ("average_width", "vessel area over centreline length, inside the zone"),
                        ("distance_tortuosity", "arc over chord, inside the zone"),
                        ("tortuosity_density", "Grisan's tortuosity density, inside the zone"),
                    ):
                        found.append(
                            Claim(
                                slug,
                                f"{column}_{own}_zone_c",
                                says,
                                source,
                                unsettled=_RING_3_TO_5,
                            )
                        )
    found += [
        Claim(
            "automorph",
            column,
            says,
            "AutoMorph's `optic_disc_centre`",
            derive=derive,
            power=1,
        )
        for column, says, derive in (
            ("Disc_height", "the disc's vertical diameter", _disc_diameter),
            ("Disc_width", "the disc's horizontal diameter", _disc_diameter),
            ("Cup_height", "the cup's vertical diameter", _cup_extent("vertical")),
            ("Cup_width", "the cup's horizontal diameter", _cup_extent("horizontal")),
        )
    ]
    for side, structure in (("artery", "artery"), ("vein", "vein"), ("binary", "vessels")):
        for zone, region in (("whole", ""), ("B", "/B"), ("C", "/C")):
            found.append(
                Claim(
                    "automorphalyzer",
                    f"average_local_calibre@{zone}_{side}",
                    "the mean local width of the vessels, sampled along them",
                    "AutoMorphalyzer's `vessel_metrics`, `average_local_calibre`",
                    canonical=f"calibre/width/{structure}{region}/length-weighted",
                    power=1,
                )
            )
    for slug, prefix in (("automorphalyzer", ""), ("automorphclass", "")):
        source = (
            "AutoMorphalyzer's `get_disc_metrics`"
            if slug == "automorphalyzer"
            else "AutoMorphClass's `Optic_Disc_Cup_Features`"
        )
        found += [
            Claim(
                slug,
                f"{prefix}disc_height",
                "the disc's vertical diameter",
                source,
                derive=_disc_diameter,
                power=1,
            ),
            Claim(
                slug,
                f"{prefix}disc_width",
                "the disc's horizontal diameter",
                source,
                derive=_disc_diameter,
                power=1,
            ),
            Claim(
                slug,
                f"{prefix}cup_height",
                "the cup's vertical diameter",
                source,
                derive=_cup_extent("vertical"),
                power=1,
            ),
            Claim(
                slug,
                f"{prefix}cup_width",
                "the cup's horizontal diameter",
                source,
                derive=_cup_extent("horizontal"),
                power=1,
            ),
        ]
    found += [
        Claim(
            "automorphalyzer",
            "cup_centre_x",
            "the cup's centre, horizontally",
            "AutoMorphalyzer's `get_disc_metrics`",
            derive=_cup_centre("x"),
            power=1,
        ),
        Claim(
            "automorphalyzer",
            "cup_centre_y",
            "the cup's centre, vertically",
            "AutoMorphalyzer's `get_disc_metrics`",
            derive=_cup_centre("y"),
            power=1,
        ),
        Claim(
            "automorphalyzer",
            "macular_centred",
            "whether the photograph is macula-centred: the disc further than a tenth of the "
            "frame from its centre",
            "AutoMorphalyzer's `get_disc_metrics`",
            derive=_macular_centred,
        ),
        Claim(
            "automorphalyzer",
            "laterality",
            "which eye, from which side of the disc has more vessel",
            "AutoMorphalyzer's `get_disc_metrics`",
            unsettled="the shapes' vessels are not laid out as an eye's are, so the side with more "
            "vessel says nothing about laterality",
        ),
    ]
    return found


def _pvbm_family() -> list[Claim]:
    found = []
    for slug in ("pvbm", "ocular"):
        source = "PVBM's `GeometryAnalysis`" if slug == "pvbm" else "OCULAR's `GeometricalVBMs`"
        for side in ("artery", "vein"):
            found += [
                Claim(
                    slug,
                    f"start_points_{side}",
                    "how many vessels leave the optic disc",
                    source,
                    derive=_start_points(side),
                ),
                Claim(
                    slug,
                    f"endpoints_{side}",
                    "how many vessel ends there are",
                    source,
                    canonical=f"topology/endpoints/{side}",
                ),
                Claim(
                    slug,
                    f"median_branching_angle_{side}",
                    "the median angle between the two daughters at a branch point",
                    source,
                    canonical=f"topology/branching-angle/{side}/median",
                ),
            ]
            ratio = "tortuosity_index" if slug == "pvbm" else "pooled_tortuosity"
            found.append(
                Claim(
                    slug,
                    f"{ratio}_{side}",
                    "total arc length over total chord length, over every segment of the map",
                    f"{source}: `arc_list.sum() / chord_list.sum()`",
                    derive=_ratio_of_sums(side),
                )
            )
            if slug == "pvbm":
                found.append(
                    Claim(
                        slug,
                        f"singularity_length_{side}",
                        "the width of the multifractal singularity spectrum",
                        "PVBM's `MultifractalVBMs.get_singularity_length`",
                        unsettled="a multifractal spectrum has no closed form on these shapes, "
                        "and a finite raster does not reach its limit",
                    )
                )
    return found


def _vascx() -> list[Claim]:
    circle = "crcl_multiplier_1p16666666667"
    found = []
    for layer, side in (("arteries", "artery"), ("veins", "vein")):
        for cap in ("0p15", "0p25"):
            found.append(
                Claim(
                    "vascx",
                    f"lw_tort_dist_max_segment_len_{cap}_{circle}_full_{layer}",
                    "arc over chord, length-weighted, with segments capped at another length",
                    "VascX's `Tortuosity` with `TortuosityMeasure.Distance`",
                    canonical=f"tortuosity/hart-tau1/{side}/length-weighted",
                )
            )
        found += [
            Claim(
                "vascx",
                f"vd_{circle}_full_{layer}",
                "vessel area over the area of its disc-centred circle, 1.1667 disc diameters",
                "VascX's `VascularDensity.compute_for_mask`",
                derive=_density_in_vascx_circle(side),
            ),
            Claim(
                "vascx",
                f"lw_tort_curv_{circle}_full_{layer}",
                "mean curvature along a spline, times the disc-to-fovea distance",
                "VascX's `Tortuosity` with `TortuosityMeasure.Curvature`",
                unsettled=_FOVEA,
            ),
            Claim(
                "vascx",
                f"median_temporal_angle_{layer}",
                "the angle the temporal arcades open at",
                "VascX's `TemporalAngle`",
                unsettled=_FOVEA,
            ),
        ]
    found += [
        Claim(
            "vascx",
            "mean_sparsity_vessels",
            "mean distance to the nearest vessel, over the disc-to-fovea distance",
            "VascX's `Sparsity`",
            unsettled=_FOVEA,
        ),
        Claim(
            "vascx",
            f"mean_sparsity_{circle}_full_vessels",
            "the same, inside its circle",
            "VascX's `Sparsity`",
            unsettled=_FOVEA,
        ),
        Claim(
            "vascx",
            "disc_fovea_distance_retina",
            "the distance from the disc to the fovea",
            "VascX's `DiscFoveaDistance`",
            unsettled=_FOVEA,
        ),
        Claim(
            "vascx",
            "disc_fovea_distance_center_retina",
            "the same, from the disc's centre",
            "VascX's `DiscFoveaDistance`",
            unsettled=_FOVEA,
        ),
    ]
    return found


def _vascx_sets() -> list[Claim]:
    """Every other unnamed column of VascX's two shipped sets. *Added 2026-11-22*, when the adapter
    first kept all 132 columns `od_centered` and `full_v3` compute.

    Most measure over a region built on the disc-to-fovea axis — a quadrant or half of its circle,
    a hemifield, the ETDRS grid, an ellipse — or are scaled by that distance, and no synthetic shape
    has a fovea, so they are listed as unsettled. The whole-image ones claim a catalogued biomarker
    outright, and are held to it.
    """
    import re

    from biomarkers import vascx
    from biomarkers.utils.closest import nearest

    held = {
        r"lw_diam_(?P<side>arteries|veins)": "calibre/width/{side}/length-weighted",
        r"md_diam_(?P<side>arteries|veins)": "calibre/width/{side}/median",
        r"lw_tort_dist_(?:max_segment_len_0p2_)?(?P<side>arteries|veins)": (
            "tortuosity/hart-tau1/{side}/length-weighted"
        ),
        r"md_tort_dist_(?P<side>arteries|veins)": "tortuosity/hart-tau1/{side}/median",
        r"lw_tort_dist_vessels_(?P<side>arteries|veins)": (
            "tortuosity/vessel-hart-tau1/{side}/length-weighted"
        ),
        r"mn_bifangle_(?P<side>arteries|veins)": "topology/branching-angle/{side}/mean",
    }
    sides = {"arteries": "artery", "veins": "vein"}
    already = {claim.column for claim in _vascx()}
    found = []
    for column, name in vascx.CANONICAL.items():
        if name or column in already:
            continue
        near = nearest(column, vascx.CLOSEST, vascx.CLOSEST_WORDS)
        says = f"{near[0]}, {near[1]}" if near and near[0] else (near[1] if near else column)
        for pattern, template in held.items():
            match = re.fullmatch(pattern, column)
            if match:
                found.append(
                    Claim(
                        "vascx",
                        column,
                        f"{template.format(side=sides[match['side']])}, over the whole image",
                        "VascX's `full_v3` feature set",
                        canonical=template.format(side=sides[match["side"]]),
                        # A width is a length, so its pixels are converted before comparing.
                        power=1 if template.startswith("calibre/") else 0,
                    )
                )
                break
        else:
            if column.startswith("sharpness_"):
                why = "it measures the photograph's focus, and a drawn shape has no photograph"
            elif "disc_full" in column:
                why = "the extent of its `disc_full` grid has not been read from VascX's source"
            else:
                why = _FOVEA
            found.append(
                Claim("vascx", column, says, "VascX's shipped feature sets", unsettled=why)
            )
    return found


#: Every claim, in the benchmark's lineage order.
CLAIMS: tuple[Claim, ...] = (*_pvbm_family(), *_automorph_family(), *_vascx(), *_vascx_sets())


def claimed(slug: str) -> dict[str, Claim]:
    """One implementation's claims, by its own column name."""
    return {claim.column: claim for claim in CLAIMS if claim.slug == slug}


# the table -------------------------------------------------------------------------------------


def settle(row: dict) -> dict[str, Truth]:
    """Every claim's value on one stored rendering, by `slug:column`.

    A claim naming a catalogued biomarker takes that biomarker's truth, from the same derivation
    `ground_truth.csv` was written from; a derived one is worked out here; an unsettled one is left
    out, because the shapes say nothing about it.
    """
    scene = library.scene(row["family"])
    catalogued = library.truths(row["family"], float(row["rotation"]))
    found: dict[str, Truth] = {}
    for claim in CLAIMS:
        if claim.unsettled:
            continue
        if claim.canonical:
            if claim.canonical in catalogued:
                found[claim.label] = catalogued[claim.canonical]
            continue
        found[claim.label] = claim.derive(scene, row)
    return found


def write(into: Path = store.STORE) -> None:
    """Write every claim's value, and how it is known, beside the store's own ground truth."""
    into = Path(into)
    values, kinds = [], []
    for row in store.read(into):
        settled = settle(row)
        values.append({"key": row["key"], **{k: store._cell(t.value) for k, t in settled.items()}})
        kinds.append({"key": row["key"], **{k: t.kind for k, t in settled.items()}})
    columns = ("key", *[claim.label for claim in CLAIMS if not claim.unsettled])
    store._write_rows(into / VALUES, columns, values)
    store._write_rows(into / KINDS, columns, kinds)


def read(into: Path = store.STORE) -> tuple[dict[str, dict[str, float]], dict[str, dict[str, str]]]:
    """The claimed values and their kinds, by rendering key, then by `slug:column`. An empty value
    with a kind is a claim the geometry settles as having no value."""
    into = Path(into)
    with (into / VALUES).open() as handle:
        values = {
            row.pop("key"): {k: float(v) for k, v in row.items() if v != ""}
            for row in csv.DictReader(handle)
        }
    with (into / KINDS).open() as handle:
        kinds = {
            row.pop("key"): {k: v for k, v in row.items() if v != ""}
            for row in csv.DictReader(handle)
        }
    return values, kinds


def turning(into: Path = store.STORE) -> set[tuple[str, str]]:
    """The `(implementation, column)` claims whose value changes when a shape is turned.

    A cup's height in the image, or where its centre lands, is *meant* to move with the
    photograph, so a rotation check must leave these out exactly as it leaves out the vertical and
    horizontal cup-to-disc ratios. Read off the table rather than listed by hand.
    """
    values, _ = read(into)
    family = {row["key"]: row["family"] for row in store.read(into)}
    seen: dict[tuple[str, str], dict[str, set[float]]] = {}
    for key, row in values.items():
        for label, value in row.items():
            slug, column = label.split(":", 1)
            seen.setdefault((slug, column), {}).setdefault(family[key], set()).add(round(value, 9))
    return {pair for pair, by_family in seen.items() if any(len(v) > 1 for v in by_family.values())}


if __name__ == "__main__":
    write()
    print(f"wrote {store.STORE / VALUES} and {store.STORE / KINDS}")
