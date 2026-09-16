# ABOUTME: The two documents a benchmark run generates — how it is configured, and what came out.
# ABOUTME: Written by the run rather than by hand, so they cannot drift from the numbers.

import json
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path

from models.utils.grading import GRADES

from . import contamination, runs

#: Where the generated documents live, beside the catalogues they refer to.
DIRECTORY = Path(__file__).resolve().parents[2] / "docs" / "benchmarks"

#: Every column of a quality benchmark's evidence, and what it means. The configuration page is
#: generated from this, so a column nobody explained is a column nobody can add.
QUALITY_COLUMNS = {
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


def write_results(
    benchmark: str,
    scored: list[dict[str, object]],
    evidence: dict[tuple[str, str], list[dict[str, str]]],
    missing_models: dict[str, str] | None = None,
    missing_datasets: dict[str, str] | None = None,
    results: Path = runs.RESULTS,
    into: Path = DIRECTORY,
) -> Path:
    """Write the page saying what came out, model by model.

    Built from **everything in `results/`**, not only from the run that has just finished: a run
    narrowed to one model or one dataset must not rewrite the page as though the rest had never
    been measured. The run's own entries are preferred where they overlap, because they are the
    freshest reading of the same pair.
    """
    into.mkdir(parents=True, exist_ok=True)
    path = into / f"{benchmark}-results.md"
    everything = _everything_measured(benchmark, scored, evidence, results)
    path.write_text(
        "\n".join(
            _results(benchmark, *everything, missing_models or {}, missing_datasets or {})
        )
        + "\n"
    )
    return path


def _everything_measured(
    benchmark: str,
    scored: list[dict[str, object]],
    evidence: dict[tuple[str, str], list[dict[str, str]]],
    results: Path,
) -> tuple[list[dict[str, object]], dict[tuple[str, str], list[dict[str, str]]]]:
    """Every result this benchmark holds, with the fresh ones in place of their stored copies."""
    fresh = {(entry["model"], entry["dataset"]): entry for entry in scored}
    merged = dict(fresh)
    rows = dict(evidence)
    for record in _stored(results / benchmark):
        pair = (record["model"], record["dataset"])
        if pair in merged:
            continue
        summary = record["summary"]
        merged[pair] = {
            "model": record["model"],
            "dataset": record["dataset"],
            "summary": summary,
            "counts": {
                name: summary[name]
                for name in ("processed", "total", "complete", "excluded")
                if name in summary
            },
        }
        rows[pair] = runs.rows(results, benchmark, *pair)
    return list(merged.values()), rows


def _docs(
    benchmark: str,
    configured: dict[str, object],
    missing_models: dict[str, str],
    missing_datasets: dict[str, str],
    columns: dict[str, str],
) -> Iterable[str]:
    models = sorted(configured["models"], key=lambda entry: entry["slug"])
    datasets = sorted(configured["datasets"], key=lambda entry: entry["slug"])
    yield f"# {benchmark.capitalize()} benchmark — how it is run"
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
            f"| [{slug}](../models/{slug}.md) | {_pin(declared.get('upstream', {}))} | "
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
            f"{_number(entry.get('padding'))} | {_excluded(entry['excluded'])} |"
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
    yield "## 8. The three counts every result carries"
    yield ""
    yield "| Recorded | Means |"
    yield "| --- | --- |"
    yield "| `processed` | how many photographs this model has actually scored |"
    yield "| `total` | how many the benchmark would ask about, after the exclusions of section 4 |"
    yield "| `excluded` | how many those exclusions removed, by reason |"
    yield ""
    yield (
        "`processed ≤ total`, and `total + excluded` is what the store holds: a photograph is "
        "either one the benchmark asks about or one it excluded, never both and never neither."
    )
    yield ""
    yield "---"
    yield ""
    yield f"**Generated by `python -m benchmarks --benchmark {benchmark}` on:** {_today()}"


def _results(
    benchmark: str,
    scored: list[dict[str, object]],
    evidence: dict[tuple[str, str], list[dict[str, str]]],
    missing_models: dict[str, str],
    missing_datasets: dict[str, str],
) -> Iterable[str]:
    models = sorted({entry["model"] for entry in scored})
    datasets = sorted({entry["dataset"] for entry in scored})
    partial = [entry for entry in scored if not entry["counts"]["complete"]]

    yield f"# {benchmark.capitalize()} benchmark — results"
    yield ""
    yield (
        "What each model said about photographs an expert had already graded, and how far apart "
        "the two were. Every number comes from `results/`, and this page is generated by the run. "
        f"How the benchmark is configured is a separate page: [{benchmark}-docs.md]"
        f"({benchmark}-docs.md)."
    )
    yield ""
    yield (
        f"**{len(models)} of {len(models) + len(missing_models)} declared models** and "
        f"**{len(datasets)} of {len(datasets) + len(missing_datasets)} declared datasets** took "
        "part in this run."
        + (
            ""
            if not (missing_models or missing_datasets)
            else " What did not: "
            + "; ".join(
                f"{name} ({why})"
                for name, why in sorted({**missing_models, **missing_datasets}.items())
            )
            + "."
        )
    )
    if partial:
        yield ""
        yield (
            "**This run is not complete.** "
            + "; ".join(
                f"{entry['model']} on {entry['dataset']}: "
                f"{entry['counts']['processed']} of {entry['counts']['total']}"
                for entry in partial
            )
            + ". A sampled result is a run that has not finished, not a smaller measurement."
        )
    yield ""
    yield "## 1. Model against the experts, dataset by dataset"
    yield ""
    yield (
        "The primary question: how often each model agreed with the grade a dataset's own readers "
        "gave. Accuracy depends on where a model's threshold sits; the area under the ROC curve "
        "does not, and is the fairer comparison between models whose thresholds were set on "
        "different data."
    )
    yield ""
    yield "| Model | Dataset | Photographs | Coverage | Accuracy | Cohen's κ | ROC AUC | Marked |"
    yield "| --- | --- | --- | --- | --- | --- | --- | --- |"
    for entry in sorted(scored, key=lambda entry: (entry["model"], entry["dataset"])):
        level = entry["summary"]["gradeable"]
        counts = entry["counts"]
        yield (
            f"| {entry['model']} | {entry['dataset']} | "
            f"{counts['processed']}{'' if counts['complete'] else ' of ' + str(counts['total'])} | "
            f"{_number(entry['summary']['coverage'])} | {_number(level['accuracy'])} | "
            f"{_number(level['kappa'])} | {_number(level['roc_auc'])} | "
            f"{contamination.mark(entry['model'], entry['dataset'])} |"
        )
    yield ""
    yield (
        "**Accuracy flatters a model on a dataset where one class dominates.** A grader that keeps "
        "everything scores well on a collection that is mostly gradeable while agreeing with "
        "nobody about anything. **Cohen's κ** is what is left after chance agreement is taken out, "
        "so the two together say what neither says alone, and a wide gap between them is the "
        "reading. κ is undefined where a reference has only one class — a dash, never a zero."
    )
    yield ""
    yield "## 2. Coverage: what each model was willing to answer"
    yield ""
    yield (
        "A model that declines a photograph has not got it wrong, and one that crashes on a "
        "photograph has not judged it. Both are counted here and neither is folded into the "
        "accuracy above."
    )
    yield ""
    yield "| Model | Dataset | Graded | Declined | Failed |"
    yield "| --- | --- | --- | --- | --- |"
    for entry in sorted(scored, key=lambda entry: (entry["model"], entry["dataset"])):
        summary = entry["summary"]
        yield (
            f"| {entry['model']} | {entry['dataset']} | {summary['graded']} | "
            f"{summary['declined']} | {summary['failed']} |"
        )
    yield ""
    if not any(entry["summary"]["declined"] for entry in scored):
        yield (
            "**No model declined a photograph in this run.** Declining is something a model does "
            "on its own judgement; where a pipeline refuses a photograph, that refusal belongs to "
            "the pipeline, and this benchmark runs the models without the pipelines around them."
        )
        yield ""
    yield "## 3. The detail, by subset and split"
    yield ""
    yield (
        "The same photographs, grouped as the dataset groups them. Where a model trained on one "
        "split of a dataset, the splits carry different marks and only this table can be read."
    )
    yield ""
    yield (
        "| Model | Dataset / subset / split | Photographs | Accuracy | Cohen's κ | ROC AUC | "
        "Marked |"
    )
    yield "| --- | --- | --- | --- | --- | --- | --- |"
    for model in models:
        for dataset in datasets:
            rows = evidence.get((model, dataset), [])
            for (subset, split), group in _grouped(rows):
                yield (
                    f"| {model} | {dataset} / {subset} / {split} | {len(group)} | "
                    f"{_number(_accuracy(group))} | {_number(_kappa(group))} | "
                    f"{_number(_auc(group))} | "
                    f"{contamination.mark(model, dataset, split)} |"
                )
    yield ""
    for model in models:
        for dataset in datasets:
            splits = sorted({row["split"] for row in evidence.get((model, dataset), [])})
            if contamination.splits_disagree(model, dataset, splits):
                yield (
                    f"**{model} on {dataset}: the splits carry different marks**, so the summary "
                    "row in section 1 is not a result — read the rows above."
                )
    yield ""
    yield "## 4. What these numbers do not say"
    yield ""
    yield (
        "Every result carries a mark. `out-of-sample` means the model's page does not name this "
        "dataset among its training data; `unknown` means nobody published what it trained on, and "
        "is never the same statement as `out-of-sample`."
    )
    yield ""
    for model in models:
        marks = sorted(
            {
                contamination.mark(model, entry["dataset"])
                for entry in scored
                if entry["model"] == model
            }
        )
        yield f"- **{model}** — {', '.join(marks)}"
    yield ""
    yield (
        "And a model agreeing with another model is not evidence that either agrees with an "
        "expert. Where two models disagree on a photograph the readers also disagreed about, the "
        "suspicion belongs on the annotation as much as on the software."
    )
    yield ""
    yield "---"
    yield ""
    yield f"**Generated by `python -m benchmarks --benchmark {benchmark}` on:** {_today()}"


def _grouped(rows: list[dict[str, str]]) -> Iterable[tuple[tuple[str, str], list[dict[str, str]]]]:
    """The evidence, in the groups the dataset itself defines."""
    groups: dict[tuple[str, str], list[dict[str, str]]] = {}
    for row in rows:
        groups.setdefault((row.get("subset", ""), row.get("split", "")), []).append(row)
    return sorted(groups.items())


def _worth(row: dict[str, str]) -> bool:
    return row["grade"] in {grade for grade in GRADES if grade != "bad"}


def _said(row: dict[str, str]) -> bool:
    if row.get("verdict"):
        return _worth({"grade": row["verdict"]})
    return float(row["gradeable"] or 0) >= 0.5


def _accuracy(rows: list[dict[str, str]]) -> float | None:
    graded = [row for row in rows if row.get("outcome") == "graded"]
    if not graded:
        return None
    return sum(_worth(row) == _said(row) for row in graded) / len(graded)


def _kappa(rows: list[dict[str, str]]) -> float | None:
    """Agreement beyond chance, from the two-by-two table these rows make.

    Undefined where the reference has only one class: there is no chance agreement to take out,
    and the formula collapses to zero, which would read as disagreement rather than as the absence
    of a question.
    """
    graded = [row for row in rows if row.get("outcome") == "graded"]
    if not graded:
        return None
    worth = [row for row in graded if _worth(row)]
    against = [row for row in graded if not _worth(row)]
    if not worth or not against:
        return None
    kept = [row for row in graded if _said(row)]
    total = len(graded)
    agreed = sum(_worth(row) == _said(row) for row in graded) / total
    by_chance = (len(worth) * len(kept) + len(against) * (total - len(kept))) / total**2
    return (agreed - by_chance) / (1 - by_chance) if by_chance < 1 else None


def _auc(rows: list[dict[str, str]]) -> float | None:
    """The area under the ROC curve, computed here so the report can group as it likes."""
    graded = [row for row in rows if row.get("outcome") == "graded" and row.get("gradeable")]
    worth = [row for row in graded if _worth(row)]
    against = [row for row in graded if not _worth(row)]
    if not worth or not against:
        return None
    ordered = sorted(graded, key=lambda row: float(row["gradeable"]))
    ranks = {id(row): index + 1 for index, row in enumerate(ordered)}
    total = sum(ranks[id(row)] for row in worth)
    return (total - len(worth) * (len(worth) + 1) / 2) / (len(worth) * len(against))


def _excluded(excluded: dict[str, int]) -> str:
    if not excluded:
        return "none"
    return "; ".join(f"{count} {reason}" for reason, count in sorted(excluded.items()))


def _first(scored: list[dict[str, object]], model: str = "", dataset: str = "") -> dict:
    for entry in scored:
        if (not model or entry["model"] == model) and (not dataset or entry["dataset"] == dataset):
            return entry
    raise LookupError(f"nothing scored for {model or dataset}")


def _pin(upstream: dict[str, object]) -> str:
    commit = str(upstream.get("commit", ""))
    return f"`{commit[:8]}`" if commit else str(upstream.get("version", "—"))


def _number(value: float | None) -> str:
    return "—" if value is None else f"{value:.3f}"


def _today() -> str:
    """The date a page was generated, in UTC, so two machines date the same run alike."""
    return datetime.now(UTC).date().isoformat()


def write_index(results: Path = runs.RESULTS, into: Path = DIRECTORY.parent) -> Path:
    """Write `docs/BENCHMARKS.md`, one section per benchmark that has results on disk."""
    into.mkdir(parents=True, exist_ok=True)
    path = into / "BENCHMARKS.md"
    path.write_text("\n".join(_index(results)) + "\n")
    return path


def _index(results: Path) -> Iterable[str]:
    yield "# Benchmarks"
    yield ""
    yield (
        "What this repository measured against what experts annotated, on the same images and on "
        "the same terms. Each section is one benchmark; the pages it links to say how it was run "
        "and what came out, and `results/` holds the score of every photograph behind every "
        "number. This file is generated by the runs."
    )
    yield ""
    yield (
        "**Read a row, not a column.** A result marked `in-sample` or `unknown` is not comparable "
        "with one marked `out-of-sample`, and a model agreeing with another model is not evidence "
        "that either agrees with an expert."
    )
    yield ""
    yield (
        "**Accuracy and κ are read together.** Accuracy flatters a model on a dataset where one "
        "class dominates; Cohen's κ is what is left after chance agreement is taken out. A dash "
        "means the metric has nothing to measure — a dataset whose reference has only one class "
        "supports neither κ nor a ranking — and a photograph count of the form *n of m* means a "
        "run that has not finished."
    )
    for benchmark in sorted(path.name for path in results.glob("*") if path.is_dir()):
        yield ""
        yield f"## {benchmark.capitalize()}"
        yield ""
        yield (
            f"[How it is run](benchmarks/{benchmark}-docs.md) · "
            f"[What came out](benchmarks/{benchmark}-results.md)"
        )
        yield ""
        yield (
            "| Model | Dataset | Photographs | Coverage | Accuracy | Cohen's κ | ROC AUC | Marked |"
        )
        yield "| --- | --- | --- | --- | --- | --- | --- | --- |"
        for record in _stored(results / benchmark):
            summary = record["summary"]
            level = summary.get("gradeable", {})
            done = summary.get("processed", "—")
            if not summary.get("complete", True):
                done = f"{done} of {summary.get('total', '—')}"
            yield (
                f"| [{record['model']}](models/{record['model']}.md) | {record['dataset']} | "
                f"{done} | {_number(summary.get('coverage'))} | "
                f"{_number(level.get('accuracy'))} | {_number(level.get('kappa'))} | "
                f"{_number(level.get('roc_auc'))} | "
                f"{contamination.mark(record['model'], record['dataset'])} |"
            )
        yield ""
        yield from _where_to_start(list(_stored(results / benchmark)))
    yield ""
    yield "---"
    yield ""
    yield f"**Generated:** {_today()}"


def _where_to_start(records: list[dict[str, object]]) -> Iterable[str]:
    """Which models lead, at which question — because the answer is not the same question twice.

    This is not a ranking. A model is best *at something*, and here the two somethings disagree
    with each other: the model that orders photographs best is the one that gates worst, because
    its published threshold sits in the wrong place. Naming the leaders without naming what they
    lead at would hide exactly that.
    """
    by_model: dict[str, list[dict[str, object]]] = {}
    for record in records:
        level = record["summary"].get("gradeable", {})
        if level.get("kappa") is not None:
            by_model.setdefault(record["model"], []).append(level)
    if len(by_model) < 2:
        return

    def average(model: str, metric: str) -> float:
        levels = by_model[model]
        return sum(level[metric] for level in levels) / len(levels)

    agreeing = sorted(by_model, key=lambda model: -average(model, "kappa"))
    ranking = sorted(by_model, key=lambda model: -average(model, "roc_auc"))
    marks = {
        model: contamination.mark(model, record["dataset"])
        for record in records
        for model in [record["model"]]
    }

    yield "### Where to start, and what the choice turns on"
    yield ""
    yield (
        "Two questions, and they do not have the same answer. Averaged over the datasets whose "
        "reference uses both classes:"
    )
    yield ""
    yield (
        f"- **As they ship**, agreeing with the readers at their own published threshold: "
        f"**{agreeing[0]}** (κ {average(agreeing[0], 'kappa'):.2f}) and **{agreeing[1]}** "
        f"(κ {average(agreeing[1], 'kappa'):.2f})."
        + (
            f" Note that {agreeing[0]} carries `{marks[agreeing[0]]}`: nobody published what it "
            f"trained on, so its lead cannot be called clean."
            if marks.get(agreeing[0]) == contamination.UNKNOWN
            else ""
        )
    )
    yield (
        f"- **At ordering photographs**, which is what matters if you will set your own "
        f"threshold: **{ranking[0]}** (ROC AUC {average(ranking[0], 'roc_auc'):.3f}) and "
        f"**{ranking[1]}** ({average(ranking[1], 'roc_auc'):.3f})."
    )
    yield ""
    if ranking[0] != agreeing[0]:
        kept = average(ranking[0], "kept_of_worth_measuring")
        yield (
            f"**Those are different models, and that is the finding.** {ranking[0]} separates good "
            f"photographs from bad ones better than anything else here and then gates on a "
            f"threshold in the wrong place: it keeps only {kept:.0%} of the photographs the "
            f"readers called worth measuring. Re-fit that threshold on your own images and it "
            f"becomes a different proposition; take it as shipped and it throws away "
            f"{1 - kept:.0%} of what your own readers would have kept."
        )
        yield ""
    yield (
        "Neither line is a verdict on the models. Coverage, contamination and the threshold each "
        "model happens to ship with all differ, and a dataset with an assumed reference measures "
        "what a model discards rather than whether it is right. Read the rows."
    )


def _stored(directory: Path) -> Iterable[dict[str, object]]:
    for path in sorted(directory.glob("*/*.json")):
        yield json.loads(path.read_text())
