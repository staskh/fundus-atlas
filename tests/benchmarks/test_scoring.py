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


def test_agreement_that_has_no_value_is_reported_as_nothing() -> None:
    truth = {"a": GOOD, "b": BAD}
    grades = [
        Grade("a", verdict=GOOD, gradeable=0.9, classes={GOOD: 0.9, USABLE: 0.1, BAD: 0.0}),
        Grade("b", outcome=FAILED, note="broke"),
    ]

    summary = scoring.summarise(truth, grades)

    assert summary["three_class"]["photographs"] == 1
    assert summary["three_class"]["kappa_quadratic"] is None, "one verdict leaves κ undefined"
    assert summary["three_class"]["accuracy"] == pytest.approx(1.0)


def test_the_gate_a_pipeline_applies_is_scored_on_its_own_terms() -> None:
    truth = {"a": GOOD, "b": USABLE, "c": BAD}
    grades = [
        Grade(
            "a", verdict=GOOD, gradeable=0.9, classes={GOOD: 0.8, USABLE: 0.1, BAD: 0.1}, gated=True
        ),
        # Its pipeline drops this one although the model called it usable.
        Grade(
            "b",
            verdict=USABLE,
            gradeable=0.7,
            classes={GOOD: 0.2, USABLE: 0.5, BAD: 0.3},
            gated=False,
        ),
        Grade(
            "c", verdict=BAD, gradeable=0.1, classes={GOOD: 0.0, USABLE: 0.1, BAD: 0.9}, gated=False
        ),
    ]

    summary = scoring.summarise(truth, grades)

    assert summary["gate"]["photographs"] == 3
    assert summary["gate"]["carried"] == 1
    assert summary["gate"]["carried_share"] == pytest.approx(1 / 3)
    assert summary["gate"]["accuracy"] == pytest.approx(2 / 3), "it drops a usable photograph"


def test_a_model_no_pipeline_gates_on_is_not_given_a_gate_score() -> None:
    truth = {"a": GOOD}
    grades = [Grade("a", verdict=GOOD, gradeable=0.9, classes={GOOD: 0.9, USABLE: 0.1, BAD: 0.0})]

    assert scoring.summarise(truth, grades)["gate"] is None


def test_the_reference_says_which_grades_it_actually_uses() -> None:
    truth = {"a": GOOD, "b": BAD}
    grades = [Grade("a", gradeable=0.9), Grade("b", gradeable=0.1)]

    summary = scoring.summarise(truth, grades)

    assert summary["reference_grades"] == [GOOD, BAD], "this reference never says usable"


def test_a_three_class_score_names_the_grades_the_reference_never_used() -> None:
    truth = {"a": GOOD, "b": BAD}
    grades = [
        Grade("a", verdict=GOOD, gradeable=0.9, classes={GOOD: 0.9, USABLE: 0.1, BAD: 0.0}),
        Grade("b", verdict=USABLE, gradeable=0.6, classes={GOOD: 0.2, USABLE: 0.5, BAD: 0.3}),
    ]

    summary = scoring.summarise(truth, grades)

    assert summary["three_class"]["unused_by_the_reference"] == [USABLE]
    assert summary["three_class"]["recall"][GOOD] == pytest.approx(1.0)
    assert summary["three_class"]["recall"][USABLE] is None, "the reference never said usable"


def test_an_answer_read_back_from_the_evidence_is_the_answer_that_was_given() -> None:
    given = Grade(
        "a",
        verdict=USABLE,
        gradeable=0.7,
        classes={GOOD: 0.2, USABLE: 0.5, BAD: 0.3},
        gated=False,
    )
    row = {
        "key": "a",
        "outcome": "graded",
        "verdict": "usable",
        "gradeable": "0.700000",
        "good": "0.200000",
        "usable": "0.500000",
        "bad": "0.300000",
        "carried_by_its_pipeline": "false",
        "note": "",
    }

    assert scoring.restored(row) == given


def test_a_failure_read_back_carries_no_answer_and_its_reason() -> None:
    row = {
        "key": "a",
        "outcome": "failed",
        "verdict": "",
        "gradeable": "",
        "carried_by_its_pipeline": "",
        "note": "ValueError()",
    }

    restored = scoring.restored(row)

    assert restored.outcome == FAILED
    assert restored.gradeable is None
    assert restored.note == "ValueError()"


def test_the_summary_carries_which_mistake_the_model_made() -> None:
    truth = {"a": GOOD, "b": GOOD, "c": BAD, "d": BAD}
    grades = [
        Grade("a", verdict=GOOD, gradeable=0.9),
        Grade("b", verdict=BAD, gradeable=0.2),
        Grade("c", verdict=GOOD, gradeable=0.6),
        Grade("d", verdict=BAD, gradeable=0.1),
    ]

    level = scoring.summarise(truth, grades)["gradeable"]

    assert level["kept_of_worth_measuring"] == pytest.approx(0.5), "one good photograph thrown away"
    assert level["discarded_of_not_worth"] == pytest.approx(0.5), "one bad one kept"


def test_a_reference_with_one_class_has_only_the_share_it_has() -> None:
    truth = {"a": GOOD, "b": GOOD}
    grades = [Grade("a", verdict=GOOD, gradeable=0.9), Grade("b", verdict=BAD, gradeable=0.2)]

    level = scoring.summarise(truth, grades)["gradeable"]

    assert level["kept_of_worth_measuring"] == pytest.approx(0.5)
    assert level["discarded_of_not_worth"] is None
