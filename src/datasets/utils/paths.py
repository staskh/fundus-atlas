# ABOUTME: Where a store lives on disk and what its directories are called.
# ABOUTME: One place, so two fetchers cannot lay out their stores differently.

import os
from argparse import Namespace
from pathlib import Path

#: Overrides the store root for every dataset at once.
ENV_VAR = "FUNDUS_ATLAS_DATA"

#: The default root: beside the repository, and git-ignored. Stores are caches, not sources.
DEFAULT_ROOT = Path(__file__).resolve().parents[3] / "data"

#: The frame every size is built from, and the one that must never be deleted.
NATIVE = "native"


def root(args: Namespace | None = None) -> Path:
    """The store root, from the command line, the environment, or the repository default."""
    if args is not None and getattr(args, "data_root", None):
        return Path(args.data_root)
    return Path(os.environ.get(ENV_VAR, DEFAULT_ROOT))


def store(args: Namespace) -> Path:
    """One dataset's directory."""
    return root(args) / args.slug


def frame(store: Path, size: int | str) -> Path:
    """The directory holding one grid: ``native`` or a pixel size."""
    return store / str(size)


def layer(store: Path, size: int | str, name: str) -> Path:
    """The directory holding one kind of map at one grid: ``images``, ``vessels``, ``fov``."""
    return frame(store, size) / name
