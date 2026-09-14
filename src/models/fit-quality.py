# ABOUTME: The Fundus Image Toolbox quality ensemble: ten networks returning one confidence that a
# ABOUTME: photograph is gradeable, which this reads into the atlas's own vocabulary.

import numpy as np
import torch

from upstreams import fit
from upstreams.utils import weights

from .utils.device import pick
from .utils.grading import FAILED, Grade

#: The store grid this reads, and the grid the networks see. The toolbox's default is 512 and it
#: keeps that default for compatibility with its own earlier release rather than because it suits
#: every image, so it is recorded rather than chosen here.
GRID = 512

#: Above this confidence the toolbox calls a photograph gradeable. Its own default, and its authors
#: are explicit that the threshold does not transfer between datasets — which is why the benchmark
#: also reports a ranking metric that does not depend on it.
THRESHOLD = 0.5


class FitQuality:
    """Ten torchvision classifiers whose mean confidence is the answer.

    Binary: it says how confident it is that the photograph is worth measuring, and names no grade,
    so nothing here invents a three-way verdict it did not give.
    """

    slug = "fit-quality"
    purpose = "quality"
    grid = GRID

    def __init__(self, device: str | None = None) -> None:
        self.device = pick(device)
        self._ensemble: list | None = None

    def declare(self) -> dict[str, object]:
        return {
            "slug": self.slug,
            "purpose": self.purpose,
            "grid": self.grid,
            "network_grid": GRID,
            "grades": "gradeable against ungradeable",
            "emits_probabilities": True,
            "threshold": THRESHOLD,
            "gate": (
                f"the toolbox's own default threshold of {THRESHOLD} on its confidence. No "
                f"catalogued pipeline runs this model; the toolbox is a library, and the "
                f"threshold is what its own inference applies"
            ),
            "ensemble": 10,
            "device": self.device,
            "upstream": fit.provenance(),
        }

    def identity(self) -> str:
        """The weights this will load, fetched if they are not there yet."""
        return weights.digest(fit.quality_weights())

    def prepare(self, pixels: np.ndarray) -> torch.Tensor:
        """A photograph as the toolbox's own batch path expects it: channels first, 0 to 1.

        The resize, the centre crop and the normalisation are the toolbox's, applied inside its
        own inference from the training transforms; nothing is done for it here. The batch stays
        on the processor it was built on, because the toolbox turns each photograph back into a
        PIL image before it moves anything to its own device.
        """
        return torch.from_numpy(pixels.transpose(2, 0, 1).copy()).float() / 255.0

    def grade(self, images: torch.Tensor, keys: list[str]) -> list[Grade]:
        from fundus_image_toolbox.quality_prediction import ensemble_predict_quality

        try:
            confidence, _ = ensemble_predict_quality(self._loaded(), list(images), img_size=GRID)
        except Exception as failure:  # a crash is the model's answer to nothing
            return [Grade(key, outcome=FAILED, note=repr(failure)) for key in keys]
        return self.interpret(keys, np.atleast_1d(np.asarray(confidence, dtype=float)))

    @staticmethod
    def interpret(keys: list[str], confidence: np.ndarray) -> list[Grade]:
        """The ensemble's mean confidence, read as the atlas reads every quality model."""
        return [
            Grade(key, gradeable=float(value), gated=bool(value >= THRESHOLD))
            for key, value in zip(keys, confidence, strict=True)
        ]

    def _loaded(self) -> list:
        if self._ensemble is None:
            self._ensemble = fit.quality_ensemble(device=self.device)
        return self._ensemble


def model(**arguments: object) -> FitQuality:
    return FitQuality(**arguments)
