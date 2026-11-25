# ABOUTME: VascX's feature machinery, reached from this repository: one pass over a retina built
# ABOUTME: from the masks, and the table saying what each of its feature names answers to.

import hashlib
import json
import warnings

import numpy as np

from upstreams import vascx as upstream

#: The shipped feature sets this adapter runs, each as VascX ships it rather than assembled from
#: parts, so what is measured is a configuration its authors published. `calc-biomarkers` has no
#: default set: its README recommends **`full_v3`**, "the latest 'full' set", and the disc-centred
#: one is the framing every disc-anchored measurement here is stated in. *Since 2026-11-22* both
#: are run, after an audit found the adapter returning 20 of the 132 columns the two compute.
FEATURE_SETS = ("fs_od_centered", "fs_full_v3")

#: The circle VascX measures over in that set, as it appears in every feature's name: 1.1667 disc
#: **diameters** from the disc centre, which is 2.33 disc *radii*. That is inside the 2-to-3 radii
#: annulus PVBM and AutoMorphalyzer measure over rather than equal to it — near enough that the two
#: are worth comparing, far enough that a difference between them is partly the region.
CIRCLE = "crcl_multiplier_1p16666666667"

#: What each computed feature answers to. `{side}` becomes `artery` or `vein`.
#:
#: **Only the orientation-independent features are catalogued.** VascX's grids are built on the
#: disc-to-fovea axis, and a synthetic shape has no macula: the fovea this adapter supplies is a
#: convention of the fixture (see `FOVEA`), so anything measured *superior*, *inferior*, *temporal*
#: or *nasal* to that axis, and anything measuring the axis itself, is a property of the fixture
#: rather than of VascX. Those are measured and stored under VascX's own names and compared against
#: nothing.
NAMES: dict[str, str | None] = {
    f"lw_diam_{CIRCLE}_full_{{layer}}": "calibre/width/{side}/length-weighted",
    # *Our finding, 2026-09-22, from reading `cre.py`:* despite the module's name and the project
    # page's description of a "Hubbard reduction", it combines pairs as `c·√(d₁² + d₂²)` with
    # c = 0.88 for arteries and 0.95 for veins — which **is** Knudtson's formula. Hubbard's carries
    # fitted constants and an additive term, and neither appears here.
    "full_cre_{layer}": "calibre/CRE-knudtson/{side}/B",
    # Arc over chord, length-weighted across segments, with segments capped at 0.2 disc diameters.
    # Three caps are shipped; this is the middle one, and the other two are kept unmapped beside it
    # so a reader can see how little the cap changes the answer.
    f"lw_tort_dist_max_segment_len_0p2_{CIRCLE}_full_{{layer}}": (
        "tortuosity/hart-tau1/{side}/length-weighted"
    ),
    f"lw_tort_dist_max_segment_len_0p15_{CIRCLE}_full_{{layer}}": None,
    f"lw_tort_dist_max_segment_len_0p25_{CIRCLE}_full_{{layer}}": None,
    # *Our finding, 2026-10-01, from `features/tortuosity.py`:* **not a curvature.**
    # `TortuosityMeasure.Curvature` returns `np.mean(spline.curvatures()) *
    # self._get_curvature_scale(...)`, and that scale is `layer.retina.disc_fovea_distance`. So
    # the number is a mean curvature **multiplied by a length** — dimensionless, expressed in
    # disc-to-fovea distances — where `tortuosity/spline-curvature` means a curvature in 1/µm.
    #
    # This is `mean_sparsity`'s defect in a second feature, and it was found the same way: on a
    # real photograph it reads about 1.5, which as 1/µm would be a vessel bending through a radius
    # of two thirds of a micron. The mapping is withdrawn rather than divided by anything, because
    # the divisor is the disc-fovea axis — a model's answer on a photograph, and this adapter's own
    # invented convention on a synthetic shape (see `FOVEA`). It was mapped from 2026-09-22 and
    # every figure the synthetic benchmark reported for it — a 280% rotation spread, a 43% error —
    # was measuring that axis rather than any curvature.
    f"lw_tort_curv_{CIRCLE}_full_{{layer}}": None,
    # Vessel area over the area of a disc-centred circle — neither the field of view nor the whole
    # frame, so neither catalogued density describes it.
    f"vd_{CIRCLE}_full_{{layer}}": None,
    # Measured against an axis this fixture invented; see above.
    "median_temporal_angle_{layer}": None,
}

