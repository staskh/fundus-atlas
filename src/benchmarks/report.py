# ABOUTME: The two documents a benchmark run generates — how it is configured, and what came out.
# ABOUTME: Written by the run rather than by hand, so they cannot drift from the numbers.

import importlib
import json
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path

from . import contamination, runs

#: Where the generated documents live, beside the catalogues they refer to.
#:
#: Only the configuration page and the index are generated. `<slug>-results.md` is **written**,
#: from the notebook's analysis, because a conclusion is a judgement — see the `report-benchmark`
#: skill. Nothing here writes it, so that a run cannot destroy what somebody concluded.
DIRECTORY = Path(__file__).resolve().parents[2] / "docs" / "benchmarks"


def write_docs(
    benchmark: str,
    configured: dict[str, object],
    missing_models: dict[str, str],
    missing_datasets: dict[str, str],
    columns: dict[str, str],
    into: Path = DIRECTORY,
) -> Path:
    """Write the page saying how this benchmark is configured and run.

    It is written **before** anything is measured — everything on it is known from the manifests —
    so that a run which dies halfway still leaves an accurate account of what it was going to do,
    and so that anybody can read what is about to happen before committing hours of it.
    """
    into.mkdir(parents=True, exist_ok=True)
    path = into / f"{benchmark}-docs.md"
    path.write_text(
        "\n".join(_docs(benchmark, configured, missing_models, missing_datasets, columns)) + "\n"
    )
    return path


def _docs(
    benchmark: str,
    configured: dict[str, object],
    missing_models: dict[str, str],
    missing_datasets: dict[str, str],
    columns: dict[str, str],
) -> Iterable[str]:
    models = sorted(configured["models"], key=lambda entry: entry["slug"])
    datasets = sorted(configured["datasets"], key=lambda entry: entry["slug"])
    yield f"# {_module(benchmark).TITLE} benchmark — how it is run"
    yield ""
    yield (
        "This page says how the benchmark is configured: what it asks, which models and datasets "
        "take part, what it excludes, how to run it, and what every column of its evidence means. "
        "It is generated **before** a run measures anything, and again whenever the benchmark's "
        "code changes, so it describes the run that is happening rather than the one that happened "
        "to finish. A column added to the evidence and not explained here is a bug rather than an "
        f"omission. What came out is a separate page: [{benchmark}-results.md]"
        f"({benchmark}-results.md)."
    )
    yield ""
    yield from _module(benchmark).docs_sections(configured, missing_models, missing_datasets)
    yield "## 5. How to run it"
    yield ""
    yield "```bash"
    yield f"python -m benchmarks --benchmark {benchmark}"
    yield (
        f"python -m benchmarks --benchmark {benchmark} "
        f"--model {models[0]['slug']} --dataset {datasets[0]['slug']}"
    )
    yield f"python -m benchmarks --benchmark {benchmark} --max-samples 20"
    yield "```"
    yield ""
    yield (
        "`--model` and `--dataset` each take one name or a comma-separated list, and naming one of "
        "each re-measures a single pair. `--max-samples N` scores the first N photographs of each "
        "dataset — `--random-samples` chooses them at random from a recorded seed — which is for "
        "development: a sampled result says it is not complete, and a later run finishes it rather "
        "than starting again. `--force` discards what is stored and measures everything afresh."
    )
    yield ""
    yield "## 6. What each column of the evidence means"
    yield ""
    yield f"`results/{benchmark}/<model>/<dataset>.csv` holds one row per photograph:"
    yield ""
    yield "| Column | Meaning |"
    yield "| --- | --- |"
    for column, meaning in columns.items():
        yield f"| `{column}` | {meaning} |"
    yield ""
    yield (
        "A model that has no opinion to record leaves a column **absent** rather than blank: a "
        "binary grader emits no class probabilities, and none are invented for it."
    )
    caveat = getattr(_module(benchmark), "COLUMNS_CAVEAT", "")
    if caveat:
        yield ""
        yield caveat
    yield ""
    yield "## 7. What a re-run repeats, and what it does not"
    yield ""
    yield (
        "Each `(model, dataset)` result is stored beside a **fingerprint** of everything that "
        "could change it: the facts the model declares — its grids, its ensemble, the thresholds "
        "it acts on — the sha256 of the weights actually loaded, the patches applied by content, "
        "the store's builder version, and this benchmark's own version. A fingerprint that differs "
        "means the stored scores describe something that no longer exists, and the pair is "
        "measured again from nothing."
    )
    yield ""
    yield (
        "**How much was done is not part of that**, because it does not change what any photograph "
        "scored. A complete result is never re-run; a partial one is finished by measuring only "
        "the photographs it is missing; and nothing is ever truncated — asking for twenty against "
        "a file that holds four hundred leaves all four hundred alone."
    )
    yield ""
    yield "## 8. The counts every result carries"
    yield ""
    yield "| Recorded | Means |"
    yield "| --- | --- |"
    yield "| `processed` | how many photographs this model has actually scored |"
    yield "| `total` | how many the benchmark would ask about, after the exclusions of section 4 |"
    yield "| `excluded` | how many those exclusions removed, by reason |"
    yield (
        "| `seconds_per_photograph` | how long the model itself took per photograph, on the "
        "device the result names |"
    )
    yield "| `timed_photographs` | how many photographs that timing covers |"
    yield ""
    yield (
        "`processed ≤ total`, and `total + excluded` is what the store holds: a photograph is "
        "either one the benchmark asks about or one it excluded, never both and never neither."
    )
    yield ""
    yield (
        "The timing covers the model's own call and nothing around it — not reading the "
        "photograph, not scoring the answer. The batch that loads the weights is left out of it "
        "whenever there is another batch to average over, and a run that measured nothing keeps "
        "the timing it already had rather than reporting none. It is **not** part of the "
        "fingerprint: how fast a model answered does not change what it said, and the same "
        "weights on another machine would give another number."
    )
    yield ""
    yield "---"
    yield ""
    yield f"**Generated by `python -m benchmarks --benchmark {benchmark}` on:** {today()}"


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

    for benchmark in sorted(
        name for name in entry.BENCHMARKS if (results / name).is_dir()
    ):
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
