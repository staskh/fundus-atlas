# ABOUTME: Tests for the synthetic biomarker benchmark: how it counts agreement with geometry, and
# ABOUTME: what it records when an implementation answers only part of what it was asked.

import csv
from pathlib import Path


from benchmarks import biomarker_synthetic as benchmark


def a_result(results, shape, rows):
    """One shape's committed evidence, in the shape `_pooled` reads it back in."""
    directory = results / benchmark.NAME / "pvbm"
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / f"{shape}.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def test_the_evidence_records_what_was_said_and_nothing_about_what_is_right() -> None:
    """A run measures; it does not judge. The two were one thing and are now separable.

    The benchmark never reads the ground truth, so its evidence carries only what each
    implementation returned, under that implementation's own column names. Joining it to the
    store's `ground_truth.csv` is the analysis's work — which means the same evidence can be
    re-read against a corrected ground truth without measuring anything again, and a run cannot
    quietly decide what counts as agreement.
    """
    columns = set(benchmark.COLUMNS)

    assert "said_<key>" in columns
    assert not [name for name in columns if name.startswith("theory_")], (
        "a run that recorded the answer would be judging as well as measuring"
    )
    source = Path(benchmark.__file__).read_text()
    assert ".theory" not in source, "the run must not reach into a shape's ground truth"


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
    built = benchmark.library.build("straight", side=2048, rotation=0.0, um_per_px=5.0)

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


def test_the_committed_configuration_page_is_current() -> None:
    """A stale page fails the suite rather than sitting wrong in a public reference.

    `document-benchmark` §4 says the page is refreshed in the commit that makes it stale. Nobody
    can be reminded of that reliably, so it is checked: every marked block has to match what the
    benchmark currently reports about itself. Written prose is not compared, because nothing
    generates it.
    """
    from benchmarks import docs

    page = Path(docs.DIRECTORY) / f"{benchmark.NAME}-docs.md"
    current = page.read_text()

    assert docs.render(current, benchmark.config()) == current, (
        f"{page} is stale — refresh it with "
        f"`python -m benchmarks --benchmark {benchmark.NAME} --docs`"
    )
