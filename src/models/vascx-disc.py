# ABOUTME: VascX's optic disc model: a U-Net ensemble on the 1024-square VascX preprocesses to,
# ABOUTME: which its own configuration then resizes to 512 and hands the contrast-enhanced copy too.

import numpy as np
import torch

from upstreams import vascx
from upstreams.utils import weights

from .utils.device import forget, pick
from .utils.outlines import Outlines

#: The store grid this reads. VascX resamples every photograph so the fundus diameter fills a
#: 1024-pixel square, which is what the store's `1024/` already is.
GRID = 1024

#: What the network itself sees, from the checkpoint's own configuration.
NETWORK_GRID = 512

#: The preparation that configuration asks for, verified against it on every run. Unlike the
#: quality model, this one wants the contrast-enhanced copy of the photograph as well: the network
#: takes six channels, the photograph and its enhancement stacked.
PREPARATION = {"square_size": GRID, "resize": NETWORK_GRID, "contrast_enhance": True}

#: Where the weights are published, AGPL-3.0.
WEIGHTS = "Eyened/vascx:disc/disc_july24.pt"

#: The two output channels, in order.
CHANNELS = ("background", "disc")


class VascxDisc:
    """One structure only: the disc. It has no opinion about the cup and is absent from those
    tables rather than scored zero on them."""

    slug = "vascx-disc"
    purpose = "disc/cup"
    grid = GRID
    structures = ("disc",)

    def __init__(self, device: str | None = None) -> None:
        self.device = pick(device)
        self._ensemble = None
        self._transform = None

    def declare(self) -> dict[str, object]:
        return {
            "slug": self.slug,
            "purpose": self.purpose,
            "grid": self.grid,
            "network_grid": NETWORK_GRID,
            "structures": list(self.structures),
            "emits_probabilities": True,
            "resampling": "probabilities to native, bilinear, thresholded there",
            "ensemble": "one checkpoint holding several folds, with test-time flips",
            "device": self.device,
            "upstream": vascx.provenance(),
        }

    def identity(self) -> str:
        return weights.digest([vascx.model_file(WEIGHTS)])

    def prepare(self, pixels: np.ndarray) -> torch.Tensor:
        """The photograph and its contrast-enhanced copy, stacked, as the dataset would stack them."""
        item = self._prepared()(image=pixels)
        return torch.cat([item["image"], item["ce"]], dim=0)

    def outline(self, images: torch.Tensor, sides: list[int]) -> list[Outlines]:
        """One probability map per photograph, resampled to each one's own native frame."""
        with torch.no_grad():
            probabilities = self._loaded().predict_step({"image": images.to(self.device)})
        return [
            Outlines.from_probabilities(
                {"disc": probabilities[index, ..., CHANNELS.index("disc")].cpu().numpy()},
                side=side,
            )
            for index, side in enumerate(sides)
        ]

    def release(self) -> None:
        self._ensemble = None
        forget()

    def _prepared(self):
        if self._transform is None:
            from rtnls_inference.transforms import FundusTestTransform

            self._transform = FundusTestTransform(preprocess=False, **PREPARATION)
        return self._transform

    def _loaded(self):
        if self._ensemble is None:
            from rtnls_inference.ensembles.ensemble_segmentation import SegmentationEnsemble

            ensemble = SegmentationEnsemble.from_huggingface(WEIGHTS).to(self.device)
            asked = ensemble.config["datamodule"]["test_transform"]
            differs = {
                name: (asked.get(name), value)
                for name, value in PREPARATION.items()
                if asked.get(name) != value
            }
            if differs:
                raise RuntimeError(
                    f"the checkpoint asks for {differs}, which is not how this adapter prepares "
                    f"its input; read the configuration before changing either"
                )
            self._ensemble = ensemble.eval()
        return self._ensemble


def model(**arguments: object) -> VascxDisc:
    return VascxDisc(**arguments)
