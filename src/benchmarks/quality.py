# ABOUTME: The quality benchmark: how well a model judges whether a photograph is worth measuring,
# ABOUTME: measured against the grade the dataset's own readers gave it.

import json
import sys
import time
from collections.abc import Callable, Iterable
from datetime import UTC, datetime
from pathlib import Path

import torch
from torch.utils.data import DataLoader

from datasets.utils import paths
from models.utils import catalogue

from . import report, runs, scoring
from .loaders.base import CROPS, FLOOR, available, collate
from .loaders.quality import QualityLoader

#: What this benchmark asks, in the two sentences the index has room for.
GOAL = (
    "**Is this photograph good enough to measure?** Every quality model here is asked that of the "
    "same photographs, and its answer is compared with the grade the dataset's own readers wrote "
    "down. A gate that throws away usable photographs costs a study its sample; one that lets bad "
    "photographs through costs it every biomarker computed from them."
)

#: What this benchmark is called in a heading, where its slug does not read as English.
TITLE = "Quality"

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


#: Every column of this benchmark's evidence, and what it means. The configuration page is
#: generated from this, so a column nobody explained is a column nobody can add.
COLUMNS = {
    "key": "the photograph, as the store names it — it joins to the manifest and to the image",
    "subset": "the dataset's own subcollection: a camera, an acquisition site, a challenge release",
    "split": "the split the dataset published, or `unspecified` where it published none",
    "grade": "the reference grade: `good`, `usable` or `bad`",
    "grade_source": "where that grade came from: `published`, `derived` or `assumed`",
    "pad_fraction": "how much of the square the store built is canvas rather than photograph",
    "readers": "each reader's own grade, where the dataset keeps its readers apart",
    "outcome": "`graded`, `declined` by the model itself, or `failed` with the reason in `note`",
    "verdict": "the model's own hard call, in the atlas's words. Empty for a model with no classes",
    "carried_by_its_pipeline": (
        "whether the model's **own project** would carry this photograph into measurement, which "
        "is not the same as its verdict. Empty where no catalogued pipeline gates on this model"
    ),
    "gradeable": (
        "the model's confidence that the photograph is worth measuring — the one question every "
        "quality model can be asked, and what the ranking metrics use"
    ),
    "good": "the probability of that grade, where the model emits three. Absent where it does not",
    "usable": "as above",
    "bad": "as above",
    "note": "why the model declined, or what it failed with",
}


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

    timed = runs.Timing()
    stored = runs.read(results, NAME, adapter.slug, slug) if kept else None

    def record_so_far(fresh: list[dict[str, object]]) -> dict[str, object]:
        """Write down everything scored to this point, complete or not."""
        evidence = sorted(kept + fresh, key=lambda entry: entry["key"])
        counted = runs.counts(len(evidence), loader.total, loader.excluded)
        described = {
            **scoring.summarise(
                {entry["key"]: entry["grade"] for entry in evidence},
                [scoring.restored(entry) for entry in evidence],
            ),
            **runs.kept_timing(stored, timed),
            "device": declared.get("device"),
        }
        runs.write(results, NAME, adapter.slug, slug, identity, {**described, **counted}, evidence)
        return {"counts": counted, "summary": described, "evidence": evidence}

    if len(loader):
        print(f"{adapter.slug} × {slug}: {len(loader)} photographs", flush=True)
        fresh = _rows(
            loader,
            _grade(
                adapter,
                loader,
                batch,
                timed,
                lambda graded: record_so_far(_rows(loader, graded)),
            ),
        )
    else:
        print(f"{adapter.slug} × {slug}: kept, nothing left to measure", flush=True)
        fresh = []

    written = record_so_far(fresh)
    counts, summary, evidence = written["counts"], written["summary"], written["evidence"]
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


def _grade(
    adapter,
    loader: QualityLoader,
    batch: int,
    timed: runs.Timing,
    record_so_far: Callable[[list], object],
) -> list:
    """Every photograph still to be scored, in batches at the model's own grid.

    What has been scored is written down every :data:`runs.CHECKPOINT` photographs, so that a run
    the machine stops part-way through is one the next run finishes rather than starts again.
    """
    graded, since = [], 0
    for sample in DataLoader(loader, batch_size=batch, collate_fn=collate, shuffle=False):
        started = time.perf_counter()
        graded.extend(adapter.grade(sample["image"], sample["key"]))
        timed.record(time.perf_counter() - started, len(sample["key"]))
        since += len(sample["key"])
        if since >= runs.CHECKPOINT:
            record_so_far(graded)
            since = 0
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
    if not asked.report:
        return

    # The results page is not written here: it states conclusions drawn from the notebook, and a
    # run must not be able to destroy them. See the `report-benchmark` skill.
    report.write_index()


