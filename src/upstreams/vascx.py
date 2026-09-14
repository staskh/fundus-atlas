# ABOUTME: VascX: one repository holding five models, installed at a pinned commit, with the
# ABOUTME: two packages it needs to run them but does not declare.

from pathlib import Path

from .utils import source

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


def quality_ensemble(device: str = "cpu") -> tuple[object, Path]:
    """The quality ensemble and the checkpoint it was loaded from.

    The checkpoint is a TorchScript ensemble that carries its own training configuration, which is
    where the grid the network actually sees comes from rather than from any documentation.
    """
    from rtnls_inference.ensembles.ensemble_classification import ClassificationEnsemble

    ensemble = ClassificationEnsemble.from_huggingface(QUALITY_WEIGHTS).to(device)
    ensemble.eval()
    return ensemble, Path(ensemble.fpath)


def provenance() -> dict[str, object]:
    return {
        **CODE.provenance(),
        "runner": RUNNER.provenance(),
        "preparation": PREPARATION.provenance(),
    }
