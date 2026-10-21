# ABOUTME: The artery/vein benchmark: how close a model's arteries, veins and the vessels they make
# ABOUTME: together are to what an expert drew, by overlap and by connectedness.

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

from datasets.utils import paths
from models.utils import catalogue
from models.utils.outlines import Outlines
from torch.utils.data import DataLoader

from . import contamination, photographs, report, runs
from .loaders.av import ArteryVeinLoader
from .loaders.base import CROPS, FLOOR, available, collate
from .metrics import av as metrics

#: What this benchmark is called in a heading, where its slug does not read as English.
TITLE = "Artery and vein"

#: What this benchmark is called: in `results/`, in `docs/benchmarks/` and in a run record.
NAME = "av"

#: The benchmark's own version. Changing what is measured, or how, changes this. Version 2 adds the
#: Betti matching error to every structure, which is measured from the masks a run already kept:
#: `--rescore` is what fills it in, and no model is asked to segment anything again.
VERSION = 2

#: What this benchmark asks, in the two sentences the index has room for.
GOAL = (
    "**Which vessels are arteries and which are veins?** Each model's segmentation is compared with "
    "what an ophthalmologist drew on the same photograph — the arteries, the veins, and the vessels "
    "they make together — by overlap and by how much of the vessel network survives. Everything "
    "computed *from* a vessel map, a calibre or an arteriovenous ratio, belongs to the biomarker "
    "benchmark instead."
)

#: The datasets this benchmark wants. A name here is intent, not inventory.
#:
#: `fives` annotates vessels and neither class, so no model is scored on arteries or veins there
#: and every model is scored on the vessel column — which is the only dataset here outside the six
#: the vessel reference trained on.
DATASETS = ("hrf", "fundus-avseg", "avrdb", "reyia", "fives", "rav", "av-wide", "les-av", "rite")

#: The models, by the slug of their catalogue page. `segan-vessel` answers about vessels alone and
#: takes part as a reference for that column rather than as an entry in the class ones.
MODELS = (
    "vascx-artery-vein",
    "ocularnet",
    "lunet",
    "automorph-artery-vein",
    "bf-net",
    "segan-vessel",
    "ocularnet-nano",
)

#: Why a declared model has no adapter, where the reason is worth more than "nobody wrote one".
WHY_NOT = {
    "ocularnet-nano": (
        "its five checkpoints answer HTTP 401 and the anonymous review account that served them now "
        "holds one repository — the weights cannot be obtained at all"
    ),
}

#: Datasets worth fetching next, and what each would settle.
WORTH_FETCHING = (
    (
        "les-av",
        "22 photographs, direct, and it completes the contamination picture for BF-Net",
        "direct",
    ),
    (
        "rite",
        (
            "the 40 DRIVE photographs every artery/vein paper reports, which is what makes a number "
            "here comparable with the literature"
        ),
        "registration",
    ),
)

#: How many photographs go to the model at once. One: these models work at 1024 and 1472, and their
#: output is resampled to the crop, which is where the memory goes.
BATCH = 1

#: What a model declares that could change its numbers.
FINGERPRINTED = (
    "slug",
    "purpose",
    "grid",
    "network_grid",
    "structures",
    "channels",
    "emits_probabilities",
    "resampling",
    "threshold",
    "ensemble",
    # The code the weights run in: its pinned commit and the content of every patch applied to it.
    # The same weights run by different code are a different measurement.
    "upstream",
)


def adapters(slugs: list[str], device: str | None = None) -> tuple[list, dict[str, str]]:
    """The model adapters that exist, and what was declared without one."""
    found, missing = [], {}
    for slug in slugs:
        try:
            found.append(catalogue.load(slug, **({"device": device} if device else {})))
        except LookupError:
            missing[slug] = WHY_NOT.get(slug, "no adapter written")
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
        loader = ArteryVeinLoader(slug, size=models[0].grid if models else 1024, root=root)
        readers = sorted(
            {reader for row in loader.rows for reader in row["readers"].split(";") if reader}
        )
        described.append(
            {
                "slug": slug,
                "total": loader.total,
                "excluded": dict(loader.excluded),
                "readers": readers,
                "vessels": DERIVED.get(slug, "unknown"),
            }
        )
    return {
        "models": [{"slug": model.slug, "declared": model.declare()} for model in models],
        "datasets": described,
    }


