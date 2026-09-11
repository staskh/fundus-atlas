# ABOUTME: Fetcher for <DATASET> — downloads, verifies, crops to the field of view and builds the store.
# ABOUTME: See docs/datasets/<slug>.md for provenance, licence and the access route.

"""<DATASET> fetcher.

<One paragraph: what arrives, in what layout, and anything peculiar about it — an archive format
needing an external tool, a labels spreadsheet, a mask palette, files that must be skipped.>

Layers
------
<One line per download, with what it supplies and whether it is optional.>
"""

from pathlib import Path

from datasets.utils import archives, build, cli, contours, fov, manifest, resolution

#: Slug, matching docs/datasets/<slug>.md and this module's filename.
SLUG = "<slug>"

#: Source downloads. A `⛔` dataset declares its route instead of a URL and sets `manual=True`.
SOURCES = [
    archives.Source(
        layer="<slug>",
        url="<https://…>",
        sha256="<…>",
        licence="<as the dataset page states it>",
        optional=False,
    ),
]

#: Native resolution. Declared here, derivation in the comment, source one of the five in the skill.
RESOLUTION = resolution.Declared(
    mm_per_px=None,          # None -> `unknown`, and consumers report pixels
    source="unknown",
    note="<derivation, or why it cannot be established>",
)


def discover(raw_root: Path) -> list[build.SourceRecord]:
    """Enumerate what the extracted tree holds.

    :param raw_root: the extracted archive.
    :return: one record per image, with the paths of its maps and the metadata the manifest needs.
    """
    raise NotImplementedError


def main(argv: list[str] | None = None) -> int:
    """Entry point: ``uv run python -m datasets.<slug>``."""
    args = cli.parse(SLUG, argv)
    return build.run(
        slug=SLUG,
        sources=SOURCES,
        discover=discover,
        resolution=RESOLUTION,
        fov_strategy=fov.FROM_MASK,   # or fov.DETECT, or fov.FULL_FRAME
        # How disc/cup reach the store: COORDINATES transforms what the authors published,
        # RASTER resamples the mask at each size and traces it there. See the skill, section 9.
        contour_source=contours.COORDINATES,
        args=args,
    )


if __name__ == "__main__":
    raise SystemExit(main())
