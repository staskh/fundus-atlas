# ABOUTME: Fetcher for FIVES — 800 photographs at 2048 square with a vessel mask on every one,
# ABOUTME: 200 each of AMD, diabetic retinopathy, glaucoma and normal eyes, and a quality grade.

"""FIVES fetcher.

One RAR from figshare, which the Python standard library cannot read; `bsdtar` can, so this is one
of the few datasets here that is unpacked rather than read where it lies. Inside are `train/` and
`test/`, each with `Original/` and `Ground truth/` under the same filenames, plus
`Quality Assessment.xlsx`.

The filename carries the diagnosis: `137_G.png` is glaucoma. The spreadsheet carries three binary
quality components and **no overall grade**, so the grade is derived from them by the rule in the
skill, section 5.4 — all three sound is `good`, one short is `usable`, more is `bad`.

Layers
------
fives: photographs, vessel masks and the quality sheet. Required.
"""

import io
from pathlib import Path

import openpyxl

from datasets.utils import archives, build, cli, fov, manifest, quality, resolution

#: Slug, matching docs/datasets/fives.md and this module's filename.
SLUG = "fives"

SOURCES = [
    archives.Source(
        layer="fives",
        url="https://ndownloader.figshare.com/files/34969398",
        filename="FIVES.rar",
        licence="CC BY 4.0",
    ),
]

#: The letter each filename ends with, and what the authors say it means.
DISEASES = {
    "A": "age-related macular degeneration",
    "D": "diabetic retinopathy",
    "G": "glaucoma",
    "N": "normal",
}

#: The quality components, as the spreadsheet heads them, and what each one is called here. Every
#: one is binary, and 1 is the sound value.
COMPONENTS = {
    "IC": "illumination_contrast",
    "Blur": "blur",
    "LC": "low_contrast",
}

#: Binary, like every other component score in this catalogue.
BINARY = {"1": "good", "0": "bad"}

#: No overall grade is published, so one is derived from the three components.
QUALITY = quality.FromComponents(dict.fromkeys(COMPONENTS.values(), "good"))

EXTRA_COLUMNS = [
    manifest.Column("illumination_contrast", "The sheet's `IC` column: good or bad"),
    manifest.Column("blur", "The sheet's `Blur` column: good or bad"),
    manifest.Column("low_contrast", "The sheet's `LC` column: good or bad"),
]

#: One camera at 50 degrees, but no scale is published and the field is cropped square.
RESOLUTION = resolution.Declared(
    um_per_px=None,
    source="unknown",
    note="a Topcon TRC-NW8 at 50 degrees, with no scale published and the field cropped square",
)

QUALITY_SHEET = "Quality Assessment.xlsx"
PHOTOGRAPHS = "Original"
VESSELS = "Ground truth"


def discover(layers: dict[str, Path]) -> list[build.SourceRecord]:
    """Enumerate the photographs, their vessel masks and their quality components.

    :param layers: the unpacked archive, under this dataset's single layer name.
    :return: one record per photograph, by split and published number.
    """
    root = _root(layers[SLUG])
    scored = _quality(root / QUALITY_SHEET)

    records = []
    for split in ("train", "test"):
        for image in sorted((root / split / PHOTOGRAPHS).glob("*.png")):
            number, letter = image.stem.split("_")
            key = f"{split}_{number}_{letter.lower()}"
            records.append(
                build.SourceRecord(
                    key=key,
                    image=image,
                    split=split,
                    disease=DISEASES[letter],
                    maps={"vessels": root / split / VESSELS / image.name},
                    extras=scored[(split, letter, int(number))],
                )
            )
    return records


def _root(unpacked: Path) -> Path:
    """The one directory the archive unpacks into, whatever it is called."""
    inside = [child for child in unpacked.iterdir() if child.is_dir()]
    return inside[0] if len(inside) == 1 else unpacked


def _quality(sheet: Path) -> dict[tuple[str, str, int], dict[str, str]]:
    """The three quality components per photograph, keyed by split, disease letter and number."""
    with open(sheet, "rb") as f:
        book = openpyxl.load_workbook(io.BytesIO(f.read()), data_only=True)

    scored = {}
    for tab in book.sheetnames:
        for row in book[tab].values:
            if not row or not row[0] or row[0] == "Disease":
                continue
            letter, number = str(row[0]), int(row[1])
            scored[(tab.lower(), letter, number)] = {
                name: BINARY[str(int(value))]
                for (column, name), value in zip(COMPONENTS.items(), row[2:5])
            }
    return scored


def main(argv: list[str] | None = None) -> int:
    """Entry point: ``uv run python -m datasets.fives``."""
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
    )


if __name__ == "__main__":
    raise SystemExit(main())
