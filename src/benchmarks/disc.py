# ABOUTME: The disc-and-cup benchmark: how close a model's outline is to the one an ophthalmologist
# ABOUTME: drew, and how far that difference travels into the numbers computed from it.

import json
import shutil
import sys
import time
from collections.abc import Callable, Iterable
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from torch.utils.data import DataLoader

from datasets.utils import paths
from models.utils import catalogue
from models.utils.outlines import Outlines

from . import contamination, report, runs
from .loaders.base import CROPS, FLOOR, available, collate
from .loaders.disc import DiscCupLoader
from .metrics import disc as metrics

#: What this benchmark is called: in `results/`, in `docs/benchmarks/` and in a run record.
NAME = "disc"

#: The benchmark's own version. Changing what is measured, or how, changes this. Version 2 records
#: what each outline itself measures — its width, height, radius and centre — beside the errors, and
#: spells every column `center` rather than `centre`.
VERSION = 2

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
        (
            "three of the models here trained on it, so it is what turns an in-sample "
            "suspicion into a measured contrast"
        ),
        "registration",
    ),
    (
        "drishti-gs",
        (
            "four experts **and soft probability maps** — the only dataset here publishing "
            "annotator uncertainty as a map rather than as separate outlines"
        ),
        "direct",
    ),
    (
        "origa",
        (
            "publishes `ExpCDR`, an expert cup-to-disc ratio **as a number**, which is the "
            "strongest available check that a ratio derived from contours means what this "
            "benchmark thinks"
        ),
        "needs an archive by hand",
    ),
    (
        "rim-one-dl",
        (
            "BEAL's other unlabelled target domain; it completes the contamination picture for "
            "that model once there is an adapter for it"
        ),
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
    rescore: bool = False,
) -> list[dict[str, object]]:
    """Score every model on every dataset, measuring only what is missing.

    :param rescore: measure the outlines a previous run kept, instead of drawing them again. What
        a model drew does not change when what is measured about it does, so a new metric costs a
        pass over the masks rather than a pass over the networks.
    """
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
                _pair(
                    adapter,
                    slug,
                    results,
                    root,
                    batch,
                    force,
                    max_samples,
                    random_samples,
                    seed,
                    record or runs.RUNS,
                    rescore,
                )
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
    keeping: Path,
    rescore: bool,
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
    #: What drew the outlines, and therefore what the kept masks are of. It does not include this
    #: benchmark's version: changing what is measured about a mask does not change the mask, which
    #: is what lets a new measurement be taken from the outlines already drawn.
    drawing = runs.fingerprint(
        {
            "model": {name: declared[name] for name in FINGERPRINTED if name in declared},
            "weights": loaded,
            "store": store,
        }
    )
    identity = runs.fingerprint(
        {"drawing": drawing, "benchmark": {"name": NAME, "version": VERSION, "floor": FLOOR}}
    )

    kept = [] if force or rescore else runs.measured(results, NAME, adapter.slug, slug, identity)
    done = {row["key"] for row in kept}
    loader.restrict({row["key"] for row in loader.rows} - done)
    masks = _masks_for(keeping / NAME / adapter.slug / slug, drawing, keep=bool(kept) or rescore)

    timed = runs.Timing()
    stored = runs.read(results, NAME, adapter.slug, slug) if kept or rescore else None

    def record_so_far(fresh: list[dict[str, object]]) -> dict[str, object]:
        """Write down everything measured to this point, complete or not."""
        evidence = sorted(kept + fresh, key=lambda row: (row["key"], row["reader"]))
        counted = runs.counts(len({row["key"] for row in evidence}), loader.total, loader.excluded)
        described = {
            **_summarise(evidence, declared["structures"]),
            **runs.kept_timing(stored, timed),
            "device": declared.get("device"),
        }
        runs.write(results, NAME, adapter.slug, slug, identity, {**described, **counted}, evidence)
        return {"counts": counted, "summary": described}

    if rescore:
        print(f"{adapter.slug} × {slug}: measuring {len(loader)} kept outlines afresh", flush=True)
        fresh = _remeasure(
            loader,
            masks,
            declared["structures"],
            record_so_far,
            drawn_by=declared.get("resampling", ""),
        )
    elif len(loader):
        print(f"{adapter.slug} × {slug}: {len(loader)} photographs", flush=True)
        fresh = _outline(adapter, loader, batch, timed, masks, record_so_far)
    else:
        print(f"{adapter.slug} × {slug}: kept — nothing left to measure", flush=True)
        fresh = []

    written = record_so_far(fresh)
    counts, summary = written["counts"], written["summary"]
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
    adapter,
    loader: DiscCupLoader,
    batch: int,
    timed: runs.Timing,
    masks: Path,
    record_so_far: Callable[[list[dict[str, object]]], object],
) -> list[dict[str, object]]:
    """Every photograph still to be scored, measured against each reader who drew on it.

    What has been measured is written down every :data:`runs.CHECKPOINT` photographs, so that a run
    the machine stops part-way through is one the next run finishes rather than starts again.
    """
    rows = []
    since = 0
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
            _keep(masks, key, answers[index])
            rows.extend(_rows(key, sample, index, answers[index], note))
        since += len(sample["key"])
        if since >= runs.CHECKPOINT:
            record_so_far(rows)
            since = 0
    return rows


