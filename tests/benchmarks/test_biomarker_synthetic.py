# ABOUTME: Tests for the synthetic biomarker benchmark: how it counts agreement with geometry, and
# ABOUTME: what it records when an implementation answers only part of what it was asked.

import csv
from types import SimpleNamespace

import pytest

from benchmarks import biomarker_synthetic as benchmark


def a_result(results, shape, rows):
    """One shape's committed evidence, in the shape `_pooled` reads it back in."""
    directory = results / benchmark.NAME / "pvbm"
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / f"{shape}.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def test_an_exact_answer_of_zero_agrees_with_a_theory_of_zero(tmp_path) -> None:
    """A straight vessel has no junctions, and saying so is the right answer, not a miss.

    Counting it as a disagreement would mark every correct zero wrong — and it did: eight of this
    benchmark's own comparisons were exact zeros reported as failures to agree.
    """
    a_result(
        tmp_path,
        "straight",
        [
            {
                "key": "straight@0",
                "rotation": "0.0",
                "said_intersections_artery": "0",
                "theory_intersections_artery": "0",
            }
        ],
    )

    pooled = benchmark._pooled([{"model": "pvbm"}], tmp_path)

    assert pooled["pvbm"]["agreed"] == "1 of 1", "0 against a required 0 is exact"


def test_a_wrong_answer_against_a_theory_of_zero_still_disagrees(tmp_path) -> None:
    """The counterpart: a junction counted where the shape has none is not agreement."""
    a_result(
        tmp_path,
        "straight",
        [
            {
                "key": "straight@0",
                "rotation": "0.0",
                "said_intersections_artery": "4",
                "theory_intersections_artery": "0",
            }
        ],
    )

    pooled = benchmark._pooled([{"model": "pvbm"}], tmp_path)

    assert pooled["pvbm"]["agreed"] == "0 of 1"


class PartlyAnswering:
    """An implementation that measures one quantity and falls over on another, as PVBM does."""

    slug = "partial"

    def keys(self):
        return ("area_artery", "crae_knudtson")

    def measure(self, artery, vein, fov, disc, um_per_px):
        self.trouble = {"equivalents_artery": "RecursionError()"}
        return {"area_artery": 1234.0, "crae_knudtson": None}


def test_a_rendering_that_answered_in_part_is_measured_rather_than_failed() -> None:
    """`failed` must mean nothing came back, or a good area is thrown away with a bad equivalent.

    PVBM's equivalents raise on a long vessel while its geometry is measured perfectly well. Marking
    the whole rendering failed would have discarded four sound area measurements per shape.
    """
    adapter = PartlyAnswering()
    built = benchmark.library.build("straight", side=256, rotation=0.0, um_per_px=5.0)

    row = benchmark._row(
        adapter,
        built,
        0.0,
        adapter.measure(None, None, None, None, None),
        0.1,
        "equivalents_artery: RecursionError()",
    )

    assert row["outcome"] == "measured", "its area came back; only the equivalent did not"
    assert "RecursionError" in row["note"], "and the reason it could not answer is still recorded"


def test_a_rendering_that_answered_nothing_is_failed() -> None:
    """The counterpart: a call that produced no value at all is a failure, note or no note."""
    adapter = PartlyAnswering()
    built = benchmark.library.build("straight", side=256, rotation=0.0, um_per_px=5.0)

    row = benchmark._row(adapter, built, 0.0, dict.fromkeys(adapter.keys()), 0.1, "boom")

    assert row["outcome"] == "failed"


def test_the_configuration_page_is_written_before_anything_is_measured(
    tmp_path, monkeypatch
) -> None:
    """A run that dies halfway must still leave an accurate account of what it set out to do.

    That is the whole reason for the ordering, so the test is the failure: measuring raises, and
    the page describing the run has to be there anyway. Asserting the order of two calls would pass
    just as well with the page written from stale state; this asserts what the order is *for*.
    """
    written = tmp_path / "docs"
    written.mkdir()

    def dies(*_args, **_arguments):
        raise RuntimeError("the machine ran out of memory at rendering 9")

    # The real writer, pointed at a temporary directory: `into` defaults to the docs folder at
    # definition time, so redirecting the call is what works, and it keeps the page real enough to
    # assert its contents.
    generate = benchmark.report.write_docs

    def into_the_temporary_directory(*arguments, **named):
        return generate(*arguments, **{**named, "into": written})

    monkeypatch.setattr(benchmark.report, "write_docs", into_the_temporary_directory)
    monkeypatch.setattr(benchmark, "run", dies)
    asked = SimpleNamespace(
        model="pvbm", dataset="straight", force=False, max_samples=1, report=True
    )

    with pytest.raises(RuntimeError, match="ran out of memory"):
        benchmark.main(asked)

    page = written / f"{benchmark.NAME}-docs.md"
    assert page.exists(), "the run died and left no account of what it was going to do"
    assert "straight" in page.read_text(), "and the account names the shape it was asked for"


def test_the_configuration_page_describes_the_whole_benchmark_not_the_invocation(
    tmp_path, monkeypatch
) -> None:
    """`--dataset straight` narrows the run, and must not narrow the page describing the run.

    Every declared shape and implementation belongs on it, including the ones a given invocation
    skipped — otherwise a development run on one shape leaves a page claiming the benchmark has one
    shape, and the next reader believes it.
    """
    written = tmp_path / "docs"
    written.mkdir()
    generate = benchmark.report.write_docs

    def into_the_temporary_directory(*arguments, **named):
        return generate(*arguments, **{**named, "into": written})

    monkeypatch.setattr(benchmark.report, "write_docs", into_the_temporary_directory)
    monkeypatch.setattr(benchmark, "run", lambda *a, **k: [])
    monkeypatch.setattr(benchmark.report, "write_index", lambda *a, **k: None)

    benchmark.main(
        SimpleNamespace(model="pvbm", dataset="straight", force=False, max_samples=1, report=True)
    )

    page = (written / f"{benchmark.NAME}-docs.md").read_text()
    for shape in benchmark.SHAPES:
        assert shape in page, f"{shape} is declared and missing from the page"
