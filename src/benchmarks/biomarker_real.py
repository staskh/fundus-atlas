# ABOUTME: The real-segmentation biomarker benchmark: every biomarker computed on the expert's artery
# ABOUTME: and vein map and on each model's, with one disc, and how far the model's map moves it.

import csv
import json
import math
import multiprocessing
import os
import sys
import time
from collections.abc import Iterable
from concurrent.futures import ProcessPoolExecutor, as_completed
from concurrent.futures.process import BrokenProcessPool
from datetime import UTC, datetime
from pathlib import Path

from biomarkers.utils import catalogue

from . import biomarker_synthetic, contamination, report, runs
from .loaders.base import CROPS, FLOOR, available
from .loaders.biomarker_real import (
    CONDEMNED,
    DISCS,
    NO_CLASSES,
    NO_DISC,
    BiomarkerLoader,
    disc_fingerprint,
    read_mask,
)
from .metrics import agreement

#: What this benchmark is called in a heading, where its slug does not read as English.
TITLE = "Biomarkers on real segmentations"

#: What it is called in `results/`, in `docs/benchmarks/` and in a run record. The module cannot
#: carry the hyphen, so it is `biomarker_real` and `report._module` translates.
NAME = "biomarker-real"

#: The benchmark's own version. Changing what is measured, or how, changes this.
VERSION = 1

#: What this benchmark asks, in the sentences the index has room for.
GOAL = (
    "**If a study replaced manual vessel tracing with a segmentation model, would its biomarkers "
    "still tell one eye from another?** Every biomarker is computed twice on each photograph an "
    "expert annotated — once on the expert's artery/vein map and once on a model's — with the same "
    "program, the same optic disc and the same scale, so any difference is the map's. The intraclass "
    "correlation says whether the two numbers agree; the signal-to-noise ratio says whether the "
    "difference between eyes outweighs the error the model introduces."
)

#: The programs that compute the numbers, in the lineage order the synthetic benchmark explains.
IMPLEMENTATIONS = biomarker_synthetic.IMPLEMENTATIONS

#: What the expert's map is called wherever a model's slug would otherwise stand.
EXPERT = "expert"

#: The segmentation models whose kept masks are measured, by the slug of their catalogue page. Only
#: those separating arteries from veins: every implementation here needs both classes.
SEGMENTERS = ("vascx-artery-vein", "ocularnet", "lunet", "automorph-artery-vein", "bf-net")

#: The datasets, every one carrying an expert's artery and vein maps. FIVES has no classes and
#: AV-WIDE is a 200° field with no scale; the configuration page says why each is left out.
DATASETS = ("hrf", "fundus-avseg", "avrdb", "reyia", "rav")

#: Why a declared implementation has no adapter, where the reason is worth more than the default.
WHY_NOT: dict[str, str] = {}

#: The artery/vein benchmark whose kept masks are this one's input.
SOURCE = "av"

#: How many maps each worker measures before the whole pool is replaced by fresh processes. Some implementations
#: keep memory they never release, and fifteen workers each growing to five gigabytes ran a
#: 62-gigabyte machine out of memory part-way through VascX. Reloading an adapter costs seconds; a
#: map costs half a minute or more.
RECYCLE = 20

#: The facts an implementation declares that change what it returns — as the synthetic benchmark.
FINGERPRINTED = biomarker_synthetic.FINGERPRINTED

#: How many processes measure at once by default. Every implementation is single-threaded Python
#: over one skeleton at a time, so a process per core is what makes a run of hours rather than days.
WORKERS = max(1, (os.cpu_count() or 2) - 1)

#: The biomarkers the index quotes, from the reference implementation: the five a reader of a
#: vascular-epidemiology paper is most likely to meet, each with its own way of failing — widths
#: fail on a vessel edge, the ratio on the classification, fractal dimension on the smallest
#: vessels, tortuosity on a broken centreline. The fractal dimension is the arteries': the
#: reference measures each class and not their union.
PANEL = (
    ("CRAE", "calibre/CRE-knudtson/artery/B"),
    ("CRVE", "calibre/CRE-knudtson/vein/B"),
    ("AVR", "calibre/AVR-knudtson/both/B"),
    ("Artery fractal dimension", "density/box-counting/artery"),
    ("Artery tortuosity", "tortuosity/hart-tau1/artery/median"),
)

#: Which implementation the index reads its panel from: the one built against the catalogue's own
#: definitions, whose every column has a catalogued name.
REFERENCE = "fundus-biomarkers"

