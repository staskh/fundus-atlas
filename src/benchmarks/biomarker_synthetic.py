# ABOUTME: The synthetic biomarker benchmark: does an implementation compute the quantity it is said
# ABOUTME: to compute, measured against shapes whose values follow from geometry rather than opinion.

import json
import sys
import time
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path

from biomarkers.utils import catalogue

from . import report, runs
from .shapes import library, store

#: What this benchmark is called in a heading, where its slug does not read as English.
TITLE = "Biomarkers against arithmetic"

#: What it is called in `results/`, in `docs/benchmarks/` and in a run record. A Python module name
#: cannot carry a hyphen, so the module is `biomarker_synthetic` and `report._module` translates.
NAME = "biomarker-synthetic"
#: How close a measurement must be to what the geometry requires to be counted as agreeing. It is
#: a way of summarising many numbers in one, not a pass mark: this benchmark selects nothing.
AGREES = 0.02

#: The benchmark's own version. Changing what is measured, or how, changes this.
VERSION = 3

#: The written pages this benchmark produces, and the notebook behind each, as `(label, stem)`.
#: **One per implementation**, because each is a different piece of somebody else's code: what is
#: true of PVBM's chord-sum length says nothing about the next implementation, and one document
#: holding both would bury each under the other. A second implementation adds a pair here.
#: What this benchmark asks, in the sentences the index has room for.
GOAL = (
    "**Does a biomarker implementation compute the quantity it is said to compute?** Every other "
    "benchmark here compares software with a human judgement; this one compares it with a number "
    "derived on paper. A straight vessel has a tortuosity of exactly 1, a circular arc a curvature "
    "of exactly 1/r, and an implementation that disagrees is wrong rather than different. It "
    "selects nothing: which implementations are fit to measure a real segmentation is a judgement "
    "made by a person on this evidence."
)

#: The shapes, which play the part a dataset plays in every other benchmark.
SHAPES = tuple(library.SHAPES)

#: The implementations, by the slug of the project page each belongs to.
#:
#: **The order is lineage, not the alphabet, and the analysis reads its columns from here.** OCULAR
#: imports PVBM's tortuosity, perimeter and branching-angle helpers at runtime and measures with a
#: modified copy of its `CREVBMs`; AutoMorphalyzer and AutoMorphClass are both rewrites of
#: AutoMorph's measuring stage; VascX shares code with none of them and reimplements every
#: biomarker. So a difference between neighbours is a change somebody made on purpose, and a
#: difference across a boundary is two programs that never shared a line — which is only legible if
#: the columns stand in this order.
IMPLEMENTATIONS = ("pvbm", "ocular", "automorph", "automorphalyzer", "automorphclass", "vascx")

#: Why a declared implementation has no adapter, where the reason is worth more than "nobody wrote
#: one yet".
WHY_NOT: dict[str, str] = {}

#: The grid every shape is drawn at. One number here rather than several: the convergence study
#: that reads four resolutions belongs in the analysis, where a reader can see the trend, and a run
#: that swept them would quadruple every table for a question the notebook answers better.
SIDE = 2048

#: Microns per pixel. A synthetic shape has no camera, so this is a stated convention — but it has
#: to be stated, because Hubbard's equivalents carry constants fitted in microns.
UM_PER_PX = 5.0

#: The angles every shape is drawn at, each generated afresh in continuous coordinates rather than
#: by turning a picture. Ninety degrees is included deliberately: it is where a vessel lands back on
#: the pixel lattice, so a measurement that is unusually good or bad there is telling us about the
#: grid rather than about the retina.
ROTATIONS = (0.0, 30.0, 60.0, 90.0)

#: What an implementation declares that could change its numbers.
FINGERPRINTED = ("slug", "needs", "keys", "units")


def implementations(slugs: list[str]) -> tuple[list, dict[str, str]]:
    """The adapters that exist, and what was declared without one."""
    found, missing = [], {}
    for slug in slugs:
        try:
            found.append(catalogue.load(slug))
        except LookupError:
            missing[slug] = WHY_NOT.get(slug, "no adapter written")
    return found, missing


