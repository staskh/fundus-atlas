# ABOUTME: The SEGAN vessel segmenter as AutoMorph ships it: ten seeds emitting one vessel
# ABOUTME: probability per pixel, averaged, and thresholded at 0.2 rather than the 0.5 upstream uses.

import numpy as np
import torch
from PIL import Image

from upstreams import automorph
from upstreams.utils import weights

from .utils.device import forget, pick
from .utils.outlines import Outlines

#: The store grid this reads. The network sees 912, which no store holds — the photograph at 1024
#: is resized down to it, as the upstream resizes its own input, and nothing is upsampled.
GRID = 1024

#: The grid the network was trained at: `Define_image_size` in `M2_Vessel_seg/utils.py` returns
#: (912, 912) for every dataset, there being one uniform size and no other branch.
NETWORK_GRID = 912

#: Which pixels the upstream standardises by: those whose red channel is over this, which on a
#: photograph cropped to its field of view is the lit circle. `--pre_threshold=40.0` in
#: `test_outside.sh`.
LIT = 40.0

#: What this repository thresholds the averaged probability at, **which is not what AutoMorph
#: does**: its own `test_outside_integrated.py` writes a binary mask at 0.5. The model is run here
#: as a vessel reference rather than as a competitor, and a reference is more useful erring towards
#: the thin vessels a higher threshold drops than towards a clean-looking mask; 0.2 is the value
#: this atlas runs it at, and every score recorded for it is a score of the model at 0.2.
THRESHOLD = 0.2

#: What the upstream itself would have used, declared so that the difference is in the fingerprint
#: rather than only in this comment.
UPSTREAM_THRESHOLD = 0.5

#: The architecture's own arguments, as `test_outside_integrated.py` constructs all ten seeds.
INPUT_CHANNELS = 3
FILTERS = 32
CLASSES = 1
BILINEAR = False


class SeganVessel:
    """Ten seeds of a GAN-trained U-Net, each emitting one logit per pixel, their sigmoids averaged.

    This is the vessel stage of AutoMorph — the masks its own biomarker stages measure from — and
    it answers about **vessels only**: it does not separate arteries from veins and is never asked
    to. In the artery/vein benchmark it is a reference for the vessel column rather than an entry
    in the artery/vein one.

    Its vessel map is its own prediction. Every artery/vein model's vessel map is instead derived,
    as the union of that model's arteries and veins, so this one column is not produced the same
    way for every row of that benchmark — which is the point of having it, and is said plainly on
    the benchmark's pages.
    """

    slug = "segan-vessel"
    purpose = "vessels"
    grid = GRID
    structures = ("vessels",)

    def __init__(self, device: str | None = None) -> None:
        self.device = pick(device)
        self._seeds: list[object] | None = None

    def declare(self) -> dict[str, object]:
        return {
            "slug": self.slug,
            "purpose": self.purpose,
            "grid": self.grid,
            "network_grid": NETWORK_GRID,
            "structures": list(self.structures),
            "emits_probabilities": True,
            "resampling": "probabilities to native, bilinear, thresholded there",
            "threshold": THRESHOLD,
            "upstream_threshold": UPSTREAM_THRESHOLD,
            "lit_pixel_floor": LIT,
            "channels": ["vessel"],
            "ensemble": len(automorph.VESSEL_SEEDS),
            "device": self.device,
            "upstream": automorph.provenance(),
        }

    def identity(self) -> str:
        return weights.digest(automorph.vessel_weights())

    def prepare(self, pixels: np.ndarray) -> torch.Tensor:
        """The upstream's own preparation: resize to its grid, then standardise by the lit pixels.

        Unlike the artery/vein stage, which multiplies by the deviation where it means to divide,
        this one divides — so the two are not the same preparation and do not share a helper.
        """
        resized = np.asarray(
            Image.fromarray(pixels).resize((NETWORK_GRID, NETWORK_GRID))
        ).astype(np.float32)
        lit = resized[resized[..., 0] > LIT]
        if not lit.size:
            return torch.zeros((INPUT_CHANNELS, NETWORK_GRID, NETWORK_GRID), dtype=torch.float32)
        spread = np.std(lit, axis=0)
        spread[spread == 0] = 1.0
        standardised = (resized - np.mean(lit, axis=0)) / spread
        return torch.from_numpy(standardised.transpose(2, 0, 1).copy()).float()

    def outline(self, images: torch.Tensor, sides: list[int]) -> list[Outlines]:
        batch = images.to(self.device, dtype=torch.float32)
        averaged = None
        with torch.no_grad():
            for network in self._loaded():
                found = torch.sigmoid(network(batch)).cpu()
                averaged = found if averaged is None else averaged + found
        probabilities = (averaged / len(self._loaded())).numpy()[:, 0]
        return self.interpret(probabilities, sides)

    @staticmethod
    def interpret(
        probabilities: np.ndarray, sides: list[int], threshold: float = THRESHOLD
    ) -> list[Outlines]:
        """One averaged probability map per photograph, read as the one structure this model knows.

        :param threshold: the probability at which a pixel becomes vessel. It is an argument so
            that a test can show what the adjustment above does; nothing but a test passes it.
        """
        return [
            Outlines.from_probabilities({"vessels": one}, side=side, threshold=threshold)
            for one, side in zip(probabilities, sides, strict=True)
        ]

    def _loaded(self) -> list[object]:
        if self._seeds is None:
            architecture = automorph.vessel_architecture()
            loaded = []
            for checkpoint in automorph.vessel_weights():
                network = architecture(
                    input_channels=INPUT_CHANNELS,
                    n_filters=FILTERS,
                    n_classes=CLASSES,
                    bilinear=BILINEAR,
                )
                network.load_state_dict(torch.load(checkpoint, map_location=self.device))
                loaded.append(network.to(self.device).eval())
            self._seeds = loaded
        return self._seeds

    def release(self) -> None:
        self._seeds = None
        forget()


def model(**arguments: object) -> SeganVessel:
    return SeganVessel(**arguments)