#: Where a project has no column for a panel biomarker as the panel defines it, the nearest one it
#: does have, in order of preference. Only tortuosity needs one: the programs differ in which
#: summary of the segments they return, and the panel's median is preferred because it resists the
#: short fragments a model adds or drops.
PANEL_FALLBACK = {
    "Artery tortuosity": (
        "tortuosity/hart-tau1/artery/length-weighted",
        "tortuosity/hart-tau1/artery/mean",
    ),
}

#: Each project's own artery/vein segmentation — the model whose maps its own pipeline measures —
#: and where that pairing comes from. The run still measures every implementation on every model's
#: map; the analysis and both pages read each project on its own model only, so a project is judged
#: as its authors ship it rather than on a map it was never paired with. PVBM is not here: it ships
#: no artery/vein model, and its users supply the masks.
NATIVE = {
    "ocular": ("ocularnet", "the model OCULARNet's own repository introduces"),
    "automorph": ("automorph-artery-vein", "AutoMorph's own `M2_Artery_vein` module"),
    "automorphalyzer": ("automorph-artery-vein", "inherited from AutoMorph with its other models"),
    "automorphclass": ("automorph-artery-vein", "AutoMorph's weights, copied into the package"),
    "vascx": ("vascx-artery-vein", "VascX's own artery/vein ensemble"),
    "fundus-biomarkers": (
        "ocularnet",
        "the artery/vein model its command-line pipeline runs, borrowed from OCULARNet",
    ),
}


def native(slug: str) -> str | None:
    """The segmentation model a project ships with, or None for one that ships none."""
    return NATIVE[slug][0] if slug in NATIVE else None


def panel_for(names: Iterable[str]) -> list[tuple[str, str]]:
    """The panel as one project can answer it: each label it has a column for, with the catalogued
    name that column answers to — the panel's own where it has it, else `PANEL_FALLBACK`'s."""
    present = set(names)
    found = []
    for label, name in PANEL:
        for candidate in (name, *PANEL_FALLBACK.get(label, ())):
            if candidate in present:
                found.append((label, candidate))
                break
    return found


def implementations(slugs: list[str]) -> tuple[list, dict[str, str]]:
    """The adapters that exist, and what was declared without one."""
    found, missing = [], {}
    for slug in slugs:
        try:
            found.append(catalogue.load(slug))
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
        elif not (DISCS / f"{slug}.csv").exists():
            missing[slug] = "no disc estimate: run `fetch_disc_estimation` first"
    return missing


def masks(
    slug: str, root: Path | None = None, kept: Path = runs.RUNS
) -> tuple[dict[str, dict[str, object]], dict[str, str]]:
    """Which models' kept masks of one dataset are still that model's, and why the rest are not.

    The drawing fingerprint is recomputed from the model's declaration, its weights and the store
    and compared with the one kept beside the masks (`build-benchmark` §6.2). A mismatch means the
    masks describe a model that no longer exists, so they are not read.
    """
    from . import av

    usable, refused = {}, {}
    for model in SEGMENTERS:
        directory = kept / SOURCE / model / slug
        marker = directory / "fingerprint.txt"
        if not marker.exists():
            refused[model] = f"no masks kept: run `--benchmark {SOURCE} --model {model}` first"
            continue
        found, missing = av.adapters([model], device="cpu")
        if not found:
            refused[model] = missing.get(model, "no adapter written")
            continue
        current = av.drawing(found[0], slug, root)
        if marker.read_text().strip() != current:
            refused[model] = f"its kept masks are stale: run `--benchmark {SOURCE} --model {model}`"
            continue
        usable[model] = {"directory": directory, "drawing": current}
    return usable, refused


def _store(slug: str, root: Path | None) -> dict[str, object]:
    from datasets.utils import paths

    build = (root or paths.root()) / slug / "build.json"
    record = json.loads(build.read_text()) if build.exists() else {}
    return {"slug": slug, "builder_version": record.get("builder_version")}


# ---------------------------------------------------------------------------------------------
# Measuring. Each worker process loads one adapter once and is handed (photograph, map) items.

_ADAPTER = None


def _start(slug: str) -> None:
    global _ADAPTER
    _ADAPTER = catalogue.load(slug)


