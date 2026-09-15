# ABOUTME: What a quality benchmark measures: coverage first, and then accuracy, agreement and
# ABOUTME: ranking on the photographs a model was willing to answer for.

import math
import warnings
from collections.abc import Iterable

from sklearn.exceptions import UndefinedMetricWarning
from sklearn.metrics import accuracy_score, cohen_kappa_score, roc_auc_score

from models.utils.grading import BAD, DECLINED, FAILED, GRADED, GRADES, Grade

#: The grades that mean the photograph is worth measuring. Every quality model in this catalogue
#: can answer this question, whether it grades in two classes or three, so it is the level at
#: which they are comparable at all.
WORTH_MEASURING = {grade for grade in GRADES if grade != BAD}

#: Where a confidence is turned into a verdict, for a model that publishes no verdict of its own.
THRESHOLD = 0.5


def restored(row: dict[str, str]) -> Grade:
    """One model's answer, read back from the evidence a previous run wrote.

    A resumed run scores photographs it measured today beside photographs it measured last week,
    and both have to be the same kind of thing for the summary to mean anything.
    """
    classes = {grade: float(row[grade]) for grade in GRADES if row.get(grade)}
    carried = str(row.get("carried_by_its_pipeline", "")).strip().lower()
    return Grade(
        key=row["key"],
        outcome=row.get("outcome") or GRADED,
        verdict=row.get("verdict") or "",
        gradeable=float(row["gradeable"]) if row.get("gradeable") else None,
        classes=classes,
        gated={"true": True, "false": False}.get(carried),
        note=row.get("note", ""),
    )


def summarise(truth: dict[str, str], grades: Iterable[Grade]) -> dict[str, object]:
    """Score one model on one evaluation unit.

    Coverage comes first and is never folded into accuracy: a grader that answers the easy 60% of
    a dataset and is right about all of them is not better than one that answers everything and is
    right about 85%. A declined photograph is counted in coverage and excluded from the accuracy
    metrics; a failure is counted separately again, because a crash is our problem or the model's
    rather than a judgement about the image.

    :param truth: the dataset's own grade, by key, for every photograph the model was given.
    :raises ValueError: if a photograph has no answer at all, which is a lost result rather than a
        model declining to give one.
    """
    grades = list(grades)
    answered = {grade.key for grade in grades}
    missing = sorted(set(truth) - answered)
    if missing:
        raise ValueError(f"{missing} were given to the model and came back with no answer")

    counts = {outcome: 0 for outcome in (GRADED, DECLINED, FAILED)}
    for grade in grades:
        counts[grade.outcome] += 1
    scored = [grade for grade in grades if grade.outcome == GRADED]

    return {
        "photographs": len(grades),
        "graded": counts[GRADED],
        "declined": counts[DECLINED],
        "failed": counts[FAILED],
        "coverage": counts[GRADED] / len(grades) if grades else 0.0,
        "reference_grades": [grade for grade in GRADES if grade in set(truth.values())],
        "gradeable": _gradeable(truth, scored),
        "three_class": _three_class(truth, scored),
        "gate": _gate(truth, scored),
    }


def _gate(truth: dict[str, str], scored: list[Grade]) -> dict[str, object] | None:
    """What the model's own project would carry into measurement, scored on the same question.

    A pipeline's gate is not the model's argmax. AutoMorph admits a photograph its grader called
    merely usable only when the same grader's probability of `bad` is under a quarter, and a model
    no catalogued pipeline gates on has no gate to score at all.
    """
    gated = [grade for grade in scored if grade.gated is not None]
    if not gated:
        return None
    reference = [truth[grade.key] in WORTH_MEASURING for grade in gated]
    carried = [bool(grade.gated) for grade in gated]
    return {
        "photographs": len(gated),
        "carried": sum(carried),
        "carried_share": sum(carried) / len(gated),
        "accuracy": accuracy_score(reference, carried),
        "kappa": _agreement(reference, carried) if len(set(reference)) == 2 else None,
        "differs_from_the_verdict": sum(
            1
            for grade, passed in zip(gated, carried, strict=True)
            if passed != _says_worth_measuring(grade)
        ),
    }


def _gradeable(truth: dict[str, str], scored: list[Grade]) -> dict[str, object]:
    """Worth measuring against not, which is the question every quality model answers."""
    reference = [truth[grade.key] in WORTH_MEASURING for grade in scored]
    predicted = [_says_worth_measuring(grade) for grade in scored]
    confidence = [grade.gradeable for grade in scored]
    both_classes = len(set(reference)) == 2
    worth = [said for was, said in zip(reference, predicted, strict=True) if was]
    against = [said for was, said in zip(reference, predicted, strict=True) if not was]
    return {
        "photographs": len(scored),
        # Which mistake the model made, not just how many: throwing away a photograph the readers
        # called usable costs a study its sample size, and keeping one they called bad costs it
        # its measurements. A single accuracy hides which of the two a model does.
        "kept_of_worth_measuring": sum(worth) / len(worth) if worth else None,
        "discarded_of_not_worth": (
            sum(not said for said in against) / len(against) if against else None
        ),
        "accuracy": accuracy_score(reference, predicted) if scored else None,
        "kappa": _agreement(reference, predicted) if both_classes else None,
        "roc_auc": (
            roc_auc_score(reference, confidence)
            if both_classes and all(value is not None for value in confidence)
            else None
        ),
    }


def _three_class(truth: dict[str, str], scored: list[Grade]) -> dict[str, object] | None:
    """Good, usable and bad, for the graders that name all three."""
    named = [grade for grade in scored if grade.verdict and grade.classes]
    if not named or len(named) != len(scored):
        return None
    reference = [truth[grade.key] for grade in named]
    predicted = [grade.verdict for grade in named]
    confusion = {was: dict.fromkeys(GRADES, 0) for was in GRADES}
    for was, said in zip(reference, predicted, strict=True):
        confusion[was][said] += 1
    seen = {grade for grade in GRADES if grade in set(reference)}
    return {
        "photographs": len(named),
        "unused_by_the_reference": [grade for grade in GRADES if grade not in seen],
        "recall": {
            grade: (
                confusion[grade][grade] / sum(confusion[grade].values())
                if sum(confusion[grade].values())
                else None
            )
            for grade in GRADES
        },
        "accuracy": accuracy_score(reference, predicted),
        "kappa_quadratic": _agreement(
            reference, predicted, labels=list(GRADES), weights="quadratic"
        ),
        "confusion": confusion,
    }


def _agreement(reference: list, predicted: list, **how: object) -> float | None:
    """Agreement beyond chance, or nothing where it has no value.

    Two sets of verdicts with only one label in common leave κ undefined. That is an answer, not a
    problem: it is reported as a dash rather than as a number nobody can read, which is why the
    library's warning about it is expected here and handled rather than printed.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UndefinedMetricWarning)
        value = cohen_kappa_score(reference, predicted, **how)
    return None if value is None or math.isnan(value) else float(value)


def _says_worth_measuring(grade: Grade) -> bool:
    """The model's own verdict where it names one, and its confidence where it does not."""
    if grade.verdict:
        return grade.verdict in WORTH_MEASURING
    return (grade.gradeable or 0.0) >= THRESHOLD
