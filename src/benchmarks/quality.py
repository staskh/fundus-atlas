# ABOUTME: The quality benchmark: how well a model judges whether a photograph is worth measuring,
# ABOUTME: measured on the datasets that graded their own photographs.

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import torch
from torch.utils.data import DataLoader

from datasets.utils import paths

from . import contamination, runs, scoring
from .loaders.base import FLOOR, Unit, collate
from .loaders.base import units as units_of
from .loaders.quality import QualityLoader
from .report import write_index, write_report

#: What this benchmark is called, in `results/`, in `docs/benchmarks/` and in a run record.
NAME = "quality"

#: The benchmark's own version. Changing what is measured, or how, changes this, and every stored
#: score whose fingerprint carries the old one is measured again.
VERSION = 1

#: The datasets this benchmark is run on by default: the ones that grade the photograph itself and
#: are not excluded by the size floor or the crop rule.
DATASETS = ("fives", "fqs", "mshf")

#: The models, by the slug of their catalogue page.
MODELS = ("fit-quality", "vascx-quality", "automorph-quality-grader", "quickqual")

#: How many photographs go to the model at once.
BATCH = 8


def run(
    adapters: list,
    units: list[Unit],
    results: Path = runs.RESULTS,
    root: Path | None = None,
    batch: int = BATCH,
    force: bool = False,
    record: Path | None = None,
) -> list[dict[str, object]]:
    """Score every model on every evaluation unit, measuring only what has changed.

    :param adapters: the model adapters, already constructed.
    :param results: where per-image scores and summaries are kept.
    :param record: where this run's own record is written; ``.atlas_runs/`` by default.
    :return: one entry per (model, unit), whether it was measured now or read from `results/`.
    """
    started = datetime.now(UTC)
    scored: list[dict[str, object]] = []
    for adapter in adapters:
        for unit in units:
            scored.append(_pair(adapter, unit, results, root, batch, force))
    _record(scored, started, record or runs.RUNS)
    return scored


def _pair(
    adapter, unit: Unit, results: Path, root: Path | None, batch: int, force: bool
) -> dict[str, object]:
    loader = QualityLoader(unit, size=adapter.grid, root=root, prepare=adapter.prepare)
    declared = adapter.declare()
    store = _store(unit, root)
    loaded = adapter.identity()
    identity = runs.fingerprint(
        {
            "model": {name: value for name, value in declared.items() if name != "device"},
            "weights": loaded,
            "store": store,
            "photographs": len(loader),
            "benchmark": {"name": NAME, "version": VERSION, "floor": FLOOR},
        }
    )
    common = {
        "model": adapter.slug,
        "unit": unit.name,
        "contamination": contamination.mark(adapter.slug, unit),
        "grid": declared["grid"],
        "network_grid": declared["network_grid"],
        "fingerprint": identity,
        "declared": declared,
        "store": store,
        "weights": loaded,
    }

    kept = None if force else runs.reusable(results, NAME, adapter.slug, unit, identity)
    if kept is not None:
        print(f"{adapter.slug} × {unit.name}: kept, nothing that could change it has", flush=True)
        return {**common, "summary": kept["summary"], "reused": True}

    print(f"{adapter.slug} × {unit.name}: {len(loader)} photographs", flush=True)
    grades = _grade(adapter, loader, batch)
    truth = {row["key"]: row["quality"] for row in loader.rows}
    summary = {
        **scoring.summarise(truth, grades),
        "without_reference": len(loader.without_reference),
        "device": declared.get("device"),
    }
    runs.write(results, NAME, adapter.slug, unit, identity, summary, _rows(loader, grades))
    print(
        f"{adapter.slug} × {unit.name}: covered {summary['coverage']:.2f}, "
        f"accuracy {summary['gradeable']['accuracy']}",
        flush=True,
    )
    return {**common, "summary": summary, "reused": False}


def _grade(adapter, loader: QualityLoader, batch: int) -> list:
    """Every photograph of one unit, in batches at the model's own grid."""
    graded = []
    for sample in DataLoader(loader, batch_size=batch, collate_fn=collate, shuffle=False):
        graded.extend(adapter.grade(sample["image"], sample["key"]))
    return graded


def _rows(loader: QualityLoader, grades: list) -> list[dict[str, object]]:
    """The per-image evidence: what the dataset said, and what the model said.

    Every row carries the same columns, including for a photograph the model failed on: a file
    whose columns depend on which photograph came first is not evidence of anything.
    """
    readers = {row["key"]: loader.readers.get(row["key"], {}) for row in loader.rows}
    truth = {row["key"]: row["quality"] for row in loader.rows}
    named = sorted({name for grade in grades for name in grade.classes})
    return [
        {
            "key": grade.key,
            "grade": truth[grade.key],
            "readers": ";".join(
                f"{reader}={value}" for reader, value in sorted(readers[grade.key].items())
            ),
            "outcome": grade.outcome,
            "verdict": grade.verdict,
            "gradeable": "" if grade.gradeable is None else f"{grade.gradeable:.6f}",
            **{
                name: ("" if name not in grade.classes else f"{grade.classes[name]:.6f}")
                for name in named
            },
            "note": grade.note,
        }
        for grade in grades
    ]


def _store(unit: Unit, root: Path | None) -> dict[str, object]:
    """What the photographs were built by, so a rebuilt store is measured again."""
    build = (root or paths.root()) / unit.slug / "build.json"
    record = json.loads(build.read_text()) if build.exists() else {}
    return {"slug": unit.slug, "builder_version": record.get("builder_version")}


def _record(scored: list[dict[str, object]], started: datetime, into: Path) -> None:
    """A run's own record: what ran, against what, and when. A score without one is an anecdote."""
    stamp = started.strftime("%Y-%m-%dT%H-%M-%SZ")
    directory = into / NAME / stamp
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "run.json").write_text(
        json.dumps(
            {
                "benchmark": NAME,
                "version": VERSION,
                "started": started.isoformat(),
                "torch": torch.__version__,
                "python": sys.version.split()[0],
                "results": scored,
            },
            indent=2,
            sort_keys=True,
            default=str,
        )
        + "\n"
    )


def main(argv: list[str] | None = None) -> None:
    from models.utils import catalogue

    parser = argparse.ArgumentParser(
        prog="python -m benchmarks.quality",
        description="Score quality models against the grades their datasets published.",
    )
    parser.add_argument("--models", default=",".join(MODELS), help="model slugs, comma separated")
    parser.add_argument("--datasets", default=",".join(DATASETS), help="dataset slugs")
    parser.add_argument("--device", help="cuda, mps or cpu; the fastest available by default")
    parser.add_argument("--batch", type=int, default=BATCH, help=f"batch size (default {BATCH})")
    parser.add_argument("--data-root", help="override the store root")
    parser.add_argument("--force", action="store_true", help="measure again, fingerprint or not")
    parser.add_argument(
        "--no-report", dest="report", action="store_false", help="skip the write-up"
    )
    args = parser.parse_args(argv)

    root = Path(args.data_root) if args.data_root else None
    adapters = [
        catalogue.load(slug, **({"device": args.device} if args.device else {}))
        for slug in args.models.split(",")
    ]
    units = [unit for slug in args.datasets.split(",") for unit in units_of(slug, root=root)]
    scored = run(adapters, units, root=root, batch=args.batch, force=args.force)
    if args.report:
        write_report(NAME, scored)
        write_index()


if __name__ == "__main__":
    main()
