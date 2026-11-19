# ABOUTME: Fetcher for HRF — 45 photographs at 3504×2336 with a hand-drawn vessel gold standard,
# ABOUTME: field-of-view masks, and artery/vein maps and disc/cup outlines two later groups added.

"""HRF fetcher.

Three sources over one set of photographs, which is the point of this dataset's three provenances:

* **HRF** publishes `all.zip` — `images/`, `manual1/` (the vessel gold standard, drawn by hand) and
  `mask/` (field-of-view masks). CC BY 4.0.
* **HRF-AV** is a separate group's artery/vein reference standard, in the `HRF_AV_GT/` folder of
  `github.com/rubenhx/av-segmentation`, at a pinned commit. It is the layer the artery/vein models
  in this catalogue train on, and **its repository carries no licence at all** — publicly
  downloadable is not the same as licensed, so it is fetched as an optional layer and a build
  without it still produces the vessel dataset HRF itself published.

**The two annotations are one tracing.** It would be reasonable to expect HRF's hand-drawn vessel
gold standard and a second group's artery/vein map to be independent — different people, six years
apart. Measured here, the union of the artery and vein masks differs from the vessel gold standard
by **1,190 pixels across all 45 photographs, 0.004% of them**: HRF-AV coloured HRF's own tracing
rather than drawing its own. What the second group contributed is the *classification*, not the
segmentation, so a model scored against both is scored against one tracing twice.

* **HRF-Seg+** is a third group's optic disc and cup masks, `HRF-Seg+.zip` on Zenodo, CC BY 4.0.
  They are **not the size of the photograph**: each is a 500-pixel square round the nerve head,
  published beside the same square cut from the photograph. That square is found in the photograph
  by template matching, at native scale, and the outlines are traced in it and moved by where it
  was found — on the real archive every square matches at a correlation of 0.995 or better.

The original release's two experts' disc centres are a separate legacy `.xls` and are not fetched.

Layers
------
hrf:          all.zip — photographs, vessel gold standard, field-of-view masks. Required.
hrf-av:       the artery/vein reference standard. Optional.
hrf-seg-plus: optic disc and cup masks on a crop round the nerve head. Optional.
"""

from pathlib import Path

from datasets.utils import archives, av, build, cli, contours, fov, manifest, resolution

#: Slug, matching docs/datasets/hrf.md and this module's filename.
SLUG = "hrf"

#: The second group's layer, and where its maps sit inside that repository.
AV_LAYER = "hrf-av"
AV_FOLDER = "HRF_AV_GT"

#: The third group's layer, and the folders inside its archive that this store reads. The vessel,
#: alpha/beta-zone and merged folders are left where they are: HRF's own vessel gold standard is
#: already in the store, and peripapillary atrophy zones have no place in its schema.
SEG_PLUS_LAYER = "hrf-seg-plus"
SEG_PLUS_DISC = "Folder_1_Optic_Disc"
SEG_PLUS_CUP = "Folder_2_Optic_Cup"
SEG_PLUS_IMAGES = "Folder_6_Original_Images"

#: HRF-Seg+ names no annotator — one creator, "reviewed by experts" — so the reader is named for
#: the release, which also keeps it apart from the original release's two experts.
SEG_PLUS_READER = "hrf_seg_plus"

#: What counts as structure in a HRF-Seg+ mask, read as grey. Each mask is one colour painted on
#: white: the disc (128, 64, 128) is grey 90 and the cup (130, 76, 0) grey 84, against paper at 255.
#: Most disc masks blend paint into paper along the edge — up to 526 distinct colours in one file —
#: so a pixel is structure when it is nearer the paint than the paper: darker than 172. Five cup
#: masks (`04_dr`, `06_dr`, `09_dr`, `14_dr`, `15_dr`) are blank paper, and trace to no cup.
STRUCTURE = contours.Layer(source=None, values=tuple(range(0, 172)))

#: Where each HRF-Seg+ square was found in its photograph.
EXTRA_COLUMNS = [
    manifest.Column("roi_x0", "Where HRF-Seg+'s crop sits in the photograph, in raw pixels"),
    manifest.Column("roi_y0", "As above, vertically"),
    manifest.Column("roi_match", "How well the crop was found: 1.0 is exact, below 0.9 is refused"),
]

SOURCES = [
    archives.Source(
        layer=SLUG,
        url="https://www5.cs.fau.de/fileadmin/research/datasets/fundus-images/all.zip",
        filename="all.zip",
        sha256="a914d02cda161b7f33f25d0397c276d50e9a6cbc705e9b364a54f0adafed57e4",
        licence="CC BY 4.0",
        extract_it=False,
    ),
    archives.GitSource(
        layer=AV_LAYER,
        repo="https://github.com/rubenhx/av-segmentation",
        commit="41415f1879f9d5bc901134de22c392b5b0078932",
        paths=[AV_FOLDER],
        licence="not stated: the repository carries no licence file",
        optional=True,
    ),
    archives.Source(
        layer=SEG_PLUS_LAYER,
        url="https://zenodo.org/api/records/16744782/files/HRF-Seg+.zip/content",
        filename="HRF-Seg+.zip",
        sha256="e4bf59bb820147aa28158b1ed2228cf59cc426605d023ab2edca651fcf3f3411",
        licence="CC BY 4.0",
        optional=True,
        extract_it=False,
    ),
]

