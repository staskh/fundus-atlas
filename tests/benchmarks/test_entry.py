# ABOUTME: Tests for the one command every benchmark is run from, and what its options mean.

import pytest

from benchmarks import __main__ as entry


def test_the_benchmark_is_named_and_the_rest_has_defaults() -> None:
    asked = entry.parse(["--benchmark", "quality"])

    assert asked.benchmark == "quality"
    assert asked.model is None and asked.dataset is None
    assert asked.max_samples is None and asked.random_samples is False


def test_one_model_on_one_dataset_is_how_a_pair_is_re_measured() -> None:
    asked = entry.parse(["--benchmark", "quality", "--model", "quickqual", "--dataset", "fives"])

    assert entry.named(asked.model) == ["quickqual"]
    assert entry.named(asked.dataset) == ["fives"]


def test_several_are_given_as_a_list() -> None:
    asked = entry.parse(["--benchmark", "quality", "--model", "quickqual,vascx-quality"])

    assert entry.named(asked.model) == ["quickqual", "vascx-quality"]


def test_a_benchmark_nobody_has_written_says_which_exist() -> None:
    with pytest.raises(SystemExit):
        entry.parse(["--benchmark", "no-such-benchmark"])


def test_the_sample_size_is_a_number_of_photographs() -> None:
    asked = entry.parse(["--benchmark", "quality", "--max-samples", "20", "--random-samples"])

    assert asked.max_samples == 20
    assert asked.random_samples is True
