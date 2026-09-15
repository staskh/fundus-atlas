# ABOUTME: VascX: one repository holding five models, installed at a pinned commit, with the
# ABOUTME: two packages it needs to run them but does not declare.

import os
from pathlib import Path

from .utils import source

# The library this runs checks for a newer release of itself on import. A benchmark run makes the
# network calls it declares and no others.
os.environ.setdefault("NO_ALBUMENTATIONS_UPDATE", "1")

#: The repository the catalogue describes, installed rather than cloned.
CODE = source.Installed(
    "retinalysis-vascx",
    commit="d0cde1c7f9b54718be9b8d4ec871a5849ca6e857",
)

#: VascX runs its models through these two packages and declares neither of them as a dependency,
#: so the atlas pins them itself, at the releases contemporary with the commit above.
RUNNER = source.Installed("retinalysis-inference", version="0.7.1")
PREPARATION = source.Installed("retinalysis-fundusprep", version="1.3.0")

#: Where the weights are published: a repository and a file inside it, AGPL-3.0.
QUALITY_WEIGHTS = "Eyened/vascx:quality/quality.pt"


def quality_weights() -> Path:
    """The published checkpoint, downloaded on first use, without loading it."""
    from huggingface_hub import hf_hub_download

    repo, path = QUALITY_WEIGHTS.split(":")
    return Path(hf_hub_download(repo_id=repo, filename=path))


def quality_ensemble(device: str = "cpu") -> object:
    """The quality ensemble, a TorchScript file that carries its own training configuration —
    which is where the grid the network actually sees comes from, rather than any documentation."""
    from rtnls_inference.ensembles.ensemble_classification import ClassificationEnsemble

    ensemble = ClassificationEnsemble.from_huggingface(QUALITY_WEIGHTS).to(device)
    ensemble.eval()
    return ensemble


def provenance() -> dict[str, object]:
    return {
        **CODE.provenance(),
        "runner": RUNNER.provenance(),
        "preparation": PREPARATION.provenance(),
    }
