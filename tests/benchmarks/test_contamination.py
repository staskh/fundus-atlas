# ABOUTME: Tests for the mark every result carries: whether the model saw these photographs while
# ABOUTME: it was learning, and the difference between saying no and saying nobody knows.

from benchmarks import contamination


def test_a_dataset_a_model_never_trained_on_is_out_of_sample() -> None:
    assert contamination.mark("quickqual", "fives") == "out-of-sample"


def test_the_split_a_model_trained_on_is_in_sample() -> None:
    assert contamination.mark("quickqual", "eyeq", "train") == "in-sample"


def test_another_split_of_the_same_dataset_is_not() -> None:
    assert contamination.mark("quickqual", "eyeq", "test") == "out-of-sample"


def test_a_dataset_trained_on_with_no_stated_split_contaminates_all_of_it() -> None:
    assert contamination.mark("fit-quality", "deepdrid", "test") == "in-sample-unclear-split"


def test_asking_about_a_whole_dataset_gives_the_answer_that_hides_least() -> None:
    assert contamination.mark("quickqual", "eyeq") == "in-sample", (
        "a summary over a dataset whose training half is in it is not out-of-sample"
    )


def test_a_model_whose_training_data_was_never_published_clears_nothing() -> None:
    assert contamination.mark("vascx-quality", "fives") == "unknown"


def test_a_model_with_no_page_saying_is_unknown_rather_than_clean() -> None:
    assert contamination.mark("not-catalogued", "fives") == "unknown"


def test_a_dataset_whose_splits_disagree_must_be_broken_out() -> None:
    assert contamination.splits_disagree("quickqual", "eyeq", ["train", "test"]) is True
    assert contamination.splits_disagree("quickqual", "fives", ["train", "test"]) is False
