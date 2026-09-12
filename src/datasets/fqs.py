# ABOUTME: Fetcher for FQS — 2,246 photographs scored 0 to 100 by six doctors, with a three-class
# ABOUTME: grade from three more, and the originals rather than the 1024-pixel renditions.

"""FQS fetcher.

One zip from figshare holding every photograph twice: `full_size_images/` as the camera produced
them, about 1942 pixels square, and `images/` resized to 1024. The store is built from the
originals — a rendition of a photograph the store already has is a copy, not a second dataset.

The labels are in `meta_data.xlsx`: six doctors' scores, their published mean, three graders'
three-class verdicts, and the median of those three. Every one of those is kept, the per-reader
values in `labels.csv` and the agreed ones in the manifest.

The archive is read where it lies rather than unpacked: the copy we do not build is 2.3 GB of it.

Layers
------
FIQSDataset.zip: photographs, labels and the published cross-validation folds. Required.
"""

from pathlib import Path

import openpyxl

from datasets.utils import archives, build, cli, fov, manifest, quality, resolution

#: Slug, matching docs/datasets/fqs.md and this module's filename.
SLUG = "fqs"

SOURCES = [
    archives.Source(
        layer="fqs",
        url="https://ndownloader.figshare.com/files/51531041",
        filename="FIQSDataset.zip",
        sha256="d8361efbd58e8c751b9055a186bd2116298d312d0fedf2aeebd458f9426bda88",
        licence="CC BY 4.0, as the figshare record states it",
        extract_it=False,
    ),
]

#: The copy of every photograph that is not built, and why.
SKIPPED = [
    "images/ — the same 2,246 photographs resized to 1024, which the store builds for itself",
]

#: The three-class grade, in the words the paper uses. 0 is the best class, not the worst.
CLASSES = {"0": "good", "1": "usable", "2": "bad"}

#: The graders whose three-class verdicts the spreadsheet keeps apart, and the six doctors whose
#: 0-to-100 scores it averages into the published mean opinion score.
GRADERS = ("level1", "level2", "level3")
DOCTORS = ("doc1", "doc2", "doc3", "doc4", "doc5", "doc6")

#: The published grade is already one of the three words, so the mapping only translates the code.
QUALITY = quality.Published(CLASSES, column="quality_class")

#: Columns only this dataset has.
EXTRA_COLUMNS = [
    manifest.Column("quality_class", "The published class code: 0 good, 1 usable, 2 reject"),
    manifest.Column("mos", "Mean opinion score, 0 to 100, averaged over six doctors"),
] + [
    manifest.Column(f"cv_{fold:02d}", f"Role in the published fold {fold:02d}: train, val or test")
    for fold in range(10)
]

#: The photographs are renditions of no camera this dataset names, and no scale is published.
RESOLUTION = resolution.Declared(
    um_per_px=None,
    source="unknown",
    note="no camera, field angle or scale is published for these photographs",
)

IMAGES = "full_size_images/"
META = "meta_data.xlsx"
FOLDS = "divisions/"


def discover(layers: dict[str, Path]) -> list[build.SourceRecord]:
    """Enumerate the photographs and everything published about them.

    :param layers: the zip, unopened, under this dataset's single layer name.
    :return: one record per photograph, in the dataset's own numbering.
    """
    archive = layers[SLUG]
    labels = _sheet(archive, META, key="file_name")
    folds = _folds(archive)
    photographs = {Path(m.name).stem: m for m in archives.members(archive, under=IMAGES)}

    records = []
    for name, label in sorted(labels.items()):
        stem = Path(name).stem
        records.append(_record(stem, photographs[stem], label, folds.get(stem, {})))
    return records


def _record(stem, photograph, label, folds) -> build.SourceRecord:
    published = str(label["qualityLevel"])
    key = f"img_{stem}"
    readings = [
        manifest.Reading(key, "quality", grader, QUALITY.word(str(label[grader])))
        for grader in GRADERS
    ]
    readings.append(manifest.Reading(key, "quality", manifest.CONSENSUS, QUALITY.word(published)))
    readings += [manifest.Reading(key, "mos", doctor, str(label[doctor])) for doctor in DOCTORS]
    readings.append(
        manifest.Reading(key, "mos", manifest.CONSENSUS, _score(label["meanOpinionScore"]))
    )

    return build.SourceRecord(
        key=key,
        image=photograph,
        quality_source="published",
        readings=readings,
        extras={
            "quality_class": published,
            **{f"cv_{fold:02d}": folds.get(f"{fold:02d}", "") for fold in range(10)},
        },
    )


def _folds(archive: Path) -> dict[str, dict[str, str]]:
    """Which role each photograph plays in each published fold.

    The fold files name photographs with a `.jpeg` extension the archive does not use, so they are
    matched by name rather than by filename.
    """
    roles: dict[str, dict[str, str]] = {}
    for member in archives.members(archive, under=FOLDS):
        fold, role = Path(member.name).stem.split("-")[1:3]
        for name in _sheet(archive, member.name, key="file_name"):
            roles.setdefault(Path(name).stem, {})[fold] = role
    return roles


def _sheet(archive: Path, name: str, key: str) -> dict[str, dict[str, object]]:
    """One spreadsheet inside the archive, keyed by a column of it."""
    with archives.Member(archive, name).open() as f:
        rows = list(openpyxl.load_workbook(f, read_only=True, data_only=True).active.values)
    header = [str(column) for column in rows[0]]
    return {str(dict(zip(header, row))[key]): dict(zip(header, row)) for row in rows[1:]}


def _score(value) -> str:
    """A mean opinion score, kept to the precision a mean of six integers actually has."""
    return f"{float(value):.4f}".rstrip("0").rstrip(".")


def main(argv: list[str] | None = None) -> int:
    """Entry point: ``uv run python -m datasets.fqs``."""
    args = cli.parse(SLUG, argv)
    return build.run(
        slug=SLUG,
        sources=SOURCES,
        discover=discover,
        resolution_of=RESOLUTION,
        args=args,
        fov_strategy=fov.DETECT,
        quality_rule=QUALITY,
        extra_columns=EXTRA_COLUMNS,
        skipped=SKIPPED,
    )


if __name__ == "__main__":
    raise SystemExit(main())
