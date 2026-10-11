# ABOUTME: Tests for the benchmark write-ups: one notebook and one results page per benchmark,
# ABOUTME: named after it.

from pathlib import Path

from benchmarks import report
from benchmarks.__main__ import BENCHMARKS


def test_every_benchmark_has_one_notebook_and_one_results_page() -> None:
    """Named after the benchmark, so the page and the notebook it was compiled from cannot drift.

    A benchmark's write-up is never split by what it measured: the comparison between its subjects
    is the one finding no subject could produce alone, and a page per subject has nothing to
    compare. See the `report-benchmark` skill.
    """
    root = Path(report.__file__).resolve().parents[2]

    for benchmark in BENCHMARKS:
        if not (root / "results" / benchmark).is_dir():
            continue  # declared, but nothing measured yet, so nothing is written up
        assert (root / "docs/benchmarks" / f"{benchmark}-results.md").exists(), (
            f"{benchmark} has no results page"
        )
        assert (root / "notebooks" / f"{benchmark}.ipynb").exists(), f"{benchmark} has no notebook"
