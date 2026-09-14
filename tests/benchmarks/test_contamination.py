# ABOUTME: Tests for the mark every result carries: whether the model saw these photographs while
# ABOUTME: it was learning, and the difference between saying no and saying nobody knows.

from benchmarks import contamination
from benchmarks.loaders.base import Unit


def test_a_dataset_a_model_never_trained_on_is_out_of_sample() -> None:
    assert contamination.mark("quickqual", Unit("fives", "main", "test")) == "out-of-sample"


def test_a_dataset_a_model_trained_on_is_in_sample() -> None:
    assert contamination.mark("quickqual", Unit("eyeq", "main", "train")) == "in-sample"


def test_a_training_set_with_no_stated_split_makes_the_whole_dataset_in_sample() -> None:
    assert (
        contamination.mark("fit-quality", Unit("deepdrid", "main", "test"))
        == "in-sample-unclear-split"
    )


def test_a_model_whose_training_data_was_never_published_clears_nothing() -> None:
    assert contamination.mark("vascx-quality", Unit("fives", "main", "test")) == "unknown"


def test_a_model_with_no_page_saying_is_unknown_rather_than_clean() -> None:
    assert contamination.mark("not-catalogued", Unit("fives", "main", "test")) == "unknown"