#: Features of the whole retina rather than of one class, kept under their own names for the same
#: reason: both describe the axis the adapter supplied.
RETINA_NAMES: dict[str, str | None] = {
    "disc_fovea_distance_retina": None,
    "disc_fovea_distance_center_retina": None,
    # *Our finding, 2026-09-30, from `features/sparsity.py`:* **not a distance.** The family was
    # rebuilt with `density/sparsity` in microns, and this was mapped to it on the strength of the
    # name — then disagreed with the shapes by a factor of about 3,900. Its constructor takes
    # `normalize=True` by default and the docstring says what that means: "sparsity is normalized
    # by the OD-fovea distance". So the number is dimensionless, expressed in disc-to-fovea
    # distances, and on a synthetic shape that distance is the convention this adapter supplied
    # (see `FOVEA`) rather than anything about the vessels. Twice uncatalogued, and the mapping is
    # withdrawn rather than divided by something.
    "mean_sparsity_vessels": None,
    f"mean_sparsity_{CIRCLE}_full_vessels": None,
}

#: Every column the two sets compute, in VascX's own canonical naming, as
#: `Retina.make_feature_display_names` lists them — od_centered's 67, then full_v3's 65 more; the
#: ten they share compute the same number. A test holds this list to what VascX generates, so a
#: change upstream fails loudly rather than dropping a column.
#:
#: Only the columns in `NAMES` and `RETINA_NAMES` are catalogued. The rest are kept under VascX's
#: names: the superior, inferior, temporal, nasal, hemifield, ETDRS and ellipse ones are built on
#: the disc-to-fovea axis this fixture invents (see `FOVEA`); the whole-image and `disc_full` ones
#: wait for a mapping the shapes can test.
COLUMNS: tuple[str, ...] = (
    "median_temporal_angle_arteries",
    "median_temporal_angle_veins",
    "mn_bifangle_crcl_multiplier_1p16666666667_full_arteries",
    "mn_bifangle_crcl_multiplier_1p16666666667_full_veins",
    "mn_bifangle_crcl_multiplier_1p16666666667_superior_arteries",
    "mn_bifangle_crcl_multiplier_1p16666666667_superior_veins",
    "mn_bifangle_crcl_multiplier_1p16666666667_inferior_arteries",
    "mn_bifangle_crcl_multiplier_1p16666666667_inferior_veins",
    "mn_bifangle_crcl_multiplier_1p16666666667_temporal_arteries",
    "mn_bifangle_crcl_multiplier_1p16666666667_temporal_veins",
    "mn_bifangle_crcl_multiplier_1p16666666667_nasal_arteries",
    "mn_bifangle_crcl_multiplier_1p16666666667_nasal_veins",
    "lw_diam_crcl_multiplier_1p16666666667_full_arteries",
    "lw_diam_crcl_multiplier_1p16666666667_full_veins",
    "lw_diam_crcl_multiplier_1p16666666667_superior_arteries",
    "lw_diam_crcl_multiplier_1p16666666667_superior_veins",
    "lw_diam_crcl_multiplier_1p16666666667_inferior_arteries",
    "lw_diam_crcl_multiplier_1p16666666667_inferior_veins",
    "lw_diam_crcl_multiplier_1p16666666667_temporal_arteries",
    "lw_diam_crcl_multiplier_1p16666666667_temporal_veins",
    "lw_diam_crcl_multiplier_1p16666666667_nasal_arteries",
    "lw_diam_crcl_multiplier_1p16666666667_nasal_veins",
    "full_cre_arteries",
    "full_cre_veins",
    "nasal_cre_arteries",
    "nasal_cre_veins",
    "temporal_cre_arteries",
    "temporal_cre_veins",
    "lw_tort_dist_max_segment_len_0p15_crcl_multiplier_1p16666666667_full_arteries",
    "lw_tort_dist_max_segment_len_0p15_crcl_multiplier_1p16666666667_full_veins",
    "lw_tort_dist_max_segment_len_0p2_crcl_multiplier_1p16666666667_full_arteries",
    "lw_tort_dist_max_segment_len_0p2_crcl_multiplier_1p16666666667_full_veins",
    "lw_tort_dist_max_segment_len_0p25_crcl_multiplier_1p16666666667_full_arteries",
    "lw_tort_dist_max_segment_len_0p25_crcl_multiplier_1p16666666667_full_veins",
    "lw_tort_curv_crcl_multiplier_1p16666666667_full_arteries",
    "lw_tort_curv_crcl_multiplier_1p16666666667_full_veins",
    "lw_tort_dist_max_segment_len_0p2_crcl_multiplier_1p16666666667_superior_arteries",
    "lw_tort_dist_max_segment_len_0p2_crcl_multiplier_1p16666666667_superior_veins",
    "lw_tort_dist_max_segment_len_0p2_crcl_multiplier_1p16666666667_inferior_arteries",
    "lw_tort_dist_max_segment_len_0p2_crcl_multiplier_1p16666666667_inferior_veins",
    "lw_tort_dist_max_segment_len_0p2_crcl_multiplier_1p16666666667_temporal_arteries",
    "lw_tort_dist_max_segment_len_0p2_crcl_multiplier_1p16666666667_temporal_veins",
    "lw_tort_dist_max_segment_len_0p2_crcl_multiplier_1p16666666667_nasal_arteries",
    "lw_tort_dist_max_segment_len_0p2_crcl_multiplier_1p16666666667_nasal_veins",
    "lw_tort_curv_crcl_multiplier_1p16666666667_superior_arteries",
    "lw_tort_curv_crcl_multiplier_1p16666666667_superior_veins",
    "lw_tort_curv_crcl_multiplier_1p16666666667_inferior_arteries",
    "lw_tort_curv_crcl_multiplier_1p16666666667_inferior_veins",
    "lw_tort_curv_crcl_multiplier_1p16666666667_temporal_arteries",
    "lw_tort_curv_crcl_multiplier_1p16666666667_temporal_veins",
    "lw_tort_curv_crcl_multiplier_1p16666666667_nasal_arteries",
    "lw_tort_curv_crcl_multiplier_1p16666666667_nasal_veins",
    "vd_crcl_multiplier_1p16666666667_full_arteries",
    "vd_crcl_multiplier_1p16666666667_full_veins",
    "vd_crcl_multiplier_1p16666666667_superior_arteries",
    "vd_crcl_multiplier_1p16666666667_superior_veins",
    "vd_crcl_multiplier_1p16666666667_inferior_arteries",
    "vd_crcl_multiplier_1p16666666667_inferior_veins",
    "vd_crcl_multiplier_1p16666666667_temporal_arteries",
    "vd_crcl_multiplier_1p16666666667_temporal_veins",
    "vd_crcl_multiplier_1p16666666667_nasal_arteries",
    "vd_crcl_multiplier_1p16666666667_nasal_veins",
    "disc_fovea_distance_center_retina",
    "disc_fovea_distance_retina",
    "mean_sparsity_vessels",
    "mean_sparsity_crcl_multiplier_1p16666666667_full_vessels",
    "sharpness_crcl_multiplier_1p16666666667_full_vessels",
    "mn_bifangle_arteries",
    "mn_bifangle_veins",
    "mn_bifangle_hf_superior_arteries",
    "mn_bifangle_hf_superior_veins",
    "mn_bifangle_hf_inferior_arteries",
    "mn_bifangle_hf_inferior_veins",
    "md_diam_arteries",
    "md_diam_veins",
    "md_diam_hf_superior_arteries",
    "md_diam_hf_superior_veins",
    "md_diam_hf_inferior_arteries",
    "md_diam_hf_inferior_veins",
    "lw_diam_arteries",
    "lw_diam_veins",
    "lw_diam_hf_superior_arteries",
    "lw_diam_hf_superior_veins",
    "lw_diam_hf_inferior_arteries",
    "lw_diam_hf_inferior_veins",
    "lw_diam_disc_full_arteries",
    "lw_diam_disc_full_veins",
    "temporal_cre_hf_superior_arteries",
    "temporal_cre_hf_superior_veins",
    "temporal_cre_hf_inferior_arteries",
    "temporal_cre_hf_inferior_veins",
    "md_tort_dist_arteries",
    "md_tort_dist_veins",
    "md_tort_curv_arteries",
    "md_tort_curv_veins",
    "lw_tort_dist_vessels_arteries",
    "lw_tort_dist_vessels_veins",
    "lw_tort_dist_arteries",
    "lw_tort_dist_veins",
    "lw_tort_dist_max_segment_len_0p2_arteries",
    "lw_tort_dist_max_segment_len_0p2_veins",
    "lw_tort_curv_arteries",
    "lw_tort_curv_veins",
    "lw_tort_dist_etdrs_full_arteries",
    "lw_tort_dist_etdrs_full_veins",
    "lw_tort_dist_max_segment_len_0p2_etdrs_full_arteries",
    "lw_tort_dist_max_segment_len_0p2_etdrs_full_veins",
    "lw_tort_curv_etdrs_full_arteries",
    "lw_tort_curv_etdrs_full_veins",
    "lw_tort_dist_disc_full_arteries",
    "lw_tort_dist_disc_full_veins",
    "lw_tort_dist_max_segment_len_0p2_disc_full_arteries",
    "lw_tort_dist_max_segment_len_0p2_disc_full_veins",
    "lw_tort_curv_disc_full_arteries",
    "lw_tort_curv_disc_full_veins",
    "vd_elps_full_arteries",
    "vd_elps_full_veins",
    "vd_disc_full_arteries",
    "vd_disc_full_veins",
    "vd_etdrs_full_arteries",
    "vd_etdrs_full_veins",
    "vd_hf_superior_arteries",
    "vd_hf_superior_veins",
    "vd_hf_inferior_arteries",
    "vd_hf_inferior_veins",
    "max_sparsity_vessels",
    "mean_sparsity_elps_full_vessels",
    "max_sparsity_elps_full_vessels",
    "mean_sparsity_disc_full_vessels",
    "max_sparsity_disc_full_vessels",
    "mean_sparsity_etdrs_full_vessels",
    "max_sparsity_etdrs_full_vessels",
)