def docs_sections(
    configured: dict[str, object],
    missing_models: dict[str, str],
    missing_datasets: dict[str, str],
) -> Iterable[str]:
    """Sections 1 to 4 of the page saying how this benchmark is run.

    They live here rather than in the report writer because what they describe — a grade, where it
    came from, and what each project's own pipeline does with it — is what this benchmark measures
    and what no other one does.
    """
    models = sorted(configured["models"], key=lambda entry: entry["slug"])
    datasets = sorted(configured["datasets"], key=lambda entry: entry["slug"])
    yield "## 1. What this benchmark asks"
    yield ""
    yield (
        "Whether a model's judgement of a photograph matches **what an expert recorded about that "
        "photograph**. The reference is a human grade published with the dataset; the score says "
        "how far the software is from it. Comparing the models with each other is a second, "
        "weaker question, and it is there to raise suspicions about the reference rather than to "
        "rank the software."
    )
    yield ""
    yield "## 2. The models"
    yield ""
    yield "| Model | Pinned at | Grid it reads | Grid the network sees | Ensemble | Emits |"
    yield "| --- | --- | --- | --- | --- | --- |"
    for entry in models:
        slug, declared = entry["slug"], entry["declared"]
        yield (
            f"| [{slug}](../models/{slug}.md) | {report.pin(declared.get('upstream', {}))} | "
            f"{declared['grid']}² | {declared['network_grid']}² | "
            f"{declared.get('ensemble', '—')} | {declared.get('grades', '—')} |"
        )
    for model, why in sorted(missing_models.items()):
        yield f"| [{model}](../models/{model}.md) | **not measured** — {why} | — | — | — | — |"
    yield ""
    yield (
        "A model named here that has no adapter is **declared, not forgotten**: the benchmark asks "
        "for it, and the run says so every time until somebody writes it."
    )
    yield ""
    yield "### 2.1 What each model's own project does with its answer"
    yield ""
    yield (
        "A grade is not a decision. Which photographs reach a segmentation model is decided by a "
        "rule belonging to the **pipeline** rather than to the model, and sometimes by a rule that "
        "overrides the model's own verdict. Each adapter declares the rule its project applies, "
        "and the `carried_by_its_pipeline` column of the evidence records what that rule did to "
        "each photograph."
    )
    yield ""
    for entry in models:
        yield f"- **{entry['slug']}** — {entry['declared'].get('gate', 'not declared')}"
    yield ""
    yield "## 3. The datasets"
    yield ""
    yield "| Dataset | Photographs | Reference | Black canvas | Excluded, and why |"
    yield "| --- | --- | --- | --- | --- |"
    for entry in datasets:
        slug = entry["slug"]
        yield (
            f"| [{slug}](../datasets/{slug}.md) | {entry['total']} | "
            f"{', '.join(entry.get('grade_source') or ['—'])} | "
            f"{report.number(entry.get('padding'))} | {report.excluded(entry['excluded'])} |"
        )
    for dataset, why in sorted(missing_datasets.items()):
        yield f"| [{dataset}](../datasets/{dataset}.md) | **not measured** — {why} | — | — | — |"
    yield ""
    yield (
        "**Reference** says where the grade came from. `published` is the dataset's own verdict; "
        "`derived` is this repository's, computed from components the dataset did publish; "
        "`assumed` is this repository's supposition that a curated dataset is all sound, which "
        "means that dataset contains no bad photographs by construction and no ranking metric is "
        "defined on it."
    )
    yield ""
    yield (
        "**Black canvas** is the share of the square the store built that is not photograph. A "
        "fundus cut off at top and bottom leaves bands there, and a model judges the square it is "
        "handed."
    )
    yield ""
    yield "## 4. What is excluded, and by which rule"
    yield ""
    yield (
        "- **Below the size floor** — a photograph whose field of view is under 512 pixels, "
        "measured on the field's own size rather than the frame's.\n"
        "- **A finding recorded against the image** — anything in `src/datasets/exclusions/`, so "
        "that a finding survives deleting and rebuilding a store.\n"
        "- **No reference to score against** — a photograph the dataset published but never "
        "graded. It is not a failure of the model and is never counted as one.\n"
        "- **Excluded whole** — a dataset whose images are crops rather than photographs. No size "
        "floor catches that, because a crop can be large."
    )
    yield ""
    yield (
        "These are **ours**: the benchmark would not ask. A model's own refusal to answer is "
        "`declined`, which is a different statement, and the two are never added together."
    )
    yield ""


