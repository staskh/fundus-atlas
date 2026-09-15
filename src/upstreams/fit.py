# ABOUTME: The Fundus Image Toolbox: where the code comes from, where its weights are cached, and
# ABOUTME: how one of its models is loaded. One module per repository, whatever it holds.

from pathlib import Path

from .utils import paths, source

#: Installed rather than cloned, at the commit its model pages describe. The toolbox publishes
#: releases to PyPI as well, but the release trails the repository by months and the catalogue
#: describes the repository.
CODE = source.Installed(
    "fundus-image-toolbox",
    commit="d7757e28fbf639856b53cfe00019f605af8c1f17",
)

#: Where the quality ensemble's weights come from, fetched by the toolbox itself on first use.
QUALITY_WEIGHTS = "https://zenodo.org/records/11174749/files/weights.tar.gz"


def quality_weights() -> list[Path]:
    """The ensemble's ten checkpoints, downloaded on first use, without loading them."""
    from fundus_image_toolbox.quality_prediction.scripts.model import download_weights

    cache = paths.weights("fit")
    cache.mkdir(parents=True, exist_ok=True)
    return sorted(Path(download_weights(cache_dir=cache)).rglob("*.pth"))


def quality_ensemble(device: str = "cpu") -> list:
    """The ten-member quality ensemble, as the toolbox returns it."""
    from fundus_image_toolbox.quality_prediction import load_quality_ensemble

    cache = paths.weights("fit")
    cache.mkdir(parents=True, exist_ok=True)
    return load_quality_ensemble(device=device, cache_dir=cache)


def provenance() -> dict[str, object]:
    return CODE.provenance()
