# ABOUTME: Tests for the two documents a run generates: the one saying how the benchmark is
# ABOUTME: configured, and the one saying what came out.

from pathlib import Path

from benchmarks import report


def scored(**overrides: object) -> dict[str, object]:
    entry = {
        "model": "quickqual",
        "dataset": "fives",
        "declared": {
            "grid": 512,
            "network_grid": 512,
            "ensemble": 1,
            "device": "mps",
            "grades": "good, usable, bad",
            "named_grades": ("good", "usable", "bad"),
            "gate": "none; no catalogued pipeline gates on it",
            "upstream": {"commit": "a94feb02a79efa5380f6b0d863d1b80ab4c73e4e"},
        },
        "grade_source": ["derived"],
        "padding": 0.0,
        "counts": {"processed": 200, "total": 200, "complete": True, "excluded": {}},
        "summary": {
            "photographs": 200,
            "graded": 198,
            "declined": 1,
            "failed": 1,
            "coverage": 0.99,
            "reference_grades": ["good", "usable", "bad"],
            "gradeable": {"photographs": 198, "accuracy": 0.885, "roc_auc": None, "kappa": 0.7},
            "three_class": None,
            "gate": None,
        },
    }
    entry.update(overrides)
    return entry


def rows(**overrides: str) -> dict[str, str]:
    entry = {
        "key": "a",
        "subset": "main",
        "split": "train",
        "grade": "good",
        "outcome": "graded",
        "verdict": "good",
        "gradeable": "0.9",
        "carried_by_its_pipeline": "",
        "readers": "",
    }
    entry.update(overrides)
    return entry


def configured() -> dict[str, object]:
    """What a run knows before it measures anything."""
    return {
        "models": [{"slug": "quickqual", "declared": scored()["declared"]}],
        "datasets": [
            {
                "slug": "fives",
                "total": 200,
                "excluded": {"below the size floor": 3},
                "grade_source": ["derived"],
                "padding": 0.0,
            }
        ],
    }


def test_the_configuration_page_names_every_declared_model_including_the_absent(
    tmp_path: Path,
) -> None:
    path = report.write_docs(
        "quality",
        configured(),
        missing_models={"lunet-quality": "no adapter written"},
        missing_datasets={"eyeq": "no store built"},
        columns={"key": "the photograph"},
        into=tmp_path,
    )

    written = path.read_text()
    assert "lunet-quality" in written and "no adapter written" in written
    assert "eyeq" in written and "no store built" in written
    assert "`a94feb02`" in written, "a number with no commit behind it is an anecdote"


def test_the_configuration_page_explains_every_column_of_the_evidence(tmp_path: Path) -> None:
    written = report.write_docs(
        "quality",
        configured(),
        missing_models={},
        missing_datasets={},
        columns={"key": "the photograph", "gradeable": "how confident it is"},
        into=tmp_path,
    ).read_text()

    assert "| `key` | the photograph |" in written
    assert "| `gradeable` | how confident it is |" in written


def test_the_configuration_page_can_be_written_before_anything_is_measured(
    tmp_path: Path,
) -> None:
    written = report.write_docs(
        "quality",
        configured(),
        missing_models={},
        missing_datasets={},
        columns={},
        into=tmp_path,
    ).read_text()

    assert "before" in written, "the page says when it was written, because it matters"
    assert "3 below the size floor" in written, "the exclusions are known from the manifest alone"