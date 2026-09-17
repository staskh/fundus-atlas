# ABOUTME: Fetcher for AVRDB — 100 photographs from Rawalpindi whose arteries and veins were drawn
# ABOUTME: on white pages by ophthalmologists, one file per vessel kind, saved as JPEG.

"""AVRDB fetcher.

One zip from Mendeley, holding a folder per photograph: the photograph itself, three drawings —
`--arteries`, `--veins`, `--vessels` — a `--both` overlay, and the Illustrator file they were drawn
in. The drawings are annotations on a **white page** rather than masks, and they are JPEG, so every
stroke carries a halo of compression: anything far enough from white is ink, per `utils.av.Ink`.

**The dataset draws crossings into both files already.** Where an artery passes over a vein, both
the artery page and the vein page carry the stroke — about 3,500 to 4,700 pixels an image — which is
the convention this store keeps anyway.

**The suffix is spelled seven different ways.** Ninety-three folders write `--arteries` and
`--veins`; the rest write `--artery`, `--artry`, `--atertries`, `--vein`, `--veisn` or `--veinds`,
and one folder files a drawing under a different photograph's id. The suffix is therefore matched
by what it most resembles rather than composed, per the skill's rule 13.9: a fetcher that builds
the path it expects reports a dataset with holes in it and no error.

**What the deposit does not hold.** The paper describes an arteriovenous ratio per image, optic
nerve head annotation, hard exudates, cotton-wool spots, and hypertensive retinopathy and
papilloedema labels. Neither version of the Mendeley deposit contains any of them: it is the
artery/vein drawings and nothing else. See `docs/datasets/avrdb.md`, section 7.

Layers
------
avrdb: the deposit's single zip — photographs and drawings. Required.
"""

import difflib
from pathlib import Path

from datasets.utils import archives, av, build, cli, fov, resolution

#: Slug, matching docs/datasets/avrdb.md and this module's filename.
SLUG = "avrdb"

SOURCES = [
    archives.Source(
        layer=SLUG,
        url=(
            "https://data.mendeley.com/public-files/datasets/3csr652p9y/files/"
            "5c07e45a-5f3f-407b-8bdb-16332a84fa23/file_downloaded"
        ),
        filename="AVRDB.zip",
        sha256="f0af3cc8714e1eaff5d2b5a3e0b77f8c6166a0d18322dd2685c2c6ed325fc230",
        licence="CC BY 4.0",
        extract_it=False,
    ),
]

#: Where the folders sit inside the archive.
ROOT = "AV"

#: The drawing each suffix holds, and the store layer it becomes. `--both` and `--map` are the
#: photograph with the vessels painted over it — a picture of the annotation, not the annotation —
#: and the `.ai` is the Illustrator file the three were drawn in; none of them is read.
DRAWINGS = {"arteries": "artery", "veins": "vein", "vessels": "vessels"}

#: What a suffix may be a misspelling of. `both` and `map` are here so that a mistyped `--vessels`
#: cannot be mistaken for the overlay, or the overlay for a drawing.
SUFFIXES = (*DRAWINGS, "both", "map")

#: How close a suffix must be to one of those to be taken for it. Measured against the deposit
#: rather than guessed: its worst misspelling, `--artry`, scores 0.62 against `arteries`, and the
#: two nearest *different* words — `veins` and `vessels` — score 0.50 against each other. Anything
#: between separates a typo from a confusion, and every other misspelling here scores 0.71 or more.
RESEMBLANCE = 0.6

#: How the drawings are read: ink on a white page. The threshold is `utils.av`'s default, which on
#: this dataset moves the annotated area by about 3% between 40 and 90 — the strokes are solid and
#: the halo around them is faint.
DRAWN = av.Ink()

#: Nothing here is left out: the deposit has no ultra-wide-field split and no second rendition.
SKIPPED: list[str] = []

#: The authors publish no scale and state no field angle. The camera is a Topcon TRC-NW8, whose
#: field is selectable, so nothing can be inferred from the model name either.
RESOLUTION = resolution.Declared(
    um_per_px=None,
    source="unknown",
    note=(
        "Neither the paper nor the deposit states microns per pixel, and the Topcon TRC-NW8's "
        "field angle is selectable and unstated. Run fetch_um_resolution."
    ),
)


def discover(layers: dict[str, Path]) -> list[build.SourceRecord]:
    """Every folder in the archive: one photograph and the drawings made on it."""
    archive = layers[SLUG]
    held: dict[str, dict[str, archives.Member]] = {}
    for member in archives.members(archive, under=f"{ROOT}/"):
        name = Path(member.name).name
        stem = Path(member.name).parent.name
        held.setdefault(stem, {})[name] = member

    records = []
    for stem in sorted(held):
        files = held[stem]
        photograph = next(
            (member for name, member in files.items() if "--" not in name
             and name.lower().endswith((".jpg", ".jpeg"))),
            None,
        )
        if photograph is None:
            raise LookupError(f"{stem} has drawings and no photograph")
        drawings = _drawings(files)
        maps = {DRAWINGS[suffix]: member for suffix, member in drawings.items()}
        missing = [suffix for suffix in DRAWINGS if suffix not in drawings]
        records.append(
            build.SourceRecord(
                key=stem.lower(),
                image=photograph,
                maps=maps,
                notes="; ".join(f"no {suffix} drawing is published" for suffix in missing),
            )
        )
    return records


def _drawings(files: dict[str, archives.Member]) -> dict[str, archives.Member]:
    """Which drawing each file in one folder holds, by what its suffix most resembles.

    The deposit misspells the suffix on seven of its hundred folders and files one drawing under
    another photograph's id, so nothing here composes a name: each file says what it is, as well as
    it can, and the closest of the known words wins. A file whose suffix resembles none of them is
    left alone rather than guessed at.
    """
    found: dict[str, archives.Member] = {}
    for name, member in files.items():
        if "--" not in name or not name.lower().endswith((".jpg", ".jpeg")):
            continue
        written = name.rsplit("--", 1)[1].rsplit(".", 1)[0].lower()
        closest = difflib.get_close_matches(written, SUFFIXES, n=1, cutoff=RESEMBLANCE)
        if closest and closest[0] in DRAWINGS and closest[0] not in found:
            found[closest[0]] = member
    return found


def main(argv: list[str] | None = None) -> int:
    """Entry point: ``uv run python -m datasets.avrdb``."""
    args = cli.parse(SLUG, argv)
    return build.run(
        slug=SLUG,
        sources=SOURCES,
        discover=discover,
        resolution_of=RESOLUTION,
        args=args,
        fov_strategy=fov.DETECT,
        skipped=SKIPPED,
        readers={layer: DRAWN for layer in DRAWINGS.values()},
    )


if __name__ == "__main__":
    raise SystemExit(main())