#: Whether a dataset's vessel annotation is its own tracing or its artery/vein annotation seen
#: again. Established per dataset, by measuring, and recorded on each dataset's page.
DERIVED = {
    "hrf": "**the same tracing**: 0.004% of pixels differ from the artery/vein union",
    "fundus-avseg": "derived from the artery/vein labels by the authors",
    "avrdb": "**drawn, but not independent**: it agrees with the union to within 0.4–0.6%",
    "reyia": "derived here as the union; the archive publishes no separate tracing",
    "fives": "**its own tracing, and the only annotation it has**: no artery/vein labels at all",
    "rav": "derived here as the union of the artery, vein and unknown layers; none published apart",
    "av-wide": "derived here as the union; the archive publishes no separate tracing",
}

#: Datasets reported beside the pooled table rather than in it, and why. Both are held out of
#: OCULARNet's training, which is what makes them worth reporting at all — and neither belongs in
#: a pool every other figure is read against.
APART = {
    "rav": (
        "in-sample for VascX, whose group annotated it, and held out of OCULARNet; its tracings "
        "were seeded by a model before the annotators corrected them"
    ),
    "av-wide": (
        "ultra-wide-field at 200°, a different instrument from every 30–45° camera in the pool, "
        "and held out of OCULARNet"
    ),
}

#: Datasets whose photographs appear in another dataset here, so that pooling a figure over both
#: counts the same eyes twice. REYIA is a compilation, and its own page names what it reuses.
OVERLAPS = {
    "fives": ("reyia", 75),
}


def config(root: Path | None = None) -> dict[str, object]:
    """What this benchmark reports about itself, as data rather than prose.

    Known from the declarations and the stores' manifests: no result is read and nothing is
    measured. The `document-benchmark` skill is the authority on the shape.
    """
    found, missing = adapters(list(MODELS))
    stores = missing_datasets(list(DATASETS), root)
    return photographs.describe(
        sys.modules[__name__],
        subjects=photographs.subjects(
            list(MODELS),
            found,
            missing,
            [
                "Pinned at",
                "Grid it reads",
                "Grid it runs at",
                "Channels it emits",
                "Read as",
                "Ensemble",
            ],
            lambda declared: {
                "Pinned at": report.pin(declared.get("upstream", {})),
                "Grid it reads": f"{declared['grid']}²",
                "Grid it runs at": f"{declared['network_grid']}²",
                "Channels it emits": ", ".join(declared.get("channels", [])) or "—",
                "Read as": ", ".join(declared.get("structures", [])),
                "Ensemble": declared.get("ensemble", "—"),
            },
            _reference,
        ),
        material=photographs.material(
            list(DATASETS),
            configuration(found, list(DATASETS), root)["datasets"],
            stores,
            ["Photographs", "Readers", "Vessel annotation", "Excluded, and why"],
            lambda entry: {
                "Photographs": entry["total"],
                "Readers": len(entry["readers"]) or 1,
                "Vessel annotation": entry["vessels"],
                "Excluded, and why": report.excluded(entry["excluded"]),
            },
            WORTH_FETCHING,
        ),
        exclusions={
            "below the size floor": photographs.FLOOR_RULE,
            "no artery/vein annotation": "a photograph the dataset published without one. Not a "
            "failure of the model, and never counted as one",
            "an annotation a finding condemns": photographs.FINDING_RULE
            + ". The map is excluded and the photograph stays",
            "excluded whole": photographs.CROP_RULE,
        },
        fingerprint=photographs.fingerprint(sys.modules[__name__], FINGERPRINTED, True),
        running=photographs.running(sys.modules[__name__], rescores=True),
    )


