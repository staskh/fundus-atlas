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


def test_a_three_way_grader_is_counted_by_what_it_said(tmp_path: Path) -> None:
    entry = scored()
    entry["summary"]["three_class"] = {
        "photographs": 3,
        "accuracy": 2 / 3,
        "kappa_quadratic": 0.5,
        "confusion": {
            "good": {"good": 1, "usable": 0, "bad": 0},
            "usable": {"good": 0, "usable": 0, "bad": 1},
            "bad": {"good": 0, "usable": 0, "bad": 1},
        },
    }

    written = report.write_report("quality", [entry], into=tmp_path).read_text()

    assert "said good" in written
    assert "| 0.667 | 0.500 | 1 | 0 | 2 |" in written


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
                "What these numbers do not say",
            ],
            start=1,
        )
    ]
