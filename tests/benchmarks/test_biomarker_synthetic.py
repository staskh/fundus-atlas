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