def index_section(records: list[dict[str, object]], results: Path) -> Iterable[str]:
    """This benchmark's entry in the index: one row per model, pooled, and where to start."""
    pooled = _pooled(records, results)
    measured = sorted({record["dataset"] for record in records if _has_two_classes(record)})
    assumed = sorted({record["dataset"] for record in records} - set(measured))

    yield (
        f"Measured on **{report.datasets_of(records)}**. **Accuracy and κ are read together**: "
        f"accuracy flatters a model on a dataset where one class dominates, and Cohen's κ is what "
        f"is left after chance agreement is taken out. Where they disagree, believe κ."
    )
    yield ""
    if assumed:
        yield (
            f"The pooled figures cover **{', '.join(measured)}**, whose readers used more than one "
            f"grade, and the Photographs column counts those. {', '.join(assumed)} is left out of "
            f"them: every photograph in it is assumed sound, so there is nothing to be right "
            f"about — what a model does there is a keep-rate, in its own column."
        )
        yield ""
    yield (
        "Each figure is computed over all those photographs **at once** rather than averaged over "
        "the datasets, which is the harder test: a model whose scores mean different things on "
        "different cameras loses here and not there."
    )
    yield ""
    yield (
        "| Model | Photographs | Coverage | Accuracy | Cohen's κ | ROC AUC | "
        + (f"{assumed[0].upper()} kept | " if assumed else "")
        + "Seconds each | Marked |"
    )
    yield "| --- | --- | --- | --- | --- | --- | " + ("--- | " if assumed else "") + "--- | --- |"
    for model, found in sorted(pooled.items(), key=lambda pair: -(pair[1]["kappa"] or -1)):
        yield (
            f"| [{model}](models/{model}.md) | {found['photographs']:,} | "
            f"{report.number(found['coverage'])} | {report.number(found['accuracy'])} | "
            f"{report.number(found['kappa'])} | {report.number(found['roc_auc'])} | "
            + (f"{report.number(found['kept_where_assumed'])} | " if assumed else "")
            + f"{report.number(found['seconds'])} | {report.mark_of(model, records)} |"
        )
    yield ""
    left = report.unfinished(records)
    if left:
        yield left
        yield ""
    yield from _where_to_start(pooled)


def _has_two_classes(record: dict[str, object]) -> bool:
    """Whether this dataset's readers used more than one grade, so agreement can be scored."""
    return record["summary"].get("gradeable", {}).get("kappa") is not None


def _pooled(records: list[dict[str, object]], results: Path) -> dict[str, dict[str, object]]:
    """Every model's answers over every dataset at once, scored as one.

    The pooling is done on the **photographs**, not on the per-dataset scores: κ over a pool is not
    the average of the κ of its parts, and an index that disagreed with its own results page would
    be worse than no index. So the evidence is read back and scored by the same function the run
    used. Where a result's evidence cannot be read that way, its own stored scores stand in, and
    what that costs is said in :func:`_stated`.
    """
    found: dict[str, dict[str, object]] = {}
    for model in sorted({str(record["model"]) for record in records}):
        mine = [record for record in records if record["model"] == model]
        truth: dict[str, str] = {}
        grades, seconds, keeps, stated = [], [], [], []
        for record in mine:
            dataset = str(record["dataset"])
            summary = record["summary"]
            taken = summary.get("seconds_per_photograph")
            if taken is not None:
                seconds.append(float(taken))
            if not _has_two_classes(record):
                keeps.append(summary.get("gradeable", {}).get("kept_of_worth_measuring"))
                continue
            rows = runs.rows(results, NAME, model, dataset)
            if rows and all({"grade", "outcome"} <= set(row) for row in rows):
                for row in rows:
                    named = {**row, "key": f"{dataset}/{row['key']}"}
                    truth[named["key"]] = named["grade"]
                    grades.append(scoring.restored(named))
            else:
                stated.append(summary)
        scored = scoring.summarise(truth, grades) if truth else _stated(stated)
        level = scored.get("gradeable", {})
        keeps = [value for value in keeps if value is not None]
        found[model] = {
            # The photographs the pooled figures are of, which is not every photograph the model
            # was given: a dataset with nothing to be right about is counted in its own column.
            "photographs": len(truth) or sum(summary.get("processed", 0) for summary in stated),
            "coverage": scored.get("coverage"),
            "accuracy": level.get("accuracy"),
            "kappa": level.get("kappa"),
            "roc_auc": level.get("roc_auc"),
            "kept_of_worth_measuring": level.get("kept_of_worth_measuring"),
            "discarded_of_not_worth": level.get("discarded_of_not_worth"),
            "kept_where_assumed": sum(keeps) / len(keeps) if keeps else None,
            "seconds": sum(seconds) / len(seconds) if seconds else None,
        }
    return found