def _ground_truth() -> dict[str, list[str]]:
    """Which catalogued biomarkers the drawn store settles, per shape, read from the store itself.

    **The run never calls this.** It is for the page that documents the benchmark, which has to be
    able to say what can be checked — and reading the store is how a reader would find out, rather
    than rebuilding every shape and trusting that the drawing agrees with the rebuild. Where no
    store has been drawn the answer is simply empty: a configuration page is writable before the
    images exist, which is the point of writing it first.
    """
    try:
        truth = store.truth(store.STORE)
    except (FileNotFoundError, OSError):
        return {}
    settled: dict[str, list[str]] = {}
    for key, values in truth.items():
        shape = key.rsplit("-", 2)[0]
        settled.setdefault(shape, sorted(values))
    return settled


def configuration(adapters: list, shapes: list[str]) -> dict[str, object]:
    """What this run is about to do, without doing any of it."""
    described = []
    for name in shapes:
        built = library.build(name, side=SIDE, um_per_px=UM_PER_PX)
        described.append(
            {
                "slug": name,
                "total": len(ROTATIONS),
                "excluded": {},
                "classes": [
                    part
                    for part, mask in (("artery", built.artery), ("vein", built.vein))
                    if mask is not None
                ],
                "settles": sorted(_ground_truth().get(name, ())),
            }
        )
    return {
        "models": [{"slug": a.slug, "declared": a.declare()} for a in adapters],
        "datasets": described,
        "side": SIDE,
        "um_per_px": UM_PER_PX,
        "rotations": list(ROTATIONS),
    }


def run(
    adapters: list,
    shapes: list[str],
    results: Path = runs.RESULTS,
    root: Path | None = None,
    batch: int = 1,
    force: bool = False,
    record: Path | None = None,
    max_samples: int | None = None,
    random_samples: bool = False,
    seed: int = 0,
    rescore: bool = False,
) -> list[dict[str, object]]:
    """Measure every implementation on every shape, at every angle."""
    started = datetime.now(UTC)
    if not adapters or not shapes:
        raise RuntimeError("nothing to measure: no shape declared, or no implementation adapted")
    scored = []
    for adapter in adapters:
        for shape in shapes:
            scored.append(_pair(adapter, shape, results, force, max_samples))
        release = getattr(adapter, "release", None)
        if release is not None:
            release()
    _record(scored, started, record or runs.RUNS)
    return scored


def _pair(
    adapter, shape: str, results: Path, force: bool, max_samples: int | None
) -> dict[str, object]:
    """One implementation on one shape, at every angle it is asked about."""
    declared = adapter.declare()
    identity = runs.fingerprint(
        {
            "benchmark": NAME,
            "version": VERSION,
            "declared": {key: declared.get(key) for key in FINGERPRINTED},
            "code": adapter.identity(),
            # The grid, the scale and the angles all change what is measured, so a result that
            # outlived a change to any of them would be describing something else. So does the
            # drawing: a shape redrawn from different parameters is a different question, and
            # nothing else here would notice, because its grid and scale are unchanged.
            "rendering": {"side": SIDE, "um_per_px": UM_PER_PX, "rotations": list(ROTATIONS)},
            "drawing": store.digest(shape),
        }
    )
    kept = [] if force else runs.measured(results, NAME, adapter.slug, shape, identity)
    wanted = list(ROTATIONS)[: max_samples or len(ROTATIONS)]
    done = {str(row.get("rotation")) for row in kept}
    todo = [angle for angle in wanted if f"{angle:.1f}" not in done]
    if not todo:
        print(f"{adapter.slug} × {shape}: kept — nothing left to measure", flush=True)
        rows = kept
    else:
        print(f"{adapter.slug} × {shape}: {len(todo)} of {len(wanted)} angles", flush=True)
        rows = list(kept) + _measure(adapter, shape, todo)
    summary = _summarise(rows, wanted)
    runs.write(results, NAME, adapter.slug, shape, identity, summary, rows)
    return {
        "model": adapter.slug,
        "dataset": shape,
        "declared": declared,
        "fingerprint": identity,
        "counts": {
            "processed": len({str(row["rotation"]) for row in rows}),
            "total": len(wanted),
            "complete": len(rows) >= len(wanted),
            "excluded": {},
        },
        "summary": summary,
    }


