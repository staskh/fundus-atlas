# ABOUTME: VascX's quality model: a three-class classifier run on the 1024-square the rest of VascX
# ABOUTME: works on, which its own shipped configuration then resizes to 224 before the network.

import numpy as np
import torch

from upstreams import vascx
from upstreams.utils import weights

from .utils.device import forget, pick
from .utils.grading import BAD, FAILED, GOOD, USABLE, Grade

#: The store grid this reads. VascX preprocesses every photograph so that the fundus diameter
#: fills a 1024-pixel square, which is what the store's ``1024/`` already is.
GRID = 1024

#: What the network itself sees. The checkpoint's own configuration resizes the 1024-pixel square
#: to 224 before inference, which no documentation of this model states.
NETWORK_GRID = 224

#: The preparation the checkpoint's configuration asks for, verified against it on every run so
#: that these constants cannot drift from the weights.
PREPARATION = {"square_size": GRID, "resize": NETWORK_GRID, "contrast_enhance": False}

#: The order of the three outputs. The shipped configuration names EyeQ as the data this model was
#: trained on, and EyeQ grades Good, Usable and Reject in that order; nothing in the checkpoint
#: states the order outright, so the benchmark reports the confusion that would expose it if this
#: assumption were wrong.
COLUMNS = (GOOD, USABLE, BAD)


class VascxQuality:
    """One TorchScript file holding an ensemble, scored through VascX's own test transform."""

    slug = "vascx-quality"
    purpose = "quality"
    grid = GRID

    def __init__(self, device: str | None = None) -> None:
        self.device = pick(device)
        self._ensemble = None
        self._transform = None

    def declare(self) -> dict[str, object]:
        return {
            "slug": self.slug,
            "purpose": self.purpose,
            "grid": self.grid,
            "network_grid": NETWORK_GRID,
            "grades": "three classes, read as good, usable and bad",
            "emits_probabilities": True,
            "named_grades": COLUMNS,
            "ensemble": "one checkpoint holding several folds",
            "gate": (
                "none. VascX writes the three outputs to `quality.csv` as raw logits named q1, q2 "
                "and q3, and nothing in the pipeline reads them again: no photograph is refused "
                "and no biomarker is withheld on their account"
            ),
            "device": self.device,
            "upstream": vascx.provenance(),
        }

    def identity(self) -> str:
        return weights.digest([vascx.quality_weights()])

    def prepare(self, pixels: np.ndarray) -> torch.Tensor:
        """VascX's own test transform: the resize to 224 and the ImageNet normalisation."""
        return self._prepared()(image=pixels)["image"]

    def grade(self, images: torch.Tensor, keys: list[str]) -> list[Grade]:
        try:
            with torch.no_grad():
                logits = self._loaded().forward(images.to(self.device))
            averaged = torch.softmax(torch.mean(logits, dim=0), dim=1).cpu().numpy()
        except Exception as failure:
            return [Grade(key, outcome=FAILED, note=repr(failure)) for key in keys]
        return self.interpret(keys, averaged)

    @staticmethod
    def interpret(keys: list[str], probabilities: np.ndarray) -> list[Grade]:
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

    def _prepared(self):
        if self._transform is None:
            from rtnls_inference.transforms import FundusTestTransform

            self._transform = FundusTestTransform(preprocess=False, **PREPARATION)
        return self._transform

    def _loaded(self):
        if self._ensemble is None:
            ensemble = vascx.quality_ensemble(device=self.device)
            asked = ensemble.config["datamodule"]["test_transform"]
            differs = {
                name: (asked.get(name), value)
                for name, value in PREPARATION.items()
                if asked.get(name) != value
            }
            if differs:
                raise RuntimeError(
                    f"the checkpoint asks for {differs}, which is not how this adapter prepares "
                    f"its input; read the configuration before changing either"
                )
            self._ensemble = ensemble
        return self._ensemble

    def release(self) -> None:
        """Give back what this model loaded, for a run that has finished with it."""
        self._ensemble = None
        forget()


def model(**arguments: object) -> VascxQuality:
    return VascxQuality(**arguments)
