# ABOUTME: Fetcher for MSHF — fundus photographs from several device classes, each scored for
# ABOUTME: illumination, clarity, contrast and overall quality by three readers kept apart.

"""MSHF fetcher.

One zip from figshare. `Original/` holds the photographs in six groups — four tabletop-camera
groups and two portable ones — plus 500 ultra-wide-field mosaics, which are **not built**, per the
skill's rule 13.7. `AI-use/train` and `AI-use/test` are the authors' split, copies of the same
photographs under the same names.

Two spreadsheets carry the scores. `Individual_scores.xlsx.xlsx` has all three readers' four binary
components for every one of the 1,302 images. `MSHF_quality_scores.xlsx` has a tab per group
carrying an agreed score — except that the tab named `DR-ZJU` holds, instead of that group's
scores, an all-zero table headed "gold standard" covering every image in the dataset. So the agreed
score exists for 1,115 photographs and not for DR-ZJU's 187, and the all-zero table is never read.

Layers
------
mshf: photographs, the authors' split and both score sheets. Required.
"""

import io
import re
from pathlib import Path

import openpyxl

from datasets.utils import archives, build, cli, fov, manifest, quality, resolution

#: Slug, matching docs/datasets/mshf.md and this module's filename.
SLUG = "mshf"

SOURCES = [
    archives.Source(
        layer="mshf",
        url="https://ndownloader.figshare.com/files/39485878",
        filename="MSHF dataset 2.0.zip",
        licence="CC BY 4.0",
        extract_it=False,
    ),
]

SKIPPED = [
    "the 500 ultra-wide-field mosaics, a 200 degree instrument beside 45 to 60 degree cameras",
    (
        "the all-zero table headed 'gold standard' on the tab named DR-ZJU: every one of its 1,302 "
        "rows reads 0, 0, 0, 0"
    ),
]

#: The groups the photographs are published in, and what each one is.
GROUPS = {
    "DR-XJU": ("cfp", "diabetic retinopathy"),
    "DR-ZJU": ("cfp", "diabetic retinopathy"),
    "Glaucoma": ("cfp", "glaucoma"),
    "Healthy": ("cfp", "healthy"),
    "Local1": ("portable", ""),
    "Local2": ("portable", ""),
}

#: The components each reader scores, as the sheets head them, and the column each column holds.
COMPONENTS = ("illumination", "clarity", "contrast")

#: Every score in this dataset is binary, on all four components.
BINARY = {"1": "good", "0": "bad"}
QUALITY = quality.Published(BINARY, column="overall")

#: The three readers, as the individual sheet heads their column blocks.
READERS = ("annotator1", "annotator2", "annotator3")

EXTRA_COLUMNS = [
    manifest.Column("group", "The group the photographs were published in: DR-XJU, Local1, …"),
    manifest.Column("illumination", "Whether the illumination is adequate: good or bad"),
    manifest.Column("clarity", "Whether the image is clear enough: good or bad"),
    manifest.Column("contrast", "Whether the contrast is adequate: good or bad"),
]

#: Three camera classes at 45, 50 and 60 degrees, with no scale published for any of them.
RESOLUTION = resolution.Declared(
    um_per_px=None,
    source="unknown",
    note="three camera classes at 45 to 60 degrees, none with a published scale",
)

ROOT = "MSHF dataset 2.0"
PHOTOGRAPHS = f"{ROOT}/Original"
SPLITS = f"{ROOT}/AI-use"
AGREED = f"{ROOT}/MSHF_quality_scores.xlsx"
INDIVIDUAL = f"{ROOT}/Individual_scores.xlsx.xlsx"

#: The tab that holds the all-zero table rather than its group's scores.
EMPTY_TAB = "DR-ZJU"


def discover(layers: dict[str, Path]) -> list[build.SourceRecord]:
    """Enumerate the photographs and the scores published for them.

    :param layers: the zip, unopened, under this dataset's single layer name.
    :return: one record per photograph, excluding the ultra-wide-field mosaics.
    """
    archive = layers[SLUG]
    agreed = _agreed(archive)
    readers = _individual(archive)
    splits = _splits(archive)

    records = []
    for member in archives.members(archive, under=f"{PHOTOGRAPHS}/"):
        group = Path(member.name).parent.name
        if group not in GROUPS:
            continue
        name = Path(member.name).name
        records.append(_record(member, group, name, splits, agreed, readers))
    return records


def _record(member, group, name, splits, agreed, readers) -> build.SourceRecord:
    subset, disease = GROUPS[group]
    stem = Path(name).stem
    split = splits.get(stem, "unspecified")
    key = f"{split}_{_flatten(stem)}"

    readings = []
    for reader, scored in readers.items():
        for field, value in zip(("illumination", "clarity", "contrast", "quality"), scored[name]):
            readings.append(manifest.Reading(key, field, reader, _word(field, value)))
    if name in agreed:
        for field, value in zip(("illumination", "clarity", "contrast", "quality"), agreed[name]):
            readings.append(manifest.Reading(key, field, manifest.CONSENSUS, _word(field, value)))

    return build.SourceRecord(
        key=key,
        image=member,
        subset=subset,
        split=split,
        disease=disease,
        quality_source="published",
        readings=readings,
        extras={"group": group},
        notes="" if name in agreed else "no agreed score is published for this group",
    )


def _word(field: str, value) -> str:
    """One binary score in words. The same two words throughout, components included."""
    return QUALITY.word("" if value is None else str(int(value)))


def _flatten(stem: str) -> str:
    """A published name as a key: lowercase, with anything else an underscore."""
    return re.sub(r"[^a-z0-9]+", "_", stem.lower()).strip("_")


def _agreed(archive: Path) -> dict[str, tuple]:
    """The agreed score per photograph, from every tab but the all-zero one."""
    book = _book(archive, AGREED)
    found: dict[str, tuple] = {}
    for tab in book.sheetnames:
        if tab == EMPTY_TAB:
            continue
        found.update(_scores(book[tab], range(1, 5)))
    return found


def _individual(archive: Path) -> dict[str, dict[str, tuple]]:
    """Each reader's score per photograph, from their own block of columns."""
    sheet = _book(archive, INDIVIDUAL)["Sheet1"]
    return {
        reader: _scores(sheet, range(start, start + 4))
        for reader, start in zip(READERS, (1, 6, 11))
    }


def _scores(sheet, columns) -> dict[str, tuple]:
    """One table of scores, keyed by the photograph's published filename."""
    found = {}
    for row in sheet.values:
        if not row or not row[0] or str(row[0]) == "image name":
            continue
        values = tuple(row[column] for column in columns)
        if all(value is None for value in values):
            continue
        found[str(row[0])] = values
    return found


def _splits(archive: Path) -> dict[str, str]:
    """Which half of the authors' split each photograph is in.

    Keyed without the extension: two photographs are `.jpg` among the originals and `.png` in the
    split, and matching on the filename would leave those two unsplit.
    """
    return {
        Path(member.name).stem: Path(member.name).parent.name
        for member in archives.members(archive, under=f"{SPLITS}/")
    }


def _book(archive: Path, name: str):
    with archives.Member(archive, name).open() as f:
        return openpyxl.load_workbook(io.BytesIO(f.read()), data_only=True)


def main(argv: list[str] | None = None) -> int:
    """Entry point: ``uv run python -m datasets.mshf``."""
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
