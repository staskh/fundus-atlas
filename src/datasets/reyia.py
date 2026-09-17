# ABOUTME: Fetcher for REYIA — a compilation of nine other collections' photographs with artery and
# ABOUTME: vein annotation, inside an archive that is mostly a generator's synthetic output.

"""REYIA fetcher.

One Kaggle archive, **link-shared rather than public**: the API answers 403, so it must be
downloaded by hand and passed with `--archive`.

What is inside is not what the name suggests. Of its 10,075 files, **7,712 are synthetic images**
produced by [RLAD](../../docs/models/rlad.md), the generator from the same group — sixteen
generations of one training split. Those are not photographs of eyes and nothing measured on them
says anything about one, so they are skipped. What is built is the 2,363 remaining files: nine
source collections, each holding `images/`, `artery/`, `veins/` and `labels/` under a shared
filename.

**The archive publishes the annotation twice**, as binary artery and vein masks and as an RGB
`labels` map, and the two agree exactly: the artery mask is red plus magenta, the vein mask blue
plus magenta, and magenta is where the two vessels cross. This fetcher reads the label map and
checks the result against the published binaries, which is what `verify` records in `build.json`.

**These are other datasets' photographs.** Eight of the nine subsets are collections catalogued
here in their own right, three of which this repository already builds; scoring REYIA beside them
counts the same eyes twice. The subset column says which is which.

Layers
------
reyia: the Kaggle archive, by hand. Required.
"""

import re
from pathlib import Path

from datasets.utils import archives, av, build, cli, fov, manifest, resolution

#: Slug, matching docs/datasets/reyia.md and this module's filename.
SLUG = "reyia"

SOURCES = [
    archives.Source(
        layer=SLUG,
        url="",
        filename="archive.zip",
        licence="MIT on the compilation, as the authors state it",
        manual=True,
        extract_it=False,
    ),
]

#: Where everything sits inside the archive.
ROOT = "REYIA"

#: The folder each map lives in, and the store layer it becomes.
LABELS = "labels"

#: The subsets built, which are the source collections that are standard colour photography.
SOURCES_BUILT = ("ENRICH", "GRAPE", "PAPILA", "FIVES", "MAGREB", "MESSIDOR", "TREND", "MBRSET")

#: What is deliberately left in the archive, per the skill's rules 13.7 and 2.
SKIPPED = [
    (
        "the 7,712 files of REYIA/GENERATED_IMAGES: sixteen generations of synthetic photographs "
        "from the RLAD generator, which are not photographs of eyes"
    ),
    "the AVWIDE subset, an ultra-wide-field instrument beside 45 degree cameras",
]

#: REYIA's colours. Magenta is the crossing, where Fundus-AVSeg and HRF-AV both use green — which is
#: why a palette is declared per dataset rather than assumed.
PALETTE = av.Palette(
    {(255, 0, 0): "artery", (0, 0, 255): "vein", (255, 0, 255): "crossing"}, tolerance=64
)

#: Jupyter leaves these in several folders of the archive; they are copies, not photographs.
JUNK = "-checkpoint"

#: The photographs come from nine collections with nine different cameras and no common scale, so
#: nothing is declared here: `fetch_um_resolution` measures each subset and size separately.
RESOLUTION = resolution.Declared(
    um_per_px=None,
    source="unknown",
    note=(
        "A compilation of nine collections, each with its own camera and none of them stating a "
        "scale in this archive. Run fetch_um_resolution, which groups by subset and native size."
    ),
)

EXTRA_COLUMNS = [
    manifest.Column(
        "source_dataset", "The collection this photograph came from, as REYIA names it"
    ),
    manifest.Column(
        "published_masks",
        "Which binary masks the archive publishes beside its label map, semicolon separated",
    ),
]


def discover(layers: dict[str, Path]) -> list[build.SourceRecord]:
    """Every photograph of every built subset, with the label map its vessels are drawn in."""
    archive = layers[SLUG]
    held: dict[tuple[str, str, str], archives.Member] = {}
    for member in archives.members(archive, under=f"{ROOT}/"):
        parts = member.name.split("/")
        if len(parts) < 4 or JUNK in parts[-1]:
            continue
        subset, folder, name = parts[1], parts[2], parts[-1]
        if subset not in SOURCES_BUILT:
            continue
        held[(subset, folder, Path(name).stem)] = member

    records = []
    for subset, folder, stem in sorted(held):
        if folder != LABELS:
            continue
        photograph = held.get((subset, "images", stem))
        if photograph is None:
            continue
        published = [
            name
            for name, layer in (("artery", "artery"), ("veins", "vein"))
            if (subset, name, stem) in held
        ]
        records.append(
            build.SourceRecord(
                key=f"{subset.lower()}_{_flatten(stem)}",
                image=photograph,
                subset=subset.lower(),
                maps={"av": held[(subset, folder, stem)]},
                extras={
                    "source_dataset": subset,
                    "published_masks": ";".join(published),
                },
                notes=(
                    f"these photographs are {subset}'s, annotated again for REYIA; scoring both "
                    f"counts the same eyes twice"
                ),
            )
        )
    return records


def _flatten(stem: str) -> str:
    """One filename as a key: lowercase, and nothing in it that a path would argue with."""
    return re.sub(r"[^a-z0-9]+", "_", stem.lower()).strip("_")


def verify(store: Path, layers: dict[str, Path], rows: list[dict[str, str]]) -> dict[str, object]:
    """Check the masks built from the label map against the binaries the archive also publishes.

    The archive says the same thing twice, so the build can be checked against the dataset rather
    than against itself: the artery mask should be exactly red plus magenta, the vein mask blue plus
    magenta. Whatever this finds goes into `build.json`.
    """
    import numpy as np
    from PIL import Image

    archive = layers[SLUG]
    published = {
        (parts[1], parts[2], Path(parts[-1]).stem): member
        for member in archives.members(archive, under=f"{ROOT}/")
        if len(parts := member.name.split("/")) >= 4 and JUNK not in parts[-1]
    }
    checked, disagreed = 0, []
    for row in rows:
        subset = row["source_dataset"]
        stem = row["source_image"].rsplit("/", 1)[-1].rsplit(".", 1)[0]
        for folder, layer in (("artery", "artery"), ("veins", "vein")):
            member = published.get((subset, folder, stem))
            built = store / "native" / layer / f"{row['key']}.png"
            if member is None or not built.exists():
                continue
            with member.open() as f, Image.open(f) as theirs:
                drawn = np.asarray(theirs.convert("L")) > 0
            with Image.open(built) as ours:
                mine = np.asarray(ours) > 0
            checked += 1
            if drawn.shape == mine.shape and int((drawn ^ mine).sum()):
                disagreed.append(
                    {"key": row["key"], "layer": layer, "pixels": int((drawn ^ mine).sum())}
                )
    return {
        "published_masks_checked": checked,
        "disagreeing": disagreed[:20],
        "disagreeing_total": len(disagreed),
    }


def main(argv: list[str] | None = None) -> int:
    """Entry point: ``uv run python -m datasets.reyia --archive <the Kaggle zip>``."""
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
        readers={"av": PALETTE},
        verify=verify,
    )


if __name__ == "__main__":
    raise SystemExit(main())
