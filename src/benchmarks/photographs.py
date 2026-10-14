# ABOUTME: What the benchmarks run on photographs report about themselves in common: the flags they
# ABOUTME: honour, the counts they keep, and how a declared model or dataset is described.

from collections.abc import Callable

from .loaders.base import FLOOR

#: The counts every photograph benchmark's result carries, and what each answers.
COUNTS = {
    "processed": "how many photographs this model has actually scored",
    "total": "how many the benchmark would ask about, after the exclusions",
    "excluded": "how many those exclusions removed, by reason; `total + excluded` is what the "
    "store holds",
    "seconds_per_photograph": "how long the model's own call took per photograph, on the device "
    "the result names — not part of the fingerprint",
    "timed_photographs": "how many photographs that timing covers",
}

#: The exclusion rules every photograph benchmark applies, before its own.
FLOOR_RULE = (
    f"a photograph whose field of view is under {FLOOR} pixels, measured on the field's own size "
    f"rather than the frame's"
)
FINDING_RULE = (
    "anything in `src/datasets/exclusions/`, so that a finding survives deleting and rebuilding a "
    "store"
)
CROP_RULE = (
    "a dataset whose images are crops rather than photographs. No size floor catches that, "
    "because a crop can be large"
)


def subjects(
    order: list[str],
    found: list,
    missing: dict[str, str],
    fields: list[str],
    facts: Callable[[dict[str, object]], dict[str, object]],
    note: Callable[[dict[str, object]], str] | None = None,
) -> dict[str, object]:
    """Every declared model, in the order the benchmark declares them, present or not."""
    declared = {adapter.slug: adapter.declare() for adapter in found}
    return {
        "label": "model",
        "fields": fields,
        "declared": [
            {
                "slug": slug,
                "page": f"../models/{slug}.md",
                "facts": facts(declared[slug]) if slug in declared else {},
                "ran": slug in declared,
                "why_not": missing.get(slug),
                **({"note": note(declared[slug])} if note and slug in declared else {}),
            }
            for slug in order
        ],
    }


#: Stores whose catalogue page is not their slug: AV-WIDE is catalogued as a layer of REYIA.
PAGES = {"av-wide": "reyia"}


def page(slug: str) -> str:
    """The catalogue page of a dataset's store, as a path from `docs/`."""
    return f"datasets/{PAGES.get(slug, slug)}.md"


def material(
    order: list[str],
    configured: list[dict[str, object]],
    missing: dict[str, str],
    fields: list[str],
    facts: Callable[[dict[str, object]], dict[str, object]],
    wanted: tuple = (),
) -> dict[str, object]:
    """Every declared dataset, read from the stores on this machine, built or not."""
    described = {entry["slug"]: entry for entry in configured}
    return {
        "label": "dataset",
        "fields": fields,
        "declared": [
            {
                "slug": slug,
                "page": f"../{page(slug)}",
                "facts": facts(described[slug]) if slug in described else {},
                "available": slug in described,
                "why_not": missing.get(slug),
            }
            for slug in order
        ],
        "wanted": [{"slug": slug, "settles": why, "cost": cost} for slug, why, cost in wanted],
    }


def fingerprint(module, fingerprinted: tuple[str, ...], keeps_masks: bool) -> list[str]:
    """What a stored result is invalidated by, as the run actually hashes it."""
    said = [
        f"the facts each model declares that bear on its numbers: {', '.join(fingerprinted)}",
        "the sha256 of the weights actually loaded",
        "the store's slug and builder version",
        f"this benchmark's name, `VERSION` ({module.VERSION}) and size floor ({FLOOR} pixels)",
    ]
    if keeps_masks:
        said.append(
            f"the first three alone also name the masks kept under "
            f"`.atlas_runs/{module.NAME}/<model>/<dataset>/`, so `--rescore` measures them afresh "
            f"without running a model, and a mask its model no longer agrees with is drawn again"
        )
    return said


def running(module, rescores: bool) -> dict[str, object]:
    """The command, and only the flags this benchmark honours."""
    name = module.NAME
    flags = {
        "--model": "one model, or several separated by commas",
        "--dataset": "one dataset, or several separated by commas; one of each re-measures a pair",
        "--device": "cuda, mps or cpu; the fastest available by default",
        "--batch": f"how many photographs go to the model at once; {module.BATCH} by default",
        "--max-samples": "score at most the first N photographs of each dataset, for "
        "development; a sampled result says it is not complete, and a later run finishes it",
        "--random-samples": "choose those photographs at random rather than first",
        "--seed": "the seed a random sample uses, recorded in the run",
        "--data-root": "read the stores from somewhere other than `.atlas_data/`",
        "--force": "discard what is stored and measure it all again",
    }
    if rescores:
        flags["--rescore"] = (
            "measure the kept masks afresh without running any model — for a new measurement of "
            "the same masks"
        )
    flags |= {
        "--no-report": "skip refreshing `docs/BENCHMARKS.md` after the run",
        "--config": "print what this benchmark reports about itself, as JSON, measuring nothing",
        "--docs": "refresh this page from that JSON, measuring nothing",
    }
    return {
        "examples": [
            f"python -m benchmarks --benchmark {name}",
            f"python -m benchmarks --benchmark {name} --model {module.MODELS[0]} "
            f"--dataset {module.DATASETS[0]}",
            f"python -m benchmarks --benchmark {name} --max-samples 20",
            f"python -m benchmarks --benchmark {name} --docs",
        ],
        "flags": flags,
    }


def describe(module, **parts: object) -> dict[str, object]:
    """The parts every photograph benchmark reports, around the ones it supplies itself."""
    return {
        "benchmark": module.NAME,
        "title": module.TITLE,
        "version": module.VERSION,
        "asks": module.GOAL,
        "unit_of_work": {"singular": "photograph", "plural": "photographs"},
        "evidence": f"results/{module.NAME}/<model>/<dataset>.csv",
        "columns": module.COLUMNS,
        "counts": COUNTS,
        **parts,
    }
