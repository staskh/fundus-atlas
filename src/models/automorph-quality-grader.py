# ABOUTME: AutoMorph's quality grader: eight EfficientNet seeds whose averaged softmax grades a
# ABOUTME: photograph Good, Usable or Reject, run here as a model without the pipeline around it.

import numpy as np
import torch

from upstreams import automorph
from upstreams.utils import weights

from .utils.device import pick
from .utils.grading import BAD, FAILED, GOOD, USABLE, Grade

#: The store grid this reads, and the grid the networks see. AutoMorph reaches it by resizing its
#: own 912-diameter preprocessed image; the store's photographs are already cropped to the field
#: of view and square, which is the same thing arrived at by a different route.
GRID = 512

#: The order of the network's three outputs, from the columns AutoMorph writes them into. Its
#: third class is named Reject, which is this atlas's `bad`.
COLUMNS = (GOOD, USABLE, BAD)

#: How much `bad` AutoMorph tolerates in a photograph its grader called merely usable before
#: dropping it. From `merge_quality_assessment.py`, which is the stage that actually decides what
#: gets measured: a `good` verdict passes, a `usable` one passes only under this, and everything
#: else is copied to `Bad_quality/` and never reaches a segmentation model.
TOLERATED_BAD = 0.25


class AutoMorphQualityGrader:
    """Eight seeds of an EfficientNet-b4 classifier, their softmax outputs averaged.

    AutoMorph's pipeline drops a photograph before this stage when its own preprocessing cannot
    find a fundus. That gate is not this model and is not run here: the store's field-of-view crop
    stands in its place, so every photograph reaches the grader and coverage is not this model's
    to lose.
    """

    slug = "automorph-quality-grader"
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
            "grades": "good, usable, reject",
            "emits_probabilities": True,
            "ensemble": 8,
            "gate": (
                f"AutoMorph's own rule, which is not this model's argmax: a `good` verdict is "
                f"carried into measurement, a `usable` one only while the probability of `bad` "
                f"stays under {TOLERATED_BAD}, and everything else is dropped before any "
                f"segmentation model sees it"
            ),
            "device": self.device,
            "upstream": automorph.provenance(),
        }

    def identity(self) -> str:
        return weights.digest(automorph.quality_weights())

    def prepare(self, pixels: np.ndarray) -> torch.Tensor:
        """AutoMorph's own preparation: standardise by the photograph's own lit pixels.

        The mean and deviation are taken over the pixels above zero, jointly across the three
        channels, so the surround the store already blacked out does not drag the image's
        brightness with it — which is what the upstream's dataset does before every inference.
        """
        image = pixels.astype(np.float32)
        lit = image[image > 0]
        image = (image - lit.mean()) / lit.std()
        return torch.from_numpy(image.transpose(2, 0, 1).copy())

    @staticmethod
    def _carried(classes: dict[str, float], verdict: str) -> bool:
        """AutoMorph's own gate, which is not this model's argmax."""
        if verdict == GOOD:
            return True
        return verdict == USABLE and classes[BAD] < TOLERATED_BAD

    def grade(self, images: torch.Tensor, keys: list[str]) -> list[Grade]:
        try:
            batch = images.to(self.device, dtype=torch.float32)
            with torch.no_grad():
                members = [
                    torch.softmax(member(batch), dim=1).cpu().numpy() for member in self._loaded()
                ]
        except Exception as failure:
            return [Grade(key, outcome=FAILED, note=repr(failure)) for key in keys]
        return self.interpret(keys, np.mean(members, axis=0))

    @staticmethod
    def interpret(keys: list[str], probabilities: np.ndarray) -> list[Grade]:
        """The eight seeds' mean softmax, read into the atlas's vocabulary."""
        graded = []
        for key, row in zip(keys, probabilities, strict=True):
            classes = dict(zip(COLUMNS, (float(value) for value in row), strict=True))
            verdict = max(classes, key=classes.get)
            graded.append(
                Grade(
                    key,
                    verdict=verdict,
                    gradeable=classes[GOOD] + classes[USABLE],
                    classes=classes,
                    gated=AutoMorphQualityGrader._carried(classes, verdict),
                )
            )
        return graded

    def _loaded(self) -> list:
        if self._ensemble is None:
            stage = automorph.quality_stage()
            self._ensemble = []
            for checkpoint in automorph.quality_weights():
                member = stage.Efficientnet_fl(pretrained=True)
                member.load_state_dict(torch.load(checkpoint, map_location=self.device))
                self._ensemble.append(member.to(self.device).eval())
        return self._ensemble


def model(**arguments: object) -> AutoMorphQualityGrader:
    return AutoMorphQualityGrader(**arguments)