def _measure(adapter, shape: str, angles: list[float]) -> list[dict[str, object]]:
    """One row per angle: what the implementation returned, beside what geometry requires."""
    rows = []
    for angle in angles:
        built = library.build(shape, side=SIDE, rotation=angle, um_per_px=UM_PER_PX)
        started = time.perf_counter()
        try:
            answered = adapter.measure(
                built.artery, built.vein, built.fov, built.disc, built.um_per_px
            )
            # What the adapter caught on its way, so an empty cell always says why it is empty.
            # Without this a defect of ours — handing PVBM 8-bit masks, which overflow on a frame
            # this size — was indistinguishable in the results from PVBM declining to answer.
            note = "; ".join(
                f"{where}: {why}" for where, why in getattr(adapter, "trouble", {}).items()
            )
        except Exception as failure:  # noqa: BLE001 — a crash is an answer about nothing
            answered, note = dict.fromkeys(adapter.keys()), repr(failure)
        taken = time.perf_counter() - started
        rows.append(_row(adapter, built, angle, answered, taken, note))
    return rows


def _row(
    adapter, built, angle: float, answered: dict, taken: float, note: str
) -> dict[str, object]:
    """What is kept about one rendering.

    The theoretical value sits **beside** the returned one rather than being subtracted from it: a
    difference is an analysis, and the analysis belongs in the notebook.
    """
    row: dict[str, object] = {
        # What was measured, named once, and spelt the way the drawn store spells it — so that a
        # row of evidence and the rendering it came from can be joined without a translation, and
        # so that the ground truth the analysis reads keys against it directly.
        "key": store.key_of(built.name, built.side, angle),
        "shape": built.name,
        "rotation": f"{angle:.1f}",
        "side": built.side,
        "um_per_px": built.um_per_px,
        # `failed` means nothing came back. A rendering whose equivalents raised while its
        # geometry was measured is a measured rendering with a note saying what it could not
        # answer — otherwise one bad column would throw away every good one beside it.
        "outcome": "measured"
        if any(value is not None for value in answered.values())
        else "failed",
        "seconds": f"{taken:.3f}",
        "note": note,
    }
    # Under the implementation's **own** column names, and with no value beside them to compare
    # against. A run records what each program said; what it should have said is in the store's
    # `ground_truth.csv`, and joining the two is the analysis's job. Keeping them apart means a run
    # cannot quietly decide what counts as agreement, and the same evidence can be re-read against
    # a corrected ground truth without measuring anything again.
    for key in adapter.keys():
        value = answered.get(key)
        row[f"said_{key}"] = "" if value is None else f"{float(value):.6f}"
    return row


def _summarise(rows: list[dict[str, object]], wanted: list[float]) -> dict[str, object]:
    """What this pair did: how much was measured, what it cost, and how far it moved when turned."""
    measured = [row for row in rows if row.get("outcome") == "measured"]
    summary: dict[str, object] = {
        "renderings": len(rows),
        "failed": len(rows) - len(measured),
        "processed": len({str(row["rotation"]) for row in rows}),
        "total": len(wanted),
        "complete": len(rows) >= len(wanted),
        "excluded": {},
        "side": SIDE,
        "um_per_px": UM_PER_PX,
    }
    taken = [float(row["seconds"]) for row in rows if row.get("seconds")]
    if taken:
        summary["seconds_per_rendering"] = sum(taken) / len(taken)
        summary["seconds_per_photograph"] = summary["seconds_per_rendering"]
        summary["timed_photographs"] = len(taken)
    return summary


def _record(scored: list[dict[str, object]], started: datetime, into: Path) -> None:
    """What ran, against what, with which pins — beside the results rather than inside them."""
    into.mkdir(parents=True, exist_ok=True)
    stamp = started.strftime("%Y-%m-%dT%H-%M-%SZ")
    directory = into / NAME / stamp
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "run.json").write_text(
        json.dumps(
            {
                "benchmark": NAME,
                "version": VERSION,
                "started": started.isoformat(),
                "side": SIDE,
                "um_per_px": UM_PER_PX,
                "rotations": list(ROTATIONS),
                "pairs": [
                    {
                        "model": entry["model"],
                        "dataset": entry["dataset"],
                        "fingerprint": entry["fingerprint"],
                        "declared": entry["declared"],
                    }
                    for entry in scored
                ],
            },
            indent=1,
            default=str,
        )
        + "\n"
    )


