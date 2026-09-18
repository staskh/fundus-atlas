# ABOUTME: Tests for what a run keeps: the per-image evidence, the summary beside it, the
# ABOUTME: fingerprint that says whether it is still valid, and the merge that finishes it.

from pathlib import Path

from benchmarks import runs


def test_a_fingerprint_is_the_same_for_the_same_facts_in_any_order() -> None:
    one = runs.fingerprint({"weights": "abc", "commit": "def"})

    assert one == runs.fingerprint({"commit": "def", "weights": "abc"})
    assert len(one) == 64


def test_a_changed_fact_is_a_different_fingerprint() -> None:
    assert runs.fingerprint({"weights": "abc"}) != runs.fingerprint({"weights": "abd"})


def test_a_result_is_written_where_its_benchmark_its_model_and_its_dataset_say(
    tmp_path: Path,
) -> None:
    runs.write(tmp_path, "quality", "quickqual", "fives", "abc", {"coverage": 1.0}, [{"key": "a"}])

    assert (tmp_path / "quality" / "quickqual" / "fives.csv").exists()
    assert (tmp_path / "quality" / "quickqual" / "fives.json").exists()


def test_a_result_is_read_back_as_it_was_written(tmp_path: Path) -> None:
    rows = [{"key": "a", "grade": "good", "outcome": "graded", "gradeable": "0.9"}]

    runs.write(tmp_path, "quality", "quickqual", "fives", "abc", {"coverage": 1.0}, rows)
    found = runs.read(tmp_path, "quality", "quickqual", "fives")

    assert found["fingerprint"] == "abc"
    assert found["summary"] == {"coverage": 1.0}
    assert list(runs.rows(tmp_path, "quality", "quickqual", "fives")) == rows


def test_nothing_is_read_back_where_nothing_was_measured(tmp_path: Path) -> None:
    assert runs.read(tmp_path, "quality", "quickqual", "fives") is None
    assert runs.measured(tmp_path, "quality", "quickqual", "fives", "abc") == []


def test_what_was_measured_under_this_fingerprint_is_offered_back(tmp_path: Path) -> None:
    runs.write(tmp_path, "quality", "quickqual", "fives", "abc", {}, [{"key": "a"}, {"key": "b"}])

    kept = runs.measured(tmp_path, "quality", "quickqual", "fives", "abc")

    assert [row["key"] for row in kept] == ["a", "b"]


def test_what_was_measured_under_another_fingerprint_is_not(tmp_path: Path) -> None:
    runs.write(tmp_path, "quality", "quickqual", "fives", "before", {}, [{"key": "a"}])

    assert runs.measured(tmp_path, "quality", "quickqual", "fives", "after") == []


def test_the_counts_say_what_was_done_of_what_there_is(tmp_path: Path) -> None:
    counts = runs.counts(processed=20, total=488, excluded={"below the size floor": 12})

    assert counts == {
        "processed": 20,
        "total": 488,
        "complete": False,
        "excluded": {"below the size floor": 12},
    }


def test_a_result_is_complete_when_everything_left_was_processed(tmp_path: Path) -> None:
    assert runs.counts(processed=488, total=488, excluded={})["complete"] is True


def test_rows_are_written_in_the_order_the_dataset_holds_them(tmp_path: Path) -> None:
    runs.write(tmp_path, "quality", "quickqual", "fives", "abc", {}, [{"key": "b"}, {"key": "a"}])

    assert [row["key"] for row in runs.rows(tmp_path, "quality", "quickqual", "fives")] == [
        "a",
        "b",
    ], "a resumed run appends, and the evidence must not depend on when a photograph was scored"


def test_the_index_reads_a_partial_result_as_unfinished(tmp_path: Path) -> None:
    from benchmarks import report

    runs.write(
        tmp_path / "results",
        "quality",
        "quickqual",
        "fives",
        "fingerprint",
        {
            "processed": 20,
            "total": 488,
            "complete": False,
            "coverage": 1.0,
            "gradeable": {"accuracy": 0.5, "kappa": 0.1, "roc_auc": None},
        },
        [{"key": "a"}],
    )

    written = report.write_index(results=tmp_path / "results", into=tmp_path / "docs").read_text()

    assert "20 of 488" in written, "an unfinished result says so on the index"
    assert "Not finished" in written
    assert "Cohen's κ" in written and "0.100" in written


def test_timing_leaves_out_the_batch_that_loaded_the_model() -> None:
    timed = runs.Timing()
    timed.record(seconds=10.0, photographs=2)  # the first batch loads the weights
    timed.record(seconds=1.0, photographs=2)
    timed.record(seconds=3.0, photographs=2)

    assert timed.summary() == {"seconds_per_photograph": 1.0, "timed_photographs": 4}


def test_one_batch_is_timed_with_its_loading_because_there_is_nothing_else() -> None:
    timed = runs.Timing()
    timed.record(seconds=8.0, photographs=4)

    assert timed.summary() == {"seconds_per_photograph": 2.0, "timed_photographs": 4}


def test_a_run_that_measured_nothing_reports_no_timing() -> None:
    assert runs.Timing().summary() == {}


def test_the_index_lists_benchmarks_and_not_every_directory_of_results(tmp_path: Path) -> None:
    """`results/` holds more than benchmarks: `um_resolution/` is a dataset measurement.

    The index took every directory there for a benchmark and tried to import a module for it.
    """
    from benchmarks import report

    (tmp_path / "results" / "um_resolution").mkdir(parents=True)
    (tmp_path / "results" / "um_resolution" / "chaksu.json").write_text("{}")

    written = report.write_index(results=tmp_path / "results", into=tmp_path / "docs").read_text()

    assert "um_resolution" not in written
    assert "# Benchmarks" in written
