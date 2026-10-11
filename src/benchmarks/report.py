# ABOUTME: The index a benchmark run generates over every benchmark's results, and the small
# ABOUTME: formatting helpers the generated tables share.

import importlib
import json
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path

from . import contamination, runs

#: Where the benchmark pages live, beside the catalogues they refer to.
#:
#: A run generates only the index. `<slug>-docs.md` is refreshed by `--docs` from what the
#: benchmark reports about itself (the `document-benchmark` skill), and `<slug>-results.md` is
#: **written**, from the notebook's analysis, because a conclusion is a judgement (the
#: `report-benchmark` skill). Nothing here writes either, so a run cannot destroy them.
DIRECTORY = Path(__file__).resolve().parents[2] / "docs" / "benchmarks"


def excluded(counted: dict[str, int]) -> str:
    if not counted:
        return "none"
    return "; ".join(f"{count} {reason}" for reason, count in sorted(counted.items()))


def pin(upstream: dict[str, object]) -> str:
    commit = str(upstream.get("commit", ""))
    return f"`{commit[:8]}`" if commit else str(upstream.get("version", "—"))


def number(value: float | None, places: int = 3) -> str:
    """One figure for a table, or an em-dash where a model was never asked the question.

    :param places: decimals to show. A count — how many topological features went unmatched — is
        not a score between nought and one and is written without a decimal point at all.
    """
    return "—" if value is None else f"{value:.{places}f}"


def seconds(summary: dict[str, object]) -> str:
    """How long a model took per photograph, where a run recorded it."""
    taken = summary.get("seconds_per_photograph")
    return "—" if taken is None else f"{float(taken):.3f}"


def today() -> str:
    """The date a page was generated, in UTC, so two machines date the same run alike."""
    return datetime.now(UTC).date().isoformat()


def write_index(results: Path = runs.RESULTS, into: Path = DIRECTORY.parent) -> Path:
    """Write `docs/BENCHMARKS.md`, one section per benchmark that has results on disk."""
    into.mkdir(parents=True, exist_ok=True)
    path = into / "BENCHMARKS.md"
    path.write_text("\n".join(_index(results)) + "\n")
    return path


def _index(results: Path) -> Iterable[str]:
    """The index: what each benchmark asks, how its models did, and where to read more.

    Everything here is a pointer. One benchmark is one section — its question in a paragraph, one
    table with a row per model, and where to start — and every number on it is a summary of a page
    that argues it properly.
    """
    yield "# Benchmarks"
    yield ""
    yield (
        "What this repository measured against what experts annotated, on the same images and on "
        "the same terms. **This page is an index**: one section per benchmark, each with what it "
        "asks, one row per model, and links to the pages that argue it. Nothing here is the "
        "argument — the per-dataset detail, the caveats and the reasoning live behind those links, "
        "and `results/` holds the score of every photograph behind every number. It is generated "
        "by the runs."
    )
    yield ""
    yield (
        "**Read a row, not a column.** A result marked `in-sample` or `unknown` is not comparable "
        "with one marked `out-of-sample`, and a model agreeing with another model is not evidence "
        "that either agrees with an expert. Every figure below is **pooled over the datasets that "
        "benchmark measured**, which the section says; a model is rarely equally good on all of "
        "them, and where it is not, that is on its results page rather than here."
    )
    # `results/` holds more than benchmarks — `um_resolution/` is a per-dataset measurement — so
    # the index walks the benchmarks this repository declares and keeps those with results on disk.
    from . import __main__ as entry

    for benchmark in sorted(name for name in entry.BENCHMARKS if (results / name).is_dir()):
        module = _module(benchmark)
        records = list(_stored(results / benchmark))
        yield ""
        yield f"## {module.TITLE}"
        yield ""
        yield module.GOAL
        yield ""
        yield (
            f"[How it is run](benchmarks/{benchmark}-docs.md) · "
            f"[What came out](benchmarks/{benchmark}-results.md) · "
            f"[The analysis](../notebooks/{benchmark}.ipynb) · "
            f"[Every score](../results/{benchmark}/)"
        )
        yield ""
        yield from module.index_section(records, results)
    yield ""
    yield "---"
    yield ""
    yield f"**Generated:** {today()}"


def datasets_of(records: list[dict[str, object]]) -> str:
    """Which datasets a benchmark has results for, as the index names them."""
    return ", ".join(sorted({str(record["dataset"]) for record in records}))


def mark_of(model: str, records: list[dict[str, object]]) -> str:
    """One contamination mark for a model, or the word that says they differ."""
    marks = {
        contamination.mark(model, str(record["dataset"]))
        for record in records
        if record["model"] == model
    }
    return marks.pop() if len(marks) == 1 else "mixed: " + ", ".join(sorted(marks))


def unfinished(records: list[dict[str, object]]) -> str:
    """A line naming what has not been measured in full, or nothing at all."""
    partial = [
        f"{record['model']} × {record['dataset']} "
        f"({record['summary'].get('processed')} of {record['summary'].get('total')})"
        for record in records
        if not record["summary"].get("complete", True)
    ]
    return (
        "**Not finished:** " + "; ".join(sorted(partial)) + ". Those rows are averages over what "
        "has been measured so far."
        if partial
        else ""
    )


def _stored(directory: Path) -> Iterable[dict[str, object]]:
    for path in sorted(directory.glob("*/*.json")):
        yield json.loads(path.read_text())


def _module(benchmark: str):
    """The benchmark's own module, which owns the prose only it can write.

    What a benchmark measures decides how its pages read, so the sections describing that live
    beside the code that measures it rather than in a switch here.
    """
    # A benchmark's name may carry a hyphen — `biomarker-synthetic` — and a module name may not.
    return importlib.import_module(f"{__package__}.{benchmark.replace('-', '_')}")
