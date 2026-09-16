# ABOUTME: The quality benchmark: how well a model judges whether a photograph is worth measuring,
# ABOUTME: measured against the grade the dataset's own readers gave it.

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import torch
from torch.utils.data import DataLoader

from datasets.utils import paths
from models.utils import catalogue

from . import report, runs, scoring
from .loaders.base import CROPS, FLOOR, available, collate
from .loaders.quality import QualityLoader

#: What this benchmark is called: in `results/`, in `docs/benchmarks/` and in a run record.
NAME = "quality"

#: The benchmark's own version. Changing what is measured, or how, changes this, and every stored
#: score whose fingerprint carries the old one is measured again.
VERSION = 3

#: The datasets this benchmark wants. A name here is a statement of intent, not an inventory: a
#: dataset whose store has not been built is warned about, recorded, and stepped over.
DATASETS = ("fives", "fqs", "mshf", "papila", "eyeq", "drimdb")

#: The models, by the slug of their catalogue page, on the same terms.
MODELS = (
    "fit-quality",
    "vascx-quality",
    "automorph-quality-grader",
    "quickqual",
    "quickqual-meme",
)

#: How many photographs go to the model at once.
BATCH = 8


def adapters(slugs: list[str], device: str | None = None) -> tuple[list, dict[str, str]]:
    """The model adapters that exist, and what was declared without one."""
    found, missing = [], {}
    for slug in slugs:
        try:
            found.append(catalogue.load(slug, **({"device": device} if device else {})))
        except LookupError:
            missing[slug] = "no adapter written"
    return found, missing


def missing_datasets(slugs: list[str], root: Path | None = None) -> dict[str, str]:
    """What was declared that this run cannot measure, and why."""
    missing = {}
    for slug in slugs:
        if slug in CROPS:
            missing[slug] = "excluded whole: its images are crops rather than photographs"
        elif not available(slug, root):
            missing[slug] = "no store built"
    return missing


def configuration(
    models: list,
    datasets: list[str],
    root: Path | None = None,
) -> dict[str, object]:
    """What this run is about to do, without doing any of it.

    A loader reads a manifest rather than an image, so every fact the configuration page states —
    the models, the datasets, how many photographs each holds, what the exclusions take out — is
    known before a photograph is scored. That is what lets the page be written first.
    """
    absent = missing_datasets(datasets, root)
    described = []
    for slug in (name for name in datasets if name not in absent):
        loader = QualityLoader(slug, size=models[0].grid if models else 512, root=root)
        described.append(
            {
                "slug": slug,
                "total": loader.total,
                "excluded": dict(loader.excluded),
                "grade_source": loader.grade_sources,
                "padding": loader.padding,
            }
        )
    return {
        "models": [{"slug": model.slug, "declared": model.declare()} for model in models],
        "datasets": described,
    }


def run(
    models: list,
    datasets: list[str],
    results: Path = runs.RESULTS,
    root: Path | None = None,
    batch: int = BATCH,
    force: bool = False,
    record: Path | None = None,
    max_samples: int | None = None,
    random_samples: bool = False,
    seed: int = 0,
) -> list[dict[str, object]]:
    """Score every model on every dataset, measuring only what is missing.

    :param models: the model adapters, already constructed.
    :param datasets: the dataset slugs to score; those with no store are stepped over.
    :param record: where this run's own record is written; ``.atlas_runs/`` by default.
    :raises RuntimeError: if nothing declared is available to measure.
    """
    started = datetime.now(UTC)
    absent = missing_datasets(datasets, root)
    for slug, why in absent.items():
        print(f"warning: {slug} is not measured — {why}", file=sys.stderr)
    present = [slug for slug in datasets if slug not in absent]
    if not present or not models:
        raise RuntimeError(
            "nothing to measure: no declared dataset has a store built, or no declared model has "
            "an adapter. A report from an empty run would say nothing while looking like one that "
            "says something."
        )

    scored = []
    for adapter in models:
        for slug in present:
            scored.append(
                _pair(adapter, slug, results, root, batch, force, max_samples, random_samples, seed)
            )
        # Ten networks here and eight there add up: a model whose datasets are done is let go of
        # rather than held until the run ends.
        let_go = getattr(adapter, "release", None)
        if let_go is not None:
            let_go()
    _record(scored, absent, started, record or runs.RUNS)
    return scored


def _pair(
    adapter,
    slug: str,
    results: Path,
    root: Path | None,
    batch: int,
    force: bool,
    max_samples: int | None,
    random_samples: bool,
    seed: int,
) -> dict[str, object]:
    """One model on one dataset: keep what still stands, measure what is missing, write it all."""
    loader = QualityLoader(
        slug,
        size=adapter.grid,
        root=root,
        prepare=adapter.prepare,
        max_samples=max_samples,
        random_samples=random_samples,
        seed=seed,
    )
    declared = adapter.declare()
    store = _store(slug, root)
    loaded = adapter.identity()
    identity = runs.fingerprint(
        {
            "model": {name: declared[name] for name in FINGERPRINTED if name in declared},
            "weights": loaded,
            "store": store,
            "benchmark": {"name": NAME, "version": VERSION, "floor": FLOOR},
        }
    )

    kept = [] if force else runs.measured(results, NAME, adapter.slug, slug, identity)
    done = {entry["key"] for entry in kept}
    loader.restrict({row["key"] for row in loader.rows} - done)

    if len(loader):
        print(f"{adapter.slug} × {slug}: {len(loader)} photographs", flush=True)
        fresh = _rows(loader, _grade(adapter, loader, batch))
    else:
        print(f"{adapter.slug} × {slug}: kept, nothing left to measure", flush=True)
        fresh = []

    evidence = sorted(kept + fresh, key=lambda entry: entry["key"])
    counts = runs.counts(len(evidence), loader.total, loader.excluded)
    summary = {
        **scoring.summarise(
            {entry["key"]: entry["grade"] for entry in evidence},
            [scoring.restored(entry) for entry in evidence],
        ),
        "device": declared.get("device"),
    }
    runs.write(results, NAME, adapter.slug, slug, identity, {**summary, **counts}, evidence)
    return {
        "model": adapter.slug,
        "dataset": slug,
        "declared": declared,
        "store": store,
        "weights": loaded,
        "fingerprint": identity,
        "grade_source": sorted({entry["grade_source"] for entry in evidence}),
        "padding": loader.padding,
        "counts": counts,
        "summary": summary,
        "measured": len(fresh),
    }


