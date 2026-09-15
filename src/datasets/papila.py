# ABOUTME: Fetcher for PAPILA — both eyes of 244 patients, disc and cup outlined by two experts,
# ABOUTME: with the clinical record of each eye and no quality grade at all.

"""PAPILA fetcher.

One zip from figshare holding four things: the photographs, both experts' contours as text files
of coordinates, a clinical spreadsheet per eye, and the authors' own example code. The contours are
in the photograph's own frame, so they need translating by the crop and nothing else.

**No quality grade is published, and this store assumes one.** Every photograph here was taken with
one camera, centred on the optic disc, in a clinical study of glaucoma; a frame nobody could read
would not have been kept and annotated twice over. So the store records `good` for all 488 with
`quality_source` set to `assumed`, which is this repository's supposition rather than the authors'
statement, and is never to be pooled with a published grade. What it makes PAPILA useful for is one
question in particular: how much of a sound dataset a quality model would throw away.

Layers
------
papila: PAPILA.zip — photographs, contours, clinical data. Required.
"""

import re
from pathlib import Path

import numpy as np
import openpyxl

from datasets.utils import archives, build, cli, fov, manifest, quality, resolution

#: Slug, matching docs/datasets/papila.md and this module's filename.
SLUG = "papila"

SOURCES = [
    archives.Source(
        layer="papila",
        url="https://ndownloader.figshare.com/files/35013982",
        filename="PAPILA.zip",
        sha256="15b053dff496bc8e53eb8a8d0707ef73ba3d56c988eea92b65832c9c82852a7d",
        licence="GPL 3.0 or later, as stated on figshare",
    ),
]

SKIPPED = [
    (
        "ImagesWithContours/ — the photographs with the outlines already drawn on them, which are "
        "a rendering of the contours rather than an annotation"
    ),
    (
        "HelpCode/kfold/ — the authors' cross-validation folds, which are an evaluation protocol "
        "rather than something published about an image"
    ),
]

#: Where each part of the archive lives, below its one hashed top directory.
PHOTOGRAPHS = "FundusImages"
CONTOURS = "ExpertsSegmentations/Contours"
CLINICAL = "ClinicalData"

#: What the clinical spreadsheets call each diagnosis. Confirmed against the counts the dataset
#: page publishes — 333 healthy, 87 suspect, 68 glaucoma — because the archive explains the codes
#: nowhere: its README points at the paper and its own helper code reads the column without
#: naming its values.
DIAGNOSES = {"0": "healthy", "1": "glaucoma suspect", "2": "glaucoma"}

#: The two ophthalmologists, as the contour filenames name them.
READERS = ("expert1", "expert2")

#: A contour file, and only a contour file: the archive also carries eleven macOS duplicates named
#: `..._cup_exp2 2.txt`, holding the same coordinates under a name no consumer should read twice.
CONTOUR = re.compile(r"^(?P<stem>RET\d+O[DS])_(?P<structure>disc|cup)_exp(?P<expert>[12])\.txt$")

#: Nothing is graded, so a grade is assumed — see this module's docstring and the dataset page.
QUALITY = quality.Assumed(
    "good",
    because=(
        "PAPILA publishes no quality annotation. Every photograph was taken with one camera, "
        "centred on the optic disc, for a glaucoma study in which two ophthalmologists outlined "
        "the disc and cup of all 488 — work nobody does on an unreadable frame. The assumption is "
        "this repository's and is marked as such in every row"
    ),
)

EXTRA_COLUMNS = [
    manifest.Column("age", "The patient's age in years, as the clinical sheet records it"),
    manifest.Column("gender", "The patient's sex, as the code the clinical sheet uses"),
    manifest.Column("dioptre_1", "Refraction, first principal meridian, dioptres"),
    manifest.Column("dioptre_2", "Refraction, second principal meridian, dioptres"),
    manifest.Column("astigmatism", "Axis of astigmatism, degrees"),
    manifest.Column("phakic", "Whether the eye is phakic or pseudophakic, as the sheet's code"),
    manifest.Column("pneumatic", "Intraocular pressure by pneumatic tonometry, mmHg"),
    manifest.Column("perkins", "Intraocular pressure by Perkins tonometry, mmHg"),
    manifest.Column("pachymetry", "Central corneal thickness, microns"),
    manifest.Column("axial_length", "Axial length of the eye, millimetres"),
    manifest.Column("vf_md", "Visual field mean deviation, decibels; less is worse"),
]