#: VascX's layer names, and the structure each answers for.
LAYERS = {"arteries": "artery", "veins": "vein"}

#: Millimetres per micron, for the one conversion this adapter makes. See `Vascx.measure`.
MM_PER_UM = 0.001

#: The features VascX returns in **millimetres**, recognised by VascX's own names rather than by
#: the catalogued name they answer to: every diameter (`lw_diam`, `md_diam`) and every central
#: retinal equivalent (`full_cre`, `nasal_cre`, `temporal_cre`, and its hemifield ones). Which
#: columns carry a physical length is a fact about VascX, and tying it to the catalogue's spelling
#: would make renaming a biomarker change a unit.
IN_MILLIMETRES = ("lw_diam_", "md_diam_", "full_cre_", "nasal_cre_", "temporal_cre_")


def _answers() -> dict[str, str]:
    """Answered name → the VascX feature behind it."""
    pairs: dict[str, str] = {}
    for layer, side in LAYERS.items():
        for template, mapped in NAMES.items():
            own = template.format(layer=layer)
            pairs[mapped.format(side=side) if mapped else own] = own
    for own, mapped in RETINA_NAMES.items():
        pairs[mapped or own] = own
    return pairs


#: Answered name → the feature behind it. Built once; the order is the order above.
ANSWERS = _answers()

