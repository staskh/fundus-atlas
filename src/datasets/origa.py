# ABOUTME: Fetcher for ORIGA — 650 photographs with disc and cup masks and, rarely, the graders'
# ABOUTME: own cup-to-disc ratio published alongside, which is what the build checks itself against.

"""ORIGA fetcher.

**This one cannot fetch anything.** ORIGA was distributed on request through the Singapore Malay
Eye Study and has no open host; in practice it arrives inside a third-party Kaggle bundle that also
carries G1020 and REFUGE. Kaggle needs an account, so the archive has to be obtained by hand and
passed with ``--archive``. The fetcher will not go looking for it.

The pieces are found rather than addressed: the spreadsheet is whichever CSV has an `ExpCDR`
column, and the photographs and masks are matched to its rows by name. A bundle that rearranges its
folders therefore still builds, and one that does not contain ORIGA fails saying so.

**The mask encoding is checked, not assumed.** ORIGA publishes `ExpCDR`, the graders' own vertical
cup-to-disc ratio, so the ratio recomputed from the stored contours can be compared against it —
and is, in the verification described on the dataset page. If the two values disagreed, the
encoding below would be the first thing to doubt.

Layers
------
origa: the bundle holding ORIGA, obtained by hand. Required, via ``--archive``.
"""

import csv
from pathlib import Path

from datasets.utils import archives, build, cli, contours, fov, manifest, resolution

#: Slug, matching docs/datasets/origa.md and this module's filename.
SLUG = "origa"

SOURCES = [
    archives.Source(
        layer="origa",
        licence="research use, historically request-based; a Kaggle bundle's licence is its uploader's",
        manual=True,
    ),
]

SKIPPED = [
    "everything in the bundle that is not ORIGA: it also carries G1020 and REFUGE, each of which "
    "has its own page and its own fetcher",
]

#: What the published masks hold. The cup sits inside the disc, so the disc is both values.
CUP = (255,)
DISC = (128, 255)

#: The graders of the study, who are not named individually.
READER = "consensus"

#: The column naming each photograph, and the one that makes this dataset worth reaching for.
NAME_COLUMNS = ("filename", "image", "name", "imagename")
RATIO_COLUMN = "expcdr"

EXTRA_COLUMNS = [
    manifest.Column("expert_cdr", "The graders' own vertical cup-to-disc ratio, as published"),
]

#: A population cohort's own protocol, with no camera or scale published.
RESOLUTION = resolution.Declared(
    um_per_px=None,
    source="unknown",
    note="the Singapore Malay Eye Study's own protocol; no camera or scale is published",
)

GLAUCOMA = {"1": "glaucoma", "0": "normal"}
EYES = {"1": "od", "2": "os", "od": "od", "os": "os"}


def discover(layers: dict[str, Path]) -> list[build.SourceRecord]:
    """Enumerate ORIGA's photographs, masks and published measurements.

    :param layers: the unpacked bundle, under whatever layer name it was given.
    :return: one record per photograph the spreadsheet names and the bundle holds.
    """
    root = next(iter(layers.values()))
    sheet = _sheet(root)
    photographs = _files(root, "image")
    masks = _files(root, "mask")

    records = []
    for row in sheet:
        stem = Path(_named(row)).stem
        image = photographs.get(stem)
        if image is None:
            continue
        records.append(_record(stem, image, masks.get(stem), row))
    if not records:
        raise ValueError(f"{root} holds a spreadsheet but none of the photographs it names")
    return records


def _record(stem, image, mask, row) -> build.SourceRecord:
    outlines = {}
    if mask is not None:
        outlines = {
            ("disc", READER): contours.Layer(archives.File(mask), DISC),
            ("cup", READER): contours.Layer(archives.File(mask), CUP),
        }
    return build.SourceRecord(
        key=stem.lower(),
        image=image,
        eye=EYES.get(_value(row, "eye").lower(), ""),
        disease=GLAUCOMA.get(_value(row, "glaucoma"), ""),
        outlines=outlines,
        # The study divided its photographs into sets A and B, which papers use as a train and test
        # split. They are the dataset's own subcollections and keep the dataset's own names.
        subset=(_value(row, "set") or _value(row, "subset")).lower() or "main",
        extras={"expert_cdr": _value(row, RATIO_COLUMN)},
        notes="" if mask is not None else "no disc and cup mask is published for this photograph",
    )


def _sheet(root: Path) -> list[dict[str, str]]:
    """The spreadsheet ORIGA is described by: whichever CSV carries the graders' ratio."""
    for path in sorted(root.rglob("*.csv")):
        with open(path, newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        if rows and RATIO_COLUMN in {str(column).strip().lower() for column in rows[0]}:
            return rows
    raise ValueError(f"no ORIGA spreadsheet under {root}: none has an {RATIO_COLUMN} column")


def _files(root: Path, what: str) -> dict[str, Path]:
    """Every image under a directory whose name says what it holds, keyed by name."""
    found = {}
    for path in root.rglob("*"):
        if path.suffix.lower() not in (".png", ".jpg", ".jpeg", ".tif", ".bmp"):
            continue
        if what in path.parent.name.lower() and "origa" in str(path).lower():
            found[path.stem] = path
    return found


def _named(row: dict[str, str]) -> str:
    for column, value in row.items():
        if str(column).strip().lower() in NAME_COLUMNS and value:
            return str(value)
    raise ValueError(f"no column naming the photograph among {list(row)}")


def _value(row: dict[str, str], wanted: str) -> str:
    for column, value in row.items():
        if str(column).strip().lower() == wanted:
            return "" if value is None else str(value).strip()
    return ""


def main(argv: list[str] | None = None) -> int:
    """Entry point: ``uv run python -m datasets.origa --archive <the bundle>``."""
    args = cli.parse(SLUG, argv)
    return build.run(
        slug=SLUG,
        sources=SOURCES,
        discover=discover,
        resolution_of=RESOLUTION,
        args=args,
        fov_strategy=fov.DETECT,
        extra_columns=EXTRA_COLUMNS,
        skipped=SKIPPED,
    )


if __name__ == "__main__":
    raise SystemExit(main())
