# ABOUTME: LUNet v2's optic disc model, an ONNX file PVBM reads one channel of — and this adapter
# ABOUTME: reads two of, because the second is a cup nobody catalogued.

import numpy as np
import torch

from upstreams import lunetv2
from upstreams.utils import weights

from .utils.device import forget
from .utils.outlines import Outlines

#: The store grid this reads, and the grid the network sees. PVBM resizes any photograph to this
#: square with the aspect ratio ignored; the store's photographs are already square.
GRID = 512

#: What each output channel holds, established by measuring them against PAPILA's outlines rather
#: than read from any documentation: there is none. PVBM uses channel 0 and ignores the rest, and
#: the file's name — `odc`, for disc **and cup** — turns out to be accurate.
#:
#: The other two channels were never trained: they answer the same thing for a photograph, a grey
#: square and random noise alike, and sit on the decision boundary so that a threshold hands each of
#: them about half the frame. They are read past rather than thresholded.
CHANNELS = {"disc": 0, "cup": 1}

#: ImageNet's statistics, as PVBM's `DiscSegmenter.segment` normalises with them.
MEAN = (0.485, 0.456, 0.406)
DEVIATION = (0.229, 0.224, 0.225)


class LunetV2Disc:
    """One network, four channels, independent rather than exclusive.

    They do not sum to one: each channel is its own logit, and the disc channel already contains
    the cup, so nothing is added together here. Reading all four as one softmax would be the
    ordinary assumption and is wrong: the two untrained channels sit at zero while the disc sits
    around −19, so they would take almost the whole frame and erode the disc.

    PVBM, the only catalogued project that runs this file, reads channel 0 and never looks at the
    cup. Measuring the cup here is therefore a measurement of the model rather than of anything
    PVBM reports.
    """

    slug = "lunetv2-odc"
    purpose = "disc/cup"
    grid = GRID
    structures = ("disc", "cup")

    def __init__(self, device: str | None = None) -> None:
        #: Recorded as asked for and not as used: the file runs on the CPU provider either way.
        self.device = "cpu"
        self._session = None

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
            "ensemble": 1,
            "channels": dict(CHANNELS),
            "device": self.device,
            "upstream": lunetv2.provenance(),
        }

    def identity(self) -> str:
        return weights.digest([lunetv2.model_file()])

    def prepare(self, pixels: np.ndarray) -> torch.Tensor:
        """PVBM's own preparation: scale to 0 to 1, then standardise by ImageNet's statistics."""
        image = pixels.astype(np.float32).transpose(2, 0, 1) / 255.0
        standardised = (image - np.reshape(MEAN, (3, 1, 1))) / np.reshape(DEVIATION, (3, 1, 1))
        return torch.from_numpy(standardised.astype(np.float32))

    def outline(self, images: torch.Tensor, sides: list[int]) -> list[Outlines]:
        emitted = self._loaded().run(None, {"images": images.numpy()})[0]
        return self.interpret(1.0 / (1.0 + np.exp(-emitted)), sides)

    @staticmethod
    def interpret(probabilities: np.ndarray, sides: list[int]) -> list[Outlines]:
        """Each channel's own sigmoid, read as two structures one of which contains the other."""
        return [
            Outlines.from_probabilities(
                {name: found[channel] for name, channel in CHANNELS.items()}, side=side
            )
            for found, side in zip(probabilities, sides, strict=True)
        ]

    def _loaded(self):
        if self._session is None:
            self._session = lunetv2.session()
            named = [entry.name for entry in self._session.get_inputs()]
            channels = self._session.get_outputs()[0].shape[1]
            if named != ["images"] or channels <= max(CHANNELS.values()):
                raise RuntimeError(
                    f"the file takes {named} and emits {channels} channels, which is not what this "
                    f"adapter reads; measure the channels again before changing either"
                )
        return self._session

    def release(self) -> None:
        self._session = None
        forget()


def model(**arguments: object) -> LunetV2Disc:
    return LunetV2Disc(**arguments)