#: Each column under **its own name**, against the catalogued biomarker it answers to — or `None`
#: where the catalogue has no name for it yet. The evidence a run writes is keyed by the
#: implementation's own names, because that is what its authors call these numbers and what a
#: reader checking against their documentation will look for; translating to a catalogued name is
#: a claim, and a claim belongs in the analysis that relies on it rather than baked into the
#: measurement.
CANONICAL: dict[str, str | None] = {
    **{own: (answered if "/" in answered else None) for answered, own in ANSWERS.items()},
    **{own: None for own in COLUMNS if own not in set(ANSWERS.values())},
}


#: For each column with no canonical name, the nearest one and what keeps it from being that name.
#: Rendered into the project page's list of every column it writes (`python -m biomarkers.pages`).
#: A close name is a pointer for a reader, never a mapping: nothing is compared against it, and a
#: column moves into the naming table above only when the shapes can test it. Patterns are matched
#: against the whole of the column's own name; a column no rule matches has nothing near.
_REGION = (
    r"crcl_multiplier_1p16666666667_(?:full|superior|inferior|temporal|nasal)"
    r"|disc_full|etdrs_full|elps_full|hf_superior|hf_inferior"
)
_SIDE = r"(?P<side>arteries|veins)"
CLOSEST = (
    (
        r"sharpness_.*",
        None,
        "how sharply the photograph is focused at the vessels' edges; it needs the photograph",
    ),
    (
        rf"(?P<stat>lw|md)_diam_(?:(?P<where>{_REGION})_)?{_SIDE}",
        "calibre/width/{side}/{stat}",
        "{where}",
    ),
    (
        rf"lw_tort_dist_vessels_{_SIDE}",
        "tortuosity/vessel-hart-tau1/{side}/length-weighted",
        "arc over chord of whole vessels rather than segments, over the whole image",
    ),
    (
        rf"(?P<stat>lw|md)_tort_dist_(?P<cap>max_segment_len_0p\d+_)?(?:(?P<where>{_REGION})_)?{_SIDE}",
        "tortuosity/hart-tau1/{side}/{stat}",
        "{cap}{where}",
    ),
    (
        rf"(?P<stat>lw|md)_tort_curv_(?:(?P<where>{_REGION})_)?{_SIDE}",
        "tortuosity/spline-curvature/{side}/{stat}",
        "mean curvature multiplied by the disc–fovea distance, so dimensionless; {where}",
    ),
    (
        rf"vd_(?P<where>{_REGION})_{_SIDE}",
        "density/over-fov/{side}",
        "vessel area over the area of its region rather than the field of view; {where}",
    ),
    (
        rf"(?P<stat>mean|max)_sparsity_(?:(?P<where>{_REGION})_)?vessels",
        "density/sparsity/vessels/{stat}",
        "divided by the disc–fovea distance, so dimensionless; {where}",
    ),
    (
        rf"mn_bifangle_(?:(?P<where>{_REGION})_)?{_SIDE}",
        "topology/branching-angle/{side}/mean",
        "{where}",
    ),
    (
        rf"(?P<which>full|nasal|temporal)_cre_(?:(?P<half>hf_superior|hf_inferior)_)?{_SIDE}",
        "calibre/CRE-knudtson/{side}/B",
        "{which}, at 2.33 disc radii, inside zone B rather than across it{half}",
    ),
    (
        rf"median_temporal_angle_{_SIDE}",
        "topology/temporal-angle/{side}",
        (
            "measured from the disc–fovea axis; on a synthetic shape that axis is this atlas's "
            "convention, so the column is kept under VascX's name"
        ),
    ),
    (
        r"disc_fovea_distance(?P<from>_center)?_retina",
        "landmarks/disc-fovea-distance",
        "from the disc's {from}; on a synthetic shape the fovea is this atlas's convention",
    ),
)
CLOSEST_WORDS = {
    "side": {"arteries": "artery", "veins": "vein"},
    "stat": {"lw": "length-weighted", "md": "median", "mean": "mean", "max": "max"},
    "where": {
        "": "over the whole image",
        "crcl_multiplier_1p16666666667_full": "over its circle at 2.33 disc radii",
        "crcl_multiplier_1p16666666667_superior": "over the superior quadrant of its circle, "
        "on the disc–fovea axis",
        "crcl_multiplier_1p16666666667_inferior": "over the inferior quadrant of its circle, "
        "on the disc–fovea axis",
        "crcl_multiplier_1p16666666667_temporal": "over the temporal quadrant of its circle, "
        "on the disc–fovea axis",
        "crcl_multiplier_1p16666666667_nasal": "over the nasal quadrant of its circle, "
        "on the disc–fovea axis",
        "disc_full": "over a disc-centred circle (`disc_full`)",
        "etdrs_full": "over the ETDRS grid, centred on the fovea",
        "elps_full": "over an ellipse on the disc–fovea axis",
        "hf_superior": "over the superior hemifield, split along the disc–fovea axis",
        "hf_inferior": "over the inferior hemifield, split along the disc–fovea axis",
    },
    "cap": {
        "max_segment_len_0p15_": "segments capped at 0.15 disc diameters, ",
        "max_segment_len_0p2_": "segments capped at 0.2 disc diameters, ",
        "max_segment_len_0p25_": "segments capped at 0.25 disc diameters, ",
    },
    "which": {
        "full": "over its full circle",
        "nasal": "over the nasal half of its circle",
        "temporal": "over the temporal half of its circle",
    },
    "from": {"": "edge", "_center": "centre"},
    "half": {
        "": "",
        "hf_superior": ", superior hemifield only",
        "hf_inferior": ", inferior hemifield only",
    },
}


