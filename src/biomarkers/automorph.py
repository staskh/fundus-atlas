# ABOUTME: AutoMorph's measuring stage, reached from this repository: retipy's whole-picture
# ABOUTME: evaluation per vessel map, and the table saying what each of its columns answers to.

import tempfile
from pathlib import Path

import numpy as np
from PIL import Image
from skimage.morphology import skeletonize

from upstreams import automorph as upstream

#: The three maps it is asked to measure, and the structure each answers for.
CLASSES = {"binary": "vessels", "artery": "artery", "vein": "vein"}

#: What `evaluate_window` returns, in order, and the catalogued biomarker each answers to.
#: `{side}` becomes `artery`, `vein` or `vessels`.
#:
#: These are the same six quantities AutoMorphalyzer and AutoMorphClass compute, which is what
#: makes the three comparable: both descend from this code.
COLUMNS: tuple[tuple[str, str | None], ...] = (
    ("fractal_dimension", "fractal-dimension/box-counting/{side}"),
    # Vessel pixels over every pixel of the frame — `vessel_density` never sees a field of view.
    ("vessel_density", "vascular-density/over-image/{side}"),
    ("average_width", "vessel-calibre/mean-width/{side}"),
    ("distance_tortuosity", "tortuosity/hart-tau1/{side}"),
    # *Our finding, 2026-09-21:* **not** Hart's τ3, despite the name. `squared_curvature_tortuosity`
    # squares nothing: it accumulates discrete curvature at each sample and integrates it over the
    # sample *index* rather than over arc length. It was mapped to τ3 until the shapes disagreed by
    # five orders of magnitude, and it does not match τ2 either — its ratio to the total curvature
    # is 10.3 on the arc and 2.0 on the sinusoid, so no constant relates them. Discrete curvature
    # on a pixel skeleton is its own quantity and the catalogue has no name for it.
    ("squared_curvature_tortuosity", None),
    ("tortuosity_density", "tortuosity/grisan-density/{side}"),
)

#: **AutoMorph's central retinal equivalents are not reachable.** Its zone stage returns per-vessel
#: width lists and the equivalents are assembled from them by a driver *script*
#: (`create_datasets.py`), not by any function this adapter could call. Reproducing that assembly
#: here would be measuring this repository's CRAE rather than AutoMorph's, which is the one thing
#: an adapter must never do — so the family is absent, and that is a finding rather than an
#: omission.
ABSENT = ("central-retinal-equivalents", "avr")


def _answers() -> dict[str, str]:
    """Answered name → the column and map behind it, as `<column>_<class>`."""
    pairs: dict[str, str] = {}
    for measured, side in CLASSES.items():
        for column, mapped in COLUMNS:
            own = f"{column}_{measured}"
            pairs[mapped.format(side=side) if mapped else own] = own
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


