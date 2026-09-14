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


def quality_ensemble(device: str = "cpu") -> tuple[list, list[Path]]:
    """The ten-member quality ensemble, and the checkpoint files it loaded.

    :return: the ensemble as the toolbox returns it, and the weight files, so the run can record
        which weights produced its numbers.
    """
    from fundus_image_toolbox.quality_prediction import load_quality_ensemble

    cache = paths.weights("fit")
    cache.mkdir(parents=True, exist_ok=True)
    ensemble = load_quality_ensemble(device=device, cache_dir=cache)
    return ensemble, sorted(cache.rglob("*.pth"))


def provenance() -> dict[str, object]:
    return CODE.provenance()
