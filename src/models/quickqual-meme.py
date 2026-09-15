# ABOUTME: QuickQual-MEME: nine of a frozen DenseNet121's features and ten numbers over them,
# ABOUTME: returning one probability that a photograph is bad. What AutoMorphalyzer actually runs.

import numpy as np
import torch
from torchvision.transforms import functional as F

from upstreams import quickqual as upstream
from upstreams.utils import weights

from .utils.device import forget, pick
from .utils.grading import FAILED, Grade

#: The store grid this reads. The published example resizes the shorter side to 512, which for a
#: square photograph is the whole of it.
GRID = 512


class QuickQualMeme:
    """The MEga Minified Estimator, and the only quality model in this catalogue with no classes.

    It answers one question with one number — how likely is this photograph to be bad — so it has
    no opinion at all about the difference between good and merely usable. That is the whole of
    what [AutoMorphalyzer](../../docs/projects/automorphalyzer.md) knows about image quality.
    """

    slug = "quickqual-meme"
    purpose = "quality"
    grid = GRID

    def __init__(self, device: str | None = None) -> None:
        self.device = pick(device)
        self._backbone = None
        self._parameters = None

    def declare(self) -> dict[str, object]:
        return {
            "slug": self.slug,
            "purpose": self.purpose,
            "grid": self.grid,
            "network_grid": GRID,
            "grades": "one probability that the photograph is bad",
            "emits_probabilities": True,
            "named_grades": (),
            "ensemble": 1,
            "backbone": upstream.BACKBONE,
            "device": self.device,
            "gate": (
                "AutoMorphalyzer carries **every** photograph into measurement. It writes this "
                "number into its results table as `QuickQual_quality`, recommends no threshold, "
                "and no code path filters on it — so every biomarker it publishes was computed "
                "whatever this model said. Measuring everything is a decision, and this is what "
                "it costs"
            ),
            "upstream": upstream.provenance(),
        }

    def identity(self) -> str:
        """What this model is, which is nine indices and ten numbers rather than a weight file.

        The frozen backbone is torchvision's ImageNet DenseNet121, identical for everyone who runs
        it; what makes this model itself is the handful of parameters read from the pinned
        repository, so those are what the run records.
        """
        found = self._published()
        return weights.digest_of(
            f"{found.features}{found.weights}{found.bias}{upstream.BACKBONE}".encode()
        )

    def prepare(self, pixels: np.ndarray) -> torch.Tensor:
        """Resize the shorter side to 512 and normalise to mean and deviation one half."""
        image = F.to_tensor(pixels)
        image = F.resize(image, GRID, antialias=True)
        return F.normalize(image, [0.5] * 3, [0.5] * 3)

    def grade(self, images: torch.Tensor, keys: list[str]) -> list[Grade]:
        found = self._published()
        try:
            with torch.no_grad():
                features = self._loaded()(images.to(self.device))
            chosen = features.cpu().reshape(len(keys), -1)[:, list(found.features)]
            bad = torch.sigmoid(
                chosen @ torch.tensor(found.weights, dtype=chosen.dtype) + found.bias
            )
        except Exception as failure:
            return [Grade(key, outcome=FAILED, note=repr(failure)) for key in keys]
        return self.interpret(keys, bad.numpy())

    @staticmethod
    def interpret(keys: list[str], bad: np.ndarray) -> list[Grade]:
        """One probability per photograph, read the way every quality model here is read.

        The model names no grade, so none is invented: what is recorded is its confidence that the
        photograph is worth measuring, which is one minus the number it emits.
        """
        return [
            Grade(key, gradeable=float(1.0 - value), gated=True)
            for key, value in zip(keys, bad, strict=True)
        ]

    def _published(self):
        if self._parameters is None:
            self._parameters = upstream.meme()
        return self._parameters

    def _loaded(self):
        if self._backbone is None:
            import timm

            self._backbone = (
                timm.create_model(upstream.BACKBONE, pretrained=True, num_classes=0)
                .eval()
                .to(self.device)
            )
        return self._backbone

    def release(self) -> None:
        """Give back what this model loaded, for a run that has finished with it."""
        self._backbone = None
        forget()


def model(**arguments: object) -> QuickQualMeme:
    return QuickQualMeme(**arguments)
