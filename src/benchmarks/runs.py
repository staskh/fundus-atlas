# ABOUTME: What a benchmark run keeps: per-image scores as the evidence, a summary beside them,
# ABOUTME: and the fingerprint that decides whether what is stored still describes anything.

import csv
import hashlib
import json
from collections.abc import Iterable
from pathlib import Path

#: Where per-image scores are committed. The benchmark's own name leads the path, so that two
#: benchmarks scoring the same model on the same photographs stay apart; the model comes next,
#: because that is how these files are read — one directory holds a model's evidence on every
#: dataset.
RESULTS = Path(__file__).resolve().parents[2] / "results"

#: Where a run's own record and anything too large to commit is kept.
RUNS = Path(__file__).resolve().parents[2] / ".atlas_runs"


def fingerprint(facts: dict[str, object]) -> str:
    """One name for everything that could change a score.

    Anything left out of this is something a stale score can outlive. What is deliberately **not**
    in it is how much of a dataset was done: that changes how complete a result is, not what any
    photograph scored.
    """
    return hashlib.sha256(json.dumps(facts, sort_keys=True, default=str).encode()).hexdigest()


def counts(processed: int, total: int, excluded: dict[str, int]) -> dict[str, object]:
    """How much of a dataset a result covers.

    ``processed`` is what the model actually scored and ``total`` what the benchmark would ask
    about; ``excluded`` is what the benchmark's own rules took out, by reason, so that
    ``total + excluded`` is what the store holds. Our `excluded` is never added to a model's
    `declined`: one says the benchmark would not ask, the other that the model would not answer.
    """
    return {
        "processed": processed,
        "total": total,
        "complete": processed >= total,
        "excluded": dict(excluded),
    }


class Timing:
    """How long a model takes per photograph, once it is loaded.

    The first batch of a run carries the weight loading with it — seconds spent starting the model
    rather than measuring a photograph — so it is left out whenever there is another batch to
    average over. A run of one batch is timed with its loading in it, because there is nothing else
    to time, and its photograph count says how thin that is.

    This is never part of a fingerprint: how fast a model answered does not change what it said.
    """

    def __init__(self) -> None:
        self.batches: list[tuple[float, int]] = []

    def record(self, seconds: float, photographs: int) -> None:
        self.batches.append((seconds, photographs))

    def summary(self) -> dict[str, object]:
        timed = self.batches[1:] if len(self.batches) > 1 else self.batches
        photographs = sum(count for _, count in timed)
        if not photographs:
            return {}
        return {
            "seconds_per_photograph": sum(seconds for seconds, _ in timed) / photographs,
            "timed_photographs": photographs,
        }


def kept_timing(stored: dict[str, object] | None, timed: Timing) -> dict[str, object]:
    """This run's timing, or the one already stored where this run measured nothing."""
    measured = timed.summary()
    if measured:
        return measured
    was = (stored or {}).get("summary", {})
    return {
        name: was[name] for name in ("seconds_per_photograph", "timed_photographs") if name in was
    }


def write(
    root: Path,
    benchmark: str,
    model: str,
    dataset: str,
    identity: str,
    summary: dict[str, object],
    rows: Iterable[dict[str, object]],
) -> None:
    """Record one model's result on one dataset, evidence and summary together."""
    rows = sorted(rows, key=lambda row: row["key"])
    directory = root / benchmark / model
    directory.mkdir(parents=True, exist_ok=True)
    if rows:
        with open(directory / f"{dataset}.csv", "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]), restval="")
            writer.writeheader()
            writer.writerows(rows)
    (directory / f"{dataset}.json").write_text(
        json.dumps(
            {
                "benchmark": benchmark,
                "model": model,
                "dataset": dataset,
                "fingerprint": identity,
                "summary": summary,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )


def read(root: Path, benchmark: str, model: str, dataset: str) -> dict[str, object] | None:
    """A stored result, or nothing where that pair was never measured."""
    path = root / benchmark / model / f"{dataset}.json"
    return json.loads(path.read_text()) if path.exists() else None


def rows(root: Path, benchmark: str, model: str, dataset: str) -> list[dict[str, str]]:
    """The per-image evidence behind one stored result."""
    path = root / benchmark / model / f"{dataset}.csv"
    if not path.exists():
        return []
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def measured(
    root: Path, benchmark: str, model: str, dataset: str, identity: str
) -> list[dict[str, str]]:
    """The photographs already scored that this run may keep.

    Nothing is kept when the fingerprint differs: those scores describe something that no longer
    exists, and finishing them would mix two measurements in one file.
    """
    found = read(root, benchmark, model, dataset)
    if not found or found.get("fingerprint") != identity:
        return []
    return rows(root, benchmark, model, dataset)
