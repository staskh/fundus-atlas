# ABOUTME: The catalogue pages that state facts the vocabulary already holds — each family's
# ABOUTME: biomarkers, its units, its structures — rendered from `canonical.py` rather than typed.

import sys
from collections.abc import Iterable
from pathlib import Path

from benchmarks import docs

from . import canonical

#: The pages this module refreshes, and where they live.
DIRECTORY = Path("docs")
PAGES = ("BIOMARKERS.md", "BIOMARKER-NAMES.md")

#: One line per family, for the summary table, and one line per biomarker, for the units tables.
#: Everything here is read out of the record, so a unit stated on a page and a unit the shapes
#: convert by cannot drift apart — which is exactly what happened to Grisan's density, declared
#: dimensionless in a table while its own derivation two sections below called it an inverse
#: length, and caught only when the physical units arrived.


def catalogue() -> dict[str, object]:
    """The vocabulary as data: what the pages below are rendered from."""
    families: list[dict[str, object]] = []
    for family, record in canonical.FAMILIES.items():
        stems = [stem for stem in canonical.NAMES if stem.startswith(f"{family}/")]
        units = sorted({canonical.NAMES[stem].unit for stem in stems})
        families.append(
            {
                "family": family,
                "means": record.means,
                "count": len(stems),
                "units": units,
                "structures": list(record.structures),
                "region": record.region,
                "regional": record.regional,
                "statistic": record.statistic,
                "biomarkers": [
                    {
                        "stem": stem,
                        "name": _written(stem),
                        "means": canonical.NAMES[stem].means,
                        "unit": canonical.NAMES[stem].unit,
                        "statistics": list(canonical.NAMES[stem].statistics),
                        "whole_vessel": canonical.NAMES[stem].whole_vessel,
                        "paper": canonical.NAMES[stem].paper,
                        "values": list(canonical.NAMES[stem].values),
                    }
                    for stem in stems
                ],
            }
        )
    return {"families": families, "names": len(canonical.names())}


def _written(stem: str) -> str:
    """A stem with its structures spelt out, the way a reader meets it in a table."""
    structures = canonical.structures(stem)
    if not structures:
        return stem
    if len(structures) == 1:
        return f"{stem}/{structures[0]}"
    return f"{stem}/{{{','.join(structures)}}}"


def _family_table(record) -> Iterable[str]:
    """`BIOMARKERS.md` §1: one row per family, counted and united from the record."""
    yield "| Family | What it measures | Biomarkers | Structures | Units |"
    yield "| --- | --- | --- | --- | --- |"
    for family in record["families"]:
        name = family["family"]
        structures = (
            ", ".join(f"`{one}`" for one in family["structures"]) if family["structures"] else "—"
        )
        yield (
            f"| [{name}](biomarkers/{name}.md) | {family['means']} | {family['count']} | "
            f"{structures} | {', '.join(family['units'])} |"
        )
    yield ""
    yield (
        f"**{record['names']} canonical names** in all, once each biomarker is expanded over the "
        f"structures it applies to, the regions it admits and the statistics it can be pooled by."
    )


def _units_tables(record) -> Iterable[str]:
    """`BIOMARKER-NAMES.md`: every name and the unit it is reported in, per family."""
    for family in record["families"]:
        yield f"**[`{family['family']}`](biomarkers/{family['family']}.md)**"
        yield ""
        yield "| Canonical name | What it measures | Unit | Statistics | Whole-vessel form |"
        yield "| --- | --- | --- | :-: | :-: |"
        for entry in family["biomarkers"]:
            statistics = ", ".join(f"`{one}`" for one in entry["statistics"]) or "—"
            # A category's unit is its list of answers, which is what a reader needs to know.
            unit = entry["unit"]
            if entry["values"]:
                unit = f"{unit}: " + ", ".join(f"`{one}`" for one in entry["values"])
            yield (
                f"| `{entry['name']}` | {entry['means']} | {unit} | {statistics} | "
                f"{'yes' if entry['whole_vessel'] else '—'} |"
            )
        yield ""


