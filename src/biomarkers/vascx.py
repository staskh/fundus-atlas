# ABOUTME: VascX's feature machinery, reached from this repository: one pass over a retina built
# ABOUTME: from the masks, and the table saying what each of its feature names answers to.

import numpy as np

from upstreams import vascx as upstream

#: The shipped feature set this adapter runs: the disc-centred one, which is the framing every
#: disc-anchored measurement here is stated in. It is used as VascX ships it rather than assembled
#: from parts, so what is measured is a configuration its authors published.
FEATURE_SET = "fs_od_centered"

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
    f"lw_diam_{CIRCLE}_full_{{layer}}": "vessel-calibre/mean-width/{side}",
    # *Our finding, 2026-09-22, from reading `cre.py`:* despite the module's name and the project
    # page's description of a "Hubbard reduction", it combines pairs as `c·√(d₁² + d₂²)` with
    # c = 0.88 for arteries and 0.95 for veins — which **is** Knudtson's formula. Hubbard's carries
    # fitted constants and an additive term, and neither appears here.
    "full_cre_{layer}": "central-retinal-equivalents/knudtson/{side}",
    # Arc over chord, length-weighted across segments, with segments capped at 0.2 disc diameters.
    # Three caps are shipped; this is the middle one, and the other two are kept unmapped beside it
    # so a reader can see how little the cap changes the answer.
    f"lw_tort_dist_max_segment_len_0p2_{CIRCLE}_full_{{layer}}": "tortuosity/hart-tau1/{side}",
    f"lw_tort_dist_max_segment_len_0p15_{CIRCLE}_full_{{layer}}": None,
    f"lw_tort_dist_max_segment_len_0p25_{CIRCLE}_full_{{layer}}": None,
    f"lw_tort_curv_{CIRCLE}_full_{{layer}}": "tortuosity/spline-mean-curvature/{side}",
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
    "mean_sparsity_vessels": None,
    f"mean_sparsity_{CIRCLE}_full_vessels": None,
}

#: VascX's layer names, and the structure each answers for.
LAYERS = {"arteries": "artery", "veins": "vein"}

#: Millimetres per micron, for the one conversion this adapter makes. See `Vascx.measure`.
MM_PER_UM = 0.001


def _answers() -> dict[str, str]:
    """Answered name → the VascX feature behind it."""
    pairs: dict[str, str] = {}
    for layer, side in LAYERS.items():
        for template, mapped in NAMES.items():
            own = template.format(layer=layer)
            pairs[mapped.format(side=side) if mapped else own] = own
    for own in RETINA_NAMES:
        pairs[own] = own
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
    own: (answered if "/" in answered else None) for answered, own in ANSWERS.items()
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
            "feature_set": FEATURE_SET,
            "circle": "1.1667 disc diameters from the disc centre",
            "fovea": self.FOVEA,
            "units": {
                "vessel-calibre/mean-width": "px, converted from VascX's mm by the shape's scale",
                "central-retinal-equivalents/knudtson": "px, likewise",
                "everything else": "as VascX returns it",
            },
            "device": self.device,
            "upstream": upstream.provenance(),
        }

    def identity(self) -> str:
        return str(upstream.provenance().get("version") or upstream.provenance().get("commit"))

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
        found = retina.calc_features(getattr(sets, FEATURE_SET))
        return {name: _number(value) for name, value in found.items()}

    def _fovea(self, side: int, x: float, y: float) -> tuple[float, float]:
        """The fovea this fixture implies. See `FOVEA` for why it is a convention."""
        centre = side / 2.0
        if abs(x - centre) < self.CENTRED_WITHIN and abs(y - centre) < self.CENTRED_WITHIN:
            # A disc-centred framing: put the macula where a macula-centred framing would have had
            # the disc relative to it, so the separation is the one the other shapes use.
            from benchmarks.shapes import library

            offset = (library.DISC_AT[0] - 0.5) * side
            return (centre - offset, centre)
        return (centre, centre)

    @staticmethod
    def _disc_mask(side: int, x: float, y: float, radius: float) -> np.ndarray:
        grid = np.arange(side, dtype=np.float64) + 0.5
        px, py = np.meshgrid(grid, grid)
        return (px - x) ** 2 + (py - y) ** 2 <= radius * radius

    @staticmethod
    def _in_pixels(
        answers: dict[str, float | None], um_per_px: float | None
    ) -> dict[str, float | None]:
        """The two mapped lengths, from VascX's millimetres back into the pixels the theory is in.

        Exact rather than approximate: the scale used is the one the shape was built with. Every
        other column is left as VascX returned it.
        """
        if not um_per_px:
            return answers
        per_pixel_mm = um_per_px * MM_PER_UM
        for own, value in answers.items():
            # Decided by what the column *means* rather than by what it is called: VascX's own
            # names say nothing about units, and only the two lengths are converted.
            catalogued = CANONICAL.get(own) or ""
            if value is not None and catalogued.startswith(
                ("vessel-calibre/", "central-retinal-equivalents/")
            ):
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
