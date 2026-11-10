# ABOUTME: Fetcher for REFUGE — the 2018 challenge's 1,200 photographs from two cameras, with its
# ABOUTME: own disc and cup masks, read from a third-party bundle it shares with ORIGA and G1020.

"""REFUGE fetcher.

**Source: the third-party Kaggle bundle https://www.kaggle.com/datasets/arnavjain1/glaucoma-datasets**, not the challenge's own
distribution at refuge.grand-challenge.org, which this atlas has not used. The challenge terms bind
the files whichever route they arrive by.

**This builds the 2018 edition's 1,200 photographs**, which is what that bundle, carrying ORIGA
and G1020 as well, holds: `train`, `val` and `test`, 400 each. REFUGE2's 800 further photographs are not in
it. Kaggle needs an account, and the challenge's own route a registration, so the bundle has to be
obtained by hand and passed with ``--archive``. It is about 6 GB and is read where it lies.

**The masks read are the challenge's own.** Each split carries `gts/*.bmp` in the organisers'
encoding — 255 outside the disc, 128 the rim, 0 the cup — beside a `Masks/*.png` re-encoding of the
same pixels as 0, 1 and 2. The BMPs are what the challenge published, so they are what is traced.

**Two cameras, one subset each.** The training split was photographed on a Zeiss Visucam 500 at
2124×2056; validation and test on a Canon CR-2 at 1634×1634. The split is the challenge's deliberate
domain shift, and the subset column keeps the camera visible.

**The test split carries no label in this bundle.** Its `index.json` gives sizes only, so `disease`
is empty there, as is the fovea.

Layers
------
refuge: the Kaggle glaucoma-datasets bundle, obtained by hand. Required, via ``--archive``.
"""

import json
from pathlib import Path

from datasets.utils import archives, build, cli, contours, fov, manifest, resolution

#: Slug, matching docs/datasets/refuge.md and this module's filename.
SLUG = "refuge"

#: Where the data this fetcher builds actually comes from: a third party's Kaggle bundle carrying
#: ORIGA, G1020 and REFUGE together — **not** the authors' official distribution, which is not used.
#: Declared so that build.json names the copy; never downloaded, since Kaggle needs an account.
BUNDLE = "https://www.kaggle.com/datasets/arnavjain1/glaucoma-datasets"

SOURCES = [
    archives.Source(
        layer=SLUG,
        url=BUNDLE,
        licence="research and educational use under the challenge terms, whatever the route",
        manual=True,
        extract_it=False,
    ),
]

SKIPPED = [
    (
        "everything in the bundle that is not REFUGE: it also carries ORIGA and G1020, each of "
        "which has its own page and its own fetcher, and a models folder of somebody's weights"
    ),
    (
        "the uploader's Images_Cropped, Masks_Cropped, Images_Square and Masks_Square copies, the "
        "Masks re-encoding of gts, and train/illustrations"
    ),
]

ROOT = "REFUGE"
SPLITS = ("train", "val", "test")
PHOTOGRAPHS = "Images"
MASKS = "gts"

#: The camera behind each split, per the challenge paper.
CAMERAS = {"train": "visucam500", "val": "cr2", "test": "cr2"}

#: The challenge's encoding. The cup sits inside the disc, so the disc is both values.
CUP = (0,)
DISC = (0, 128)

#: The challenge's reference standard is a consensus of its ophthalmologists.
READER = "consensus"

GLAUCOMA = {"1": "glaucoma", "0": "normal"}

EXTRA_COLUMNS = [
    manifest.Column("fovea_x", "Fovea, x, in the published photograph's pixels (not the crop's)"),
    manifest.Column("fovea_y", "Fovea, y, in the published photograph's pixels (not the crop's)"),
]

RESOLUTION = resolution.Declared(
    um_per_px=None,
    source="unknown",
    note=(
        "neither camera's scale nor field is published. Run fetch_um_resolution, which groups "
        "by subset and raw size"
    ),
)


def discover(layers: dict[str, Path]) -> list[build.SourceRecord]:
    """Every photograph of every split, with the challenge's mask and whatever its index says.

    :param layers: the bundle, by name.
    """
    archive = layers[SLUG]
    held = {member.name: member for member in archives.members(archive, under=f"{ROOT}/")}

    missing = [split for split in SPLITS if f"{ROOT}/{split}/index.json" not in held]
    if missing:
        named = ", ".join(f"{ROOT}/{split}/index.json" for split in missing)
        raise ValueError(f"{archive} holds no {named}: a split is missing from the bundle")

    records = []
    for split in SPLITS:
        with held[f"{ROOT}/{split}/index.json"].open() as f:
            entries = list(json.load(f).values())
        for entry in entries:
            stem = Path(entry["ImgName"]).stem
            image = held.get(f"{ROOT}/{split}/{PHOTOGRAPHS}/{entry['ImgName']}")
            if image is None:
                raise ValueError(f"{split}/index.json names {entry['ImgName']}, which is missing")
            mask = held.get(f"{ROOT}/{split}/{MASKS}/{stem}.bmp")
            records.append(_record(split, stem, image, mask, entry))
    return records


def _record(split, stem, image, mask, entry) -> build.SourceRecord:
    outlines = {}
    if mask is not None:
        outlines = {
            ("disc", READER): contours.Layer(mask, DISC),
            ("cup", READER): contours.Layer(mask, CUP),
        }
    label = "" if entry.get("Label") is None else str(entry["Label"])
    return build.SourceRecord(
        key=f"{split}_{stem.lower()}",
        image=image,
        subset=CAMERAS[split],
        split=split,
        disease=manifest.spell_out(label, GLAUCOMA, "Label"),
        outlines=outlines,
        extras={
            "fovea_x": _text(entry.get("Fovea_X")),
            "fovea_y": _text(entry.get("Fovea_Y")),
        },
        notes="" if mask is not None else "no disc and cup mask is published for this photograph",
    )


def _text(value) -> str:
    return "" if value is None else str(value)


def main(argv: list[str] | None = None) -> int:
    """Entry point: ``uv run python -m datasets.refuge --archive <the bundle>``."""
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
