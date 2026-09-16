# ABOUTME: What a disc-and-cup adapter answers with: one mask per structure, in the frame the
# ABOUTME: expert drew in, and the record of how it got there.

from dataclasses import dataclass, field

import numpy as np
import torch
import torch.nn.functional as F

#: What became of one prediction, on the same three terms every benchmark uses.
GRADED = "graded"
DECLINED = "declined"
FAILED = "failed"
OUTCOMES = (GRADED, DECLINED, FAILED)

#: Where a probability becomes a structure.
THRESHOLD = 0.5


@dataclass
class Outlines:
    """One model's answer about one photograph.

    The masks are in **native** coordinates, because that is where the expert drew and where every
    measurement is made. How they got there is recorded rather than assumed: a probability map
    resampled and then thresholded is not the same answer as a binary mask resampled, and the
    difference lands exactly on the boundary every metric turns on.
    """

    masks: dict[str, np.ndarray] = field(default_factory=dict)
    resampling: str = ""
    outcome: str = GRADED
    note: str = ""

    def __post_init__(self) -> None:
        if self.outcome not in OUTCOMES:
            raise ValueError(f"{self.outcome!r} is not one of {OUTCOMES}")
        if self.outcome != GRADED and self.masks:
            raise ValueError("a prediction that was not made carries no masks")

    @classmethod
    def from_probabilities(
        cls, probabilities: dict[str, np.ndarray], side: int, threshold: float = THRESHOLD
    ) -> "Outlines":
        """Resample each probability map to the native square, then threshold **there**.

        Thresholding first and resampling the mask throws away the boundary detail the model
        actually produced. Bilinear rather than bicubic: bicubic overshoots past 0 and 1, and the
        overshoot lands where the threshold sits.
        """
        masks = {}
        for structure, probability in probabilities.items():
            grown = F.interpolate(
                torch.from_numpy(np.ascontiguousarray(probability))[None, None].float(),
                size=(side, side),
                mode="bilinear",
                align_corners=False,
            )[0, 0].numpy()
            masks[structure] = grown >= threshold
        return cls(masks=masks, resampling="probabilities to native, bilinear, then thresholded")

    @classmethod
    def from_masks(cls, masks: dict[str, np.ndarray], side: int) -> "Outlines":
        """Resample binary masks to the native square, nearest neighbour, for want of anything better."""
        grown = {}
        for structure, mask in masks.items():
            grown[structure] = (
                F.interpolate(
                    torch.from_numpy(np.ascontiguousarray(mask))[None, None].float(),
                    size=(side, side),
                    mode="nearest",
                )[0, 0].numpy()
                > 0.5
            )
        return cls(masks=grown, resampling="binary masks to native, nearest neighbour")
