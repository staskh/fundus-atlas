# ABOUTME: QuickQual: a frozen ImageNet DenseNet121 used as a feature extractor, with a support
# ABOUTME: vector machine over its features returning probabilities of Good, Usable and Bad.

import numpy as np
import torch
from torchvision.transforms import functional as F

from upstreams import quickqual as upstream
from upstreams.utils import weights

from .utils.device import forget, pick
from .utils.grading import BAD, FAILED, GOOD, USABLE, Grade

#: The store grid this reads. QuickQual resizes the shorter side to 512 and leaves the other
#: proportional; every photograph in a store is square, so the two amount to the same thing here.
GRID = 512

#: The order the classifier's columns come in, from the published example.
COLUMNS = (GOOD, USABLE, BAD)


class QuickQual:
    """Feature extraction and a small classifier, with nothing fine-tuned.

    The inference is five lines of the repository's README rather than a function it publishes, so
    those five lines are reproduced here — the pinned checkout is what they can be read against.
    """

    slug = "quickqual"
    purpose = "quality"
    grid = GRID

    def __init__(self, device: str | None = None) -> None:
        self.device = pick(device)
        self._backbone = None
        self._classifier = None

    def declare(self) -> dict[str, object]:
        return {
            "slug": self.slug,
            "purpose": self.purpose,
            "grid": self.grid,
            "network_grid": GRID,
            "grades": "good, usable, bad",
            "emits_probabilities": True,
            "named_grades": COLUMNS,
            "ensemble": 1,
            "gate": (
                "none. AutoMorphalyzer is the only catalogued pipeline that reaches for QuickQual, "
                "and it runs the MEME variant — a nine-feature linear model emitting one "
                "probability of `bad` — not this three-class classifier, and it writes that "
                "number into its results table without ever acting on it"
            ),
            "backbone": upstream.BACKBONE,
            "device": self.device,
            "upstream": upstream.provenance(),
        }

    def identity(self) -> str:
        return weights.digest([upstream.classifier()])

    def prepare(self, pixels: np.ndarray) -> torch.Tensor:
        """Resize the shorter side to 512 and normalise to mean and deviation one half."""
        image = F.to_tensor(pixels)
        image = F.resize(image, GRID, antialias=True)
        return F.normalize(image, [0.5] * 3, [0.5] * 3)

    def grade(self, images: torch.Tensor, keys: list[str]) -> list[Grade]:
        try:
            with torch.no_grad():
                features = self._loaded_backbone()(images.to(self.device))
            probabilities = self._loaded_classifier().predict_proba(
                features.cpu().numpy().reshape(len(keys), -1)
            )
        except Exception as failure:
            return [Grade(key, outcome=FAILED, note=repr(failure)) for key in keys]
        return self.interpret(keys, np.asarray(probabilities, dtype=float))

    @staticmethod
    def interpret(keys: list[str], probabilities: np.ndarray) -> list[Grade]:
        """Three probabilities per photograph, in the published column order."""
        graded = []
        for key, row in zip(keys, probabilities, strict=True):
            classes = dict(zip(COLUMNS, (float(value) for value in row), strict=True))
            graded.append(
                Grade(
                    key,
                    verdict=max(classes, key=classes.get),
                    gradeable=classes[GOOD] + classes[USABLE],
                    classes=classes,
                )
            )
        return graded

    def _loaded_backbone(self):
        if self._backbone is None:
            import timm

            self._backbone = (
                timm.create_model(upstream.BACKBONE, pretrained=True, num_classes=0)
                .eval()
                .to(self.device)
            )
        return self._backbone

    def _loaded_classifier(self):
        if self._classifier is None:
            import joblib

            self._classifier = joblib.load(upstream.classifier())
        return self._classifier

    def release(self) -> None:
        """Give back what this model loaded, for a run that has finished with it."""
        self._backbone = None
        self._classifier = None
        forget()


def model(**arguments: object) -> QuickQual:
    return QuickQual(**arguments)