#: The colours HRF-AV uses. It has no fourth class: every vessel pixel is called artery, vein, or
#: the crossing of the two.
#:
#: Forty-two of the forty-five maps hold exactly those four colours and nothing else. Three —
#: `11_h`, `12_h` and `13_h` — were saved with anti-aliased strokes and carry 3,133 stray pixels
#: between them, **0.013% of that layer**: blends down each colour's ramp such as (60, 60, 217) and
#: (253, 22, 22), and greys up to (231, 231, 231).
#:
#: The tolerance is therefore opened all the way, which for a ramp palette means *assign every pixel
#: to the ramp it is nearest* rather than refuse it: a blend goes to its own colour, and a grey —
#: equally far from every ramp — falls to the background, which is what an artefact between two
#: strokes should be. The cost is that this layer's guard against an undeclared class is not active,
#: so the three maps were inspected by hand instead; see `docs/datasets/hrf.md`, section 7.
PALETTE = av.Palette(
    {(255, 0, 0): "artery", (0, 0, 255): "vein", (0, 255, 0): "crossing"}, tolerance=256
)

#: The three groups of fifteen the dataset is built from, named in every filename.
DISEASES = {"dr": "diabetic retinopathy", "g": "glaucoma", "h": "healthy"}

#: HRF ships its own field-of-view masks, so nothing here detects one.
FOV_STRATEGY = fov.FROM_MASK

#: Nothing is left out: HRF publishes no ultra-wide-field split.
SKIPPED: list[str] = []

#: The authors publish no scale. They state a 45° field, which gives one per photograph from the
#: field's own diameter — about 300 µm of retina to a degree at the posterior pole.
RESOLUTION = resolution.Declared(
    um_per_px=None,
    source="field_angle",
    degrees=45,
    note=(
        "The Canon CR-1's 45° field, stated by the authors. The scale follows from each "
        "photograph's own fitted field rather than from the dataset, since the field's diameter in "
        "pixels differs between photographs."
    ),
)


def discover(layers: dict[str, Path]) -> list[build.SourceRecord]:
    """Every photograph, its vessel gold standard, its field mask and its artery/vein map."""
    archive = layers[SLUG]
    photographs = {
        Path(member.name).stem: member for member in archives.members(archive, under="images/")
    }
    vessels = {
        Path(member.name).stem: member for member in archives.members(archive, under="manual1/")
    }
    masks = {
        Path(member.name).stem.removesuffix("_mask"): member
        for member in archives.members(archive, under="mask/")
    }
    drawn = _artery_vein(layers.get(AV_LAYER))
    outlined = _disc_and_cup(layers.get(SEG_PLUS_LAYER))

    records = []
    for stem in sorted(photographs):
        maps = {}
        if stem in vessels:
            maps["vessels"] = vessels[stem]
        if stem in masks:
            maps["fov"] = masks[stem]
        if stem in drawn:
            maps["av"] = drawn[stem]
        roi, outlines = outlined.get(stem, (None, {}))
        notes = []
        if "av" not in maps:
            notes.append("no artery/vein reference standard was fetched")
        if not outlines:
            notes.append("no disc and cup outline was fetched")
        records.append(
            build.SourceRecord(
                key=stem,
                image=photographs[stem],
                disease=DISEASES[stem.rsplit("_", 1)[1]],
                maps=maps,
                roi=roi,
                outlines=outlines,
                notes="; ".join(notes),
            )
        )
    return records


def _disc_and_cup(archive: Path | None) -> dict[str, tuple[archives.Member, dict]]:
    """HRF-Seg+'s crop and its two outlines, by the photograph they annotate, or nothing at all.

    A photograph is outlined only when the release has its crop and both masks: an outline without
    the crop it was drawn on could not be placed.
    """
    if archive is None:
        return {}
    folders: dict[str, dict[str, archives.Member]] = {}
    for member in archives.members(archive):
        parts = Path(member.name).parts
        if len(parts) >= 2:
            folders.setdefault(parts[-2], {})[Path(member.name).stem] = member
    crops = folders.get(SEG_PLUS_IMAGES, {})
    discs, cups = folders.get(SEG_PLUS_DISC, {}), folders.get(SEG_PLUS_CUP, {})
    return {
        stem: (
            crops[stem],
            {
                ("disc", SEG_PLUS_READER): contours.Layer(discs[stem], STRUCTURE.values),
                ("cup", SEG_PLUS_READER): contours.Layer(cups[stem], STRUCTURE.values),
            },
        )
        for stem in sorted(crops)
        if stem in discs and stem in cups
    }


def _artery_vein(tree: Path | None) -> dict[str, Path]:
    """The second group's maps, by the photograph they annotate, or nothing at all."""
    if tree is None:
        return {}
    folder = tree / AV_FOLDER
    if not folder.is_dir():
        return {}
    return {path.stem.removesuffix("_AVmanual"): path for path in sorted(folder.glob("*.png"))}


def main(argv: list[str] | None = None) -> int:
    """Entry point: ``uv run python -m datasets.hrf``."""
    args = cli.parse(SLUG, argv)
    return build.run(
        slug=SLUG,
        sources=SOURCES,
        discover=discover,
        resolution_of=RESOLUTION,
        args=args,
        fov_strategy=FOV_STRATEGY,
        skipped=SKIPPED,
        extra_columns=EXTRA_COLUMNS,
        readers={"av": PALETTE},
    )


if __name__ == "__main__":
    raise SystemExit(main())
