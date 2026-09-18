# ABOUTME: LUNet: a Keras U-Net on a 1472 grid — the largest in this catalogue — whose three output
# ABOUTME: channels are read as arteries and veins after being measured against an annotation.

import numpy as np
import torch

from upstreams import lunet
from upstreams.utils import weights

from .utils.device import forget
from .utils.outlines import Outlines

#: The store grid this reads, and the grid the network was built at: `final_shape = 1472` in its own
#: `main.py`, commented as the shape the images will be resized to. It is the point of the model —
#: arterioles a coarser grid cannot resolve — and it is why the artery/vein stores build 1472.
GRID = lunet.GRID

#: What each output channel holds, **established by measuring** against HRF's own artery and vein
#: annotation rather than read from documentation, which states none. The order is not the one a
#: reader would guess: the veins come first, and the third channel is a vessel map of the model's
#: own — which this benchmark does not use, since it derives `vessels` from the two classes
#: identically for every model.
CHANNELS = ("vein", "artery", "vessels")


#: The model emits **logits**, not probabilities: its output runs to about −180 and +11, so nothing
#: can be thresholded at a half until it has been through a sigmoid.
def _probabilities(logits: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-logits, dtype=np.float64))


class Lunet:
    """One Keras model, three channels, arteries and veins.

    It runs on the CPU through TensorFlow while every other model here runs on torch, which is a
    fact about the model rather than a choice: its checkpoint is a Keras 2.11 file and the Keras 2
    compatibility layer is what reads it.
    """

    slug = "lunet"
    purpose = "artery/vein"
    grid = GRID
    structures = ("artery", "vein")

    def __init__(self, device: str | None = None) -> None:
        #: Recorded as what it is rather than what was asked for: TensorFlow places the work itself.
        self.device = "tensorflow"
        self._network = None

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
            "ensemble": 1,
            "runtime": lunet.DECLINED_PIN,
            "device": self.device,
            "upstream": lunet.provenance(),
        }

    def identity(self) -> str:
        return weights.digest([lunet.model_file()])

    def prepare(self, pixels: np.ndarray) -> torch.Tensor:
        """Its own preparation, which is one division: `x / 255.0` and nothing else."""
        image = pixels.astype(np.float32).transpose(2, 0, 1) / 255.0
        return torch.from_numpy(image)

    def outline(self, images: torch.Tensor, sides: list[int]) -> list[Outlines]:
        # Keras wants the channels last; the loader hands over what every torch model expects.
        batch = images.permute(0, 2, 3, 1).cpu().numpy()
        emitted = self._loaded().predict(batch, verbose=0)
        return self.interpret(_probabilities(np.asarray(emitted).transpose(0, 3, 1, 2)), sides)

    @staticmethod
    def interpret(probabilities: np.ndarray, sides: list[int]) -> list[Outlines]:
        """The three channels, read as the two vessels this benchmark asks for.

        :param probabilities: after the sigmoid, since the model itself emits logits.
        """
        artery, vein = (CHANNELS.index(name) for name in ("artery", "vein"))
        return [
            Outlines.from_probabilities({"artery": found[artery], "vein": found[vein]}, side=side)
            for found, side in zip(probabilities, sides, strict=True)
        ]

    def _loaded(self):
        if self._network is None:
            self._network = lunet.loaded()
        return self._network

    def release(self) -> None:
        self._network = None
        forget()


def model(**arguments: object) -> Lunet:
    return Lunet(**arguments)
