# ABOUTME: AutoMorph: a pipeline of stages rather than a package, cloned at a pinned commit and
# ABOUTME: imported one stage at a time. Its weights are committed in the repository.

from pathlib import Path

from .utils import source

#: The quality stage, and the only part of AutoMorph this atlas checks out. The pipeline itself is
#: not benchmarked — its two children are — but this model is reached from neither of them.
QUALITY_STAGE = "M1_Retinal_Image_quality_EyePACS"

CODE = source.Checkout(
    "automorph",
    "https://github.com/rmaphoh/AutoMorph",
    "9a953e5edfa419b454e9fb7b06235eb413828d05",
    subtrees=[QUALITY_STAGE],
    imports_from=QUALITY_STAGE,
)

#: Where the eight seeds live inside the checkout.
QUALITY_WEIGHTS = f"{QUALITY_STAGE}/Retinal_quality/EyePACS_quality/efficientnet"


def quality_weights() -> list[Path]:
    """The eight seeds of the quality ensemble, committed in the repository."""
    tree = CODE.obtain()
    checkpoints = sorted((tree / QUALITY_WEIGHTS).glob("*/best_loss_checkpoint.pth"))
    if len(checkpoints) != 8:
        raise RuntimeError(
            f"expected the eight seeds of the quality ensemble in {tree / QUALITY_WEIGHTS}, "
            f"found {len(checkpoints)}"
        )
    return checkpoints


def quality_stage() -> object:
    """The stage's own model module, reached because its directory is on ``sys.path``."""
    CODE.on_path()
    import model

    return model


def provenance() -> dict[str, object]:
    return CODE.provenance()
