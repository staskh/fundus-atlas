# ABOUTME: Tests for what each adapter does to a photograph before its model sees it, and for how
# ABOUTME: it reads that model's output into the atlas's vocabulary.

import numpy as np
import pytest

from models.utils import catalogue
from models.utils.grading import BAD, GOOD, USABLE

SLUGS = catalogue.slugs()


def photograph(size: int) -> np.ndarray:
    """A square with a lit disc in it, dark outside, as a store's photographs are."""
    pixels = np.zeros((size, size, 3), dtype=np.uint8)
    y, x = np.ogrid[:size, :size]
    inside = (y - size / 2) ** 2 + (x - size / 2) ** 2 < (size / 2) ** 2
    pixels[inside] = (180, 90, 40)
    return pixels


@pytest.mark.parametrize("slug", SLUGS)
def test_a_prepared_photograph_is_a_three_channel_tensor_at_the_networks_grid(slug: str) -> None:
    adapter = catalogue.load(slug, device="cpu")
    declared = adapter.declare()

    prepared = adapter.prepare(photograph(declared["grid"]))

    assert prepared.shape == (3, declared["network_grid"], declared["network_grid"])
    assert prepared.dtype.is_floating_point


@pytest.mark.parametrize("slug", SLUGS)
def test_every_adapter_reads_its_model_into_one_vocabulary(slug: str) -> None:
    adapter = catalogue.load(slug, device="cpu")
    emitted = (
        np.array([[0.7, 0.2, 0.1], [0.05, 0.15, 0.8]])
        if adapter.declare()["grades"] != "gradeable against ungradeable"
        else np.array([0.7, 0.05])
    )

    graded = type(adapter).interpret(["a", "b"], emitted)

    assert [grade.key for grade in graded] == ["a", "b"]
    assert graded[0].gradeable > graded[1].gradeable
    assert all(grade.outcome == "graded" for grade in graded)


def test_a_three_way_grader_names_the_class_it_was_most_confident_of() -> None:
    adapter = catalogue.load("quickqual", device="cpu")

    graded = type(adapter).interpret(["a", "b", "c"], np.eye(3))

    assert [grade.verdict for grade in graded] == [GOOD, USABLE, BAD]


def test_automorph_standardises_a_photograph_by_its_own_lit_pixels() -> None:
    adapter = catalogue.load("automorph-quality-grader", device="cpu")

    prepared = adapter.prepare(photograph(512)).numpy()

    lit = prepared[prepared > prepared.min()]
    assert lit.std() > 0, "a standardised photograph still has contrast in it"
    assert prepared.min() < 0, "the blacked-out surround sits below the mean"