def _measure(item: dict[str, object]) -> dict[str, object]:
    """One implementation over one map of one photograph, as a row of evidence."""
    started = time.perf_counter()
    note = ""
    try:
        artery = read_mask(Path(item["artery"]))
        vein = read_mask(Path(item["vein"]))
        field = read_mask(Path(item["fov"]))
        if hasattr(_ADAPTER, "trouble"):
            _ADAPTER.trouble = {}
        answered = _ADAPTER.measure(artery, vein, field, tuple(item["disc"]), item["um_per_px"])
        note = "; ".join(f"{where}: {why}" for where, why in getattr(_ADAPTER, "trouble", {}).items())
    except Exception as failure:  # noqa: BLE001 — a crash is an answer about nothing
        answered, note = dict.fromkeys(_ADAPTER.keys()), repr(failure)
    taken = time.perf_counter() - started
    row: dict[str, object] = {
        "key": item["key"],
        "subset": item["subset"],
        "split": item["split"],
        "source": item["source"],
        "drawing": item["drawing"],
        "um_per_px": "" if item["um_per_px"] is None else f"{item['um_per_px']:.6f}",
        "disc_x": f"{item['disc'][0]:.2f}",
        "disc_y": f"{item['disc'][1]:.2f}",
        "disc_r": f"{item['disc'][2]:.2f}",
        "outcome": "measured" if any(v is not None for v in answered.values()) else "failed",
        "seconds": f"{taken:.2f}",
        "note": note,
    }
    for key in _ADAPTER.keys():
        row[f"said_{key}"] = _said(answered.get(key))
    return row


