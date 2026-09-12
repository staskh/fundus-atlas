# ABOUTME: Fetcher for GRAPE — a longitudinal glaucoma cohort, the same eyes followed over visits,
# ABOUTME: with disc and cup drawn on a crop around the nerve head rather than on the photograph.

"""GRAPE fetcher.

Four downloads from one figshare collection: the photographs, the crops around the optic nerve, the
contours as JSON, and a spreadsheet of clinical and visual-field data. Every file is named
`<subject>_<laterality>_<visit>`, which is what makes this the one dataset here that can be split by
person and followed through time.

**The contours are in the crop's coordinate system, not the photograph's.** The archive never says
where each crop was taken from, so the crop is located in its own photograph by correlation — the
match is better than 0.998 where it works — and the offset it finds, along with that score, is
written into every row. Taking the coordinates for full-frame ones would put the optic disc
somewhere plausible and wrong.

Layers
------
photographs: CFPs.rar. Required.
crops: ROI images.rar — needed to place the contours at all. Required.
contours: json.rar. Required.
clinical: the visual-field and clinical spreadsheet. Required.
"""

import json
from pathlib import Path

import numpy as np
import openpyxl

from datasets.utils import archives, build, cli, fov, manifest, resolution

#: Slug, matching docs/datasets/grape.md and this module's filename.
SLUG = "grape"

SOURCES = [
    archives.Source(
        layer="photographs",
        url="https://ndownloader.figshare.com/files/41358156",
        filename="CFPs.rar",
        licence="CC BY 4.0 per the paper; the figshare files are marked CC0",
    ),
    archives.Source(
        layer="crops",
        url="https://ndownloader.figshare.com/files/41358150",
        filename="ROI images.rar",
        licence="CC BY 4.0 per the paper; the figshare files are marked CC0",
    ),
    archives.Source(
        layer="contours",
        url="https://ndownloader.figshare.com/files/41358162",
        filename="json.rar",
        licence="CC BY 4.0 per the paper; the figshare files are marked CC0",
    ),
    archives.Source(
        layer="clinical",
        url="https://ndownloader.figshare.com/files/41670009",
        filename="VF and clinical information.xlsx",
        licence="CC BY 4.0 per the paper; the figshare files are marked CC0",
        extract_it=False,
    ),
]

SKIPPED = [
    "the annotated images, which are the crops with the contours already drawn on them",
    "the visual-field point sensitivities, 52 numbers a visit, which are not an image annotation",
]

#: What the JSON calls each structure.
STRUCTURES = {"OD": "disc", "OC": "cup"}

#: The one ophthalmologist who drew them.
READER = "expert1"

EXTRA_COLUMNS = [
    manifest.Column("roi_x0", "Where the annotated crop sits in the photograph, in native pixels"),
    manifest.Column("roi_y0", "As above, vertically"),
    manifest.Column("roi_match", "How well the crop was found: 1.0 is exact, below 0.9 is refused"),
    manifest.Column("visit_interval_years", "Years since this eye's baseline visit"),
    manifest.Column("iop", "Intraocular pressure at this visit, mmHg"),
    manifest.Column("device", "The camera, as the spreadsheet names it"),
    manifest.Column("age", "The subject's age at baseline, years"),
    manifest.Column("sex", "The subject's sex, as recorded"),
    manifest.Column("cct", "Central corneal thickness at baseline, microns"),
    manifest.Column("total_visits", "How many visits this eye has in the cohort"),
    manifest.Column("progression", "The cohort's progression status for this eye"),
]

#: A Topcon TRC-NW8 at 50 degrees, with no scale published.
RESOLUTION = resolution.Declared(
    um_per_px=None,
    source="unknown",
    note="a Topcon TRC-NW8 at 50 degrees, with no scale published",
)

EYES = {"OD": "od", "OS": "os"}


def discover(layers: dict[str, Path]) -> list[build.SourceRecord]:
    """Enumerate the photographs, their crops, their contours and their clinical data.

    :param layers: the four downloads, by name.
    :return: one record per photograph, by subject, eye and visit.
    """
    photographs = _by_stem(layers["photographs"], ".jpg")
    crops = _by_stem(layers["crops"], ".jpg")
    drawn = _by_stem(layers["contours"], ".json")
    baseline, visits = _clinical(layers["clinical"])

    records = []
    for stem, image in sorted(photographs.items()):
        subject, laterality, visit = stem.split("_")
        eye = EYES[laterality]
        records.append(
            build.SourceRecord(
                key=f"{subject}_{eye}_{visit}",
                image=image,
                patient=subject,
                visit=visit,
                eye=eye,
                disease=baseline.get((subject, laterality), {}).get("category", ""),
                roi=crops.get(stem),
                outlines=_outlines(drawn.get(stem)),
                extras=_extras(baseline.get((subject, laterality), {}), visits.get(stem, {})),
                notes="" if stem in crops else "no annotated crop is published for this visit",
            )
        )
    return records


def _outlines(path: Path | None) -> dict[tuple[str, str], np.ndarray]:
    """The disc and cup polygons a visit has, in the crop's own coordinates."""
    if path is None:
        return {}
    drawn = json.loads(Path(path).read_text())
    return {
        (STRUCTURES[shape["label"]], READER): np.array(shape["points"], dtype=float)
        for shape in drawn.get("shapes", [])
        if shape.get("label") in STRUCTURES
    }


def _extras(eye: dict[str, str], visit: dict[str, str]) -> dict[str, str]:
    """The clinical columns, which are per eye, and the visit columns, which are per photograph."""
    return {
        "visit_interval_years": visit.get("interval", ""),
        "iop": visit.get("iop", ""),
        "device": visit.get("device", ""),
        "age": eye.get("age", ""),
        "sex": eye.get("sex", ""),
        "cct": eye.get("cct", ""),
        "total_visits": eye.get("visits", ""),
        "progression": eye.get("progression", ""),
    }


def _by_stem(where: Path, suffix: str) -> dict[str, Path]:
    """Every file of one kind, keyed by its name without the extension."""
    return {
        path.stem: path for path in Path(where).rglob(f"*{suffix}") if not path.name.startswith(".")
    }


def _clinical(sheet: Path) -> tuple[dict[tuple[str, str], dict], dict[str, dict]]:
    """What the spreadsheet says about each eye, and about each visit.

    Both sheets carry a two-row header, so the values start at the third row.
    """
    book = openpyxl.load_workbook(sheet, data_only=True)
    baseline = {}
    for row in list(book["Baseline"].values)[2:]:
        if not row or not row[0]:
            continue
        baseline[(str(row[0]), str(row[1]))] = {
            "age": _text(row[2]),
            "sex": _text(row[3]),
            "cct": _text(row[5]),
            "visits": _text(row[6]),
            "progression": _text(row[7]),
            "category": _text(row[10]).lower(),
        }

    visits = {}
    for row in list(book["Follow-up"].values)[2:]:
        if not row or not row[0] or not row[5]:
            continue
        visits[Path(str(row[5])).stem] = {
            "interval": _text(row[3]),
            "iop": _text(row[4]),
            "device": _text(row[6]),
        }
    return baseline, visits


def _text(value) -> str:
    """A spreadsheet cell as the store writes it: the value, or nothing at all."""
    return "" if value is None else str(value).strip()


def main(argv: list[str] | None = None) -> int:
    """Entry point: ``uv run python -m datasets.grape``."""
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
