# ABOUTME: VascX: one repository holding five models, cloned at a pinned commit, with the three
# ABOUTME: Eyened packages it runs on — two it does not declare, and one it does.

import os
from pathlib import Path

from .utils import source

# The library this runs checks for a newer release of itself on import. A benchmark run makes the
# network calls it declares and no others.
os.environ.setdefault("NO_ALBUMENTATIONS_UPDATE", "1")

#: The commit `docs/projects/vascx.md` describes, which is what a result here is attributable to.
COMMIT = "d0cde1c7f9b54718be9b8d4ec871a5849ca6e857"

#: **Cloned rather than installed**, although all four of these are on PyPI and were installed
#: until now.
#:
#: The reason is the one PVBM's module already records: a clone is the only way to read the code a
#: result came from without going to look at somebody's site-packages, and this is the upstream
#: this atlas has had to read most often. Every correction on `docs/projects/vascx.md` — that its
#: quality checkpoint resizes to 224 and names EyeQ, that its "Hubbard reduction" is Knudtson's
#: formula, that its sparsity is normalised by the optic-disc-to-fovea distance and so is not a
#: distance at all — came from reading these files. `add-upstream` §2 prefers an install for
#: anything pip-installable; §2.1 is where the exception is written down.
CODE = source.Checkout("vascx", "https://github.com/Eyened/retinalysis-vascx", COMMIT)

#: VascX runs its models through these two and **declares neither**, so the atlas pins them itself,
#: at the commits carrying the releases contemporary with the commit above — 0.7.1 and 1.3.0.
#:
#: `retinalysis-inference` 0.7.1 is the one pin here that is not a tag: its repository tags 0.7.0
#: and stops, and the release on PyPI is one commit later. The commit is identified by what that
#: commit did — it added the `pydantic` requirement, which 0.7.1's metadata carries and 0.7.0's
#: does not — rather than by a tag nobody pushed.
RUNNER = source.Checkout(
    "rtnls-inference",
    "https://github.com/Eyened/retinalysis-inference",
    "e5823fe0653fe3d5b7944088f6add1e3fdc4a3c8",
)
PREPARATION = source.Checkout(
    "rtnls-fundusprep",
    "https://github.com/Eyened/retinalysis-fundusprep",
    "ff47bfbda58782954264178ce14fbcd26f9b2fbd",
)

#: **A third Eyened package, and this one VascX does declare** — `retinalysis-enface==1.2.0`, which
#: `vascx.fundus.retina` imports at module load for its `OpticDisc` and `Fundus`. It is pinned here
#: for the same reason as the other two: installing it would leave the only readable copy of code
#: this atlas has corrected its own pages from inside site-packages.
ENFACE = source.Checkout(
    "rtnls-enface",
    "https://github.com/Eyened/retinalysis-enface",
    "ec1ca00a80b569bd7f2d67c7d9db07cd3efcb1f7",
)

#: All four, in the order their provenance is recorded. Each is a flat-layout repository — the
#: package sits at the repository root — so the tree itself goes on `sys.path` and the packages are
#: reached by their own names.
TREES = (CODE, RUNNER, PREPARATION, ENFACE)

#: **What a clone does not bring.** These four distributions declare the packages below, and
#: installing them is what used to put those in the environment; a clone brings the code and none
#: of the metadata, so `pyproject.toml` now pins them directly. The list is here rather than only
#: there so that a reader of this module can see what the four actually need, and `add-upstream`
#: §3 is the rule it follows: pin the release contemporary with the commit, and say why.
NEEDS = (
    "albumentations",
    "click",
    "GPUtil",
    "huggingface-hub",
    "lightning",
    "matplotlib",
    "monai",
    "nbstripout",
    "networkx",
    "opencv-python",
    "opencv-python-headless",
    "pydantic",
    "pydicom",
    "PyYAML",
    "simplejpeg",
    "sortedcontainers",
    "tqdm",
)

#: Where the weights are published: a repository and a file inside it, AGPL-3.0.
QUALITY_WEIGHTS = "Eyened/vascx:quality/quality.pt"


def on_path(root: Path | None = None) -> None:
    """Clone all four if they are not there, and put each on `sys.path`.

    All four together, every time, because they import one another: `vascx` reaches for
    `rtnls_enface` the moment `vascx.fundus.retina` is imported, and putting one tree on the path
    without the others would find whichever happens to be installed instead.
    """
    for tree in TREES:
        tree.on_path(root)


def model_file(published: str) -> Path:
    """One of the published checkpoints, downloaded on first use, without loading it.

    :param published: the repository and file, as `Eyened/vascx:disc/disc_july24.pt`.
    """
    from huggingface_hub import hf_hub_download

    repo, path = published.split(":")
    return Path(hf_hub_download(repo_id=repo, filename=path))


def quality_weights() -> Path:
    """The quality checkpoint, downloaded on first use, without loading it."""
    return model_file(QUALITY_WEIGHTS)


def quality_ensemble(device: str = "cpu") -> object:
    """The quality ensemble, a TorchScript file that carries its own training configuration —
    which is where the grid the network actually sees comes from, rather than any documentation."""
    on_path()
    from rtnls_inference.ensembles.ensemble_classification import ClassificationEnsemble

    ensemble = ClassificationEnsemble.from_huggingface(QUALITY_WEIGHTS).to(device)
    ensemble.eval()
    return ensemble


def provenance() -> dict[str, object]:
    return {
        **CODE.provenance(),
        "runner": RUNNER.provenance(),
        "preparation": PREPARATION.provenance(),
        "enface": ENFACE.provenance(),
        "pinned_here": list(NEEDS),
    }


def features():
    """VascX's feature machinery: the retina, its vessel layers, and the shipped feature sets.

    Imported here rather than at module level so that this module stays importable for its
    provenance alone, on a machine where nothing has been cloned yet.
    """
    on_path()
    from vascx.fundus import feature_sets
    from vascx.fundus.layer import VesselTreeLayer
    from vascx.fundus.retina import Retina
    from vascx.fundus.vessels_layer import FundusVesselsLayer

    return Retina, VesselTreeLayer, FundusVesselsLayer, feature_sets
