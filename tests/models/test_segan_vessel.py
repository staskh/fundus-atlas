# ABOUTME: Tests for the SEGAN vessel ensemble AutoMorph ships: the standardisation its upstream
# ABOUTME: bakes in, and the threshold this atlas runs it at, which is not the one upstream ships.

import numpy as np
import pytest

from models.utils import catalogue

SLUG = "segan-vessel"


def photograph(size: int) -> np.ndarray:
    """A square with a lit disc in it, dark outside, as a store's photographs are."""
    pixels = np.zeros((size, size, 3), dtype=np.uint8)
    y, x = np.ogrid[:size, :size]
    inside = (y - size / 2) ** 2 + (x - size / 2) ** 2 < (size / 2) ** 2
    pixels[inside] = (180, 90, 40)
    return pixels


def test_it_answers_about_vessels_and_says_nothing_about_arteries_or_veins() -> None:
    """The benchmark leaves its artery and vein columns empty rather than scoring it zero there."""
    adapter = catalogue.load(SLUG, device="cpu")

    assert adapter.purpose == "vessels"
    assert adapter.structures == ("vessels",)
    assert adapter.declare()["structures"] == ["vessels"]


def test_the_threshold_is_declared_as_a_number_and_is_not_the_upstreams() -> None:
    """A threshold inside a sentence can be changed without invalidating a single stored score."""
    declared = catalogue.load(SLUG, device="cpu").declare()

    assert declared["threshold"] == pytest.approx(0.2)
    assert declared["upstream_threshold"] == pytest.approx(0.5)


def test_a_lower_threshold_keeps_more_of_what_the_ensemble_was_unsure_about() -> None:
    """What the adjustment does, on a probability map whose answer is arithmetic."""
    adapter = catalogue.load(SLUG, device="cpu")
    probabilities = np.array([[[0.05, 0.25], [0.45, 0.95]]])

    ours = type(adapter).interpret(probabilities, [2])[0].masks["vessels"]
    upstreams = type(adapter).interpret(probabilities, [2], threshold=0.5)[0].masks["vessels"]

    assert ours.sum() == 3, "everything at or above 0.2 is vessel"
    assert upstreams.sum() == 1, "only the one above a half would have been"


def test_a_photograph_is_standardised_by_the_pixels_its_upstream_calls_lit() -> None:
    """Divided by the deviation of the lit pixels, not multiplied by it.

    The artery/vein stage of the same repository multiplies where it means to divide, and its
    adapter reproduces that because its weights were trained through it. This stage does not, so
    the two preparations are different and the difference is worth a test: a photograph with real
    variation in it comes back with its lit pixels centred on zero and spread by about one.
    """
    adapter = catalogue.load(SLUG, device="cpu")
    varied = photograph(adapter.grid)
    gradient = np.linspace(0, 60, adapter.grid, dtype=np.uint8)
    varied[varied[..., 0] > 0] += gradient[np.nonzero(varied[..., 0] > 0)[1]][:, None]

    prepared = adapter.prepare(varied).numpy()

    assert prepared.shape == (3, 912, 912), "the store's 1024 is resized down to the network's grid"
    assert prepared.min() < 0 < prepared.max(), "standardisation puts the surround below the mean"
    lit = prepared[:, prepared[0] > prepared[0].min()]
    assert abs(float(lit.mean())) < 1.0, "the lit pixels are centred on zero"
    assert 0.2 < float(lit.std()) < 5.0, "and spread by about one, rather than by the variance"


def test_a_photograph_with_nothing_lit_in_it_is_not_a_division_by_zero() -> None:
    adapter = catalogue.load(SLUG, device="cpu")

    prepared = adapter.prepare(np.zeros((adapter.grid, adapter.grid, 3), dtype=np.uint8))

    assert prepared.shape == (3, 912, 912)
    assert np.isfinite(prepared.numpy()).all()
