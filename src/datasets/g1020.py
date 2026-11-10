# ABOUTME: Fetcher for G1020 — 1,020 unposed clinic photographs with the authors' own disc and cup
# ABOUTME: polygons, read from the LabelMe files in a third-party bundle it shares with ORIGA and REFUGE.

"""G1020 fetcher.

**Source: the third-party Kaggle bundle https://www.kaggle.com/datasets/arnavjain1/glaucoma-datasets**, not the authors' own host at
DFKI, which this atlas has not used. The authors' host has been unreliable, and this bundle, which
also carries ORIGA and REFUGE, is the route people use. The bundle is the uploader's packaging: its
G1020.csv carries only the glaucoma label, without the ratios and rim widths the paper describes.

**This one cannot fetch anything.** Kaggle needs an account, so the bundle has to
be obtained by hand and passed with ``--archive``. It is about 6 GB and is read where it lies.

**The outlines are the authors' polygons, not the uploader's masks.** Beside each photograph in
`G1020/Images` sits a LabelMe JSON file holding the polygons as drawn, labelled `disc` and `cup`,
plus a `discLoc` rectangle — the disc's bounding box, which is not an outline and is not read. The
bundle's `Masks` folder is a rasterisation of those same polygons; reading it would mean tracing back
a shape somebody has already drawn as coordinates.

Two things in the polygons are not what the paper's description would lead a reader to expect, and
both are kept visible rather than smoothed over:

- **Three photographs carry two `disc` polygons.** The larger is kept, as the disc, and the row's
  `notes` says so.
- **One photograph carries a cup and no disc.** It is built with the cup alone.

Layers
------
g1020: the Kaggle glaucoma-datasets bundle, obtained by hand. Required, via ``--archive``.
"""

import csv
import io
import json
from pathlib import Path

import numpy as np

from datasets.utils import archives, build, cli, fov, manifest, resolution

#: Slug, matching docs/datasets/g1020.md and this module's filename.
SLUG = "g1020"

#: Where the data this fetcher builds actually comes from: a third party's Kaggle bundle carrying
#: ORIGA, G1020 and REFUGE together — **not** the authors' official distribution, which is not used.
#: Declared so that build.json names the copy; never downloaded, since Kaggle needs an account.
BUNDLE = "https://www.kaggle.com/datasets/arnavjain1/glaucoma-datasets"

SOURCES = [
    archives.Source(
        layer=SLUG,
        url=BUNDLE,
        licence="research use per the paper; a Kaggle bundle's licence is its uploader's",
        manual=True,
        extract_it=False,
    ),
]

SKIPPED = [
    (
        "everything in the bundle that is not G1020: it also carries ORIGA and REFUGE, each of "
        "which has its own page and its own fetcher"
    ),
    (
        "the uploader's Images_Cropped, Images_Square, Masks, Masks_Cropped, Masks_Square and "
        "NerveRemoved_Images, which are derived from the photographs and polygons that are built"
    ),
]

#: Where the dataset sits in the bundle, and its two files that matter.
ROOT = "G1020"
PHOTOGRAPHS = "Images"
SHEET = "G1020.csv"

#: The one annotator, who is not named.
READER = "expert1"

#: LabelMe labels that are outlines. `discLoc` is a bounding box and is left alone.
STRUCTURES = ("disc", "cup")

GLAUCOMA = {"1": "glaucoma", "0": "normal"}

#: The paper states a 45 degree field and no scale.
RESOLUTION = resolution.Declared(
    um_per_px=None,
    source="field_angle",
    degrees=45,
    note=(
        "45 degrees, per the paper; no scale is published. Each photograph is cropped to the "
        "fundus, so the field is fitted per image. Run fetch_um_resolution as well"
    ),
)


def discover(layers: dict[str, Path]) -> list[build.SourceRecord]:
    """Every photograph the sheet names, with its glaucoma label and the polygons drawn on it.

    :param layers: the bundle, by name.
    """
    archive = layers[SLUG]
    held = {member.name: member for member in archives.members(archive, under=f"{ROOT}/")}
    if f"{ROOT}/{SHEET}" not in held:
        raise ValueError(f"{archive} holds no {ROOT}/{SHEET}: is it the glaucoma-datasets bundle?")

    with held[f"{ROOT}/{SHEET}"].open() as f:
        sheet = list(csv.DictReader(io.TextIOWrapper(f, encoding="utf-8-sig", newline="")))

    records = []
    for row in sheet:
        stem = Path(row["imageID"]).stem
        image = held.get(f"{ROOT}/{PHOTOGRAPHS}/{row['imageID']}")
        if image is None:
            continue
        drawn = held.get(f"{ROOT}/{PHOTOGRAPHS}/{stem}.json")
        outlines, notes = _outlines(drawn)
        records.append(
            build.SourceRecord(
                key=stem.lower(),
                image=image,
                disease=manifest.spell_out(row["binaryLabels"].strip(), GLAUCOMA, "binaryLabels"),
                outlines=outlines,
                notes=notes,
            )
        )
    if not records:
        raise ValueError(f"{archive} names G1020 photographs but holds none of them")
    return records


def _outlines(member: archives.Member | None) -> tuple[dict[tuple[str, str], np.ndarray], str]:
    """The disc and cup polygons drawn on one photograph, and anything odd about them."""
    if member is None:
        return {}, "no polygon file is published for this photograph"
    with member.open() as f:
        shapes = json.load(f).get("shapes", [])

    drawn: dict[str, list[np.ndarray]] = {}
    for shape in shapes:
        if shape.get("label") in STRUCTURES and len(shape.get("points", [])) >= 3:
            drawn.setdefault(shape["label"], []).append(np.array(shape["points"], dtype=float))

    notes = []
    outlines = {}
    for structure, polygons in drawn.items():
        if len(polygons) > 1:
            notes.append(
                f"two {structure} polygons are published; the larger, of "
                f"{_area(max(polygons, key=_area)):.0f} px against "
                f"{_area(min(polygons, key=_area)):.0f} px, is kept"
            )
        outlines[(structure, READER)] = max(polygons, key=_area)
    if "cup" in drawn and "disc" not in drawn:
        notes.append("a cup is published with no disc around it")
    return outlines, "; ".join(notes)


def _area(polygon: np.ndarray) -> float:
    """A polygon's area by the shoelace formula."""
    x, y = polygon[:, 0], polygon[:, 1]
    return 0.5 * abs(float(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1))))


def main(argv: list[str] | None = None) -> int:
    """Entry point: ``uv run python -m datasets.g1020 --archive <the bundle>``."""
    args = cli.parse(SLUG, argv)
    return build.run(
        slug=SLUG,
        sources=SOURCES,
        discover=discover,
        resolution_of=RESOLUTION,
        args=args,
        fov_strategy=fov.DETECT,
        skipped=SKIPPED,
    )


if __name__ == "__main__":
    raise SystemExit(main())
