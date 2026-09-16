# ABOUTME: A SegFormer fine-tuned for the optic disc and cup: one network, three classes, and a
# ABOUTME: decode head that answers on a quarter-scale grid however large the photograph was.

import numpy as np
import torch

from upstreams import segformer
from upstreams.utils import weights

from .utils.device import forget, pick
from .utils.outlines import Outlines

#: The store grid this reads, and the grid the network sees: its own processor resizes to this.
GRID = 512

#: What the decode head answers on — a quarter of the input on each side. Every boundary this model
#: draws is a 128-grid boundary, whatever it is upsampled to afterwards.
DECODE_GRID = 128

#: ImageNet's statistics, from the repository's own `preprocessor_config.json`. Held here so that
#: preparation is a pure function of the pixels, and checked against the published configuration
#: whenever the model is loaded.
MEAN = (0.485, 0.456, 0.406)
DEVIATION = (0.229, 0.224, 0.225)

#: What each output channel is, as the repository's configuration names them.
CHANNELS = {"Background": "background", "Optic disc": "disc", "Optic cup": "cup"}


class SegformerDiscCup:
    """One network answering for both structures, on a grid a quarter of what it was handed.

    Its three classes are **exclusive**, so the pixels it calls cup are not in its disc class,
    while the disc an ophthalmologist draws contains the cup. The disc measured here is therefore
    the disc class and the cup class together, which is the region the expert outlined.
    """

    slug = "segformer-disc-cup"
    purpose = "disc/cup"
    grid = GRID
    structures = ("disc", "cup")

    def __init__(self, device: str | None = None) -> None:
        self.device = pick(device)
        self._network = None

    def declare(self) -> dict[str, object]:
        return {
            "slug": self.slug,
            "purpose": self.purpose,
            "grid": self.grid,
            "network_grid": GRID,
            "decode_grid": DECODE_GRID,
            "structures": list(self.structures),
            "emits_probabilities": True,
            "resampling": "probabilities to native, bilinear, thresholded there",
            "threshold": 0.5,
            "ensemble": 1,
            "device": self.device,
            "upstream": segformer.provenance(),
        }

    def identity(self) -> str:
        return weights.digest([segformer.weights()])

    def prepare(self, pixels: np.ndarray) -> torch.Tensor:
        """The processor's own preparation: scale to 0 to 1, then standardise by ImageNet's."""
        image = pixels.astype(np.float32).transpose(2, 0, 1) / 255.0
        standardised = (image - np.reshape(MEAN, (3, 1, 1))) / np.reshape(DEVIATION, (3, 1, 1))
        return torch.from_numpy(standardised.astype(np.float32))

    def outline(self, images: torch.Tensor, sides: list[int]) -> list[Outlines]:
        with torch.no_grad():
            emitted = self._loaded()(pixel_values=images.to(self.device)).logits
        return self.interpret(torch.softmax(emitted, dim=1).cpu().numpy(), sides)

    @staticmethod
    def interpret(probabilities: np.ndarray, sides: list[int]) -> list[Outlines]:
        """The softmax over three exclusive classes, read as a disc containing a cup."""
        order = list(CHANNELS.values())
        disc, cup = order.index("disc"), order.index("cup")
        return [
            Outlines.from_probabilities(
                {"disc": found[disc] + found[cup], "cup": found[cup]}, side=side
            )
            for found, side in zip(probabilities, sides, strict=True)
        ]

    def _loaded(self):
        if self._network is None:
            published = segformer.labels()
            named = [CHANNELS.get(published[index]) for index in sorted(published)]
            if named != list(CHANNELS.values()):
                raise RuntimeError(
                    f"the repository now emits {published}, which is not the three classes this "
                    f"adapter reads; read the configuration before changing either"
                )
            self._network = segformer.segmenter(self.device)
        return self._network

    def release(self) -> None:
        self._network = None
        forget()


def model(**arguments: object) -> SegformerDiscCup:
    return SegformerDiscCup(**arguments)
