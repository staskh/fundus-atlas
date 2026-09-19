# ABOUTME: BF-Net: one seed of a binary-to-multi fusion network, whose four classes name background,
# ABOUTME: arteries, veins and the crossings that belong to both.

import numpy as np
import torch

from upstreams import bfnet
from upstreams.utils import weights

from .utils import fusion
from .utils.device import forget, pick
from .utils.outlines import Outlines

#: The store grid this reads. The networks see 720, which no store holds — the photograph at 1024
#: is resized down to it, as the upstream resizes its own input, and nothing is upsampled.
GRID = 1024

#: Which of the three published archives is run, and why: the only one trained on none of the
#: datasets this benchmark has a store for.
TRAINED_ON = bfnet.DEFAULT

#: The four channels it emits, established by measurement rather than read from a document.
CHANNELS = fusion.CLASSES


class BFNet:
    """One seed, three checkpoints: an artery branch and a vein branch fused into a main generator.

    The fourth class is the crossings, which an annotator marks as both vessels — so the artery
    this adapter answers with is the artery class plus the crossing class, and the vein likewise.
    That is the same rule the other artery/vein adapters follow, and it is what AutoMorph's own
    postprocessing does with the same network's output.

    AutoMorph goes on to delete specks under thirty pixels from the argmaxed masks. That is done to
    a thresholded mask and cannot be done to a probability, so it is not applied here: the
    benchmark measures what the network said.
    """

    slug = "bf-net"
    purpose = "artery/vein"
    grid = GRID
    structures = ("artery", "vein")

    def __init__(self, device: str | None = None) -> None:
        self.device = pick(device)
        self._seeds: list[fusion.Seed] | None = None

    def declare(self) -> dict[str, object]:
        return {
            "slug": self.slug,
            "purpose": self.purpose,
            "grid": self.grid,
            "network_grid": fusion.GRID,
            "structures": list(self.structures),
            "emits_probabilities": True,
            "resampling": "probabilities to native, bilinear, thresholded there",
            "threshold": 0.5,
            "channels": list(CHANNELS),
            "ensemble": f"one seed, trained on {TRAINED_ON}",
            "device": self.device,
            "upstream": bfnet.provenance(TRAINED_ON),
        }

    def identity(self) -> str:
        return weights.digest(bfnet.seed_weights(TRAINED_ON))

    def prepare(self, pixels: np.ndarray) -> torch.Tensor:
        return fusion.prepare(pixels)

    def outline(self, images: torch.Tensor, sides: list[int]) -> list[Outlines]:
        return self.interpret(fusion.probabilities(self._loaded(), images, self.device), sides)

    @staticmethod
    def interpret(probabilities: np.ndarray, sides: list[int]) -> list[Outlines]:
        return fusion.vessels(probabilities, sides)

    def _loaded(self) -> list[fusion.Seed]:
        if self._seeds is None:
            self._seeds = fusion.seeds(
                bfnet.architecture(), [bfnet.seed_folder(TRAINED_ON)], self.device
            )
        return self._seeds

    def release(self) -> None:
        self._seeds = None
        forget()


def model(**arguments: object) -> BFNet:
    return BFNet(**arguments)
