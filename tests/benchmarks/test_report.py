# ABOUTME: Tests for the document a run generates: that it carries the pins, the marks and the
# ABOUTME: coverage, and that it never turns a missing metric into a number.

from pathlib import Path

from benchmarks import report


def scored(**overrides: object) -> dict[str, object]:
    entry = {
        "model": "quickqual",
        "unit": "fives/main/test",
        "contamination": "out-of-sample",
        "grid": 512,
        "network_grid": 512,
        "fingerprint": "abc",
        "declared": {
            "grid": 512,
            "network_grid": 512,
            "ensemble": 1,
            "device": "mps",
            "upstream": {"commit": "a94feb02a79efa5380f6b0d863d1b80ab4c73e4e"},
        },
        "summary": {
            "photographs": 200,
            "graded": 198,
            "declined": 1,
            "failed": 1,
            "coverage": 0.99,
            "without_reference": 3,
            "gradeable": {
                "photographs": 198,
                "accuracy": 0.885,
                "roc_auc": None,
                "kappa": 0.7,
            },
            "three_class": None,
        },
        "reused": False,
    }
    entry.update(overrides)
    return entry


def test_the_document_carries_the_pin_the_coverage_and_the_mark(tmp_path: Path) -> None:
    path = report.write_report("quality", [scored()], into=tmp_path)

    written = path.read_text()
    assert "`a94feb02`" in written, "a number with no commit behind it is an anecdote"
    assert "0.990" in written, "coverage is reported beside accuracy"
    assert "out-of-sample" in written


def test_a_metric_that_does_not_exist_is_a_dash(tmp_path: Path) -> None:
    written = report.write_report("quality", [scored()], into=tmp_path).read_text()

    assert "| 0.885 | — | 0.700 |" in written


def test_a_binary_grader_gets_no_three_class_table(tmp_path: Path) -> None:
    written = report.write_report("quality", [scored()], into=tmp_path).read_text()

    assert "No model in this run named all three grades." in written


def three_class() -> dict[str, object]:
    return {
        "photographs": 3,
        "accuracy": 2 / 3,
        "kappa_quadratic": 0.5,
        "unused_by_the_reference": [],
        "recall": {"good": 1.0, "usable": 0.0, "bad": 1.0},
        "confusion": {
            "good": {"good": 1, "usable": 0, "bad": 0},
            "usable": {"good": 0, "usable": 0, "bad": 1},
            "bad": {"good": 0, "usable": 0, "bad": 1},
        },
    }


def test_a_three_way_grader_is_scored_by_how_often_each_grade_is_found(tmp_path: Path) -> None:
    entry = scored()
    entry["summary"]["three_class"] = three_class()

    written = report.write_report("quality", [entry], into=tmp_path).read_text()

    assert "recall on usable" in written
    assert "| 0.667 | 0.500 | 1.000 | 0.000 | 1.000 |" in written


def test_the_confusion_behind_a_three_class_score_is_shown(tmp_path: Path) -> None:
    entry = scored()
    entry["summary"]["three_class"] = three_class()

    written = report.write_report("quality", [entry], into=tmp_path).read_text()

    assert "Dataset said ↓ / model said →" in written
    assert "| usable | 0 | 0 | 1 |" in written


def test_a_reference_that_never_says_usable_is_named_as_such(tmp_path: Path) -> None:
    entry = scored()
    entry["summary"]["three_class"] = {**three_class(), "unused_by_the_reference": ["usable"]}

    written = report.write_report("quality", [entry], into=tmp_path).read_text()

    assert "never says `usable`" in written


def test_the_gate_a_project_applies_is_reported_with_its_rule(tmp_path: Path) -> None:
    entry = scored()
    entry["declared"]["gate"] = "good passes; usable passes only under a quarter of bad"
    entry["summary"]["gate"] = {
        "photographs": 200,
        "carried": 150,
        "carried_share": 0.75,
        "accuracy": 0.82,
        "kappa": 0.6,
        "differs_from_the_verdict": 12,
    }

    written = report.write_report("quality", [entry], into=tmp_path).read_text()

    assert "usable passes only under a quarter of bad" in written
    assert "| 150 of 200 | 0.750 | 0.820 | 12 |" in written


def test_a_model_no_pipeline_gates_on_says_so(tmp_path: Path) -> None:
    written = report.write_report("quality", [scored()], into=tmp_path).read_text()

    assert "No catalogued pipeline gates on any model in this run." in written


def test_every_heading_is_numbered(tmp_path: Path) -> None:
    written = report.write_report("quality", [scored()], into=tmp_path).read_text()

    headings = [line for line in written.splitlines() if line.startswith("## ")]
    assert headings == [
        f"## {index}. {heading}"
        for index, heading in enumerate(
            [
                "What ran",
                "What it ran on",
                "Coverage: what each model was willing to answer",
                "Worth measuring, or not",
                "The three grades",
                "What each model's own project would carry into measurement",
                "What these numbers do not say",
            ],
            start=1,
        )
    ]


def test_a_run_in_which_nothing_declined_says_so(tmp_path: Path) -> None:
    entry = scored()
    entry["summary"]["declined"] = 0

    written = report.write_report("quality", [entry], into=tmp_path).read_text()

    assert "No model declined a photograph in this run." in written


def test_a_run_in_which_something_declined_does_not_claim_otherwise(tmp_path: Path) -> None:
    entry = scored()
    entry["summary"]["declined"] = 4

    written = report.write_report("quality", [entry], into=tmp_path).read_text()

    assert "No model declined" not in written


def test_an_assumed_reference_is_explained_rather_than_read_as_a_grade(tmp_path: Path) -> None:
    entry = scored()
    entry["grade_source"] = ["assumed"]

    written = report.write_report("quality", [entry], into=tmp_path).read_text()

    assert "contains no bad photographs at all" in written
    assert "how much of" in written


def test_a_run_without_an_assumed_reference_does_not_mention_one(tmp_path: Path) -> None:
    entry = scored()
    entry["grade_source"] = ["published"]

    written = report.write_report("quality", [entry], into=tmp_path).read_text()

    assert "assumed" not in written


def test_how_much_of_the_square_is_canvas_is_reported(tmp_path: Path) -> None:
    entry = scored()
    entry["padding"] = 0.188

    written = report.write_report("quality", [entry], into=tmp_path).read_text()

    assert "Black canvas" in written
    assert "| 0.188 |" in written