#: What a model declares that could change its numbers, and therefore what its fingerprint is made
#: of. Everything else an adapter declares — the prose describing its gate, the vocabulary it
#: emits, the processor it happened to run on — is documentation: rewording it must not throw away
#: hours of measurement, and a number the model acts on must not hide inside a sentence, which is
#: why a threshold is declared as a number of its own.
FINGERPRINTED = (
    "slug",
    "purpose",
    "grid",
    "network_grid",
    "ensemble",
    "emits_probabilities",
    "threshold",
    "gate_threshold",
    "backbone",
)


def _grade(adapter, loader: QualityLoader, batch: int) -> list:
    """Every photograph still to be scored, in batches at the model's own grid."""
    graded = []
    for sample in DataLoader(loader, batch_size=batch, collate_fn=collate, shuffle=False):
        graded.extend(adapter.grade(sample["image"], sample["key"]))
    return graded


def _rows(loader: QualityLoader, grades: list) -> list[dict[str, object]]:
    """The per-image evidence: what the dataset said, and what the model said.

    Every row carries the same columns, including for a photograph the model failed on: a file
    whose columns depend on which photograph came first is not evidence of anything.
    """
    rows = {row["key"]: row for row in loader.rows}
    named = sorted({name for grade in grades for name in grade.classes})
    return [
        {
            "key": grade.key,
            "subset": rows[grade.key]["subset"],
            "split": rows[grade.key]["split"],
            "grade": rows[grade.key]["quality"],
            "grade_source": rows[grade.key]["quality_source"],
            "pad_fraction": rows[grade.key]["pad_fraction"],
            "readers": ";".join(
                f"{reader}={value}"
                for reader, value in sorted(loader.readers.get(grade.key, {}).items())
            ),
            "outcome": grade.outcome,
            "verdict": grade.verdict,
            "carried_by_its_pipeline": "" if grade.gated is None else str(grade.gated).lower(),
            "gradeable": "" if grade.gradeable is None else f"{grade.gradeable:.6f}",
            **{
                name: ("" if name not in grade.classes else f"{grade.classes[name]:.6f}")
                for name in named
            },
            "note": grade.note,
        }
        for grade in grades
    ]


def _store(slug: str, root: Path | None) -> dict[str, object]:
    """What the photographs were built by, so a rebuilt store is measured again."""
    build = (root or paths.root()) / slug / "build.json"
    record = json.loads(build.read_text()) if build.exists() else {}
    return {"slug": slug, "builder_version": record.get("builder_version")}


def _record(
    scored: list[dict[str, object]],
    absent: dict[str, str],
    started: datetime,
    into: Path,
) -> None:
    """A run's own record: what ran, against what, and when. A score without one is an anecdote."""
    directory = into / NAME / started.strftime("%Y-%m-%dT%H-%M-%SZ")
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "run.json").write_text(
        json.dumps(
            {
                "benchmark": NAME,
                "version": VERSION,
                "started": started.isoformat(),
                "torch": torch.__version__,
                "python": sys.version.split()[0],
                "not_measured": absent,
                "results": scored,
            },
            indent=2,
            sort_keys=True,
            default=str,
        )
        + "\n"
    )


def main(asked) -> None:
    """Run the benchmark as `python -m benchmarks --benchmark quality` asked for it."""
    from . import __main__ as entry

    root = Path(asked.data_root) if asked.data_root else None
    wanted_models = entry.named(asked.model) or list(MODELS)
    wanted_datasets = entry.named(asked.dataset) or list(DATASETS)

    models, no_adapter = adapters(wanted_models, asked.device)
    for slug, why in no_adapter.items():
        print(f"warning: {slug} is not measured — {why}", file=sys.stderr)

    # The documents describe the benchmark, not the command line: a run narrowed to one model or
    # one dataset must not rewrite them as though the rest had never been measured.
    declared, missing_adapters = adapters(list(MODELS), asked.device)
    missing_stores = missing_datasets(list(DATASETS), root)

    # The configuration page is written first: it describes the run that is about to happen, so a
    # run that dies halfway still leaves an accurate account of itself.
    if asked.report:
        report.write_docs(
            NAME,
            configuration(declared, list(DATASETS), root),
            missing_adapters,
            missing_stores,
            report.QUALITY_COLUMNS,
        )

    scored = run(
        models,
        wanted_datasets,
        root=root,
        batch=asked.batch or BATCH,
        force=asked.force,
        max_samples=asked.max_samples,
        random_samples=asked.random_samples,
        seed=asked.seed,
    )
    if not asked.report:
        return

    evidence = {
        (entry_["model"], entry_["dataset"]): runs.rows(
            runs.RESULTS, NAME, entry_["model"], entry_["dataset"]
        )
        for entry_ in scored
    }
    report.write_results(NAME, scored, evidence, missing_adapters, missing_stores)
    report.write_index()
