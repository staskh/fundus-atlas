# ABOUTME: AutoMorphClass's feature calculation, pinned and reached as a package: AutoMorph's
# ABOUTME: measurements reimplemented as a PyTorch module, called here for the vessel features only.

from .utils import source

#: The commit `docs/projects/automorphclass.md` §1 describes. The repository publishes no tags or
#: releases, so a commit is the only pin available.
COMMIT = "8f4d18fe961aeec1f52df55d7f174f9f3baad812"

#: `pytorch_automorph` lives under `src/`, so that is what goes on the path.
CODE = source.Checkout(
    "automorphclass",
    "https://github.com/kikatuso/AutoMorphClass",
    COMMIT,
    imports_from="src",
)


def features():
    """`pytorch_automorph.feature_calculation`, for `Vessel_Features`.

    Only the vessel half is reached. Its optic disc and cup features need a cup segmentation, which
    a biomarker adapter is not handed — the cup-to-disc ratio is measured against ophthalmologists'
    own outlines in the disc benchmark instead.
    """
    CODE.on_path()
    from pytorch_automorph import feature_calculation as module

    return module


def provenance() -> dict[str, object]:
    """What a run records about the code that produced the number."""
    return CODE.provenance()
