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
        if adapter.declare()["named_grades"]
        else np.array([0.7, 0.05])
    )

    graded = type(adapter).interpret(["a", "b"], emitted)

    assert [grade.key for grade in graded] == ["a", "b"]
    assert all(grade.outcome == "graded" for grade in graded)
    assert all(0.0 <= grade.gradeable <= 1.0 for grade in graded), (
        "every model here answers the one comparable question with a confidence"
    )
    assert all(
        grade.verdict in adapter.declare()["named_grades"] or not grade.verdict for grade in graded
    )


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


def test_the_toolbox_gates_on_its_own_default_threshold() -> None:
    adapter = catalogue.load("fit-quality", device="cpu")

    graded = type(adapter).interpret(["over", "under"], np.array([0.51, 0.49]))

    assert [grade.gated for grade in graded] == [True, False]
    assert "0.5" in adapter.declare()["gate"]


def test_automorph_admits_a_usable_photograph_only_when_bad_is_unlikely() -> None:
    adapter = catalogue.load("automorph-quality-grader", device="cpu")

    graded = type(adapter).interpret(
        ["good", "usable_and_safe", "usable_but_doubted", "bad"],
        np.array(
            [
                [0.80, 0.15, 0.05],
                [0.35, 0.45, 0.20],
                [0.10, 0.60, 0.30],
                [0.05, 0.15, 0.80],
            ]
        ),
    )

    assert [grade.verdict for grade in graded] == [GOOD, USABLE, USABLE, BAD]
    assert [grade.gated for grade in graded] == [True, True, False, False], (
        "AutoMorph carries a usable photograph only while its bad probability is under a quarter"
    )


@pytest.mark.parametrize("slug", ["quickqual", "vascx-quality"])
def test_a_model_no_pipeline_gates_on_gates_nothing(slug: str) -> None:
    adapter = catalogue.load(slug, device="cpu")

    graded = type(adapter).interpret(["a"], np.array([[0.7, 0.2, 0.1]]))

    assert graded[0].gated is None
    assert "none" in adapter.declare()["gate"].lower()


def test_the_meme_variant_reads_one_probability_that_the_photograph_is_bad() -> None:
    adapter = catalogue.load("quickqual-meme", device="cpu")

    graded = type(adapter).interpret(["sound", "poor"], np.array([0.05, 0.95]))

    assert [grade.gradeable for grade in graded] == [pytest.approx(0.95), pytest.approx(0.05)]
    assert [grade.verdict for grade in graded] == ["", ""], "it names no grade, it scores one"


def test_automorphalyzer_carries_every_photograph_into_measurement() -> None:
    adapter = catalogue.load("quickqual-meme", device="cpu")

    graded = type(adapter).interpret(["sound", "poor"], np.array([0.05, 0.99]))

    assert [grade.gated for grade in graded] == [True, True], (
        "measuring everything is a decision, and the one AutoMorphalyzer makes"
    )
    assert "every" in adapter.declare()["gate"].lower()