def _reference(declared: dict[str, object]) -> str:
    """What a vessels-only model is here for, and the threshold it is run at — or nothing."""
    if list(declared.get("structures", [])) != ["vessels"]:
        return ""
    said = (
        "does not separate arteries from veins, so its own vessel map is its answer and its "
        "artery and vein cells are left empty; a reference for the vessel column, not a "
        "competitor in it"
    )
    if "upstream_threshold" in declared:
        said += (
            f". Run at a threshold of **{declared['threshold']}**, where its own pipeline uses "
            f"{declared['upstream_threshold']}, to keep the thin vessels the higher one drops"
        )
    return said


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

    :param rescore: measure the masks a previous run kept, instead of drawing them again. What a
        model drew does not change when what is measured about it does, so a new metric costs a
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
    loader = ArteryVeinLoader(
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
    #: What drew the masks, and therefore what the kept files are of. It does not include this
    #: benchmark's version: changing what is measured about a mask does not change the mask, which
    #: is what lets a new measurement be taken from the segmentations already drawn — and what lets
    #: the biomarker benchmark say whether the masks it is reading are still the model's.
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
        print(
            f"{adapter.slug} × {slug}: measuring {len(loader)} kept segmentations afresh",
            flush=True,
        )
        fresh = _remeasure(
            loader,
            masks,
            declared["structures"],
            record_so_far,
            drawn_by=declared.get("resampling", ""),
        )
    elif len(loader):
        print(f"{adapter.slug} × {slug}: {len(loader)} photographs", flush=True)
        fresh = _segment(adapter, loader, batch, timed, masks, record_so_far)
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
        "drawing": drawing,
        "masks": str(masks),
        "counts": counts,
        "summary": summary,
        "measured": len({row["key"] for row in fresh}),
    }


def _segment(
    adapter,
    loader: ArteryVeinLoader,
    batch: int,
    timed: runs.Timing,
    masks: Path,
    record_so_far: Callable[[list[dict[str, object]]], object],
) -> list[dict[str, object]]:
    """Every photograph still to be scored, measured against the annotation drawn on it.

    What has been measured is written down every :data:`runs.CHECKPOINT` photographs, so that a run
    the machine stops part-way through is one the next run finishes rather than starts again.
    """
    rows = []
    since = 0
    for sample in DataLoader(loader, batch_size=batch, collate_fn=collate, shuffle=False):
        started = time.perf_counter()
        try:
            answers = adapter.outline(sample["image"], sample["crop_side"])
        except Exception as failure:  # a crash is the model's answer to nothing
            answers = [None] * len(sample["key"])
            note = repr(failure)
        else:
            note = ""
            timed.record(time.perf_counter() - started, len(sample["key"]))
        for index, key in enumerate(sample["key"]):
            _keep(masks, key, answers[index])
            rows.append(_row(key, sample, index, answers[index], note))
        since += len(sample["key"])
        if since >= runs.CHECKPOINT:
            record_so_far(rows)
            since = 0
    return rows


def _remeasure(
    loader: ArteryVeinLoader,
    masks: Path,
    structures: list[str],
    record_so_far: Callable[[list[dict[str, object]]], object],
    drawn_by: str = "",
) -> list[dict[str, object]]:
    """Measure the segmentations a previous run drew, without asking any model to draw them again."""
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
            "crop_side": [side],
            "reader": [loader.readers_of(key)[0]],
            "masks": [loader.masks_of(key)],
        }
        rows.append(_row(key, sample, 0, drawn, note=""))
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
    """One photograph's kept segmentation, read back in the frame it was drawn in."""
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


#: What a rescored row adds to the resampling path its model declares: the segmentation is the one
#: that path produced, and only the measuring of it happened later.
KEPT = ", and these numbers were measured from the masks that run kept"


def _masks_for(directory: Path, identity: str, keep: bool) -> Path:
    """Where this pair's predicted masks go, emptied where they describe something else.

    The masks are kept because the biomarker benchmark's input is exactly these rather than the
    scores computed from them. They are named by the fingerprint of what produced them, so a mask a
    model no longer agrees with is never read as one it does.
    """
    marker = directory / "fingerprint.txt"
    stale = not keep or not marker.exists() or marker.read_text().strip() != identity
    if directory.exists() and stale:
        shutil.rmtree(directory)
    directory.mkdir(parents=True, exist_ok=True)
    marker.write_text(identity + "\n")
    return directory


def _keep(directory: Path, key: str, answer) -> None:
    """One photograph's masks, in the crop frame: the two classes and the vessels they make.

    The union is written as well as derived, because it is what a vessel-width or a fractal
    measurement reads, and recomputing it in every consumer is how two of them come to disagree.
    """
    if answer is None or answer.outcome != "graded":
        return
    for structure, mask in answer.masks.items():
        Image.fromarray(np.asarray(mask, dtype=bool)).save(directory / f"{key}-{structure}.png")
    Image.fromarray(metrics.vessels_of(answer.masks)).save(directory / f"{key}-vessels.png")


