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
            yield (
                f"| `{entry['name']}` | {entry['means']} | {entry['unit']} | {statistics} | "
                f"{'yes' if entry['whole_vessel'] else '—'} |"
            )
        yield ""


#: Every block these pages may mark, and what fills it.
BLOCKS = {"families": _family_table, "units": _units_tables}


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
    for path in write():
        print(f"refreshed {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