#: Every column of this benchmark's evidence, and what it means.
COLUMNS = {
    "key": "the rendering: the shape and the angle it was drawn at",
    "shape": "which shape was drawn — `straight`, `arc`, `spokes-macula-centred` and the rest",
    "rotation": "the angle it was drawn at, in degrees, generated afresh rather than turned",
    "side": "the grid it was drawn on, in pixels",
    "um_per_px": "the microns per pixel the shape was built with",
    "outcome": "`measured` if any quantity came back, else `failed`; `note` says what fell over",
    "seconds": "how long the implementation took over this rendering",
    "said_<key>": (
        "what the implementation returned, under **its own** column name — what its authors call "
        "that number and what a reader checking against their documentation will look for. No "
        "value to compare against sits beside it: the ground truth lives in the store's "
        "`ground_truth.csv`, the catalogued name each column answers to is in the adapter's "
        "declaration, and joining the three is the analysis's work rather than the run's"
    ),
    "note": "what an implementation failed with",
}


def config() -> dict[str, object]:
    """What this benchmark reports about itself, as data rather than prose.

    Everything here is known from the declarations: no result is read and nothing is measured, so
    it answers in seconds and a narrowed invocation cannot change it. The `document-benchmark`
    skill is the authority on the shape.
    """
    from biomarkers import canonical

    adapters, missing = implementations(list(IMPLEMENTATIONS))
    declared = {adapter.slug: adapter.declare() for adapter in adapters}
    # Built once, at the benchmark's own grid, and used for both the shape table and the
    # vocabulary below: a smaller grid cannot hold the ring the equivalents are measured over.
    settles = _ground_truth()
    # A canonical name is either a template applying to several structures or a literal naming one
    # — `avr/knudtson/both` is its own name rather than a `{s}` form — so both are recorded.
    pinned: set[str] = set()
    for names in settles.values():
        for name in names:
            head, _structure = name.rsplit("/", 1)
            pinned.update({f"{head}/{{s}}", name})
    return {
        "benchmark": NAME,
        "title": TITLE,
        "version": VERSION,
        "asks": GOAL,
        # A row here is a drawing, not a photograph. Every generated sentence uses this word.
        "unit_of_work": {"singular": "rendering", "plural": "renderings"},
        "subjects": {
            "label": "implementation",
            "declared": [
                {
                    "slug": slug,
                    # An implementation's slug need not name its catalogue page — OCULAR's page
                    # is `ocularnet.md` — so the adapter says, and the slug is only the fallback.
                    "page": f"../projects/{declared.get(slug, {}).get('page', slug)}.md",
                    "pinned": f"`{str(declared[slug]['upstream'].get('commit', ''))[:7]}`"
                    if slug in declared
                    else "—",
                    "columns": len(declared[slug]["keys"]) if slug in declared else "—",
                    "ran": slug in declared,
                    "why_not": missing.get(slug),
                }
                for slug in IMPLEMENTATIONS
            ],
        },
        "material": {
            "label": "shape",
            "describes": "What its geometry settles",
            "declared": [
                {
                    "slug": name,
                    "detail": f"{len(settles.get(name, ()))} quantities with a known value",
                    "available": True,
                }
                for name in SHAPES
            ],
        },
        # What a stored result is invalidated by — and nothing else. This benchmark loads no
        # weights, applies no patches and reads no dataset store, so none of those appear.
        "fingerprint": [
            "this benchmark's name and `VERSION`",
            "a sha256 of the masks this shape is drawn as, so a redrawing re-measures it",
            f"the facts each implementation declares that bear on its numbers: {', '.join(FINGERPRINTED)}",
            "the pinned commit of the code that will run, as the adapter reports it",
            f"the rendering: a {SIDE}px grid at {UM_PER_PX:g} µm per pixel, drawn at "
            f"{', '.join(f'{angle:g}°' for angle in ROTATIONS)}",
        ],
        "running": {
            "examples": [
                f"python -m benchmarks --benchmark {NAME}",
                f"python -m benchmarks --benchmark {NAME} --model pvbm --dataset straight",
                f"python -m benchmarks --benchmark {NAME} --docs",
            ],
            # Only what this benchmark honours. It takes `--random-samples` and `--seed` from the
            # shared command line and ignores both, so neither is listed.
            "flags": {
                "--model": "one implementation, or several separated by commas",
                "--dataset": "one shape, or several separated by commas",
                "--max-samples": "draw only the first N of the four angles, for a development run",
                "--force": "discard what is stored and measure it all again",
                "--docs": "refresh this page from the declarations, measuring nothing",
            },
        },
        "evidence": f"results/{NAME}/<implementation>/<shape>.csv",
        "columns": COLUMNS,
        "counts": {
            "processed": "how many angles of this shape the implementation has measured",
            "total": "how many it was asked for",
            "complete": "whether those are all of them",
            "seconds_per_rendering": "how long the implementation took, on the device named beside it",
        },
        # The whole vocabulary an implementation may answer under, whether or not a shape here
        # pins a value for it — a name nothing settles is a gap in the shapes, and saying so is
        # more useful than leaving it off the page.
        "biomarkers": [
            {
                "name": template.replace("{s}", "<structure>"),
                "biomarker": template.split("/")[0],
                "variant": template.split("/")[1],
                "means": means,
                "settled": template in pinned,
            }
            for template, means in canonical.NAMES.items()
        ],
        "structures": list(canonical.STRUCTURES),
    }


