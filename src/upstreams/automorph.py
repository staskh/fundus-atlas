# ABOUTME: AutoMorph: a pipeline of stages rather than a package, cloned at a pinned commit and
# ABOUTME: imported one stage at a time. Its weights are committed in the repository.

import json
from pathlib import Path

from .utils import source

#: The two stages of AutoMorph this atlas checks out, each holding one catalogued model. The
#: pipeline itself is not benchmarked — its two children are — but these models are reached from
#: neither of them.
QUALITY_STAGE = "M1_Retinal_Image_quality_EyePACS"
DISC_STAGE = "M2_lwnet_disc_cup"

CODE = source.Checkout(
    "automorph",
    "https://github.com/rmaphoh/AutoMorph",
    "9a953e5edfa419b454e9fb7b06235eb413828d05",
    subtrees=[QUALITY_STAGE, DISC_STAGE],
    imports_from=QUALITY_STAGE,
)

#: Where the eight seeds of each ensemble live inside the checkout. The disc-and-cup folder is
#: named for a resolution nothing in the shipped inference runs at: every one of its configurations
#: says 512.
QUALITY_WEIGHTS = f"{QUALITY_STAGE}/Retinal_quality/EyePACS_quality/efficientnet"
DISC_WEIGHTS = f"{DISC_STAGE}/experiments/wnet_All_three_1024_disc_cup"


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


def disc_weights() -> list[Path]:
    """The eight seeds of the disc-and-cup ensemble, one per random seed."""
    tree = CODE.obtain()
    checkpoints = sorted((tree / DISC_WEIGHTS).glob("*/model_checkpoint.pth"))
    if len(checkpoints) != 8:
        raise RuntimeError(
            f"expected the eight seeds of the disc-and-cup ensemble in {tree / DISC_WEIGHTS}, "
            f"found {len(checkpoints)}"
        )
    return checkpoints


def disc_configuration() -> list[dict[str, object]]:
    """What each seed was trained with, read rather than assumed."""
    tree = CODE.obtain()
    return [
        json.loads(path.read_text()) for path in sorted((tree / DISC_WEIGHTS).glob("*/config.cfg"))
    ]


def disc_architecture() -> object:
    """The stage's own model factory.

    Its folder is called `models`, which is what this repository calls its adapters, so it is
    imported under a name of ours rather than put on ``sys.path``.
    """
    stage = source.package("automorph_lwnet", CODE.obtain() / DISC_STAGE / "models")
    return stage.get_model.get_arch


def quality_stage() -> object:
    """The stage's own model module, reached because its directory is on ``sys.path``."""
    CODE.on_path()
    import model

    return model


def provenance() -> dict[str, object]:
    return CODE.provenance()
