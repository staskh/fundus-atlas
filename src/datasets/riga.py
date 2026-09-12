# ABOUTME: Fetcher for RIGA — 744 photographs whose optic disc and cup were outlined by six
# ABOUTME: ophthalmologists each, taken from the RIGA+ repackaging because the original host blocks it.

"""RIGA fetcher.

**This builds RIGA+, not the original deposit, and what it builds is not whole photographs.** RIGA
is published by the University of Michigan's Deep Blue, which answers an automated request with a
bot challenge, so it cannot be fetched by a script at all. RIGA+ is a repackaging on Zenodo for
domain-adaptation work, and it is fetchable — but its images are **800x800 crops around the optic
nerve, not the photographs**. Most show no field-of-view edge at all, and those that do show a
sliver of one.

Three consequences, all of them recorded:

- **There is no field of view to find, so none is looked for.** The frame is taken as it is. A
  store built from this cannot support anything measured in camera pixels — a vessel calibre, a
  disc diameter in microns, a fractal dimension — because the pixel scale of the original is gone
  and the visible field is a fragment. What it does support is disc and cup segmentation, which is
  what RIGA+ was assembled for.
- **`um_per_px` is empty and `resolution_source` is `unknown`**, and would be even if the cameras'
  scales were published, because these are crops of resized images.
- **Its licence field says CC BY 4.0 where RIGA's own says CC BY-NC 4.0.** The atlas records the
  licence the owner states, so RIGA stays non-commercial whatever the repackaging claims.

Each mask holds both structures: the optic cup is 128 and the rim around it is 255, so the disc is
the two together. Six masks per photograph, one per ophthalmologist.

Layers
------
riga: RIGAPlus.zip — photographs, masks and the repackagers' domain splits. Required.
"""

import re
from pathlib import Path

from datasets.utils import archives, build, cli, contours, fov, resolution

#: Slug, matching docs/datasets/riga.md and this module's filename.
SLUG = "riga"

SOURCES = [
    archives.Source(
        layer="riga",
        url="https://zenodo.org/api/records/6325549/files/RIGAPlus.zip/content",
        filename="RIGAPlus.zip",
        licence="RIGA is CC BY-NC 4.0; the RIGA+ record claims CC BY 4.0 for the same photographs",
        extract_it=False,
    ),
]

SKIPPED = [
    (
        "the unlabelled MESSIDOR photographs RIGA+ adds for domain adaptation: they carry no RIGA "
        "annotation and belong to MESSIDOR"
    ),
    "the repackagers' own train and test CSVs, which are their split rather than RIGA's",
]

#: The six ophthalmologists, as the mask filenames number them.
READERS = tuple(f"expert{n}" for n in range(1, 7))

#: What each value in a mask is. The cup is inside the rim, and the disc is both.
CUP = (128,)
DISC = (128, 255)

#: The three sources the photographs come from, and the folder each one is under.
SOURCES_BY_FOLDER = {
    "BinRushed": "binrushed",
    "Magrabia": "magrabia",
    "MESSIDOR_Base1": "messidor",
    "MESSIDOR_Base2": "messidor",
    "MESSIDOR_Base3": "messidor",
}

#: RIGA+ crops and resizes, so no scale survives even where the camera's was known.
RESOLUTION = resolution.Declared(
    um_per_px=None,
    source="unknown",
    note="RIGA+ ships 800x800 crops around the nerve head, not whole photographs at camera scale",
)

PHOTOGRAPHS = "RIGA/"
MASKS = "RIGA-mask/"


def discover(layers: dict[str, Path]) -> list[build.SourceRecord]:
    """Enumerate the annotated photographs and the six outlines of each.

    :param layers: the zip, unopened, under this dataset's single layer name.
    :return: one record per annotated photograph, by source and published name.
    """
    archive = layers[SLUG]
    masks = _masks(archive)

    records = []
    for member in sorted(archives.members(archive, under=PHOTOGRAPHS), key=lambda m: m.name):
        parts = Path(member.name).parts
        folder = parts[1]
        if folder not in SOURCES_BY_FOLDER or "Unlabeled" in member.name:
            continue
        collection = parts[2]
        stem = Path(member.name).stem
        drawn = masks.get((collection, stem), {})
        if not drawn:
            continue
        records.append(_record(member, folder, collection, stem, drawn))
    return records


def _record(member, folder, collection, stem, drawn) -> build.SourceRecord:
    key = f"{SOURCES_BY_FOLDER[folder]}_{collection.lower()}_{stem.lower()}"
    return build.SourceRecord(
        key=key,
        image=member,
        subset=SOURCES_BY_FOLDER[folder],
        outlines={
            (structure, reader): contours.Layer(mask, values)
            for reader, mask in drawn.items()
            for structure, values in (("disc", DISC), ("cup", CUP))
        },
        extras={"collection": collection},
    )


def _masks(archive: Path) -> dict[tuple[str, str], dict[str, archives.Member]]:
    """Every reader's mask, indexed by the collection and photograph it belongs to.

    A mask is named after its photograph with the reader's number appended — `image9-4.tif` is
    reader four's outline of `image9.tif`.
    """
    found: dict[tuple[str, str], dict[str, archives.Member]] = {}
    for member in archives.members(archive, under=MASKS):
        parts = Path(member.name).parts
        matched = re.fullmatch(r"(.+)-(\d+)", Path(member.name).stem)
        if not matched or len(parts) < 4:
            continue
        stem, number = matched.groups()
        found.setdefault((parts[-2], stem), {})[f"expert{number}"] = member
    return found


def main(argv: list[str] | None = None) -> int:
    """Entry point: ``uv run python -m datasets.riga``."""
    args = cli.parse(SLUG, argv)
    return build.run(
        slug=SLUG,
        sources=SOURCES,
        discover=discover,
        resolution_of=RESOLUTION,
        args=args,
        # There is no field of view in a crop of a photograph. Looking for one finds a sliver of
        # the edge where it is in frame at all, and any radius fits a nearly straight arc: doing
        # that here produced circles 36 and 13,646 pixels across on 800-pixel images.
        fov_strategy=fov.WHOLE,
        extra_columns=[
            build.manifest.Column(
                "collection", "The folder inside its source: BinRushed1, MESSIDOR_Base2, …"
            )
        ],
        skipped=SKIPPED,
    )


if __name__ == "__main__":
    raise SystemExit(main())
