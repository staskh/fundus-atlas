# ABOUTME: Tests for what a run keeps: the per-image evidence, the summary beside it, and the
# ABOUTME: fingerprint that says whether a stored score still describes the thing that made it.

from pathlib import Path

from benchmarks import runs
from benchmarks.loaders.base import Unit


def test_a_fingerprint_is_the_same_for_the_same_facts_in_any_order() -> None:
    one = runs.fingerprint({"weights": "abc", "commit": "def"})
    other = runs.fingerprint({"commit": "def", "weights": "abc"})

    assert one == other
    assert len(one) == 64


def test_a_changed_fact_is_a_different_fingerprint() -> None:
    before = runs.fingerprint({"weights": "abc"})

    assert runs.fingerprint({"weights": "abd"}) != before


def test_a_result_is_read_back_as_it_was_written(tmp_path: Path) -> None:
    unit = Unit("fives", "main", "test")
    rows = [{"key": "a", "grade": "good", "outcome": "graded", "gradeable": "0.9"}]

    runs.write(tmp_path, "quality", "quickqual", unit, "fingerprint", {"coverage": 1.0}, rows)
    found = runs.read(tmp_path, "quality", "quickqual", unit)

    assert found["fingerprint"] == "fingerprint"
    assert found["summary"] == {"coverage": 1.0}
    assert list(runs.rows(tmp_path, "quality", "quickqual", unit)) == rows


def test_nothing_is_read_back_where_nothing_was_measured(tmp_path: Path) -> None:
    assert runs.read(tmp_path, "quality", "quickqual", Unit("fives", "main", "test")) is None


def test_a_stored_score_is_kept_only_while_its_fingerprint_holds(tmp_path: Path) -> None:
    unit = Unit("fives", "main", "test")
    runs.write(tmp_path, "quality", "quickqual", unit, "before", {}, [{"key": "a"}])

    assert runs.reusable(tmp_path, "quality", "quickqual", unit, "before") is not None
    assert runs.reusable(tmp_path, "quality", "quickqual", unit, "after") is None


def test_the_index_lists_every_benchmark_that_has_results(tmp_path: Path) -> None:
    from benchmarks import report

    unit = Unit("fives", "main", "test")
    runs.write(
        tmp_path / "results",
        "quality",
        "quickqual",
        unit,
        "fingerprint",
        {
            "photographs": 2,
            "coverage": 1.0,
            "graded": 2,
            "declined": 0,
            "failed": 0,
            "gradeable": {"photographs": 2, "accuracy": 0.5, "roc_auc": None, "kappa": None},
            "three_class": None,
        },
        [{"key": "a"}],
    )

    path = report.write_index(results=tmp_path / "results", into=tmp_path / "docs")

    written = path.read_text()
    assert "quality" in written
    assert "quickqual" in written
    assert "fives/main/test" in written
    assert "—" in written, "a metric that does not exist is a dash, not a zero"
