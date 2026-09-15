# ABOUTME: Where third-party code and its weights live on disk, and what the directories are called.
# ABOUTME: One place, so two upstreams cannot disagree about where a checkout goes.

import os
from pathlib import Path

#: Overrides the checkout root for every upstream at once.
ENV_VAR = "FUNDUS_ATLAS_CODE"

#: The default root: inside the repository, hidden and git-ignored. Third-party code is fetched,
#: never committed, and the leading dot also keeps it out of pytest collection and linting.
DEFAULT_ROOT = Path(__file__).resolve().parents[3] / ".atlas_code"

#: Where a downloaded weight file is cached, under the root, per upstream.
WEIGHTS = "weights"


def root() -> Path:
    """The checkout root, from the environment or the repository default."""
    return Path(os.environ.get(ENV_VAR, DEFAULT_ROOT))


def checkout(slug: str) -> Path:
    """One upstream's working tree."""
    return root() / slug


def weights(slug: str) -> Path:
    """Where one upstream's downloaded weights are cached."""
    return root() / WEIGHTS / slug
