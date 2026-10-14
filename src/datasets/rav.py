# ABOUTME: Fetcher for RAV — 206 Rotterdam Study photographs, already cropped to 1024 square, whose
# ABOUTME: arteries, veins and unknown vessels are painted on separate layers in the colour channels.

"""RAV fetcher.

One zip from DataverseNL (DOI 10.34894/9OIMWY): `dataset/rgb/` and `dataset/av_masks/` sharing a
filename, `dataset/metadata.csv` naming each photograph's camera and the participant's age and sex,
and the authors' README. The artery/vein map is not a palette: the annotators painted arteries,
veins and vessels they could not classify on three separate layers, written into the red, blue and
green channels, so a crossing is simply a pixel on both the artery and the vein layer. It is stored
as the binary masks of `utils.av`: `artery`, `vein` and their union with the unknown layer,
`vessels`.

**The `vessels` mask here is derived**, being the union of the three layers rather than an
independent tracing; the archive publishes no other.

**The photographs are the authors' renditions**, cropped to the field and resized to 1024×1024, not
camera natives. Nine cameras took them and the archive does not say at what resolution, so the
camera is the subset and a scale is inferred per camera by `fetch_um_resolution`.

Layers
------
rav: the DataverseNL zip — photographs, artery/vein layers, metadata. Required.
"""

import csv
import io
import re
from pathlib import Path

from datasets.utils import archives, av, build, cli, fov, manifest, resolution

#: Slug, matching docs/datasets/rav.md.
SLUG = "rav"

#: DataverseNL zips the record on request, so the bytes are not stable enough to carry a checksum;
#: the manifest's per-image checksums prove the files are intact. Its host also refuses some
#: networks' automated requests, which is what `--archive` is for.
SOURCES = [
    archives.Source(
        layer=SLUG,
        url="https://dataverse.nl/api/access/dataset/:persistentId/?persistentId=doi:10.34894/9OIMWY",
        filename="doi-10.34894-9oimwy.zip",
        licence="CC BY-NC 4.0 per the authors' README; CC0-1.0 per the record's metadata",
        extract_it=False,
    ),
]

#: Where things sit inside the archive.
ROOT = "dataset"
PHOTOGRAPHS = f"{ROOT}/rgb"
ANNOTATIONS = f"{ROOT}/av_masks"
METADATA = f"{ROOT}/metadata.csv"

#: The layers, as the README states them: "R = arteries, B = veins, G = unknown".
LAYERS = av.Layers(artery=0, vein=2, uncertain=1)

EXTRA_COLUMNS = [
    manifest.Column("patient_age", "The participant's age in years when photographed"),
    manifest.Column("patient_sex", "The participant's sex, M or F, as the metadata writes it"),
]

#: Nothing in this archive is left out.
SKIPPED: list[str] = []

#: The authors publish no scale and state no field angle, so the store carries none until
#: `python -m datasets.fetch_um_resolution` has measured one from the optic disc.
RESOLUTION = resolution.Declared(
    um_per_px=None,
    source="unknown",
    note=(
        "Neither the paper nor the archive states microns per pixel or a field angle, and every "
        "photograph is a 1024 rendition. Run fetch_um_resolution, which measures each camera "
        "separately."
    ),
)


def subset_of(camera: str) -> str:
    """The camera, as a subset name: lowercase words joined by underscores."""
    return "_".join(re.findall(r"[a-z0-9]+", camera.lower()))


def discover(layers: dict[str, Path]) -> list[build.SourceRecord]:
    """Every photograph in the archive, with its layered map and its metadata row."""
    archive = layers[SLUG]
    described = _metadata(archive)
    maps = {
        Path(member.name).name: member
        for member in archives.members(archive, under=f"{ANNOTATIONS}/")
    }

    records = []
    for member in archives.members(archive, under=f"{PHOTOGRAPHS}/"):
        name = Path(member.name).name
        identifier = Path(name).stem.removeprefix("RAV_")
        if identifier not in described:
            raise LookupError(f"{name} is in the archive and not in {METADATA}")
        row = described[identifier]
        records.append(
            build.SourceRecord(
                key=f"rav_{identifier}",
                image=member,
                subset=subset_of(row["device"]),
                split="unspecified",
                maps={"av": maps[name]} if name in maps else {},
                extras={"patient_age": row["patient_age"], "patient_sex": row["patient_sex"]},
                notes="" if name in maps else "no artery/vein map is published for this photograph",
            )
        )
    return records


def _metadata(archive: Path) -> dict[str, dict[str, str]]:
    """The metadata, by the number in each photograph's filename."""
    with archives.Member(archive, METADATA).open() as f:
        rows = csv.DictReader(io.StringIO(f.read().decode()))
        return {row["id"].strip(): row for row in rows}


def main(argv: list[str] | None = None) -> int:
    """Entry point: ``uv run python -m datasets.rav``."""
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
        readers={"av": LAYERS},
    )


if __name__ == "__main__":
    raise SystemExit(main())