def _row(key, sample, index, answer, note) -> dict[str, object]:
    """One row: this photograph, scored against the annotation drawn on it."""
    side = sample["crop_side"][index]
    truth = sample["masks"][index]
    common = {
        "key": key,
        "subset": sample["subset"][index],
        "split": sample["split"][index],
        "reader": sample["reader"][index],
        "crop_side": side,
    }
    if answer is None or answer.outcome != "graded":
        return {**common, "outcome": "failed", "resampling": "", "note": note}
    measured = metrics.measure(answer.masks, truth)
    return {
        **common,
        "outcome": "graded",
        "resampling": answer.resampling,
        # Every score column, on every row, whatever this pair could measure: a model that answers
        # about vessels alone, or a dataset that annotates them alone, leaves the class columns
        # empty rather than absent. A file whose columns depend on which model wrote it cannot be
        # read beside another, and an empty cell says "not asked" where a zero would say "wrong".
        **dict.fromkeys(_MEASURED, ""),
        **{name: "" if value is None else f"{value:.6f}" for name, value in measured.items()},
        **{
            "said_artery_px": int(np.asarray(answer.masks.get("artery", [])).sum()),
            "said_vein_px": int(np.asarray(answer.masks.get("vein", [])).sum()),
            "truth_artery_px": int(np.asarray(truth.get("artery", [])).sum()),
            "truth_vein_px": int(np.asarray(truth.get("vein", [])).sum()),
        },
        "note": note,
    }


