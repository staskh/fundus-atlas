# ABOUTME: VascX's artery/vein model: a U-Net ensemble on the 1024-square VascX preprocesses to,
# ABOUTME: which it reads together with a contrast-enhanced copy of the same photograph.

import numpy as np
import torch

from upstreams import vascx
from upstreams.utils import weights

from .utils.device import forget, pick
from .utils.outlines import Outlines

#: The store grid this reads, and the grid the network sees. VascX resamples every photograph so the
#: fundus diameter fills a 1024-pixel square, which is what the store's `1024/` already is.
GRID = 1024

#: The preparation the checkpoint's own configuration asks for, verified against it on every load.
#: Unlike the disc model there is no `resize`: this network works at the full 1024.
PREPARATION = {"square_size": GRID, "contrast_enhance": True}

#: Where the weights are published, AGPL-3.0.
WEIGHTS = "Eyened/vascx:artery_vein/av_july24.pt"

#: What each output channel holds. **Established by measuring, not read from documentation**: the
#: channels were scored against [HRF](../datasets/hrf.md)'s own artery and vein annotation, where
#: channel 1 overlaps the arteries at Dice 0.78 against 0.04 for the veins, and channel 2 the
#: reverse. Channel 3 covers about a thousand pixels of a million and matches neither; VascX writes
#: no fifth class and this benchmark asks for none, so it is read past.
CHANNELS = ("background", "artery", "vein", "unclassified")


class VascxArteryVein:
    """One network, four channels, arteries and veins as separate probabilities.

    The vessel map this benchmark scores is the union of the two, derived the same way for every
    model, rather than any vessel output a project may also publish.
    """

    slug = "vascx-artery-vein"
    purpose = "artery/vein"
    grid = GRID
    structures = ("artery", "vein")

    def __init__(self, device: str | None = None) -> None:
        self.device = pick(device)
        self._ensemble = None
        self._transform = None

    def declare(self) -> dict[str, object]:
        return {
            "slug": self.slug,
            "purpose": self.purpose,
            "grid": self.grid,
            "network_grid": GRID,
            "structures": list(self.structures),
            "emits_probabilities": True,
            "resampling": "probabilities to native, bilinear, thresholded there",
            "threshold": 0.5,
            "channels": list(CHANNELS),
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
        """One probability map per vessel kind, resampled to each photograph's own native frame."""
        with torch.no_grad():
            probabilities = self._loaded().predict_step({"image": images.to(self.device)})
        return [
            Outlines.from_probabilities(
                {
                    name: probabilities[index, ..., CHANNELS.index(name)].cpu().numpy()
                    for name in self.structures
                },
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


def model(**arguments: object) -> VascxArteryVein:
    return VascxArteryVein(**arguments)