def docs_sections(
    configured: dict[str, object],
    missing_models: dict[str, str] | None = None,
    missing_datasets: dict[str, str] | None = None,
) -> Iterable[str]:
    """What only this benchmark's configuration page says."""
    yield "## 1. What this benchmark asks"
    yield ""
    yield GOAL
    yield ""
    yield (
        f"Every shape is drawn on a **{configured['side']}²** grid at "
        f"**{configured['um_per_px']} µm per pixel**, at "
        f"{', '.join(f'{angle:.0f}°' for angle in configured['rotations'])}. Each angle is a fresh "
        f"rendering from continuous coordinates, never a turned picture: resampling a structure a "
        f"few pixels wide destroys it, and a rotated bitmap would measure the resampler."
    )
    yield ""
    yield "## 2. The implementations"
    yield ""
    yield "| Implementation | Pinned at | Needs | Claims invariance under | Columns |"
    yield "| --- | --- | --- | --- | --- |"
    for entry in configured["models"]:
        declared = entry["declared"]
        upstream = declared.get("upstream", {})
        pin = str(upstream.get("commit") or upstream.get("version") or "—")[:12]
        yield (
            f"| [{entry['slug']}](../projects/{entry['slug']}.md) | `{pin}` | "
            f"{', '.join(declared.get('needs', []))} | "
            f"{', '.join(declared.get('invariant', [])) or '—'} | "
            f"{len(declared.get('keys', []))} |"
        )
    for slug, why in sorted((missing_models or {}).items()):
        yield f"| [{slug}](../projects/{slug}.md) | **not measured** — {why} | — | — | — |"
    yield ""
    yield "## 3. The shapes, and what each one settles"
    yield ""
    yield "| Shape | Classes drawn | Quantities it defines |"
    yield "| --- | --- | --- |"
    for entry in configured["datasets"]:
        yield (f"| `{entry['slug']}` | {', '.join(entry['classes'])} | {len(entry['settles'])} |")
    yield ""
    yield (
        "Every value a shape defines follows from its geometry and is written out in "
        "[the shapes notebook](../../notebooks/biomarker-synthetic-shapes.ipynb), so a reader can "
        "disagree with the arithmetic rather than with the code."
    )
    yield ""
    yield (
        "The shapes are **drawn before any of this runs**, by `python -m benchmarks.shapes`, into "
        "the committed store at `data/synthetic/av/`. How that works — the command, the two tables "
        "it writes, and what each family settles — is "
        "[biomarker-synthetic-shapes.md](biomarker-synthetic-shapes.md)."
    )


