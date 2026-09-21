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
from .shapes import library

#: What this benchmark is called in a heading, where its slug does not read as English.
TITLE = "Biomarkers against arithmetic"

#: What it is called in `results/`, in `docs/benchmarks/` and in a run record. A Python module name
#: cannot carry a hyphen, so the module is `biomarker_synthetic` and `report._module` translates.
NAME = "biomarker-synthetic"
#: How close a measurement must be to what the geometry requires to be counted as agreeing. It is
#: a way of summarising many numbers in one, not a pass mark: this benchmark selects nothing.
AGREES = 0.02

#: The benchmark's own version. Changing what is measured, or how, changes this.
VERSION = 2

#: The written pages this benchmark produces, and the notebook behind each, as `(label, stem)`.
#: **One per implementation**, because each is a different piece of somebody else's code: what is
#: true of PVBM's chord-sum length says nothing about the next implementation, and one document
#: holding both would bury each under the other. A second implementation adds a pair here.
REPORTS = (
    ("PVBM", "biomarker-synthetic-pvbm"),
    # The three AutoMorph projects share a page because they share a lineage: AutoMorphalyzer and
    # AutoMorphClass both descend from AutoMorph's measuring stage, so the interesting question is
    # what each changed, which only a side-by-side can answer.
    ("AutoMorph", "biomarker-synthetic-automorph"),
)

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
IMPLEMENTATIONS = ("pvbm", "automorph", "automorphalyzer", "automorphclass")

#: The AutoMorph family, by the page they are written up on together. A family is a lineage rather
#: than a category: these three measure the same quantities because two of them are rewrites of the
#: first, so a difference between their numbers is a change somebody made on purpose.
FAMILIES = {"biomarker-synthetic-automorph": ("automorph", "automorphalyzer", "automorphclass")}

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
                "settles": sorted(built.theory),
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
            # outlived a change to any of them would be describing something else.
            "rendering": {"side": SIDE, "um_per_px": UM_PER_PX, "rotations": list(ROTATIONS)},
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
            note = "; ".join(f"{where}: {why}" for where, why in getattr(adapter, "trouble", {}).items())
        except Exception as failure:  # noqa: BLE001 — a crash is an answer about nothing
            answered, note = dict.fromkeys(adapter.keys()), repr(failure)
        taken = time.perf_counter() - started
        rows.append(_row(adapter, built, angle, answered, taken, note))
    return rows


