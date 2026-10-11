# ABOUTME: Where a store lives on disk and what its directories are called.
# ABOUTME: One place, so two fetchers cannot lay out their stores differently.

import os
from argparse import Namespace
from pathlib import Path

#: Overrides the store root for every dataset at once.
ENV_VAR = "FUNDUS_ATLAS_DATA"

#: The default root: inside the repository, hidden and git-ignored. Stores are caches, not
#: sources, and the dot keeps them out of the way of anything the repository itself publishes.
DEFAULT_ROOT = Path(__file__).resolve().parents[3] / ".atlas_data"

#: The one frame a store keeps: the field-of-view crop at full resolution. Any size a model needs
#: is made from it when it is read.
CROP = "crop"


def root(args: Namespace | None = None) -> Path:
    """The store root, from the command line, the environment, or the repository default."""
    if args is not None and getattr(args, "data_root", None):
        return Path(args.data_root)
    return Path(os.environ.get(ENV_VAR, DEFAULT_ROOT))


def store(args: Namespace) -> Path:
    """One dataset's directory."""
    return root(args) / args.slug


def layer(store: Path, name: str) -> Path:
    """The directory holding one kind of map in the crop: ``images``, ``vessels``, ``fov``."""
    return store / CROP / name