def index_section(records: list[dict[str, object]], results: Path) -> Iterable[str]:
    """This benchmark's entry in the index: what each implementation returned, and how steady it was.

    **No score.** A run does not read the ground truth, so the index cannot say how close anybody
    got — and saying it here from a different source would put two answers to one question in two
    places. What belongs here is what the evidence alone supports: how much each program returned,
    and how much of it moved when the same shape was turned, where the geometry did not.
    """
    summarised = _pooled(records, results)
    yield (
        "Every shape is drawn at 0°, 30°, 60° and 90°, where the geometry is identical — so "
        "**turns with the image** is the largest spread one quantity showed across the four, and "
        "anything above zero there is the implementation or the pixel grid rather than the eye. "
        "How far each measurement is from what the geometry requires is on the results page, "
        "which reads the drawn store's ground truth."
    )
    yield ""
    yield "| Implementation | Renderings | Columns | Values returned | Turns with the image |"
    yield "| --- | --- | --- | --- | --- |"
    # An implementation's slug need not name its catalogue page — OCULAR's is `ocularnet.md` — and
    # a stored result records no declaration, so the adapters are asked. This runs only when the
    # index is generated, never during a run.
    adapters, _absent = implementations(list(IMPLEMENTATIONS))
    pages = {a.slug: str(a.declare().get("page", a.slug)) for a in adapters}
    for model, found in sorted(summarised.items()):
        # An implementation's slug need not name its catalogue page — OCULAR's is `ocularnet.md`.
        page = f"projects/{pages.get(model, model)}.md"
        yield (
            f"| [{model}]({page}) | {found['renderings']} | {found['columns']} | "
            f"{found['answered']} | {found['spread']} |"
        )
    yield ""


def _pooled(records: list[dict[str, object]], results: Path) -> dict[str, dict[str, object]]:
    """What each implementation produced, counted over every rendering in `results/`.

    **Nothing here is scored.** The benchmark does not read the ground truth, so it cannot say how
    close anybody got; what it can say is what each program returned and how steady it was when the
    same shape was turned, both of which are properties of the evidence alone. How far any of it is
    from what the geometry requires is on the results page, which reads the store.
    """
    import csv

    found: dict[str, dict[str, object]] = {}
    for model in sorted({str(record["model"]) for record in records}):
        renderings = answered = 0
        columns: set[str] = set()
        by_quantity: dict[str, list[float]] = {}
        for path in sorted((results / NAME / model).glob("*.csv")):
            for row in csv.DictReader(path.open()):
                renderings += 1
                for column, said in row.items():
                    if not column.startswith("said_"):
                        continue
                    key = column[len("said_") :]
                    columns.add(key)
                    if not said:
                        continue
                    answered += 1
                    by_quantity.setdefault(f"{path.stem}/{key}", []).append(float(said))
        spreads = [
            (max(values) - min(values)) / max(abs(v) for v in values)
            for values in by_quantity.values()
            if len(values) > 1 and max(abs(v) for v in values) > 0
        ]
        found[model] = {
            "renderings": renderings,
            "columns": len(columns),
            "answered": answered,
            "spread": f"{max(spreads):.1%}" if spreads else "—",
        }
    return found


def main(arguments) -> None:
    """Run this benchmark from the one command every benchmark is run from."""
    chosen = arguments.model.split(",") if arguments.model else list(IMPLEMENTATIONS)
    shapes = arguments.dataset.split(",") if arguments.dataset else list(SHAPES)
    adapters, missing = implementations([slug.strip() for slug in chosen])
    for slug, why in missing.items():
        print(f"warning: {slug} is not measured — {why}", file=sys.stderr)
    wanted = [shape.strip() for shape in shapes]

    # A run does not write the configuration page. That page describes the benchmark rather than
    # any run of it, so it is refreshed by `--docs` in seconds — which is what lets eight shapes be
    # measured in parallel without racing on one file, and what stops `--dataset straight` from
    # rewriting the page as though the benchmark had one shape. See `document-benchmark`.
    scored = run(
        adapters,
        wanted,
        force=arguments.force,
        max_samples=arguments.max_samples,
    )

    # The index is written after, because it summarises what came out rather than what was asked.
    if arguments.report:
        report.write_index()
    print(f"{len(scored)} pairs measured")