def _row(adapter, built, angle: float, answered: dict, taken: float, note: str) -> dict[str, object]:
    """What is kept about one rendering.

    The theoretical value sits **beside** the returned one rather than being subtracted from it: a
    difference is an analysis, and the analysis belongs in the notebook.
    """
    row: dict[str, object] = {
        # What was measured, named once. A rendering plays the part a photograph plays in every
        # other benchmark here, so it carries the same kind of key and the evidence sorts alike.
        "key": f"{built.name}@{angle:.0f}",
        "shape": built.name,
        "rotation": f"{angle:.1f}",
        "side": built.side,
        "um_per_px": built.um_per_px,
        # `failed` means nothing came back. A rendering whose equivalents raised while its
        # geometry was measured is a measured rendering with a note saying what it could not
        # answer — otherwise one bad column would throw away every good one beside it.
        "outcome": "measured" if any(value is not None for value in answered.values()) else "failed",
        "seconds": f"{taken:.3f}",
        "note": note,
    }
    for key in adapter.keys():
        value = answered.get(key)
        row[f"said_{key}"] = "" if value is None else f"{float(value):.6f}"
        # The adapter answers under catalogued names, and a shape states its theory under the same
        # ones, so the two meet without a translation step in between. A column the catalogue has
        # no name for carries the implementation's own name and no theory — which is a gap in the
        # catalogue rather than a reason to leave the measurement out.
        theory = built.theory.get(key)
        row[f"theory_{key}"] = "" if theory is None else f"{float(theory):.6f}"
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
        "what the implementation returned. `<key>` is a **catalogued biomarker name** — "
        "`biomarker/variant/structure` — wherever the implementation's adapter maps its own column "
        "to one, so two implementations' evidence lines up column by column. A column the "
        "catalogue has no name for yet keeps the implementation's own name, recognisable by "
        "carrying no `/`, and is measured and stored all the same"
    ),
    "theory_<key>": (
        "what the shape's geometry requires for that quantity, where it defines one. A shape "
        "states its theory under catalogued names too, so the two meet without translation; a "
        "column under an implementation's own name therefore has no theory beside it"
    ),
    "note": "what an implementation failed with",
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
        yield (
            f"| `{entry['slug']}` | {', '.join(entry['classes'])} | "
            f"{len(entry['settles'])} |"
        )
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
    """This benchmark's entry in the index: what each implementation got right, and how far off.

    One row per implementation. The figure that matters is not an average error — averaging a
    tortuosity with a fractal dimension means nothing — but **how many of the quantities it
    reports land on the value geometry requires**, and how far its answers move when the same
    shape is turned.
    """
    summarised = _pooled(records, results)
    yield (
        "Every value is compared with what the shape's geometry requires rather than with another "
        "implementation. **Agrees** counts the measurements within 2% of the required value; "
        "**turns with the image** is the largest spread one measurement showed across 0°, 30°, 60° "
        "and 90°, where the geometry is identical and the answer should be too."
    )
    yield ""
    yield "| Implementation | Renderings | Quantities with a known value | Agrees | Turns with the image |"
    yield "| --- | --- | --- | --- | --- |"
    for model, found in sorted(summarised.items()):
        yield (
            f"| [{model}](projects/{model}.md) | {found['renderings']} | {found['comparable']} | "
            f"{found['agreed']} | {found['spread']} |"
        )
    yield ""
    yield (
        "**This benchmark selects nothing.** Which implementations are fit to measure a real "
        "segmentation is a judgement made by a person on this evidence, and the numbers above are "
        "a summary of it rather than a ranking."
    )


def _pooled(records: list[dict[str, object]], results: Path) -> dict[str, dict[str, object]]:
    """How each implementation did, counted over every rendering in `results/`."""
    import csv

    found: dict[str, dict[str, object]] = {}
    for model in sorted({str(record["model"]) for record in records}):
        comparable = agreed = renderings = 0
        spreads: list[float] = []
        by_quantity: dict[str, list[float]] = {}
        for path in sorted((results / NAME / model).glob("*.csv")):
            for row in csv.DictReader(path.open()):
                renderings += 1
                for column, said in row.items():
                    if not column.startswith("said_") or not said:
                        continue
                    key = column[len("said_") :]
                    theory = row.get(f"theory_{key}", "")
                    if not theory:
                        continue
                    comparable += 1
                    required, answered = float(theory), float(said)
                    # A required value of zero — a shape with no junctions — is agreed with by
                    # answering zero and by nothing else. A relative tolerance cannot express that,
                    # and treating it as unanswerable counted every correct zero as a miss.
                    close = (
                        answered == required
                        if required == 0
                        else abs(answered - required) / abs(required) <= AGREES
                    )
                    if close:
                        agreed += 1
                    by_quantity.setdefault(f"{path.stem}/{key}", []).append(answered)
        for values in by_quantity.values():
            if len(values) > 1 and max(abs(v) for v in values) > 0:
                spreads.append((max(values) - min(values)) / max(abs(v) for v in values))
        found[model] = {
            "renderings": renderings,
            "comparable": comparable,
            "agreed": f"{agreed} of {comparable}" if comparable else "—",
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
    scored = run(
        adapters,
        [shape.strip() for shape in shapes],
        force=arguments.force,
        max_samples=arguments.max_samples,
    )
    if arguments.report:
        configured = configuration(adapters, [shape.strip() for shape in shapes])
        report.write_docs(NAME, configured, missing, {}, COLUMNS)
        report.write_index()
    print(f"{len(scored)} pairs measured")