def _said(value: object) -> str:
    """One answer as the evidence spells it: six significant figures, or the category it said."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    number = float(value)
    return "" if math.isnan(number) else f"{number:.6g}"


def run(
    adapters: list,
    datasets: list[str],
    results: Path = runs.RESULTS,
    root: Path | None = None,
    force: bool = False,
    max_samples: int | None = None,
    random_samples: bool = False,
    seed: int = 0,
    workers: int = WORKERS,
    kept: Path = runs.RUNS,
    record: Path | None = None,
    sources: dict[str, tuple[dict, dict]] | None = None,
    discs: Path = DISCS,
) -> list[dict[str, object]]:
    """Measure every implementation on every map of every photograph of every dataset.

    :param sources: per dataset, the models' kept masks that may be read and those refused, as
        :func:`masks` returns them. Worked out here when not given; a test gives it, because
        working it out loads every segmentation model's declaration and weights.
    """
    started = datetime.now(UTC)
    if not adapters or not datasets:
        raise RuntimeError("nothing to measure: no dataset available, or no implementation adapted")
    given = sources or {}
    sources = {}
    for slug in datasets:
        usable, refused = given[slug] if slug in given else masks(slug, root, kept)
        for model, why in refused.items():
            print(f"warning: {model} × {slug} is not measured — {why}", file=sys.stderr)
        sources[slug] = (usable, refused)
    scored = []
    for adapter in adapters:
        for slug in datasets:
            usable, refused = sources[slug]
            scored.append(
                _pair(
                    adapter, slug, usable, refused, results, root, force, max_samples,
                    random_samples, seed, workers, discs,
                )
            )
        write_pooled(adapter, results)
    _record(scored, started, record or kept)
    return scored


def _pair(
    adapter,
    slug: str,
    usable: dict[str, dict[str, object]],
    refused: dict[str, str],
    results: Path,
    root: Path | None,
    force: bool,
    max_samples: int | None,
    random_samples: bool,
    seed: int,
    workers: int,
    discs: Path = DISCS,
) -> dict[str, object]:
    """One implementation on one dataset: every photograph, on the expert's map and each model's."""
    loader = BiomarkerLoader(
        slug,
        root=root,
        max_samples=max_samples,
        random_samples=random_samples,
        seed=seed,
        discs_from=discs,
    )
    declared = adapter.declare()
    identity = runs.fingerprint(
        {
            "benchmark": NAME,
            "version": VERSION,
            "declared": {key: declared.get(key) for key in FINGERPRINTED},
            "code": adapter.identity(),
            "store": _store(slug, root),
            "discs": disc_fingerprint(slug, discs),
            "floor": FLOOR,
        }
    )
    drawings = {EXPERT: ""} | {model: str(entry["drawing"]) for model, entry in usable.items()}
    kept = [] if force else runs.measured(results, NAME, adapter.slug, slug, identity)
    # A row of a model whose masks have been redrawn since describes the old drawing: dropped and
    # measured again, while every other source's rows stand.
    kept = [row for row in kept if drawings.get(row["source"]) == row.get("drawing", "")]
    done = {(row["key"], row["source"]) for row in kept}

    items = []
    for index in range(len(loader)):
        sample = loader[index]
        key = sample["key"]
        common = {
            "key": key,
            "subset": sample["subset"],
            "split": sample["split"],
            "um_per_px": sample["um_per_px"],
            "disc": sample["disc"],
            "fov": str(loader.field_of(key)),
        }
        expert = loader.expert_of(key)
        if (key, EXPERT) not in done:
            items.append(
                common
                | {"source": EXPERT, "drawing": "", "artery": str(expert["artery"]),
                   "vein": str(expert["vein"])}
            )
        for model, entry in usable.items():
            directory = Path(entry["directory"])
            if (key, model) in done or not (directory / f"{key}-artery.png").exists():
                # No kept file means the model failed on this photograph in the artery/vein run;
                # its row there says so, and there is no map here to measure.
                continue
            items.append(
                common
                | {"source": model, "drawing": entry["drawing"],
                   "artery": str(directory / f"{key}-artery.png"),
                   "vein": str(directory / f"{key}-vein.png")}
            )

    wanted = len(loader) * (1 + len(usable))
    total_sources = 1 + len(usable)

    def record_so_far(fresh: list[dict[str, object]]) -> dict[str, object]:
        evidence = sorted(kept + fresh, key=lambda row: (row["key"], row["source"]))
        measured_keys = {row["key"] for row in evidence if row["source"] == EXPERT}
        counted = runs.counts(len(measured_keys), loader.total, loader.excluded)
        # Complete when every map this run set out to measure has been: a model with no kept mask
        # for a photograph failed there in the artery/vein run and owes no row here.
        counted["complete"] = counted["complete"] and len(fresh) >= len(items)
        taken = [float(row["seconds"]) for row in evidence if row.get("seconds")]
        summary = {
            **counted,
            "sources": [EXPERT, *usable],
            "not_measured": refused,
            "maps": len(evidence),
            "failed": sum(row["outcome"] == "failed" for row in evidence),
            "seconds_per_map": sum(taken) / len(taken) if taken else None,
            "seconds_per_photograph": sum(taken) / len(taken) * total_sources if taken else None,
            "timed_photographs": len(taken) // max(1, total_sources),
            "device": "cpu, one core per worker",
        }
        runs.write(results, NAME, adapter.slug, slug, identity, summary, evidence)
        return {"counts": counted, "summary": summary, "evidence": evidence}

    print(f"{adapter.slug} × {slug}: {len(items)} maps to measure of {wanted}", flush=True)
    fresh: list[dict[str, object]] = []
    if items and workers <= 1:
        # In this process, with the adapter already loaded: what a test and a debugger need.
        global _ADAPTER
        _ADAPTER = adapter
        for since, item in enumerate(items, start=1):
            fresh.append(_measure(item))
            if since % runs.CHECKPOINT == 0:
                record_so_far(fresh)
    elif items:
        context = multiprocessing.get_context("spawn")
        # One thread per worker: these programs are numpy over one image at a time, and a pool of
        # processes each spawning a thread per core is slower than either alone.
        for variable in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
            os.environ[variable] = "1"
        # An executor rather than multiprocessing.Pool: a worker the kernel kills for memory leaves a
        # Pool waiting forever on a result that will never come, where an executor raises.
        #
        # Workers are recycled by giving each batch of RECYCLE maps per worker a fresh executor, so
        # memory an implementation never gives back (VascX holds several gigabytes) cannot
        # accumulate until the machine runs out. Not with `max_tasks_per_child`: on Python 3.12 an
        # executor retiring its workers that way deadlocked with none left (CPython gh-115634).
        size = min(workers, len(items))
        batch = size * RECYCLE
        since = 0
        for start in range(0, len(items), batch):
            with ProcessPoolExecutor(
                size, mp_context=context, initializer=_start, initargs=(adapter.slug,)
            ) as pool:
                try:
                    chunk = items[start : start + batch]
                    for future in as_completed([pool.submit(_measure, item) for item in chunk]):
                        fresh.append(future.result())
                        since += 1
                        if since >= runs.CHECKPOINT:
                            record_so_far(fresh)
                            since = 0
                            print(f"  {adapter.slug} × {slug}: {len(fresh)} of {len(items)}", flush=True)
                except BrokenProcessPool as broken:
                    record_so_far(fresh)
                    raise RuntimeError(
                        f"{adapter.slug} × {slug}: a worker died, most likely killed for running "
                        f"the machine out of memory. {len(fresh)} maps are written; run again with "
                        "fewer --workers and it finishes the rest."
                    ) from broken
    written = record_so_far(fresh)
    write_agreement(adapter, slug, written["evidence"], results)
    return {
        "model": adapter.slug,
        "dataset": slug,
        "declared": declared,
        "fingerprint": identity,
        "counts": written["counts"],
        "summary": written["summary"],
    }


# ---------------------------------------------------------------------------------------------
# Agreement: what the run writes beside the evidence, so every table quotes one computation.


def _converter(declared: dict[str, object]):
    """How one of this implementation's numbers becomes a number in its catalogued unit.

    Every adapter reports what its implementation returned, in pixels, unless its declared units say
    a column is already in microns — PVBM's Hubbard equivalents are, because Hubbard's constants
    only mean anything on microns. Converting those again would multiply by the scale twice.
    """
    from biomarkers import canonical

    units = declared.get("units")
    already = (
        {own for own, unit in units.items() if isinstance(unit, str) and "µm" in unit}
        if isinstance(units, dict)
        else set()
    )

    def convert(own: str, name: str | None, value: float, scale: float | None) -> float | None:
        if not name or own in already:
            return value
        if canonical.length_power(name) == 0:
            return value
        return None if scale is None else canonical.from_pixels(name, value, scale)

    return convert


def _numbers(evidence: list[dict[str, object]], declared: dict[str, object]):
    """Every (source, column) → {key: value}, in catalogued units where a column has a name."""
    from biomarkers import canonical

    names = declared.get("names", {})
    convert = _converter(declared)
    table: dict[tuple[str, str], dict[str, float]] = {}
    for row in evidence:
        scale = float(row["um_per_px"]) if row.get("um_per_px") else None
        for column, said in row.items():
            if not column.startswith("said_") or said in ("", None):
                continue
            own = column[len("said_") :]
            name = names.get(own)
            if name and canonical.unit(name) == "category":
                continue
            try:
                value = float(said)
            except (TypeError, ValueError):
                continue
            if not math.isfinite(value):
                continue
            converted = convert(own, name, value, scale)
            if converted is not None:
                table.setdefault((str(row["source"]), own), {})[str(row["key"])] = converted
    return table


#: The columns of every agreement table, in order.
AGREEMENT_COLUMNS = {
    "model": "the segmentation model whose map was measured against the expert's",
    "column": "the implementation's own name for the number",
    "name": "the catalogued biomarker it answers to, from the adapter's naming table; empty where "
    "the catalogue has none",
    "unit": "the unit the statistics are in: the catalogued unit where there is a name — lengths in "
    "microns — and the implementation's own otherwise",
    "contamination": "whether this model trained on this dataset, from `contamination.py`; a "
    "dataset whose subsets differ is `mixed`",
    "n": "photographs both maps produced a value for — every statistic is over these",
    "expert_only": "photographs the expert's map produced a value for and the model's did not",
    "model_only": "photographs the model's map produced a value for and the expert's did not",
    "expert_mean": "the mean on the expert's maps",
    "expert_sd": "the standard deviation across photographs on the expert's maps — the signal",
    "model_mean": "the mean on the model's maps",
    "bias": "the mean of model minus expert, in the unit",
    "relative_bias": "that bias as a fraction of the expert mean",
    "sd_difference": "the standard deviation of model minus expert — the noise",
    "icc_agreement": "ICC(A,1): two-way, absolute agreement, one measurement",
    "icc_consistency": "ICC(C,1): two-way, consistency, one measurement — forgives a constant offset",
    "snr": "signal over noise: `expert_sd / sd_difference`; a constant offset is not noise",
    "iqr_pct": "the interquartile range of the expert-map values over their median, in percent — "
    "the signal as fundus-biomarkers measures it",
    "mape_pct": "the mean of |model − expert| / |expert|, in percent, leaving out expert values of "
    "0 — the noise as fundus-biomarkers measures it, a constant offset included",
    "iqr_mape": "`iqr_pct / mape_pct`, fundus-biomarkers' target metric: above 1, eyes differ more "
    "than the map moves the value. Roughly 1.7 × `snr` where there is no bias",
}


def agreement_rows(
    adapter_slug: str, declared: dict[str, object], datasets: dict[str, list[dict[str, object]]]
) -> list[dict[str, object]]:
    """One row per (model, column), over every photograph of the datasets given, pooled."""
    from biomarkers import canonical

    names = declared.get("names", {})
    table: dict[tuple[str, str], dict[str, float]] = {}
    marks: dict[str, set[str]] = {}
    for slug, evidence in datasets.items():
        for (source, own), values in _numbers(evidence, declared).items():
            target = table.setdefault((source, own), {})
            target.update({f"{slug}/{key}": value for key, value in values.items()})
        for row in evidence:
            if row["source"] != EXPERT:
                marks.setdefault(str(row["source"]), set()).add(
                    contamination.mark(str(row["source"]), slug, str(row["split"]), str(row["subset"]))
                )
    models = sorted({source for source, _ in table if source != EXPERT}, key=_model_order)
    columns = sorted({own for _, own in table})
    rows = []
    for model in models:
        seen = sorted(marks.get(model, set()))
        mark = seen[0] if len(seen) == 1 else "mixed: " + ", ".join(seen)
        for own in columns:
            expert = table.get((EXPERT, own), {})
            said = table.get((model, own), {})
            if not expert and not said:
                continue
            keys = sorted(set(expert) | set(said))
            found = agreement.summary([expert.get(k) for k in keys], [said.get(k) for k in keys])
            name = names.get(own) or ""
            rows.append(
                {
                    "model": model,
                    "column": own,
                    "name": name,
                    "unit": canonical.unit(name) if name else "as returned",
                    "contamination": mark,
                    **{k: _cell(found.get(k)) for k in list(AGREEMENT_COLUMNS)[5:]},
                }
            )
    return rows


def _model_order(model: str) -> int:
    return SEGMENTERS.index(model) if model in SEGMENTERS else len(SEGMENTERS)


def _cell(value: object) -> object:
    if value is None:
        return ""
    if isinstance(value, float):
        return "inf" if math.isinf(value) else f"{value:.6g}"
    return value


def _write_table(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(AGREEMENT_COLUMNS), restval="")
        writer.writeheader()
        writer.writerows(rows)


def write_agreement(adapter, slug: str, evidence: list[dict[str, object]], results: Path) -> None:
    rows = agreement_rows(adapter.slug, adapter.declare(), {slug: evidence})
    _write_table(results / NAME / adapter.slug / "agreement" / f"{slug}.csv", rows)


def write_pooled(adapter, results: Path = runs.RESULTS) -> None:
    """The agreement over every dataset this implementation has evidence for, pooled on photographs."""
    slug = adapter.slug
    datasets = {
        path.stem: runs.rows(results, NAME, slug, path.stem)
        for path in sorted((results / NAME / slug).glob("*.csv"))
    }
    if datasets:
        rows = agreement_rows(slug, adapter.declare(), datasets)
        _write_table(results / NAME / slug / "agreement" / "pooled.csv", rows)


def _record(scored: list[dict[str, object]], started: datetime, into: Path) -> None:
    directory = into / NAME / started.strftime("%Y-%m-%dT%H-%M-%SZ")
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "run.json").write_text(
        json.dumps(
            {
                "benchmark": NAME,
                "version": VERSION,
                "started": started.isoformat(),
                "python": sys.version.split()[0],
                "pairs": [
                    {k: entry[k] for k in ("model", "dataset", "fingerprint", "counts")}
                    | {"declared": entry["declared"]}
                    for entry in scored
                ],
            },
            indent=1,
            default=str,
        )
        + "\n"
    )


# ---------------------------------------------------------------------------------------------
# What the benchmark says about itself.

#: Every column of this benchmark's evidence, and what it means.
COLUMNS = {
    "key": "the photograph, by the store's own key",
    "subset": "the part of the dataset it came from — a camera, or for REYIA the source collection",
    "split": "the split the dataset assigned it, where it assigned one",
    "source": "whose artery/vein map was measured: `expert` for the dataset's own annotation, else "
    "the segmentation model's slug",
    "drawing": "the drawing fingerprint of the model's kept masks (`build-benchmark` §6.2); empty for "
    "the expert's map, whose store version is in the result's fingerprint",
    "um_per_px": "the microns per pixel from the store's manifest; empty where none was published "
    "or inferred",
    "disc_x": "the optic disc centre's column in the crop, from `results/disc_estimation/`",
    "disc_y": "its row",
    "disc_r": "its equivalent radius, in pixels — the one disc every map of this photograph is "
    "measured with",
    "outcome": "`measured` if any number came back, else `failed`; `note` says what fell over",
    "seconds": "how long the implementation took over this one map, on one core",
    "note": "what the implementation complained about or failed with",
    "said_<key>": "what the implementation returned, under **its own** column name and in its own "
    "unit — pixels for a length, as the adapter declares. The catalogued name and the conversion to "
    "microns are applied in the agreement tables, never here",
}


def _pinned(upstream: dict) -> str:
    return biomarker_synthetic._pinned(upstream)


def configuration(datasets: list[str], root: Path | None = None) -> list[dict[str, object]]:
    """Each available dataset, as the loader sees it on this machine."""
    absent = missing_datasets(datasets, root)
    described = []
    for slug in (name for name in datasets if name not in absent):
        loader = BiomarkerLoader(slug, root=root)
        scaled = sum(1 for row in loader.rows if row.get("um_per_px"))
        described.append(
            {
                "slug": slug,
                "total": loader.total,
                "scaled": scaled,
                "excluded": dict(loader.excluded),
            }
        )
    return described


def config(root: Path | None = None) -> dict[str, object]:
    """What this benchmark reports about itself, as data rather than prose."""
    from . import photographs

    adapters, missing = implementations(list(IMPLEMENTATIONS))
    declared = {adapter.slug: adapter.declare() for adapter in adapters}
    absent = missing_datasets(list(DATASETS), root)
    described = {entry["slug"]: entry for entry in configuration(list(DATASETS), root)}
    return {
        "benchmark": NAME,
        "title": TITLE,
        "version": VERSION,
        "asks": GOAL,
        "unit_of_work": {"singular": "map of a photograph", "plural": "maps of photographs"},
        "subjects": {
            "label": "implementation",
            "fields": ["Pinned at", "Columns it returns"],
            "declared": [
                {
                    "slug": slug,
                    "page": f"../projects/{declared.get(slug, {}).get('page', slug)}.md",
                    "facts": {
                        "Pinned at": _pinned(declared[slug]["upstream"]),
                        "Columns it returns": len(declared[slug]["keys"]),
                    }
                    if slug in declared
                    else {},
                    "ran": slug in declared,
                    "why_not": missing.get(slug),
                }
                for slug in IMPLEMENTATIONS
            ],
        },
        "segmenters": list(SEGMENTERS),
        "native": [
            {"project": slug, "page": f"../projects/{declared.get(slug, {}).get('page', slug)}.md",
             "model": model, "why": why}
            for slug, (model, why) in NATIVE.items()
        ],
        "material": {
            "label": "dataset",
            "fields": ["Photographs", "With a scale", "Excluded, and why"],
            "declared": [
                {
                    "slug": slug,
                    "page": f"../{photographs.page(slug)}",
                    "facts": {
                        "Photographs": described[slug]["total"],
                        "With a scale": described[slug]["scaled"],
                        "Excluded, and why": report.excluded(described[slug]["excluded"]),
                    }
                    if slug in described
                    else {},
                    "available": slug in described,
                    "why_not": absent.get(slug),
                }
                for slug in DATASETS
            ],
            "wanted": [],
        },
        "exclusions": {
            "below the size floor": photographs.FLOOR_RULE,
            "a finding recorded against the image": photographs.FINDING_RULE,
            NO_CLASSES: "a photograph without both an artery and a vein map; every implementation "
            "here needs both",
            CONDEMNED: "an artery or vein map `src/datasets/exclusions/` records as wrong. Unlike the "
            "artery/vein benchmark the photograph goes, not the map: a biomarker needs both",
            NO_DISC: "a photograph the SegFormer disc model found no disc on, in "
            "`results/disc_estimation/`. Every implementation measures in zones counted in disc "
            "radii, and handing the two maps different discs would measure the discs",
            "excluded whole": photographs.CROP_RULE,
        },
        "fingerprint": [
            "this benchmark's name, `VERSION` and size floor",
            f"the facts each implementation declares that bear on its numbers: {', '.join(FINGERPRINTED)}",
            "the pinned commit of the implementation's code and the content of every patch applied to "
            "it, as its declared `upstream` records them",
            "the store's slug and builder version, which pins the expert's maps and the field of view",
            "the fingerprint of the disc estimate in `results/disc_estimation/<dataset>.json`",
            f"**per row**, the drawing fingerprint of the model's masks kept by the `{SOURCE}` "
            "benchmark. A model redrawn there has its rows here measured again, and only its rows",
        ],
        "running": {
            "examples": [
                f"python -m benchmarks --benchmark {NAME} --workers 15",
                f"python -m benchmarks --benchmark {NAME} --model vascx --dataset hrf",
                f"python -m benchmarks --benchmark {NAME} --max-samples 10",
                f"python -m benchmarks --benchmark {NAME} --docs",
            ],
            "flags": {
                "--model": "one implementation, or several separated by commas",
                "--dataset": "one dataset, or several separated by commas",
                "--workers": f"how many processes measure at once; {WORKERS} on this machine by "
                "default, one fewer than its cores",
                "--max-samples": "measure only the first N photographs of each dataset, for "
                "development; a sampled result says it is not complete, and a later run finishes it",
                "--random-samples": "choose those photographs at random rather than first",
                "--seed": "the seed a random sample uses",
                "--data-root": "read the stores from somewhere other than `.atlas_data/`",
                "--force": "discard what is stored and measure it all again",
                "--no-report": "skip refreshing `docs/BENCHMARKS.md` after the run",
                "--config": "print what this benchmark reports about itself, as JSON, measuring nothing",
                "--docs": "refresh this page from that JSON, measuring nothing",
            },
        },
        "evidence": f"results/{NAME}/<implementation>/<dataset>.csv",
        "columns": COLUMNS,
        "agreement": f"results/{NAME}/<implementation>/agreement/<dataset>.csv and `pooled.csv`",
        "agreement_columns": AGREEMENT_COLUMNS,
        "counts": {
            "processed": "how many photographs the expert's map has been measured on",
            "total": "how many the benchmark would ask about, after the exclusions",
            "excluded": "how many those exclusions removed, by reason",
            "complete": "whether every map of every photograph has been measured",
            "maps": "how many maps were measured: the expert's and each model's, per photograph",
            "failed": "how many of those returned nothing at all",
            "not_measured": "the segmentation models declared and not read, with the reason",
            "seconds_per_photograph": "how long the implementation took over every map of one "
            "photograph, on one core — not part of the fingerprint",
        },
    }


# ---------------------------------------------------------------------------------------------
# The index.


def index_section(records: list[dict[str, object]], results: Path) -> Iterable[str]:
    """One row per project, measured on its own segmentation model: how well the headline
    biomarkers it computes survive that map."""
    rows_of: dict[str, list[dict[str, str]]] = {}
    for slug in NATIVE:
        pooled = results / NAME / slug / "agreement" / "pooled.csv"
        if pooled.exists():
            with open(pooled, newline="") as f:
                rows_of[slug] = [row for row in csv.DictReader(f) if row["model"] == native(slug)]
    if not rows_of:
        yield f"No pooled agreement yet: run `--benchmark {NAME}`."
        yield ""
        return
    datasets = sorted({str(r["dataset"]) for r in records if r["model"] in rows_of})
    yield (
        "Each project is read on **its own artery/vein model**, as its authors ship it. ICC(A,1) — "
        "absolute agreement between the biomarker measured on that model's map and on the expert's — "
        f"**pooled over the photographs of {', '.join(datasets)}**. 1 is perfect; below 0.75 a study "
        "could not swap one map for the other. A dash is a biomarker the project does not compute; "
        "a tortuosity in italics is the project's mean or length-weighted mean, where it returns no "
        "median. PVBM ships no artery/vein model and is not in this table."
    )
    yield ""
    yield "| Project | Its model | " + " | ".join(label for label, _ in PANEL) + " | Contamination |"
    yield "| --- | --- | " + "--- | " * len(PANEL) + "--- |"
    leaders: dict[str, list[tuple[float, str]]] = {label: [] for label, _ in PANEL}
    for slug, rows in rows_of.items():
        by = {row["name"]: row for row in rows if row["name"]}
        chosen = dict(panel_for(by))
        cells = []
        for label, name in PANEL:
            found = chosen.get(label)
            value = by[found]["icc_agreement"] if found else ""
            if not value:
                cells.append("—")
                continue
            leaders[label].append((float(value), slug))
            cells.append(f"{float(value):.2f}" if found == name else f"*{float(value):.2f}*")
        mark = rows[0]["contamination"] if rows else "—"
        model = native(slug)
        page = catalogue.load(slug).declare().get("page", slug)
        yield (
            f"| [{slug}](projects/{page}.md) | [{model}](models/{model}.md) | "
            + " | ".join(cells) + f" | {mark} |"
        )
    yield ""
    unfinished = report.unfinished([r for r in records if r["model"] in rows_of])
    if unfinished:
        yield unfinished
        yield ""
    said = []
    for label, found in leaders.items():
        if len(found) >= 2:
            (a, first), (b, second) = sorted(found, reverse=True)[:2]
            said.append(f"{label}, {first} ({a:.2f}) then {second} ({b:.2f})")
        elif found:
            said.append(f"{label}, {found[0][1]} alone ({found[0][0]:.2f})")
    if said:
        yield (
            "**Where to start:** by pooled ICC(A,1), biomarker by biomarker — " + "; ".join(said)
            + ". Pooled figures include AVRDB, whose wide-stroke annotation decides much of the "
            "calibre ranking: the results page reads it dataset by dataset."
        )
        yield ""


def main(arguments) -> None:
    """Run this benchmark from the one command every benchmark is run from."""
    chosen = arguments.model.split(",") if arguments.model else list(IMPLEMENTATIONS)
    wanted = arguments.dataset.split(",") if arguments.dataset else list(DATASETS)
    adapters, missing = implementations([slug.strip() for slug in chosen])
    for slug, why in missing.items():
        print(f"warning: {slug} is not measured — {why}", file=sys.stderr)
    root = Path(arguments.data_root) if arguments.data_root else None
    absent = missing_datasets([slug.strip() for slug in wanted], root)
    for slug, why in absent.items():
        print(f"warning: {slug} is not measured — {why}", file=sys.stderr)
    datasets = [slug.strip() for slug in wanted if slug.strip() not in absent]
    scored = run(
        adapters,
        datasets,
        root=root,
        force=arguments.force,
        max_samples=arguments.max_samples,
        random_samples=arguments.random_samples,
        seed=arguments.seed,
        workers=getattr(arguments, "workers", None) or WORKERS,
    )
    if arguments.report:
        report.write_index()
    print(f"{len(scored)} pairs measured")