def _stated(summaries: list[dict[str, object]]) -> dict[str, object]:
    """What the stored results say about themselves, for evidence that cannot be pooled.

    An average of κ is not the κ of the pool, so this is a fallback rather than an equivalent: it
    is exact for one dataset and an approximation for several, which is why the evidence is read
    whenever it can be.
    """
    if not summaries:
        return {}

    def across(name: str) -> float | None:
        values = [
            summary.get("gradeable", {}).get(name)
            for summary in summaries
            if summary.get("gradeable", {}).get(name) is not None
        ]
        return sum(values) / len(values) if values else None

    covered = [summary["coverage"] for summary in summaries if summary.get("coverage") is not None]
    return {
        "coverage": sum(covered) / len(covered) if covered else None,
        "gradeable": {
            name: across(name)
            for name in (
                "accuracy",
                "kappa",
                "roc_auc",
                "kept_of_worth_measuring",
                "discarded_of_not_worth",
            )
        },
    }


def _where_to_start(pooled: dict[str, dict[str, object]]) -> Iterable[str]:
    """Which model to reach for, and at which question — because they are not the same question.

    This is computed from the stored results rather than argued: the argument, with its caveats, is
    on the results page, and this paragraph exists to point a reader at it.
    """
    agreeing = [name for name in pooled if pooled[name]["kappa"] is not None]
    if not agreeing:
        return
    agreeing.sort(key=lambda name: -pooled[name]["kappa"])
    best = agreeing[0]
    ranking = sorted(
        (name for name in pooled if pooled[name]["roc_auc"] is not None),
        key=lambda name: -pooled[name]["roc_auc"],
    )

    yield "**Where to start.**"
    yield ""
    line = (
        f"- **As it ships**, agreeing with the readers at its own published threshold: "
        f"**{best}** (κ {pooled[best]['kappa']:.3f})."
    )
    if len(agreeing) > 1:
        second = agreeing[1]
        margin = pooled[best]["kappa"] - pooled[second]["kappa"]
        line += (
            f" **{second}** is {margin:.3f} behind (κ {pooled[second]['kappa']:.3f}), which is "
            f"{'close enough that the choice is about which mistake you would rather make' if margin < 0.02 else 'a real gap'}."
        )
    yield line
    if ranking:
        first = ranking[0]
        line = (
            f"- **At ordering photographs**, which is what matters if you will set your own "
            f"threshold rather than take the one it ships with: **{first}** "
            f"(ROC AUC {pooled[first]['roc_auc']:.3f})"
        )
        if len(ranking) > 1:
            runner = ranking[1]
            gap = pooled[first]["roc_auc"] - pooled[runner]["roc_auc"]
            line += f", with **{runner}** at {pooled[runner]['roc_auc']:.3f}" + (
                " — too close to order by." if gap < 0.01 else "."
            )
        else:
            line += "."
        yield line
        if first != best:
            kept = pooled[first]["kept_of_worth_measuring"]
            yield (
                f"- **Those are different models, and that is the finding.** {first} separates "
                f"good photographs from bad ones better than anything else here and then gates in "
                f"the wrong place: it keeps {kept:.0%} of the photographs the readers called worth "
                f"measuring."
            )
    yield ""
    yield (
        f"Read [what came out](benchmarks/{NAME}-results.md) before acting on this: coverage, "
        f"contamination and the threshold each model happens to ship with all differ, and the "
        f"caveats are there rather than here."
    )
