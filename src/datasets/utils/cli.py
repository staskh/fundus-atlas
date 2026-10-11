# ABOUTME: The command-line contract every fetcher accepts, with the same flags and meanings.
# ABOUTME: Defined once so running a new fetcher needs no new instructions.

import argparse
import os
from argparse import Namespace


def parse(slug: str, argv: list[str] | None = None) -> Namespace:
    """Parse a fetcher's arguments.

    :param slug: the dataset, carried on the result so helpers need no second argument.
    """
    parser = argparse.ArgumentParser(
        prog=f"python -m datasets.{slug}",
        description=f"Fetch {slug} and build the standard store. See docs/datasets/{slug}.md.",
    )
    parser.add_argument("--archive", help="an archive already on disk, instead of downloading")
    parser.add_argument("--raw", help="an already-extracted tree, skipping download and extraction")
    parser.add_argument("--data-root", help="override the store root")
    parser.add_argument(
        "--keep-raw",
        action="store_true",
        help="keep the download after building; the default deletes it",
    )
    parser.add_argument("--force", action="store_true", help="rebuild even if the store looks done")
    parser.add_argument("--limit", type=int, help="build only the first N images, for development")
    parser.add_argument(
        "--jobs",
        type=int,
        default=os.cpu_count() or 1,
        help="how many images to build at once (default: one per core; 1 to build in this process)",
    )
    parser.add_argument(
        "--no-verify",
        dest="verify",
        action="store_false",
        help="skip checksum verification; prints a warning",
    )
    args = parser.parse_args(argv)
    args.slug = slug
    return args