def _remeasure(
    loader: DiscCupLoader,
    masks: Path,
    structures: list[str],
    record_so_far: Callable[[list[dict[str, object]]], object],
    drawn_by: str = "",
) -> list[dict[str, object]]:
    """Measure the outlines a previous run drew, without asking any model to draw them again."""
    rows: list[dict[str, object]] = []
    since, missing = 0, []
    for index in range(len(loader)):
        row = loader.rows[index]
        key, side = row["key"], int(row["crop_side"])
        drawn = _kept(masks, key, structures, side, drawn_by)
        if drawn is None:
            missing.append(key)
            continue
        sample = {
            "key": [key],
            "subset": [row["subset"]],
            "split": [row["split"]],
            "native_side": [side],
            "outlines": [loader.outlines_of(key)],
        }
        rows.extend(_rows(key, sample, 0, drawn, note=""))
        since += 1
        if since >= runs.CHECKPOINT:
            record_so_far(rows)
            since = 0
    if missing:
        raise RuntimeError(
            f"no kept masks for {len(missing)} of {len(loader)} photographs — a rescore measures "
            f"what a run drew, so run it without --rescore first (first missing: {missing[0]})"
        )
    return rows


def _kept(
    masks: Path, key: str, structures: list[str], side: int, drawn_by: str = ""
) -> Outlines | None:
    """One photograph's kept outlines, read back in the frame they were drawn in."""
    found = {}
    for structure in structures:
        path = masks / f"{key}-{structure}.png"
        if not path.exists():
            return None
        with Image.open(path) as mask:
            found[structure] = np.asarray(mask) > 0
        if found[structure].shape != (side, side):
            raise RuntimeError(
                f"{path} is {found[structure].shape} and the photograph's own frame is "
                f"{(side, side)}; the store has been rebuilt since these were drawn"
            )
    return Outlines(masks=found, resampling=f"{drawn_by}{KEPT}" if drawn_by else KEPT)


#: What a rescored row adds to the resampling path its model declares: the outline is the one that
#: path produced, and only the measuring of it happened later.
KEPT = ", and these numbers were measured from the outlines that run kept"


def _masks_for(directory: Path, identity: str, keep: bool) -> Path:
    """Where this pair's predicted masks go, emptied where they describe something else.

    The masks are kept because the biomarker benchmark's input is exactly these outlines rather
    than the scores computed from them. They are named by the fingerprint of what produced them,
    so a mask a model no longer agrees with is never read as one it does.
    """
    marker = directory / "fingerprint.txt"
    stale = not keep or not marker.exists() or marker.read_text().strip() != identity
    if directory.exists() and stale:
        shutil.rmtree(directory)
    directory.mkdir(parents=True, exist_ok=True)
    marker.write_text(identity + "\n")
    return directory


