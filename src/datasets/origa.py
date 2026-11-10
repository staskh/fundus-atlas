# ABOUTME: Fetcher for ORIGA — 650 photographs with disc and cup masks and the graders' own
# ABOUTME: cup-to-disc ratio published alongside, which is what the build checks itself against.

"""ORIGA fetcher.

**Source: the third-party Kaggle bundle https://www.kaggle.com/datasets/arnavjain1/glaucoma-datasets**, not the study's own
distribution, which this atlas has not used. ORIGA was distributed on request through the Singapore
Malay Eye Study and has no open host; in practice it arrives inside this bundle, which also carries
G1020 and REFUGE. The bundle's copy is the uploader's, cropped at the sides (docs/datasets/origa.md,
section 7), so the store is that copy and not the study's original frames.

**This one cannot fetch anything.** Kaggle needs an account, so the archive has to be obtained by hand and
passed with ``--archive``. The fetcher will not go looking for it. The bundle is about 6 GB and is
read where it lies rather than unpacked.

The pieces are found rather than addressed: the spreadsheet is whichever CSV has an `ExpCDR`
column, and the photographs and masks are matched to its rows by name. A bundle that renames the
ORIGA folder therefore still builds, and one that does not contain ORIGA fails saying so.

**The bundle holds the uploader's derived copies beside the dataset.** `Images_Cropped`,
`Images_Square`, `Masks_Cropped` and `Masks_Square` are crops and squares made for a training
notebook. Only the folders named exactly `Images` and `Masks` are read.

**The mask encoding is checked, not assumed.** The bundle writes 0 outside the disc, 1 for the rim
and 2 for the cup. ORIGA publishes `ExpCDR`, the graders' own vertical cup-to-disc ratio, so the
ratio recomputed from the stored contours is compared against it by :func:`verify`, and the result
is written into `build.json`. Had the encoding been read the wrong way round, that is where it would
show.

Layers
------
origa: the Kaggle glaucoma-datasets bundle, obtained by hand. Required, via ``--archive``.
"""

import csv
import io
from pathlib import Path

import numpy as np

from datasets.utils import archives, build, cli, contours, fov, manifest, paths, resolution

#: Slug, matching docs/datasets/origa.md and this module's filename.
SLUG = "origa"

#: Where the data this fetcher builds actually comes from: a third party's Kaggle bundle carrying
#: ORIGA, G1020 and REFUGE together — **not** the authors' official distribution, which is not used.
#: Declared so that build.json names the copy; never downloaded, since Kaggle needs an account.
BUNDLE = "https://www.kaggle.com/datasets/arnavjain1/glaucoma-datasets"

SOURCES = [
    archives.Source(
        layer=SLUG,
        url=BUNDLE,
        licence="research use, historically request-based; a Kaggle bundle's licence is its uploader's",
        manual=True,
        extract_it=False,
    ),
]

SKIPPED = [
    (
        "everything in the bundle that is not ORIGA: it also carries G1020 and REFUGE, each of "
        "which has its own page and its own fetcher"
    ),
    (
        "the uploader's Images_Cropped, Images_Square, Masks_Cropped and Masks_Square copies, "
        "which are derived from the photographs and masks that are built"
    ),
    "ORIGA/Semi-automatic-annotations, 650 MATLAB files the dataset page does not describe",
]

#: What the bundle's masks hold. The cup sits inside the disc, so the disc is both values.
CUP = (2,)
DISC = (1, 2)

#: The graders of the study, who are not named individually.
READER = "consensus"

#: The folders holding the dataset itself, as opposed to the uploader's copies of it.
PHOTOGRAPHS = "Images"
MASKS = "Masks"

#: The column naming each photograph, and the one that makes this dataset worth reaching for.
NAME_COLUMNS = ("filename", "image", "name", "imagename")
RATIO_COLUMN = "expcdr"

#: How far the recomputed ratio may stray from the graders' before :func:`verify` names the image.
TOLERANCE = 0.05

EXTRA_COLUMNS = [
    manifest.Column("expert_cdr", "The graders' own vertical cup-to-disc ratio, as published"),
]

#: A population cohort's own protocol, with no camera or scale published.
RESOLUTION = resolution.Declared(
    um_per_px=None,
    source="unknown",
    note=(
        "the Singapore Malay Eye Study's own protocol; no camera or scale is published. Run "
        "fetch_um_resolution, which groups by subset and raw size"
    ),
)

GLAUCOMA = {"1": "glaucoma", "0": "normal"}
EYES = {"1": "od", "2": "os", "od": "od", "os": "os"}


