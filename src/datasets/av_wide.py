# ABOUTME: Fetcher for AV-WIDE — REYIA's 26 ultra-wide-field photographs, re-annotated from WIDE and
# ABOUTME: built from REYIA's archive into a store of their own, so they are never pooled with 45°.

"""AV-WIDE fetcher.

AV-WIDE is not a release of its own: it is the `AVWIDE` folder of [REYIA](../../docs/datasets/reyia.md)'s
link-shared Kaggle archive — 26 of [WIDE](../../docs/datasets/wide.md)'s 30 Optos 200Tx photographs,
reduced from 3900×3072 to squares of 1217 to 1631 pixels, the photograph letterboxed in black, and
annotated for arteries and veins. The REYIA fetcher leaves it
out, because a 200° photograph is a different instrument from the 30–45° cameras of every other
subset; this one builds it, and only it, from the same archive, read the same way.

Layers
------
av-wide: REYIA's Kaggle archive, by hand. Required.
"""

from dataclasses import replace
from pathlib import Path

from datasets import reyia
from datasets.utils import build, cli, fov, resolution

#: Slug of this store. The photographs are catalogued on docs/datasets/reyia.md, as its AV-WIDE
#: layer, and the original release on docs/datasets/wide.md.
SLUG = "av-wide"

#: REYIA's archive, which is the only place these renditions are published.
SOURCES = [replace(reyia.SOURCES[0], layer=SLUG)]

#: The one subset built here.
SUBSETS = ("AVWIDE",)

#: REYIA's colours, since these are REYIA's label maps.
PALETTE = reyia.PALETTE

#: An Optos frame has no circular field to find: a circle fitted to its edge pushed photographs off
#: centre and padded up to a third of the square with nothing, so the frame is kept as it is.
FIELD = fov.WHOLE

#: Everything else in the archive belongs to the REYIA store, or to nobody.
SKIPPED = [
    "every REYIA subset but AVWIDE, which datasets.reyia builds",
    "the 7,712 files of REYIA/GENERATED_IMAGES, which are not photographs of eyes",
]

#: Neither REYIA nor WIDE states a scale for the rendition. An ultra-wide-field image is not one
#: scale across its field either: projection stretches the periphery, so a scale inferred at the
#: optic disc holds near the disc and nowhere else.
RESOLUTION = resolution.Declared(
    um_per_px=None,
    source="unknown",
    note=(
        "REYIA's square renditions of 3900x3072 Optos 200Tx photographs; no scale is published "
        "for either, and an ultra-wide-field image has none that holds across its field."
    ),
)


def discover(layers: dict[str, Path]) -> list[build.SourceRecord]:
    """Every AV-WIDE photograph in REYIA's archive, as REYIA's fetcher would read it."""
    return reyia.discover({reyia.SLUG: layers[SLUG]}, subsets=SUBSETS)


def verify(store: Path, layers: dict[str, Path], rows: list[dict[str, str]]) -> dict[str, object]:
    """REYIA's check of the label maps against the binaries the archive also publishes."""
    return reyia.verify(store, {reyia.SLUG: layers[SLUG]}, rows)


def main(argv: list[str] | None = None) -> int:
    """Entry point: ``uv run python -m datasets.av_wide --archive <REYIA's Kaggle zip>``."""
    args = cli.parse(SLUG, argv)
    return build.run(
        slug=SLUG,
        sources=SOURCES,
        discover=discover,
        resolution_of=RESOLUTION,
        args=args,
        fov_strategy=FIELD,
        extra_columns=reyia.EXTRA_COLUMNS,
        skipped=SKIPPED,
        readers={"av": PALETTE},
        verify=verify,
    )


if __name__ == "__main__":
    raise SystemExit(main())