def _summarise(rows: list[dict[str, object]], structures: list[str]) -> dict[str, object]:
    """What a model did on one dataset, over every photograph it was asked about."""
    graded = [row for row in rows if row.get("outcome") == "graded"]
    summary: dict[str, object] = {
        "segmentations": len(graded),
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
    "artery_dice",
    "vein_dice",
    "vessels_dice",
    "artery_cldice",
    "vein_cldice",
    "vessels_cldice",
    "artery_betti",
    "vein_betti",
    "vessels_betti",
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
    """Run the benchmark as `python -m benchmarks --benchmark av` asked for it."""
    from . import __main__ as entry

    root = Path(asked.data_root) if asked.data_root else None
    wanted_models = entry.named(asked.model) or list(MODELS)
    wanted_datasets = entry.named(asked.dataset) or list(DATASETS)

    models, no_adapter = adapters(wanted_models, asked.device)
    for slug, why in no_adapter.items():
        print(f"warning: {slug} is not measured — {why}", file=sys.stderr)

    run(
        models,
        wanted_datasets,
        root=root,
        batch=asked.batch or BATCH,
        force=asked.force,
        max_samples=asked.max_samples,
        random_samples=asked.random_samples,
        seed=asked.seed,
        rescore=asked.rescore,
    )

    if asked.report:
        report.write_index()


#: Every column of this benchmark's evidence, and what it means.
COLUMNS = {
    "key": "the photograph, as the store names it",
    "subset": "the dataset's own subcollection — for REYIA, the collection the photograph came from",
    "split": "the split the dataset published, or `unspecified`",
    "reader": "which annotator the row is scored against, where a dataset keeps them apart",
    "crop_side": "the side of the crop square, in pixels — every score below is measured in it",
    "outcome": "`graded`, or `failed` with the reason in `note`",
    "resampling": "how the model's output reached the crop frame",
    "artery_dice": "overlap with the reader's arteries, 0 to 1 — **empty** where the model or the "
    "dataset says nothing about the classes, which is not the same as a zero",
    "vein_dice": "overlap with the reader's veins, on the same terms",
    "vessels_dice": "overlap with the reader's vessels — **derived as artery ∪ vein on each side "
    "that has the two classes**, and the map itself on a side that has only vessels",
    "artery_cldice": "how much of each artery network's centreline lies inside the other's mask",
    "vein_cldice": "as above, for the veins",
    "vessels_cldice": "as above, for the vessels",
    "artery_betti": "**Betti matching error** for the arteries: how many topological features — "
    "connected components and loops — of either map have no counterpart in the other. 0 is "
    "perfect; unlike Dice and clDice it counts upwards and has no ceiling",
    "vein_betti": "as above, for the veins",
    "vessels_betti": "as above, for the vessels",
    "said_artery_px": "how many pixels the model called artery, so a score can be read beside the "
    "size of the thing scored",
    "said_vein_px": "how many it called vein",
    "truth_artery_px": "how many **this reader** drew as artery",
    "truth_vein_px": "how many as vein",
    "note": "what the model failed with",
}


def index_section(records: list[dict[str, object]], results: Path) -> Iterable[str]:
    """This benchmark's entry in the index: one row per model, pooled, and where to start.

    The datasets in `APART` are left out of the pool and given a table of their own after it.
    """
    apart = [record for record in records if record["dataset"] in APART]
    records = [record for record in records if record["dataset"] not in APART]
    pooled = _pooled(records)
    yield (
        f"Pooled over **{report.datasets_of(records)}**. **Dice** is overlap with what the "
        f"annotator drew, 0 to 1. **clDice** asks the connectedness question instead — how much of "
        f"each centreline falls inside the other's mask — and the two are read together: a model "
        f"can cover the vessels and lose the network, or trace the network at the wrong width. "
        f"**Vessels** is the union of each model's own arteries and veins, derived the same way "
        f"for every model and for every annotator. **Betti** counts the topological features — "
        f"components and loops — of either map that have no counterpart in the other, so it counts "
        f"downwards where the other two count upwards, and it has no ceiling. It is pooled here as "
        f"a **mean over photographs**, which is the only form that pools exactly; the results page "
        f"quotes medians, which are lower, because the tail is long."
    )
    # Read from the stored summary rather than a declaration: the index is built from what is in
    # `results/`, which is what makes it agree with the evidence it links to.
    references = sorted(
        {
            str(record["model"])
            for record in records
            if list(record.get("summary", {}).get("structures", [])) == ["vessels"]
        }
    )
    if references:
        yield ""
        yield (
            "**Except for "
            + ", ".join(f"[{model}](models/{model}.md)" for model in references)
            + "**, which does not separate arteries from veins: its vessel map is its own "
            "prediction rather than a union, and its class cells are empty because it was never "
            "asked. It is a reference for that column, not a competitor in it."
        )
    yield ""
    yield (
        "| Model | Photographs | Artery Dice | Vein Dice | Vessels Dice | Vessels clDice | "
        "Vessels Betti | Seconds each | Marked |"
    )
    yield "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"
    for model, found in sorted(pooled.items(), key=lambda pair: -(pair[1]["vessels_dice"] or -1)):
        yield (
            f"| [{model}](models/{model}.md) | {found['photographs']:,} | "
            f"{report.number(found['artery_dice'])} | {report.number(found['vein_dice'])} | "
            f"{report.number(found['vessels_dice'])} | "
            f"{report.number(found['vessels_cldice'])} | "
            f"{report.number(found['vessels_betti'], places=0)} | "
            f"{report.number(found['seconds'])} | {report.mark_of(model, records)} |"
        )
    yield ""
    left = report.unfinished(records)
    if left:
        yield left
        yield ""
    yield from _where_to_start(pooled)
    yield from _held_apart(apart)


def _held_apart(records: list[dict[str, object]]) -> Iterable[str]:
    """The datasets kept out of the pool, one row per model and dataset, each with its reason."""
    if not records:
        return
    yield ""
    yield (
        "**Held apart from the pool**, and reported here dataset by dataset rather than averaged "
        "into it:"
    )
    yield ""
    for dataset in sorted({str(record["dataset"]) for record in records}):
        yield f"- [{dataset}]({photographs.page(dataset)}): {APART[dataset]}."
    yield ""
    yield (
        "| Model | Dataset | Photographs | Artery Dice | Vein Dice | Vessels Dice | "
        "Vessels clDice | Vessels Betti | Marked |"
    )
    yield "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"
    for record in sorted(records, key=lambda found: (found["dataset"], found["model"])):
        model, dataset = str(record["model"]), str(record["dataset"])
        found = _pooled([record])[model]
        yield (
            f"| [{model}](models/{model}.md) | {dataset} | {found['photographs']:,} | "
            f"{report.number(found['artery_dice'])} | {report.number(found['vein_dice'])} | "
            f"{report.number(found['vessels_dice'])} | "
            f"{report.number(found['vessels_cldice'])} | "
            f"{report.number(found['vessels_betti'], places=0)} | "
            f"{contamination.mark(model, dataset)} |"
        )


def _pooled(records: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    """Every model's measurements over every dataset at once.

    A mean over segmentations is exactly the mean of the per-dataset means weighted by how many
    each holds, so this needs the summaries rather than the evidence — and it agrees with the
    results page by arithmetic rather than by coincidence.
    """
    found: dict[str, dict[str, object]] = {}
    for model in sorted({str(record["model"]) for record in records}):
        mine = [record["summary"] for record in records if record["model"] == model]
        entry: dict[str, object] = {
            "photographs": sum(summary.get("processed", 0) for summary in mine),
            "segmentations": sum(summary.get("segmentations", 0) for summary in mine),
        }
        for measurement in _MEASURED:
            weighted = [
                (summary[measurement]["mean"], summary[measurement]["n"])
                for summary in mine
                if isinstance(summary.get(measurement), dict)
            ]
            counted = sum(count for _, count in weighted)
            entry[measurement] = (
                sum(mean * count for mean, count in weighted) / counted if counted else None
            )
        taken = [
            float(summary["seconds_per_photograph"])
            for summary in mine
            if summary.get("seconds_per_photograph") is not None
        ]
        entry["seconds"] = sum(taken) / len(taken) if taken else None
        found[model] = entry
    return found


def _where_to_start(pooled: dict[str, dict[str, object]]) -> Iterable[str]:
    """Which model to reach for, and at which question.

    Two questions, and they need not have the same answer: finding the vessels and naming them are
    different skills, and a model that traces the network well can still get the classes wrong.
    Computed from the stored results; the argument is on the results page.
    """
    classed = [
        name
        for name in pooled
        if pooled[name]["artery_dice"] is not None and pooled[name]["vein_dice"] is not None
    ]
    if not classed:
        return
    named = sorted(classed, key=lambda name: -_both(pooled[name]))

    yield "**Where to start.**"
    yield ""
    best = named[0]
    line = (
        f"- **For arteries against veins**: **{best}** (artery {pooled[best]['artery_dice']:.3f}, "
        f"vein {pooled[best]['vein_dice']:.3f})."
    )
    if len(named) > 1:
        second = named[1]
        margin = _both(pooled[best]) - _both(pooled[second])
        line += f" **{second}** is {margin:.3f} behind on the two together" + (
            ", which is not a difference this benchmark can separate."
            if margin < 0.015
            else f" (artery {pooled[second]['artery_dice']:.3f}, "
            f"vein {pooled[second]['vein_dice']:.3f})."
        )
    yield line

    network = [name for name in pooled if pooled[name]["vessels_cldice"] is not None]
    if network:
        network.sort(key=lambda name: -pooled[name]["vessels_cldice"])
        yield (
            f"- **For the vessel network itself**, which is what a connectedness measurement "
            f"rests on: **{network[0]}** (clDice {pooled[network[0]]['vessels_cldice']:.3f}"
            + (
                f", against {pooled[network[1]]['vessels_cldice']:.3f} for {network[1]})."
                if len(network) > 1
                else ")."
            )
        )
    topological = [name for name in pooled if pooled[name]["vessels_betti"] is not None]
    if topological:
        topological.sort(key=lambda name: pooled[name]["vessels_betti"])
        first = topological[0]
        yield (
            f"- **For a network that will be measured rather than looked at**, where a broken "
            f"branch is a branch nothing counts: **{first}** ({pooled[first]['vessels_betti']:.0f} "
            f"unmatched features a photograph"
            + (
                f", against {pooled[topological[1]]['vessels_betti']:.0f} for {topological[1]})."
                if len(topological) > 1
                else ")."
            )
        )
    yield ""
    yield (
        f"**A vessel score is not a second opinion on a class score.** In most of these datasets "
        f"the vessel annotation *is* the artery/vein annotation, so the two columns are one "
        f"measurement seen twice — [what came out](benchmarks/{NAME}-results.md) says which, and "
        f"holds the per-dataset detail these pooled figures hide."
    )


def _both(found: dict[str, object]) -> float:
    """How well a model named the two classes, as the mean of the two Dice scores."""
    return (found["artery_dice"] + found["vein_dice"]) / 2
