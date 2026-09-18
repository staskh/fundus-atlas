# ABOUTME: OCULARNet: a RepVGG-b3 U-Net that names arteries, veins and their crossings at 1024,
# ABOUTME: averaged over four flips of every photograph as its own inference script does.

import numpy as np
import torch

from upstreams import ocular
from upstreams.utils import weights

from .utils.device import forget, pick
from .utils.outlines import Outlines

#: The store grid this reads, and the grid the network sees. Its own script resizes to this only
#: when `--resize` is passed — off by default, which its page records as a trap — and 1024 is the
#: grid it was trained on, so the store's `1024/` is handed over as it is.
GRID = 1024

#: ImageNet's statistics, from `norm_fn` in its `inference.py`.
MEAN = (0.485, 0.456, 0.406)
DEVIATION = (0.229, 0.224, 0.225)

#: Its four exclusive classes, in the order `postprocess_prediction` writes them out. Documented by
#: the upstream rather than inferred here, unusually for this catalogue.
CHANNELS = ocular.CLASSES

#: Its own inference averages the logits over the photograph and its three flips before the softmax.
FLIPS = ((-1,), (-2,), (-1, -2))


class Ocularnet:
    """One network, four exclusive classes, arteries and veins with their crossings between them.

    The classes are exclusive and a crossing is its own, while an annotator marks a crossing as both
    vessels — so the artery this adapter answers with is the artery class **plus** the crossing
    class, and the vein likewise. That is the region the expert drew, and it is the same rule the
    disc adapters use for a ring and the cup inside it.
    """

    slug = "ocularnet"
    purpose = "artery/vein"
    grid = GRID
    structures = ("artery", "vein")

    def __init__(self, device: str | None = None) -> None:
        self.device = pick(device)
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
            "ensemble": "one model, averaged over four flips of the photograph",
            "architecture": ocular.ARCHITECTURE,
            "device": self.device,
            "upstream": ocular.provenance(),
        }

    def identity(self) -> str:
        return weights.digest([ocular.model_file()])

    def prepare(self, pixels: np.ndarray) -> torch.Tensor:
        """Its own preparation: scale to 0 to 1, then standardise by ImageNet's statistics."""
        image = pixels.astype(np.float32).transpose(2, 0, 1) / 255.0
        standardised = (image - np.reshape(MEAN, (3, 1, 1))) / np.reshape(DEVIATION, (3, 1, 1))
        return torch.from_numpy(standardised.astype(np.float32))

    def outline(self, images: torch.Tensor, sides: list[int]) -> list[Outlines]:
        batch = images.to(self.device, dtype=torch.float32)
        network = self._loaded()
        with torch.no_grad():
            logits = network(batch)
            for flip in FLIPS:
                logits = logits + network(batch.flip(dims=flip)).flip(dims=flip)
            probabilities = torch.softmax(logits / (1 + len(FLIPS)), dim=1).cpu().numpy()
        return self.interpret(probabilities, sides)

    @staticmethod
    def interpret(probabilities: np.ndarray, sides: list[int]) -> list[Outlines]:
        """The softmax over four exclusive classes, read as two vessels sharing their crossings."""
        artery, vein, crossing = (CHANNELS.index(name) for name in ("artery", "vein", "crossing"))
        return [
            Outlines.from_probabilities(
                {
                    "artery": found[artery] + found[crossing],
                    "vein": found[vein] + found[crossing],
                },
                side=side,
            )
            for found, side in zip(probabilities, sides, strict=True)
        ]

    def _loaded(self):
        if self._network is None:
            network = ocular.architecture()
            checkpoint = torch.load(ocular.model_file(), map_location=self.device)
            state = checkpoint.get("model_state_dict", checkpoint)
            network.load_state_dict(state)
            self._network = network.to(self.device).eval()
        return self._network

    def release(self) -> None:
        self._network = None
        forget()


def model(**arguments: object) -> Ocularnet:
    return Ocularnet(**arguments)