#: Every block these pages may mark, and what fills it.
BLOCKS = {"families": _family_table, "units": _units_tables}

#: The project pages that list every column their implementation writes, by adapter slug. Each is
#: rendered from that adapter's own naming table — the one place a column is translated — and its
#: `CLOSEST` rules, so a page cannot claim a mapping the code does not make.
PROJECTS = {
    "automorph": "projects/automorph.md",
    "automorphalyzer": "projects/automorphalyzer.md",
    "automorphclass": "projects/automorphclass.md",
    "pvbm": "projects/pvbm.md",
    "ocular": "projects/ocularnet.md",
    "vascx": "projects/vascx.md",
    "fundus-biomarkers": "projects/fundus-biomarkers.md",
}

#: Above this many rows a list is folded, so the page around it stays readable.
FOLD_ABOVE = 80


def columns(slug: str) -> list[dict[str, str | None]]:
    """Every column an adapter returns, with the canonical name it answers to, or the nearest one
    and why it is not that name."""
    import importlib

    from .utils import catalogue
    from .utils.closest import nearest

    module = importlib.import_module(f"biomarkers.{slug}")
    names = getattr(module, "CANONICAL", None)
    if names is None:
        names = catalogue.load(slug).declare()["names"]
    rules = getattr(module, "CLOSEST", ())
    words = getattr(module, "CLOSEST_WORDS", {})
    rows = []
    for own, mapped in names.items():
        if mapped:
            rows.append({"own": own, "name": mapped, "match": "exact", "why": ""})
            continue
        near = nearest(own, rules, words)
        if near is None or near[0] is None:
            why = near[1] if near else ""
            rows.append({"own": own, "name": None, "match": "none", "why": why})
        else:
            rows.append({"own": own, "name": near[0], "match": "close", "why": near[1]})
    return rows


def _columns_table(record) -> Iterable[str]:
    """A project page's list of every column its implementation writes."""
    rows = record["columns"]
    counted = {
        match: sum(row["match"] == match for row in rows) for match in ("exact", "close", "none")
    }
    yield (
        f"**{len(rows)} columns**: {counted['exact']} answer to a canonical name exactly, "
        f"{counted['close']} are close to one and {counted['none']} to none. A close name is a "
        f"pointer for a reader, never a mapping: nothing is compared against it. Rendered from "
        f"the naming table in `src/biomarkers/{record['source']}` by `python -m biomarkers.pages`."
    )
    yield ""
    folded = len(rows) > FOLD_ABOVE
    if folded:
        yield f"<details><summary>All {len(rows)} columns</summary>"
        yield ""
    yield "| Its column | Canonical name | Match | What differs |"
    yield "| --- | --- | :-: | --- |"
    for row in rows:
        name = f"`{row['name']}`" if row["name"] else "—"
        yield f"| `{row['own']}` | {name} | {row['match']} | {row['why']} |"
    if folded:
        yield ""
        yield "</details>"


def write_projects(into: Path = DIRECTORY) -> list[Path]:
    """Refresh the list of columns on every project page that marks one."""
    written = []
    for slug, page in PROJECTS.items():
        path = Path(into) / page
        source = f"{slug}.py"
        record = {"columns": columns(slug), "source": source}
        path.write_text(docs.render(path.read_text(), record, {"columns": _columns_table}))
        written.append(path)
    return written


def write(into: Path = DIRECTORY) -> list[Path]:
    """Refresh every marked block on every catalogue page, in place."""
    record = catalogue()
    written = []
    for page in PAGES:
        path = Path(into) / page
        path.write_text(docs.render(path.read_text(), record, BLOCKS))
        written.append(path)
    return written


def main() -> int:
    for path in [*write(), *write_projects()]:
        print(f"refreshed {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
