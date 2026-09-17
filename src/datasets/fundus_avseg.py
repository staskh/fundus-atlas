# ABOUTME: Fetcher for Fundus-AVSeg — 100 photographs from Shenzhen Eye Hospital whose arteries and
# ABOUTME: veins are painted red and blue, with the authors' own split, disease and quality labels.

"""Fundus-AVSeg fetcher.

One zip from figshare: `images/` and `annotation/` sharing a filename, a metadata spreadsheet, and
the authors' `training.txt` and `testing.txt`. The artery/vein map is an RGB image — red artery,
blue vein, green where the two cross, white where the annotator could not tell — and is stored as
the binary masks of `utils.av`: `artery`, `vein` and their union `vessels`, at native resolution
only, with a crossing belonging to both vessels.

**The `vessels` mask here is derived**, being the union of the classes above rather than an
independent tracing. This dataset publishes no independent one either — its own vessel mask is
derived the same way — so a model scored against both is scored twice against one annotation, and
the second score is not corroboration.

The module is `fundus_avseg` while the slug is `fundus-avseg`: a module name cannot hold a hyphen,
and the store, the page and the manifest all use the slug.

Layers
------
fundus-avseg: Fundus-AVSeg.zip — photographs, artery/vein maps, metadata, splits. Required.
"""

import io
from pathlib import Path

import openpyxl
from PIL import Image

from datasets.utils import archives, av, build, cli, fov, manifest, quality, resolution

#: Slug, matching docs/datasets/fundus-avseg.md. The module spells it with an underscore.
SLUG = "fundus-avseg"

SOURCES = [
    archives.Source(
        layer=SLUG,
        url="https://ndownloader.figshare.com/files/54093641",
        filename="Fundus-AVSeg.zip",
        sha256="6db5ff43c4e9c25aa93093aa295c67b10fa0c089ac650df6665c7a6bbae9539f",
        licence="CC BY 4.0",
        extract_it=False,
    ),
]

#: Where things sit inside the archive.
ROOT = "Fundus-AVSeg"
PHOTOGRAPHS = f"{ROOT}/images"
ANNOTATIONS = f"{ROOT}/annotation"
METADATA = f"{ROOT}/metadata.xlsx"
SPLITS = {"train": f"{ROOT}/training.txt", "test": f"{ROOT}/testing.txt"}

#: The colours the annotation uses, established by reading every map in the archive rather than
#: from the paper, which does not state them. Green is where an artery and a vein cross; white is
#: where the annotator marked a vessel without saying which kind.
PALETTE = av.Palette(
    {
        (255, 0, 0): "artery",
        (0, 0, 255): "vein",
        (0, 255, 0): "crossing",
        (255, 255, 255): "uncertain",
    }
)

#: The two sensor sizes, which is the only separator the archive offers: it names a Zeiss VISUCAM
#: and a Canon without saying which photograph came from which.
SENSORS = {(2656, 1992): "large", (1280, 1280): "square"}

#: The disease the filename's suffix and the spreadsheet both carry, in the authors' own words.
DISEASES = {
    "Normal": "normal",
    "DR": "diabetic retinopathy",
    "AMD": "age-related macular degeneration",
    "Glaucoma": "glaucoma",
}

#: Which eye, as the spreadsheet writes it.
EYES = {"left": "os", "right": "od"}

#: The authors grade each photograph high or low, so the grade is theirs and is only translated.
#: There is no middle level because they did not publish one; inventing `usable` would be inventing
#: a judgement.
QUALITY = quality.Published(
    {"High-quality": "good", "Low-quality": "bad"}, column="published_quality"
)

EXTRA_COLUMNS = [
    manifest.Column("published_quality", "The authors' own grade: High-quality or Low-quality"),
]

#: Nothing in this archive is left out: no ultra-wide-field split, no second rendition.
SKIPPED: list[str] = []

#: The authors publish no scale and state no field angle, so the store carries none until
#: `python -m datasets.fetch_um_resolution` has measured one from the optic disc.
RESOLUTION = resolution.Declared(
    um_per_px=None,
    source="unknown",
    note=(
        "Neither the paper nor the archive states microns per pixel or a field angle, and the two "
        "cameras are not attributed per photograph. Run fetch_um_resolution, which measures each "
        "sensor size separately."
    ),
)


def subset_of(width: int, height: int) -> str:
    """Which sensor a photograph came off, which is all the archive lets anyone say."""
    return SENSORS.get((width, height), "other")


def discover(layers: dict[str, Path]) -> list[build.SourceRecord]:
    """Every photograph in the archive, with its map, its split and its metadata row."""
    archive = layers[SLUG]
    described = _metadata(archive)
    splits = _splits(archive)
    maps = {
        Path(member.name).name: member
        for member in archives.members(archive, under=f"{ANNOTATIONS}/")
    }

    records = []
    for member in archives.members(archive, under=f"{PHOTOGRAPHS}/"):
        name = Path(member.name).name
        if name not in described:
            raise LookupError(f"{name} is in the archive and not in {METADATA}")
        row = described[name]
        split = splits.get(name, "unspecified")
        records.append(
            build.SourceRecord(
                key=f"{split if split != 'unspecified' else 'image'}_{Path(name).stem.lower()}",
                image=member,
                subset=subset_of(*_size(member)),
                split=split,
                eye=EYES.get(row["eye id"], ""),
                disease=DISEASES[row["disease type"]],
                maps={"av": maps[name]} if name in maps else {},
                extras={"published_quality": row["image quality"]},
                notes="" if name in maps else "no artery/vein map is published for this photograph",
            )
        )
    return records


def _size(member: archives.Member) -> tuple[int, int]:
    """One photograph's dimensions, from its header rather than by decoding it."""
    with member.open() as f, Image.open(io.BytesIO(f.read())) as photograph:
        return photograph.size


def _metadata(archive: Path) -> dict[str, dict[str, str]]:
    """The spreadsheet, by filename: eye side, disease and the authors' quality grade."""
    with archives.Member(archive, METADATA).open() as f:
        book = openpyxl.load_workbook(io.BytesIO(f.read()), read_only=True)
    rows = list(book.active.values)
    columns = [str(cell).strip() for cell in rows[0]]
    described = {}
    for row in rows[1:]:
        if row[0] is None:
            continue
        entry = {
            name: ("" if value is None else str(value).strip())
            for name, value in zip(columns, row, strict=False)
        }
        described[entry["image name"]] = entry
    return described


def _splits(archive: Path) -> dict[str, str]:
    """The authors' own split, from the two text files that publish it."""
    found = {}
    for split, member in SPLITS.items():
        with archives.Member(archive, member).open() as f:
            for line in f.read().decode().splitlines():
                name = line.strip()
                if name:
                    found[name] = split
    return found


def main(argv: list[str] | None = None) -> int:
    """Entry point: ``uv run python -m datasets.fundus_avseg``."""
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
        palettes={"av": PALETTE},
    )


if __name__ == "__main__":
    raise SystemExit(main())