#: A Topcon TRC-NW400 at 30 degrees, which the authors state, with no scale published. At the
#: posterior pole a degree of field is about 300 microns of retina.
RESOLUTION = resolution.Declared(
    um_per_px=None,
    source="field_angle",
    degrees=30,
    note="a Topcon TRC-NW400 at 30 degrees, per the paper; no scale is published",
)

EYES = {"OD": "od", "OS": "os"}


def discover(layers: dict[str, Path]) -> list[build.SourceRecord]:
    """Enumerate the photographs, both experts' outlines and the clinical row of each eye.

    :param layers: the one download, by name.
    :return: one record per photograph, keyed by patient and eye.
    """
    tree = _tree(layers["papila"])
    outlines = _outlines(tree / CONTOURS)
    clinical = _clinical(tree / CLINICAL)

    records = []
    for image in sorted((tree / PHOTOGRAPHS).glob("RET*.jpg")):
        stem = image.stem
        patient, side = stem[:-2], stem[-2:]
        eye = EYES[side]
        row = clinical.get((patient, eye))
        drawn = outlines.get(stem, {})
        records.append(
            build.SourceRecord(
                key=f"{patient.lower()}_{eye}",
                image=image,
                patient=patient,
                eye=eye,
                disease=_diagnosis(row),
                outlines=drawn,
                readers=[reader for reader in READERS if any(r == reader for _, r in drawn)],
                extras=_extras(row),
                notes="" if row else "no clinical row is published for this eye",
            )
        )
    return records


def _tree(where: Path) -> Path:
    """The one directory the zip unpacks into, found rather than composed: its name carries a
    commit hash that will change with the next release."""
    for candidate in (where, *sorted(where.iterdir())):
        if candidate.is_dir() and (candidate / PHOTOGRAPHS).is_dir():
            return candidate
    raise FileNotFoundError(f"{where} holds no {PHOTOGRAPHS} directory")


def _outlines(where: Path) -> dict[str, dict[tuple[str, str], np.ndarray]]:
    """Every expert's disc and cup, by photograph, in the photograph's own coordinates."""
    found: dict[str, dict[tuple[str, str], np.ndarray]] = {}
    for path in sorted(where.iterdir()):
        named = CONTOUR.match(path.name)
        if named is None:
            continue
        nodes = np.loadtxt(path, dtype=float, ndmin=2)
        reader = f"expert{named['expert']}"
        found.setdefault(named["stem"], {})[(named["structure"], reader)] = nodes
    return found


def _clinical(where: Path) -> dict[tuple[str, str], dict[str, str]]:
    """What the two spreadsheets say about each eye.

    Each has a two-row header and then a row holding only `ID`, so the values start at the fourth.
    """
    rows = {}
    for side in ("od", "os"):
        book = openpyxl.load_workbook(where / f"patient_data_{side}.xlsx", data_only=True)
        for row in list(book[book.sheetnames[0]].values)[3:]:
            if not row or not row[0]:
                continue
            rows[(f"RET{str(row[0]).lstrip('#')}", side)] = {
                "age": _text(row[1]),
                "gender": _text(row[2]),
                "diagnosis": _text(row[3]),
                "dioptre_1": _text(row[4]),
                "dioptre_2": _text(row[5]),
                "astigmatism": _text(row[6]),
                "phakic": _text(row[7]),
                "pneumatic": _text(row[8]),
                "perkins": _text(row[9]),
                "pachymetry": _text(row[10]),
                "axial_length": _text(row[11]),
                "vf_md": _text(row[12]),
            }
    return rows


def _diagnosis(row: dict[str, str] | None) -> str:
    """The eye's diagnosis in the dataset's own words rather than its code."""
    if not row:
        return ""
    return manifest.spell_out(row["diagnosis"], DIAGNOSES, "diagnosis")


def _extras(row: dict[str, str] | None) -> dict[str, str]:
    """This dataset's own columns, verbatim, and empty where an eye has no clinical row."""
    return {column.name: (row or {}).get(column.name, "") for column in EXTRA_COLUMNS}


def _text(value) -> str:
    """A spreadsheet cell as the store writes it: the value, or nothing at all."""
    return "" if value is None else str(value).strip()


def main(argv: list[str] | None = None) -> int:
    """Entry point: ``uv run python -m datasets.papila``."""
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
