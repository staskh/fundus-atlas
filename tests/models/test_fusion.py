# ABOUTME: Tests for the binary-to-multi fusion two catalogued models share: how a photograph is
# ABOUTME: scaled before it, how its two branches reach its main generator, and how four classes
# ABOUTME: become two vessels.

import numpy as np
import torch

from models.utils import fusion


def photograph(side: int) -> np.ndarray:
    """A lit disc on a black surround, with texture in it, as a store's photographs are."""
    pixels = np.zeros((side, side, 3), dtype=np.uint8)
    y, x = np.ogrid[:side, :side]
    inside = (y - side / 2) ** 2 + (x - side / 2) ** 2 < (side / 2) ** 2
    pixels[inside] = (180, 90, 40)
    pixels[inside & (y % 7 == 0)] = (60, 30, 20)
    return pixels


def test_a_photograph_arrives_at_the_grid_the_seeds_were_trained_on() -> None:
    prepared = fusion.prepare(photograph(1024))

    assert prepared.shape == (3, fusion.GRID, fusion.GRID)
    assert prepared.dtype.is_floating_point


def test_a_photograph_is_scaled_by_the_statistics_of_its_own_lit_pixels() -> None:
    """The upstream's own expression, which centres on the mean of every pixel with red in it."""
    prepared = fusion.prepare(photograph(1024)).numpy()

    assert prepared.min() < 0, "the blacked-out surround sits below the mean of the lit pixels"
    assert prepared.std() > 0, "a scaled photograph still has contrast in it"


def test_an_unlit_photograph_is_handed_over_rather_than_dividing_by_nothing() -> None:
    """A photograph with no red in it has no statistics; the upstream's expression yields zeros."""
    prepared = fusion.prepare(np.zeros((1024, 1024, 3), dtype=np.uint8)).numpy()

    assert np.all(np.isfinite(prepared))


class Branch:
    """A stand-in for one branch generator, which answers with a segmentation and a fusion map."""

    def __init__(self, marker: float) -> None:
        self.marker = marker

    def __call__(self, images: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        shape = (images.shape[0], len(fusion.CLASSES), *images.shape[-2:])
        return torch.zeros(shape), torch.full(shape, self.marker)


class Main:
    """A stand-in for the main generator, recording what its two branches handed it."""

    def __init__(self, logits: torch.Tensor) -> None:
        self.logits = logits
        self.given: tuple[float, float] = ()

    def __call__(
        self, images: torch.Tensor, artery: torch.Tensor, vein: torch.Tensor
    ) -> tuple[torch.Tensor, None, None, None]:
        self.given = (float(artery.flatten()[0]), float(vein.flatten()[0]))
        return self.logits, None, None, None


def seed(logits: torch.Tensor) -> fusion.Seed:
    return fusion.Seed(main=Main(logits), artery=Branch(0.25), vein=Branch(0.75))


def test_the_branches_fusion_maps_are_what_reaches_the_main_generator() -> None:
    """Each branch answers with two maps, and it is the second the main generator is fused with."""
    one = seed(torch.zeros((1, len(fusion.CLASSES), 4, 4)))

    fusion.probabilities([one], torch.zeros((1, 3, 4, 4)), device="cpu")

    assert one.main.given == (0.25, 0.75), "the artery branch first, then the vein branch"


def test_the_seeds_are_averaged_after_their_own_softmax() -> None:
    """Averaging logits and averaging probabilities are different answers; the upstream averages
    probabilities, seed by seed."""
    confident = torch.zeros((1, len(fusion.CLASSES), 2, 2))
    confident[0, fusion.CLASSES.index("artery")] = 100.0
    undecided = torch.zeros((1, len(fusion.CLASSES), 2, 2))

    averaged = fusion.probabilities([seed(confident), seed(undecided)], torch.zeros((1, 3, 2, 2)))

    artery = averaged[0, fusion.CLASSES.index("artery")]
    assert np.allclose(artery, (1.0 + 0.25) / 2), "one certain seed and one with no opinion"
    assert np.allclose(averaged.sum(axis=1), 1.0)


def test_a_crossing_belongs_to_both_vessels() -> None:
    """Measured, not assumed: the fourth class is exactly the crossings an annotator drew.

    Scored against [HRF](../datasets/hrf.md), the class matches this repository's own crossing
    layer pixel for pixel — 56,690 of them on `09_dr`, with none left over — so an artery here is
    the artery class plus the crossing class, as it is for every other model in the benchmark.
    """
    probabilities = np.zeros((1, len(fusion.CLASSES), 4, 4), dtype=np.float32)
    probabilities[0, fusion.CLASSES.index("background")] = 1.0
    probabilities[0, :, 1, 1] = [0.0, 1.0, 0.0, 0.0]  # an artery pixel
    probabilities[0, :, 2, 2] = [0.0, 0.0, 1.0, 0.0]  # a vein pixel
    probabilities[0, :, 3, 3] = [0.0, 0.0, 0.0, 1.0]  # a crossing

    outlined = fusion.vessels(probabilities, sides=[4])[0]

    assert outlined.masks["artery"][1, 1] and outlined.masks["artery"][3, 3]
    assert outlined.masks["vein"][2, 2] and outlined.masks["vein"][3, 3]
    assert outlined.masks["artery"].sum() == 2
    assert outlined.masks["vein"].sum() == 2
