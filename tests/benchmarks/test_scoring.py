# ABOUTME: Tests for what a quality benchmark measures: coverage first, then accuracy, agreement
# ABOUTME: and ranking on the photographs a model was willing to answer for.

import pytest

from benchmarks import scoring
from models.utils.grading import BAD, DECLINED, FAILED, GOOD, USABLE, Grade


def test_coverage_counts_what_the_model_would_answer_for() -> None:
    truth = {"a": GOOD, "b": GOOD, "c": BAD, "d": BAD}
    grades = [
        Grade("a", verdict=GOOD, gradeable=0.9),
        Grade("b", verdict=GOOD, gradeable=0.8),
        Grade("c", outcome=DECLINED, note="refused"),
        Grade("d", outcome=FAILED, note="ValueError"),
    ]

    summary = scoring.summarise(truth, grades)

    assert summary["photographs"] == 4
    assert (summary["graded"], summary["declined"], summary["failed"]) == (2, 1, 1)
    assert summary["coverage"] == pytest.approx(0.5)


def test_accuracy_is_measured_only_on_what_was_graded() -> None:
    truth = {"a": GOOD, "b": BAD, "c": BAD, "d": GOOD}
    grades = [
        Grade("a", verdict=GOOD, gradeable=0.9),
        Grade("b", verdict=BAD, gradeable=0.1),
        Grade("c", verdict=GOOD, gradeable=0.7),
        Grade("d", outcome=DECLINED, note="refused"),
    ]

    summary = scoring.summarise(truth, grades)

    assert summary["gradeable"]["photographs"] == 3
    assert summary["gradeable"]["accuracy"] == pytest.approx(2 / 3)


def test_usable_counts_as_worth_measuring() -> None:
    truth = {"a": USABLE, "b": BAD}
    grades = [Grade("a", verdict=GOOD, gradeable=0.9), Grade("b", verdict=BAD, gradeable=0.2)]

    summary = scoring.summarise(truth, grades)

    assert summary["gradeable"]["accuracy"] == pytest.approx(1.0)


def test_a_score_that_separates_the_two_classes_ranks_perfectly() -> None:
    truth = {"a": GOOD, "b": USABLE, "c": BAD, "d": BAD}
    grades = [
        Grade("a", gradeable=0.9),
        Grade("b", gradeable=0.6),
        Grade("c", gradeable=0.4),
        Grade("d", gradeable=0.1),
    ]

    summary = scoring.summarise(truth, grades)

    assert summary["gradeable"]["roc_auc"] == pytest.approx(1.0)


def test_a_unit_with_one_class_has_no_ranking_to_measure() -> None:
    truth = {"a": GOOD, "b": GOOD}
    grades = [Grade("a", gradeable=0.9), Grade("b", gradeable=0.1)]

    summary = scoring.summarise(truth, grades)

    assert summary["gradeable"]["roc_auc"] is None


def test_agreement_beyond_chance_is_reported() -> None:
    truth = {"a": GOOD, "b": GOOD, "c": BAD, "d": BAD}
    grades = [
        Grade("a", verdict=GOOD, gradeable=0.9),
        Grade("b", verdict=GOOD, gradeable=0.8),
        Grade("c", verdict=BAD, gradeable=0.2),
        Grade("d", verdict=BAD, gradeable=0.1),
    ]

    summary = scoring.summarise(truth, grades)

    assert summary["gradeable"]["kappa"] == pytest.approx(1.0)


def test_a_binary_model_is_scored_on_its_confidence_when_it_names_no_grade() -> None:
    truth = {"a": GOOD, "b": BAD}
    grades = [Grade("a", gradeable=0.9), Grade("b", gradeable=0.1)]

    summary = scoring.summarise(truth, grades)

    assert summary["gradeable"]["accuracy"] == pytest.approx(1.0)
    assert summary["three_class"] is None, "a binary grader has no three-class score"


def test_a_three_way_grader_is_also_scored_on_all_three_grades() -> None:
    truth = {"a": GOOD, "b": USABLE, "c": BAD}
    grades = [
        Grade("a", verdict=GOOD, gradeable=0.9, classes={GOOD: 0.8, USABLE: 0.1, BAD: 0.1}),
        Grade("b", verdict=BAD, gradeable=0.3, classes={GOOD: 0.1, USABLE: 0.2, BAD: 0.7}),
        Grade("c", verdict=BAD, gradeable=0.1, classes={GOOD: 0.0, USABLE: 0.1, BAD: 0.9}),
    ]

    summary = scoring.summarise(truth, grades)

    assert summary["three_class"]["accuracy"] == pytest.approx(2 / 3)
    assert summary["three_class"]["confusion"][USABLE][BAD] == 1


def test_a_photograph_the_model_never_saw_is_an_error_rather_than_a_silent_gap() -> None:
    truth = {"a": GOOD, "b": BAD}

    with pytest.raises(ValueError, match="b"):
        scoring.summarise(truth, [Grade("a", verdict=GOOD, gradeable=0.9)])