def discover(layers: dict[str, Path]) -> list[build.SourceRecord]:
    """Enumerate ORIGA's photographs, masks and published measurements.

    :param layers: the bundle, under whatever layer name it was given.
    :return: one record per photograph the spreadsheet names and the bundle holds.
    """
    archive = next(iter(layers.values()))
    held = archives.members(archive)
    sheet = _sheet(held)
    photographs = _files(held, PHOTOGRAPHS)
    masks = _files(held, MASKS)

    records = []
    for row in sheet:
        stem = Path(_named(row)).stem
        image = photographs.get(stem)
        if image is None:
            continue
        records.append(_record(stem, image, masks.get(stem), row))
    if not records:
        raise ValueError(f"{archive} holds a spreadsheet but none of the photographs it names")
    return records


def _record(stem, image, mask, row) -> build.SourceRecord:
    outlines = {}
    if mask is not None:
        outlines = {
            ("disc", READER): contours.Layer(mask, DISC),
            ("cup", READER): contours.Layer(mask, CUP),
        }
    return build.SourceRecord(
        key=stem.lower(),
        image=image,
        eye=EYES.get(_value(row, "eye").lower(), ""),
        disease=manifest.spell_out(_value(row, "glaucoma"), GLAUCOMA, "glaucoma"),
        outlines=outlines,
        # The study divided its photographs into sets A and B, which papers use as a train and test
        # split. They are the dataset's own subcollections and keep the dataset's own names.
        subset=(_value(row, "set") or _value(row, "subset")).lower() or "main",
        extras={"expert_cdr": _value(row, RATIO_COLUMN)},
        notes="" if mask is not None else "no disc and cup mask is published for this photograph",
    )


def _sheet(held: list[archives.Member]) -> list[dict[str, str]]:
    """The spreadsheet ORIGA is described by: whichever CSV carries the graders' ratio."""
    for member in sorted(held, key=lambda m: m.name):
        if not member.name.lower().endswith(".csv"):
            continue
        with member.open() as f:
            rows = list(csv.DictReader(io.TextIOWrapper(f, encoding="utf-8-sig", newline="")))
        if rows and RATIO_COLUMN in {str(column).strip().lower() for column in rows[0]}:
            return rows
    raise ValueError(f"no ORIGA spreadsheet in the bundle: none has an {RATIO_COLUMN} column")


def _files(held: list[archives.Member], folder: str) -> dict[str, archives.Member]:
    """Every image in an ORIGA folder of exactly this name, keyed by its stem.

    Exactly, because the uploader's derived copies live in `Images_Cropped` and `Images_Square`,
    and a looser match would pick whichever of the three came last.
    """
    found = {}
    for member in held:
        parts = member.name.split("/")
        if len(parts) < 2 or parts[-2] != folder or "origa" not in member.name.lower():
            continue
        if Path(parts[-1]).suffix.lower() in (".png", ".jpg", ".jpeg", ".tif", ".bmp"):
            found[Path(parts[-1]).stem] = member
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


def vertical_cdr(drawn: dict[tuple[str, str], np.ndarray]) -> float | None:
    """The vertical cup-to-disc ratio of one image's contours: the cup's height over the disc's.

    :return: the ratio, or `None` where the image lacks either structure.
    """
    disc, cup = drawn.get(("disc", READER)), drawn.get(("cup", READER))
    if disc is None or cup is None or len(disc) < 2 or len(cup) < 2:
        return None
    height = float(np.ptp(disc[:, 1]))
    return float(np.ptp(cup[:, 1])) / height if height else None


def verify(store: Path, layers: dict[str, Path], rows: list[dict[str, str]]) -> dict[str, object]:
    """Compare the ratio recomputed from the stored contours with the graders' published one.

    This is the check the dataset exists for, and the first thing that would fail if the masks had
    been read with the cup and the rim the wrong way round. Whatever it finds goes into
    `build.json`.
    """
    differences, disagreed = [], []
    for row in rows:
        where = paths.layer(store, "contours") / f"{row['key']}.csv"
        published = row.get("expert_cdr", "")
        if not where.exists() or not published:
            continue
        ours = vertical_cdr(contours.read(where))
        if ours is None:
            continue
        difference = abs(ours - float(published))
        differences.append(difference)
        if difference > TOLERANCE:
            disagreed.append(row["key"])
    return {
        "checked": len(differences),
        "median_abs_difference": round(float(np.median(differences)), 4) if differences else None,
        "max_abs_difference": round(float(np.max(differences)), 4) if differences else None,
        f"disagree_by_more_than_{TOLERANCE}": disagreed,
    }


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
        verify=verify,
    )


if __name__ == "__main__":
    raise SystemExit(main())
