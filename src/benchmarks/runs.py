# ABOUTME: What a benchmark run keeps: per-image scores as the evidence, a summary beside them,
# ABOUTME: and the fingerprint that decides whether a stored score may be reused.

import csv
import hashlib
import json
from collections.abc import Iterable, Iterator
from pathlib import Path

from .loaders.base import Unit

#: Where per-image scores are committed. A summary table is a claim; these are its evidence, and
#: they are not reproducible without re-running everything.
RESULTS = Path(__file__).resolve().parents[2] / "results"

#: Where a run's own record and anything too large to commit is kept.
RUNS = Path(__file__).resolve().parents[2] / ".atlas_runs"


def fingerprint(facts: dict[str, object]) -> str:
    """One name for everything that could change a score.

    A re-run recomputes a (model, unit) pair only when this differs, so anything left out of it is
    something a stale score can outlive.
    """
    return hashlib.sha256(json.dumps(facts, sort_keys=True, default=str).encode()).hexdigest()


def write(
    root: Path,
    benchmark: str,
    model: str,
    unit: Unit,
    identity: str,
    summary: dict[str, object],
    rows: Iterable[dict[str, object]],
) -> None:
    """Record one model's result on one evaluation unit, evidence and summary together."""
    rows = list(rows)
    directory = root / benchmark / model
    directory.mkdir(parents=True, exist_ok=True)
    if rows:
        with open(directory / f"{unit.filename}.csv", "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]), restval="")
            writer.writeheader()
            writer.writerows(rows)
    (directory / f"{unit.filename}.json").write_text(
        json.dumps(
            {"model": model, "unit": unit.name, "fingerprint": identity, "summary": summary},
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )


def read(root: Path, benchmark: str, model: str, unit: Unit) -> dict[str, object] | None:
    """A stored result, or nothing where that pair was never measured."""
    path = root / benchmark / model / f"{unit.filename}.json"
    return json.loads(path.read_text()) if path.exists() else None


def rows(root: Path, benchmark: str, model: str, unit: Unit) -> Iterator[dict[str, str]]:
    """The per-image evidence behind one stored result."""
    path = root / benchmark / model / f"{unit.filename}.csv"
    if not path.exists():
        return
    with open(path, newline="") as f:
        yield from csv.DictReader(f)


def reusable(
    root: Path, benchmark: str, model: str, unit: Unit, identity: str
) -> dict[str, object] | None:
    """The stored result, where it still describes the thing that would be run now."""
    found = read(root, benchmark, model, unit)
    return found if found and found.get("fingerprint") == identity else None
