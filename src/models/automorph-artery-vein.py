# ABOUTME: AutoMorph's artery/vein model: eight seeds of BF-Net's architecture retrained on three
# ABOUTME: datasets at once, their softmax outputs averaged into one four-class answer.

import numpy as np
import torch

from upstreams import automorph
from upstreams.utils import weights

from .utils import fusion
from .utils.device import forget, pick
from .utils.outlines import Outlines

#: The store grid this reads. The networks see 720, which no store holds — the photograph at 1024
#: is resized down to it, as the upstream resizes its own input, and nothing is upsampled.
GRID = 1024

#: The four channels it emits, established by measurement rather than read from a document.
CHANNELS = fusion.CLASSES


class AutoMorphArteryVein:
    """Eight seeds of the same architecture, each a main generator fed by two branches.

    This is [BF-Net](../../docs/models/bf-net.md)'s network retrained by AutoMorph on DRIVE-AV,
    HRF-AV and LES-AV together — a training set they call `ALL-AV` — and shipped as eight random
    seeds rather than the one BF-Net publishes. So the two models share an architecture, a grid and
    a channel order, and differ in what they saw and in how many of them there are.

    The fourth class is the crossings, which an annotator marks as both vessels, so an artery here
    is the artery class plus the crossing class. AutoMorph's own pipeline reaches the same masks by
    a longer route: it argmaxes, writes red, green and blue channels, and then reads red-or-green as
    artery and blue-or-green as vein.

    What is left out is AutoMorph's speck removal — objects under thirty pixels, deleted from the
    argmaxed masks. It cannot be done to a probability, and the benchmark measures what the network
    said.
    """

    slug = "automorph-artery-vein"
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
            "ensemble": 8,
            "device": self.device,
            "upstream": automorph.provenance(),
        }

    def identity(self) -> str:
        return weights.digest(automorph.av_weights())

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
                automorph.av_architecture(), automorph.av_seeds(), self.device
            )
        return self._seeds

    def release(self) -> None:
        self._seeds = None
        forget()


def model(**arguments: object) -> AutoMorphArteryVein:
    return AutoMorphArteryVein(**arguments)