class Automorph:
    """AutoMorph's measuring stage, run as it ships.

    Its measuring code is retipy's, vendored rather than installed, and it reads its inputs **from
    files** in a directory layout it derives by string surgery: the skeleton's path must contain
    `_skeleton`, the vessel map is looked for at the same name under the store path, and the scale
    is read from an `M0/crop_info.csv` above the `M2` in that path. So each call lays that tree out
    in a temporary directory. None of it is a defect; it is what a stage of a pipeline looks like
    when it is called outside its pipeline.

    Two inputs the benchmark does not supply, and what is done about them:

    - **The skeleton.** AutoMorph's own M2 stage writes one; this adapter skeletonises the mask it
      was handed, with the same `skimage` routine its siblings use. An input, not a repair.
    - **The scale.** `global_cal` multiplies its width by the per-image `Scale_resolution`, so a
      scale of 1 is written and the width comes back **in pixels** — which is what the other two
      implementations report and what the shapes' theory is stated in. On a real photograph
      AutoMorph would report microns. Declared rather than applied quietly.
    """

    slug = "automorph"
    needs = ("artery", "vein")
    invariant = ("rotation",)

    #: What retipy's own configuration file sets, and what `evaluate_window` defaults to. They are
    #: numbers the measurement acts on, so they are declared rather than left inside a call.
    MIN_PIXELS_PER_VESSEL = 10
    SAMPLING_SIZE = 6
    R2_THRESHOLD = 0.80

    #: The scale written into `crop_info.csv`, and the reason the width is in pixels. See above.
    SCALE = 1.0

    #: The size retipy measures at, **whatever it is given**. `Retina._open_image` calls
    #: `cv2.resize(..., dsize=(912, 912), interpolation=cv2.INTER_CUBIC)` on every file it opens,
    #: so the mask that reaches the measuring code is a bicubically resampled copy of the mask this
    #: adapter wrote. Two things follow, and both belong in the reading of any number below:
    #:
    #: - **A pixel-valued width is in 912-pixels**, not in the pixels of the image it was handed.
    #:   On a 2048 frame a vessel 16 px across arrives about 7 px across.
    #: - **A binary mask does not survive bicubic interpolation**: the resampled copy has grey
    #:   edges, and thin vessels lose contrast against the background.
    #:
    #: The window is therefore built at this size, which is what AutoMorph itself does. Resizing
    #: the input first, or asking for a window the size of the frame, would both be this repository
    #: measuring something other than what AutoMorph measures.
    WORKING_SIZE = 912

    def __init__(self, device: str | None = None) -> None:
        self.device = "cpu"
        self.trouble: dict[str, str] = {}
        self._measures = None
        self._retina = None

    def declare(self) -> dict[str, object]:
        return {
            "slug": self.slug,
            "needs": list(self.needs),
            "invariant": list(self.invariant),
            "keys": list(self.keys()),
            "names": dict(CANONICAL),
            "calls": {own: [f"evaluate_{own.rsplit('_', 1)[-1]}"] for own in CANONICAL},
            "min_pixels_per_vessel": self.MIN_PIXELS_PER_VESSEL,
            "sampling_size": self.SAMPLING_SIZE,
            "r2_threshold": self.R2_THRESHOLD,
            "scale_written": self.SCALE,
            "working_size": self.WORKING_SIZE,
            "absent": list(ABSENT),
            "units": {"every measurement": "px"},
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
    ) -> dict[str, float | None]:
        """Its six measurements per map, under catalogued names, with `None` where it could not."""
        self.trouble = {}
        computed: dict[str, float | None] = dict.fromkeys(ANSWERS.values())
        maps = {
            "artery": artery,
            "vein": vein,
            "binary": None if artery is None and vein is None else _union(artery, vein),
        }
        for measured, mask in maps.items():
            if mask is None or not mask.any():
                continue
            try:
                for column, value in zip(
                    [name for name, _ in COLUMNS], self._one_map(mask, measured), strict=False
                ):
                    computed[f"{column}_{measured}"] = _number(value)
            except Exception as failure:  # noqa: BLE001 — a measurement that fell over has no value
                self.trouble[f"evaluate_{measured}"] = repr(failure)
        return {own: computed.get(own) for own in CANONICAL}

    def _one_map(self, mask: np.ndarray, measured: str) -> tuple:
        """One vessel map, through the file tree retipy insists on."""
        measures, retina = self._loaded()
        binary = np.asarray(mask) > 0
        with tempfile.TemporaryDirectory(prefix="automorph-") as where:
            root = Path(where)
            skeletons = root / "M2" / f"{measured}_skeleton"
            vessels = root / "M2" / f"{measured}_process"
            for directory in (root / "M0", skeletons, vessels):
                directory.mkdir(parents=True, exist_ok=True)
            name = f"{measured}.png"
            _write(vessels / name, binary)
            _write(skeletons / name, skeletonize(binary))
            # It reads the scale from here, finding the file by splitting the store path at `M2`.
            (root / "M0" / "crop_info.csv").write_text(
                f"Name,Scale_resolution\n{name},{self.SCALE}\n"
            )

            picture = retina.Retina(None, str(skeletons / name), store_path=str(vessels))
            # One window covering the whole picture, at the size retipy resampled it to.
            window = retina.Window(
                picture, self.WORKING_SIZE, min_pixels=self.MIN_PIXELS_PER_VESSEL
            )
            return measures.evaluate_window(
                window,
                self.MIN_PIXELS_PER_VESSEL,
                self.SAMPLING_SIZE,
                self.R2_THRESHOLD,
                store_path=str(vessels) + "/",
            )

    def _loaded(self):
        if self._measures is None:
            self._measures, self._retina = upstream.measurements()
        return self._measures, self._retina

    def release(self) -> None:
        self._measures = self._retina = None


def _write(path: Path, mask: np.ndarray) -> None:
    """A mask as an 8-bit PNG, which is what retipy's reader expects to find."""
    Image.fromarray((np.asarray(mask) > 0).astype(np.uint8) * 255).save(path)


def _union(artery: np.ndarray | None, vein: np.ndarray | None) -> np.ndarray:
    parts = [np.asarray(part) > 0 for part in (artery, vein) if part is not None]
    return parts[0] if len(parts) == 1 else parts[0] | parts[1]


def _number(value: object) -> float | None:
    try:
        found = float(value)
    except (TypeError, ValueError):
        return None
    return None if not np.isfinite(found) else found


def implementation(**arguments: object) -> Automorph:
    return Automorph(**arguments)