class Vascx:
    """VascX, measured as it ships.

    One pass over a retina assembled from the masks computes every feature of the shipped
    disc-centred set. Three things this adapter must know, and declares rather than hides:

    - **It works in millimetres.** Every length VascX returns is physical, because it is given a
      scale. The shapes state their theory in pixels, so the two lengths this adapter maps —
      calibre and the central retinal equivalents — are converted back to pixels using the very
      scale the shape was built with, which makes the conversion exact rather than an estimate.
      Declared here and in `declare()["units"]`; nothing else is converted.
    - **It needs a fovea.** Its grids are oriented on the disc-to-fovea axis and every feature
      fails with "Disc or fovea location not set" without one. A synthetic shape has no macula, so
      the adapter supplies one by the convention in `FOVEA`, and everything that depends on the
      *direction* of that axis is left uncatalogued.
    - **It wants a disc mask**, not a centre and a radius, so the adapter draws the circle it was
      given — and then rebuilds the disc at the frame's own size.

    *Our finding, 2026-09-22:* `rtnls_enface.disc.OpticDisc.__init__` takes `size=1024` and nothing
    passes the retina's resolution to it, so a disc handed to a 2048-pixel retina is resized to
    1024 and every feature measured on a circle around it then indexes out of bounds — 34 of the
    36 computable features are lost, silently, with only a warning per feature. The adapter
    rebuilds the disc at the frame's size, which is what makes VascX measurable at all here.
    """

    slug = "vascx"
    needs = ("artery", "vein", "disc")
    invariant = ("rotation",)

    #: Where the fovea is taken to be, and why this is a convention rather than a measurement.
    #:
    #: A macula-centred photograph puts the macula at the centre of the frame — which is what the
    #: `spokes-macula-centred` family is named for, and the point every shape here is rotated
    #: about. So the frame centre is the fovea implied by the framing rather than a number invented
    #: for the occasion. Where the disc is itself at the frame centre the framing is disc-centred,
    #: and the fovea is placed one standard separation away, on the side the macula-centred framing
    #: puts it.
    FOVEA = "frame centre, or one disc offset from a centred disc"

    #: How close to the frame centre a disc must be for the framing to count as disc-centred.
    CENTRED_WITHIN = 2.0

    def __init__(self, device: str | None = None) -> None:
        self.device = "cpu"
        self.trouble: dict[str, str] = {}
        self._parts = None

    def declare(self) -> dict[str, object]:
        return {
            "slug": self.slug,
            "needs": list(self.needs),
            "invariant": list(self.invariant),
            "keys": list(self.keys()),
            "names": dict(CANONICAL),
            "calls": {own: ["calc_features"] for own in CANONICAL},
            "feature_sets": list(FEATURE_SETS),
            "circle": "1.1667 disc diameters from the disc centre",
            "fovea": self.FOVEA,
            "units": {
                "every measurement": "px",
                "converted from VascX's mm by the shape's scale": sorted(IN_MILLIMETRES),
                "everything else": "as VascX returns it",
            },
            "device": self.device,
            "upstream": upstream.provenance(),
        }

    def identity(self) -> str:
        """All four pinned commits, not just VascX's.

        VascX is one repository and the code that produces these numbers is four. Its measuring
        code lives in `vascx`, but `rtnls_enface` supplies the optic disc and the fundus that
        `vascx.fundus.retina` is built on, so a change there moves the numbers exactly as a change
        in `vascx` would. Identifying the run by one commit of the four would let the other three
        move underneath a stored score.
        """
        return hashlib.sha256(
            json.dumps(upstream.provenance(), sort_keys=True).encode()
        ).hexdigest()

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
        """Everything the shipped set computes, under catalogued names where one applies."""
        self.trouble = {}
        computed: dict[str, float | None] = dict.fromkeys(CANONICAL)
        if artery is None or vein is None:
            # Its retina is assembled from both classes at once; one alone is not a retina, and
            # substituting the other would be invisible in the evidence.
            self.trouble["calc_features"] = "VascX is assembled from both classes and was given one"
            return dict.fromkeys(CANONICAL)
        try:
            found = self._one_retina(artery, vein, fov, disc, um_per_px)
        except Exception as failure:  # noqa: BLE001 — a measurement that fell over has no value
            self.trouble["calc_features"] = repr(failure)
            return dict.fromkeys(CANONICAL)
        computed.update(found)
        return self._in_pixels({own: computed.get(own) for own in CANONICAL}, um_per_px)

    def _one_retina(self, artery, vein, fov, disc, um_per_px):
        """Build the retina VascX expects, and run the shipped feature set over it once."""
        Retina, VesselTreeLayer, FundusVesselsLayer, sets = self._loaded()
        artery, vein = np.asarray(artery) > 0, np.asarray(vein) > 0
        side = artery.shape[0]
        x, y, radius = (float(value) for value in disc)
        layers = {
            "arteries": VesselTreeLayer("arteries", artery, color=(1, 0, 0)),
            "veins": VesselTreeLayer("veins", vein, color=(0, 0, 1)),
            # The union is formed here rather than taken as given.
            "vessels": FundusVesselsLayer(name="vessels", mask=(artery | vein)),
        }
        retina = Retina(
            disc_path_or_mask=self._disc_mask(side, x, y, radius).astype(np.uint8),
            layers=layers,
            resolution=(side, side),
            mm_per_pixel=None if um_per_px is None else um_per_px * MM_PER_UM,
            fovea_location=self._fovea(side, x, y),
            roi_mask=np.asarray(fov).astype(np.uint8),
        )
        # See the class docstring: its optic disc defaults to 1024 pixels whatever the retina is.
        from rtnls_enface.disc import OpticDisc

        retina.disc = OpticDisc(
            self._disc_mask(side, x, y, radius).astype(np.uint8), fundus=retina, size=side
        )
        found: dict[str, float | None] = {}
        for feature_set in FEATURE_SETS:
            # It catches every feature's exception itself and says so in a warning; those
            # warnings are the only record of why a column is empty, so they are kept.
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                answered = retina.calc_features(getattr(sets, feature_set))
            for warned in caught:
                message = str(warned.message)
                if message.startswith("Error computing feature"):
                    self.trouble[f"{feature_set}: {message[:80]}"] = message
            for name, value in answered.items():
                found.setdefault(name, _number(value))
        return found

    def _fovea(self, side: int, x: float, y: float) -> tuple[float, float]:
        """The fovea this fixture implies. See `FOVEA` for why it is a convention."""
        # Pixel i's centre is at i, so the frame's centre is half a pixel short of side / 2.
        centre = (side - 1) / 2.0
        if abs(x - centre) < self.CENTRED_WITHIN and abs(y - centre) < self.CENTRED_WITHIN:
            # A disc-centred framing: put the macula where a macula-centred framing would have had
            # the disc relative to it, so the separation is the one the other shapes use. The
            # synthetic frame spans the field of view, which is what turns microns into pixels.
            from benchmarks.shapes import scene

            offset = scene.MACULA_CENTRED_DISC[0] / scene.FOV_DIAMETER_UM * side
            return (centre - offset, centre)
        return (centre, centre)

    @staticmethod
    def _disc_mask(side: int, x: float, y: float, radius: float) -> np.ndarray:
        # Pixel i's centre is at i — the convention the disc is handed over in.
        grid = np.arange(side, dtype=np.float64)
        px, py = np.meshgrid(grid, grid)
        return (px - x) ** 2 + (py - y) ** 2 <= radius * radius

    @staticmethod
    def _in_pixels(
        answers: dict[str, float | None], um_per_px: float | None
    ) -> dict[str, float | None]:
        """The lengths VascX reports in millimetres, put back onto the pixel grid.

        Every adapter in this repository reports what its implementation measured **in pixels**,
        and the analysis is where a pixel value meets the microns its canonical name is in — one
        conversion, in one place, driven by `canonical.length_power`. VascX is the only upstream
        that hands back a physical length, so it is the only adapter that converts, and it
        converts *towards* pixels rather than away from them so that it lines up with its five
        siblings. Exact rather than approximate: the scale used is the one the shape was built
        with. Every other column is left as VascX returned it.
        """
        if not um_per_px:
            return answers
        per_pixel_mm = um_per_px * MM_PER_UM
        for own, value in answers.items():
            if value is not None and own.startswith(IN_MILLIMETRES):
                answers[own] = value / per_pixel_mm
        return answers

    def _loaded(self):
        if self._parts is None:
            self._parts = upstream.features()
        return self._parts

    def release(self) -> None:
        self._parts = None


def _number(value: object) -> float | None:
    try:
        found = float(value)
    except (TypeError, ValueError):
        return None
    return None if not np.isfinite(found) else found


def implementation(**arguments: object) -> Vascx:
    return Vascx(**arguments)
