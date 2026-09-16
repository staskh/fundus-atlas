# ABOUTME: The disc-and-cup benchmark: how close a model's outline is to the one an ophthalmologist
# ABOUTME: drew, and how far that difference travels into the numbers computed from it.

import json
import sys
import time
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader

from datasets.utils import paths
from models.utils import catalogue

from . import contamination, report, runs
from .loaders.base import CROPS, FLOOR, available, collate
from .loaders.disc import DiscCupLoader
from .metrics import disc as metrics

#: What this benchmark is called: in `results/`, in `docs/benchmarks/` and in a run record.
NAME = "disc"

#: The benchmark's own version. Changing what is measured, or how, changes this.
VERSION = 1

#: The datasets this benchmark wants. A name here is intent, not inventory: one whose store is not
#: built is warned about, recorded, and stepped over.
DATASETS = ("chaksu", "grape", "papila", "refuge", "drishti-gs", "origa", "rim-one-dl")

#: The models, by the slug of their catalogue page.
MODELS = ("vascx-disc", "automorph-disc-cup", "segformer-disc-cup", "beal", "lunetv2-odc", "isfa")

#: Why a declared model has no adapter, where the reason is worth more than "nobody wrote one".
#: A model the benchmark asks for and cannot run is a standing question, not an oversight.
WHY_NOT = {
    "isfa": (
        "its repository publishes an ImageNet backbone under `pretrained_model/`, not trained "
        "weights — checked against the repository, and its own weights link now 404s"
    ),
    "beal": (
        "no adapter yet: its weights are an unversioned Google Drive folder, so nothing can be "
        "pinned, and its inference expects the authors' own preprocessed directory layout"
    ),
}

#: Datasets worth fetching next, and what each would settle that the built ones cannot. Three of
#: the models here trained on REFUGE, so the first line is what turns "these models agree with each
#: other" from a suspicion into a measured contrast.
WORTH_FETCHING = (
    (
        "refuge",
        "three of the models here trained on it, so it is what turns an in-sample suspicion into "
        "a measured contrast",
        "registration",
    ),
    (
        "drishti-gs",
        "four experts **and soft probability maps** — the only dataset here publishing annotator "
        "uncertainty as a map rather than as separate outlines",
        "direct",
    ),
    (
        "origa",
        "publishes `ExpCDR`, an expert cup-to-disc ratio **as a number**, which is the strongest "
        "available check that a ratio derived from contours means what this benchmark thinks",
        "needs an archive by hand",
    ),
    (
        "rim-one-dl",
        "BEAL's other unlabelled target domain; it completes the contamination picture for that "
        "model once there is an adapter for it",
        "direct",
    ),
)

#: How many photographs go to the model at once. Lower than the quality benchmark's: these models
#: work at 512 or 1024 and their outputs are resampled to native, which is where the memory goes.
BATCH = 4

#: What a model declares that could change its numbers. Prose is documentation; these are facts.
FINGERPRINTED = (
    "slug",
    "purpose",
    "grid",
    "network_grid",
    "structures",
    "emits_probabilities",
    "resampling",
    "threshold",
    "ensemble",
)


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