def _keep(directory: Path, key: str, answer) -> None:
    """One photograph's masks, in the native frame, one file per structure."""
    if answer is None or answer.outcome != "graded":
        return
    for structure, mask in answer.masks.items():
        Image.fromarray(np.asarray(mask, dtype=bool)).save(directory / f"{key}-{structure}.png")


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
    "disc_center_offset",
    "cup_center_offset",
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
        rescore=asked.rescore,
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
    "then thresholded, a binary mask resampled nearest, or — where a later run measured new things "
    "about outlines an earlier one drew — the note that these came from the kept masks",
    "disc_dice": "overlap with this reader's disc, 0 to 1",
    "cup_dice": "overlap with this reader's cup; absent for a model that finds no cup",
    "said_disc_width": "**how wide the model's disc is**, in native pixels — a measurement in its "
    "own right rather than a distance from somebody else's",
    "said_disc_height": "how tall the model's disc is",
    "said_disc_radius": "the radius of a circle of the same area as the model's disc",
    "said_disc_center_x": "where the model puts the disc's centre, in native pixels from the left",
    "said_disc_center_y": "and from the top",
    "said_cup_width": "how wide the model's cup is",
    "said_cup_height": "how tall",
    "said_cup_radius": "the radius of a circle of the same area as the model's cup",
    "said_cup_center_x": "where the model puts the cup's centre",
    "said_cup_center_y": "and from the top",
    "disc_center_offset": "distance between the two disc centres, in native pixels",
    "cup_center_offset": "as above, for the cup",
    "disc_center_offset_diameters": "the same distance **in the expert's own disc diameters**, "
    "which is the only camera-independent form: ten pixels means one thing on a 2,576-pixel "
    "photograph and another on a 1,444-pixel one",
    "cup_center_offset_diameters": "the cup's offset, measured in that same disc diameter rather "
    "than in the cup's own — the disc is the ruler",
    "disc_width_error": "signed: the model's disc width less the reader's, in pixels",
    "disc_height_error": "signed, likewise",
    "cup_width_error": "signed, for the cup",
    "cup_height_error": "signed, for the cup",
    "disc_radius_error": "signed: the radius of a circle of the same area, less the reader's",
    "cup_radius_error": "as above, for the cup",
    "truth_disc_width": "how wide **this reader** drew the disc, in native pixels — the size every "
    "error above is an error of",
    "truth_disc_height": "how tall, likewise",
    "truth_disc_radius": "the radius of a circle of the same area as the reader's disc",
    "truth_disc_center_x": "where the reader put the disc's centre",
    "truth_disc_center_y": "and from the top",
    "truth_cup_width": "how wide the reader drew the cup",
    "truth_cup_height": "how tall",
    "truth_cup_radius": "the radius of a circle of the same area as the reader's cup",
    "truth_cup_center_x": "where the reader put the cup's centre",
    "truth_cup_center_y": "and from the top",
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
    yield (
        "**The outlines themselves are kept**, one image per structure per photograph, under "
        "`.atlas_runs/disc/<model>/<dataset>/` beside the fingerprint of the model that drew them. "
        "A score is a summary of a shape, and the shape is what the next benchmark measures "
        "biomarkers from; a mask whose fingerprint no longer matches its model is drawn again "
        "rather than read."
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
    yield (
        "**Every reference here is a contour somebody drew**, and the ratios are computed from it. "
        "[Chákṣu](../datasets/chaksu.md) also publishes each expert's own cup-to-disc ratio **as a "
        "number**, which would be the strongest available check that a ratio derived from a "
        "contour means what this benchmark thinks it means — but its store does not carry those "
        "numbers yet, so nothing here is scored against them. That is a gap in the fetcher rather "
        "than in the dataset."
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
            f"{_mean(summary, 'disc_center_offset')} | "
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
