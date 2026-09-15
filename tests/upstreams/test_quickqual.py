# ABOUTME: Tests that the MEME variant's parameters are read from the pinned repository rather than
# ABOUTME: copied into this one, and that a repository which stopped publishing them is not guessed at.

from pathlib import Path

import pytest

from upstreams import quickqual


def test_the_meme_parameters_come_from_the_pinned_repository() -> None:
    found = quickqual.meme()

    assert len(found.features) == 9, "nine of the backbone's features, chosen by index"
    assert len(found.weights) == 9
    assert isinstance(found.bias, float)


def test_the_parameters_are_the_ones_the_repository_publishes() -> None:
    found = quickqual.meme()

    assert found.features[0] == 71
    assert found.weights[0] == pytest.approx(-1411.32)
    assert found.bias == pytest.approx(5.18)


def test_a_repository_that_does_not_publish_them_is_not_guessed_at(tmp_path: Path) -> None:
    readme = tmp_path / "README.md"
    readme.write_text("QuickQual is a method for scoring retinal image quality.\n")

    with pytest.raises(LookupError, match="README"):
        quickqual.meme(readme)