def configuration(models: list, datasets: list[str], root: Path | None = None) -> dict[str, object]:
    """What this run is about to do, without doing any of it."""
    absent = missing_datasets(datasets, root)
    described = []
    for slug in (name for name in datasets if name not in absent):
        loader = DiscCupLoader(slug, size=models[0].grid if models else 512, root=root)
        readers = sorted(
            {reader for row in loader.rows for reader in row["readers"].split(";") if reader}
        )
        described.append(
            {
                "slug": slug,
                "total": loader.total,
                "excluded": dict(loader.excluded),
                "readers": readers,
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
    """Score every model on every dataset, measuring only what is missing."""
    started = datetime.now(UTC)
    absent = missing_datasets(datasets, root)
    for slug, why in absent.items():
        print(f"warning: {slug} is not measured — {why}", file=sys.stderr)
    present = [slug for slug in datasets if slug not in absent]
    if not present or not models:
        raise RuntimeError(
            "nothing to measure: no declared dataset has a store built, or no declared model has "
            "an adapter"
        )

    scored = []
    for adapter in models:
        for slug in present:
            scored.append(
                _pair(adapter, slug, results, root, batch, force, max_samples, random_samples, seed)
            )
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
    loader = DiscCupLoader(
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
    done = {row["key"] for row in kept}
    loader.restrict({row["key"] for row in loader.rows} - done)

    timed = runs.Timing()
    if len(loader):
        print(f"{adapter.slug} × {slug}: {len(loader)} photographs", flush=True)
        fresh = _outline(adapter, loader, batch, timed)
    else:
        print(f"{adapter.slug} × {slug}: kept — nothing left to measure", flush=True)
        fresh = []

    evidence = sorted(kept + fresh, key=lambda row: (row["key"], row["reader"]))
    counts = runs.counts(len({row["key"] for row in evidence}), loader.total, loader.excluded)
    stored = runs.read(results, NAME, adapter.slug, slug) if kept else None
    summary = {
        **_summarise(evidence, declared["structures"]),
        **runs.kept_timing(stored, timed),
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
        "padding": loader.padding,
        "counts": counts,
        "summary": summary,
        "measured": len({row["key"] for row in fresh}),
    }


def _outline(
    adapter, loader: DiscCupLoader, batch: int, timed: runs.Timing
) -> list[dict[str, object]]:
    """Every photograph still to be scored, measured against each reader who drew on it."""
    rows = []
    for sample in DataLoader(loader, batch_size=batch, collate_fn=collate, shuffle=False):
        started = time.perf_counter()
        try:
            answers = adapter.outline(sample["image"], sample["native_side"])
        except Exception as failure:  # a crash is the model's answer to nothing
            answers = [None] * len(sample["key"])
            note = repr(failure)
        else:
            note = ""
            timed.record(time.perf_counter() - started, len(sample["key"]))
        for index, key in enumerate(sample["key"]):
            rows.extend(_rows(key, sample, index, answers[index], note))
    return rows


def _rows(key, sample, index, answer, note) -> list[dict[str, object]]:
    """One row per reader who outlined this photograph."""
    side = sample["native_side"][index]
    drawn = sample["outlines"][index]
    readers = sorted({reader for _, reader in drawn})
    common = {
        "key": key,
        "subset": sample["subset"][index],
        "split": sample["split"][index],
        "native_side": side,
    }
    if answer is None or answer.outcome != "graded":
        return [
            {**common, "reader": reader, "outcome": "failed", "resampling": "", "note": note}
            for reader in readers
        ]
    rows = []
    for reader in readers:
        truth = {
            structure: metrics.mask_of(nodes, (side, side))
            for (structure, drawn_by), nodes in drawn.items()
            if drawn_by == reader
        }
        measured = metrics.measure(answer.masks, truth)
        rows.append(
            {
                **common,
                "reader": reader,
                "outcome": "graded",
                "resampling": answer.resampling,
                **{
                    name: "" if value is None else f"{value:.6f}"
                    for name, value in measured.items()
                },
                "note": note,
            }
        )
    return rows


def _summarise(rows: list[dict[str, object]], structures: list[str]) -> dict[str, object]:
    """What a model did on one dataset, over every reader who drew on it."""
    graded = [row for row in rows if row.get("outcome") == "graded"]
    summary: dict[str, object] = {
        "outlines": len(graded),
        "photographs": len({row["key"] for row in rows}),
        "failed": len([row for row in rows if row.get("outcome") == "failed"]),
        "structures": list(structures),
    }
    for name in _MEASURED:
        values = [float(row[name]) for row in graded if row.get(name) not in (None, "")]
        if not values:
            continue
        summary[name] = {
            "n": len(values),
            "mean": float(np.mean(values)),
            "median": float(np.median(values)),
            "spread": float(np.std(values)),
        }
    return summary


#: The measurements a summary carries, in the order a table lists them.
_MEASURED = (
    "disc_dice",
    "cup_dice",
    "disc_centre_offset",
    "cup_centre_offset",
    "disc_height_error",
    "cup_height_error",
    "disc_radius_error",
    "cup_radius_error",
    "cup_vertical_ratio_error",
    "cup_area_ratio_error",
    "cup_outside_its_disc",
)


def _store(slug: str, root: Path | None) -> dict[str, object]:
    build = (root or paths.root()) / slug / "build.json"
    record = json.loads(build.read_text()) if build.exists() else {}
    return {"slug": slug, "builder_version": record.get("builder_version")}


def _record(scored, absent, started, into: Path) -> None:
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
    """Run the benchmark as `python -m benchmarks --benchmark disc` asked for it."""
    from . import __main__ as entry

    root = Path(asked.data_root) if asked.data_root else None
    wanted_models = entry.named(asked.model) or list(MODELS)
    wanted_datasets = entry.named(asked.dataset) or list(DATASETS)

    models, no_adapter = adapters(wanted_models, asked.device)
    for slug, why in no_adapter.items():
        print(f"warning: {slug} is not measured — {why}", file=sys.stderr)

    declared, missing_adapters = adapters(list(MODELS), asked.device)
    missing_adapters = {slug: WHY_NOT.get(slug, why) for slug, why in missing_adapters.items()}
    missing_stores = missing_datasets(list(DATASETS), root)

    if asked.report:
        report.write_docs(
            NAME,
            configuration(declared, list(DATASETS), root),
            missing_adapters,
            missing_stores,
            COLUMNS,
        )

    run(
        models,
        wanted_datasets,
        root=root,
        batch=asked.batch or BATCH,
        force=asked.force,
        max_samples=asked.max_samples,
        random_samples=asked.random_samples,
        seed=asked.seed,
    )
    if asked.report:
        report.write_index()


#: Every column of this benchmark's evidence, and what it means. The page describing the run is
#: generated from this, so a column nobody explained is a column nobody can add.
COLUMNS = {
    "key": "the photograph, as the store names it",
    "subset": "the dataset's own subcollection: a camera, a site, a challenge release",
    "split": "the split the dataset published, or `unspecified`",
    "reader": "**which expert drew the outline this row is scored against**; a photograph with "
    "five readers makes five rows",
    "native_side": "the side of the native square, in pixels — every measurement below is in it",
    "outcome": "`graded`, or `failed` with the reason in `note`",
    "resampling": "how the model's output reached the native frame: probabilities interpolated and "
    "then thresholded, or a binary mask resampled nearest",
    "disc_dice": "overlap with this reader's disc, 0 to 1",
    "cup_dice": "overlap with this reader's cup; absent for a model that finds no cup",
    "disc_centre_offset": "distance between the two disc centres, in native pixels",
    "cup_centre_offset": "as above, for the cup",
    "disc_width_error": "signed: the model's disc width less the reader's, in pixels",
    "disc_height_error": "signed, likewise",
    "cup_width_error": "signed, for the cup",
    "cup_height_error": "signed, for the cup",
    "disc_radius_error": "signed: the radius of a circle of the same area, less the reader's",
    "cup_radius_error": "as above, for the cup",
    "said_vertical_ratio": "the model's cup height over its disc height",
    "truth_vertical_ratio": "this reader's own vertical cup-to-disc ratio",
    "cup_vertical_ratio_error": "**signed**: the model's vertical ratio less the reader's — the "
    "number a referral rests on",
    "said_area_ratio": "the model's cup area over its disc area",
    "truth_area_ratio": "this reader's own area ratio",
    "cup_area_ratio_error": "signed, likewise",
    "cup_outside_its_disc": "the share of the model's cup that falls outside its own disc, "
    "measured rather than repaired",
    "note": "what the model failed with",
}


def docs_sections(
    configured: dict[str, object],
    missing_models: dict[str, str],
    missing_datasets: dict[str, str],
) -> Iterable[str]:
    """Sections 1 to 4 of the page saying how this benchmark is run."""
    models = sorted(configured["models"], key=lambda entry: entry["slug"])
    datasets = sorted(configured["datasets"], key=lambda entry: entry["slug"])
    yield "## 1. What this benchmark asks"
    yield ""
    yield (
        "How close a model's optic disc and optic cup are to **the outline an ophthalmologist "
        "drew on that photograph**, and how far the difference travels into the numbers a clinic "
        "would read off it. Overlap is measured as the Dice score — twice the area the two "
        "outlines share, divided by the sum of their areas, so 1 is perfect agreement and 0 no "
        "overlap at all. Beside it are the measurements a report actually quotes: where the centre "
        "of the disc sits, how wide and how tall each structure is, the radius of a circle of the "
        "same area, and the **cup-to-disc ratio**, which is the number a glaucoma referral rests "
        "on. Comparing the models with each other is a second, weaker question, and it is there to "
        "raise suspicions about the outlines rather than to rank the software."
    )
    yield ""
    yield (
        "**Every measurement is made in the native frame** — the full-resolution square the store "
        "built, which is where the expert drew. A model working at 512 pixels has its answer "
        "carried back there first, and how it was carried is recorded per photograph: a "
        "probability map is resampled and thresholded **after** it arrives, because thresholding "
        "first and resampling the mask throws away the boundary detail the model produced, and the "
        "boundary is what every one of these numbers turns on."
    )
    yield ""
    yield (
        "**Signed errors are kept signed.** A model whose discs are three pixels too wide and one "
        "whose discs are three pixels too narrow do not average to agreement, and a cup-to-disc "
        "ratio that reads high sends the wrong patients to a clinic."
    )
    yield ""
    yield "## 2. The models"
    yield ""
    yield "| Model | Pinned at | Grid it reads | Grid the network sees | Finds | Emits |"
    yield "| --- | --- | --- | --- | --- | --- |"
    for entry in models:
        slug, declared = entry["slug"], entry["declared"]
        emits = (
            "probabilities, thresholded in the native frame"
            if declared.get("emits_probabilities")
            else "a binary mask"
        )
        yield (
            f"| [{slug}](../models/{slug}.md) | {report.pin(declared.get('upstream', {}))} | "
            f"{declared['grid']}² | {declared['network_grid']}² | "
            f"{', '.join(declared.get('structures', []))} | {emits} |"
        )
    for model, why in sorted(missing_models.items()):
        yield f"| [{model}](../models/{model}.md) | **not measured** — {why} | — | — | — | — |"
    yield ""
    yield (
        "A model named here that has no adapter is **declared, not forgotten**: the benchmark asks "
        "for it, and the run says so every time until somebody writes it."
    )
    yield ""
    yield (
        "A model that finds only the disc is scored on the disc alone. Its rows carry no cup "
        "columns rather than empty ones, and it is never counted as having got the cup wrong."
    )
    yield ""
    yield "## 3. The datasets"
    yield ""
    yield "| Dataset | Photographs | Readers | Black canvas | Excluded, and why |"
    yield "| --- | --- | --- | --- | --- |"
    for entry in datasets:
        slug = entry["slug"]
        readers = entry.get("readers") or []
        yield (
            f"| [{slug}](../datasets/{slug}.md) | {entry['total']} | "
            f"{len(readers)}: {', '.join(readers) if readers else '—'} | "
            f"{report.number(entry.get('padding'))} | {report.excluded(entry['excluded'])} |"
        )
    for dataset, why in sorted(missing_datasets.items()):
        yield f"| [{dataset}](../datasets/{dataset}.md) | **not measured** — {why} | — | — | — |"
    yield ""
    yield (
        "**Readers are never merged.** A photograph five ophthalmologists outlined makes five rows "
        "of evidence, one per reader, and a model is scored against each of them separately. "
        "Averaging the outlines first would invent a consensus nobody drew and would hide the "
        "range the readers themselves disagree over — which, on these structures, is often wider "
        "than the gap between two models."
    )
    yield ""
    yield (
        "**Black canvas** is the share of the square the store built that is not photograph. A "
        "fundus cut off at top and bottom leaves bands there, and a model sees the square it is "
        "handed."
    )
    yield ""
    yield "### 3.1 What is worth fetching next, and what each would settle"
    yield ""
    yield "| Dataset | What it would settle | Cost |"
    yield "| --- | --- | --- |"
    for slug, why, cost in WORTH_FETCHING:
        yield f"| [{slug}](../datasets/{slug}.md) | {why} | {cost} |"
    yield ""
    yield (
        "[RIGA](../datasets/riga.md) is the painful exclusion: 750 photographs each outlined by "
        "**six** ophthalmologists, and every one of its images is a crop rather than a photograph, "
        "so the crop rule of section 4 excludes it whole."
    )
    yield ""
    yield "## 4. What is excluded, and by which rule"
    yield ""
    yield (
        "- **Below the size floor** — a photograph whose field of view is under 512 pixels, "
        "measured on the field's own size rather than the frame's.\n"
        "- **A finding recorded against the image** — anything in `src/datasets/exclusions/`, so "
        "that a finding survives deleting and rebuilding a store. An outline a finding condemns is "
        "dropped on its own, leaving the other readers' outlines of that photograph in place.\n"
        "- **No outline to score against** — a photograph the dataset published but nobody "
        "outlined. It is not a failure of the model and is never counted as one.\n"
        "- **Excluded whole** — a dataset whose images are crops rather than photographs. No size "
        "floor catches that, because a crop can be large."
    )
    yield ""
    yield (
        "These are **ours**: the benchmark would not ask. A model's own refusal to answer is "
        "`declined`, which is a different statement, and the two are never added together."
    )


def index_section(records: list[dict[str, object]]) -> Iterable[str]:
    """This benchmark's rows of `docs/BENCHMARKS.md`, and what to make of them."""
    yield (
        "**A Dice score is read with the errors beside it.** Two models a hundredth apart on "
        "overlap can differ by a tenth on the cup-to-disc ratio, which is the number a clinic "
        "acts on; the ratio error is signed, so a positive value means the model reads the ratio "
        "**high**. Every figure is the mean over each reader's own outline, measured in the native "
        "frame, and a photograph count of the form *n of m* means a run that has not finished. "
        "**Seconds each** is how long the model itself took per photograph, on the device named in "
        "its result, once it was loaded — a measurement of this machine as much as of the model."
    )
    yield ""
    yield (
        "| Model | Dataset | Photographs | Outlines | Disc Dice | Cup Dice | "
        "Disc centre, px | Cup ratio error | Seconds each | Marked |"
    )
    yield "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"
    for record in records:
        summary = record["summary"]
        done = summary.get("processed", "—")
        if not summary.get("complete", True):
            done = f"{done} of {summary.get('total', '—')}"
        yield (
            f"| [{record['model']}](models/{record['model']}.md) | {record['dataset']} | "
            f"{done} | {summary.get('outlines', '—')} | "
            f"{_mean(summary, 'disc_dice')} | {_mean(summary, 'cup_dice')} | "
            f"{_mean(summary, 'disc_centre_offset')} | "
            f"{_mean(summary, 'cup_vertical_ratio_error')} | "
            f"{report.seconds(summary)} | "
            f"{contamination.mark(record['model'], record['dataset'])} |"
        )
    yield ""
    yield (
        "Read a dash as *not measured* rather than as zero: a model that finds no cup has no cup "
        "row to average."
    )


def _mean(summary: dict[str, object], measurement: str) -> str:
    found = summary.get(measurement)
    return report.number(found["mean"]) if isinstance(found, dict) else "—"
