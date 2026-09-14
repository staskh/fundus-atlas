# ABOUTME: Tests for the vocabulary every quality adapter answers in: the three outcomes, the
# ABOUTME: atlas's own grade names, and what a model is allowed to leave unsaid.

import pytest

from models import grading


def test_a_graded_photograph_carries_a_verdict_in_the_atlas_vocabulary() -> None:
    grade = grading.Grade(key="img_00000", verdict=grading.USABLE, gradeable=0.7)

    assert grade.outcome == grading.GRADED
    assert grade.verdict == "usable"


def test_a_model_may_answer_with_a_confidence_and_no_named_grade() -> None:
    grade = grading.Grade(key="img_00000", gradeable=0.92)

    assert grade.verdict == ""
    assert grade.gradeable == pytest.approx(0.92)


def test_a_declined_photograph_says_why_and_scores_nothing() -> None:
    grade = grading.Grade(key="img_00000", outcome=grading.DECLINED, note="no field found")

    assert grade.gradeable is None
    assert grade.note == "no field found"


def test_a_verdict_outside_the_vocabulary_is_refused() -> None:
    with pytest.raises(ValueError, match="reject"):
        grading.Grade(key="img_00000", verdict="reject")


def test_an_outcome_outside_the_three_is_refused() -> None:
    with pytest.raises(ValueError, match="skipped"):
        grading.Grade(key="img_00000", outcome="skipped")


def test_a_declined_or_failed_photograph_may_not_also_carry_a_verdict() -> None:
    with pytest.raises(ValueError, match="declined"):
        grading.Grade(key="img_00000", outcome=grading.DECLINED, verdict=grading.GOOD)


def test_three_class_probabilities_are_named_rather_than_ordered() -> None:
    grade = grading.Grade(
        key="img_00000",
        verdict=grading.BAD,
        classes={grading.GOOD: 0.1, grading.USABLE: 0.2, grading.BAD: 0.7},
    )

    assert grade.classes[grading.BAD] == pytest.approx(0.7)


def test_a_class_outside_the_vocabulary_is_refused() -> None:
    with pytest.raises(ValueError, match="ungradeable"):
        grading.Grade(key="img_00000", classes={"ungradeable": 1.0})
