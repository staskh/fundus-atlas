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

from datasets.utils import archives, build, cli, contours, fov, manifest, quality, resolution

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

#: Columns this dataset publishes that no other does, appended after `notes`. Values verbatim, in
#: the dataset's own units and vocabulary. Repeat each description in the page's "How to fetch".
EXTRA_COLUMNS = [
    manifest.Column("<name>", "<what it holds, and in what units>"),
]

#: How `quality` is arrived at. `quality.PUBLISHED` where the dataset states an overall grade;
#: `quality.FromComponents({...})` where it publishes only per-aspect ratings, each entry naming the
#: value that counts as full marks; `None` where the dataset grades nothing. See the skill, 5.4.
QUALITY = None

#: Native resolution. Declared here, derivation in the comment, source one of the five in the skill.
RESOLUTION = resolution.Declared(
    um_per_px=None,          # microns per pixel; None -> `unknown`, and consumers report pixels
    source="unknown",
    note="<derivation, or why it cannot be established>",
)


def discover(raw_root: Path) -> list[build.SourceRecord]:
    """Enumerate what the extracted tree holds.

    :param raw_root: the extracted archive.
    :return: one record per image, with the paths of its maps and the metadata the manifest needs.
        Where a dataset names its graders, give every grader's reading in the record's ``labels``
        rather than choosing one: ``manifest`` writes both ``labels.csv`` and the manifest cell.
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
        # How disc/cup reach the native frame: COORDINATES translates what the authors published,
        # RASTER traces the native mask once. Every size is scaled from native either way; see the
        # skill, section 10.
        contour_source=contours.COORDINATES,
        extra_columns=EXTRA_COLUMNS,
        quality=QUALITY,
        args=args,
    )


if __name__ == "__main__":
    raise SystemExit(main())
