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
AV_STAGE = "M2_Artery_vein"

CODE = source.Checkout(
    "automorph",
    "https://github.com/rmaphoh/AutoMorph",
    "9a953e5edfa419b454e9fb7b06235eb413828d05",
    subtrees=[QUALITY_STAGE, DISC_STAGE, AV_STAGE],
    imports_from=QUALITY_STAGE,
)

#: Where the eight seeds of each ensemble live inside the checkout. The disc-and-cup folder is
#: named for a resolution nothing in the shipped inference runs at: every one of its configurations
#: says 512.
QUALITY_WEIGHTS = f"{QUALITY_STAGE}/Retinal_quality/EyePACS_quality/efficientnet"
DISC_WEIGHTS = f"{DISC_STAGE}/experiments/wnet_All_three_1024_disc_cup"
AV_WEIGHTS = f"{AV_STAGE}/ALL-AV"

#: The three checkpoints each artery/vein seed is, in the order `test_outside.py` loads them.
AV_CHECKPOINTS = ("CP_best_F1_A.pth", "CP_best_F1_V.pth", "CP_best_F1_all.pth")


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


def av_seeds() -> list[Path]:
    """The eight artery/vein seed folders, each holding the three checkpoints of one seed."""
    tree = CODE.obtain()
    folders = sorted((tree / AV_WEIGHTS).glob("*/Discriminator_unet"))
    if len(folders) != 8:
        raise RuntimeError(
            f"expected the eight seeds of the artery/vein ensemble in {tree / AV_WEIGHTS}, "
            f"found {len(folders)}"
        )
    return folders


def av_weights() -> list[Path]:
    """Every checkpoint the artery/vein ensemble loads: three per seed, twenty-four in all."""
    return [folder / name for folder in av_seeds() for name in AV_CHECKPOINTS]


def av_architecture() -> object:
    """The stage's own generators.

    Its folder is called `scripts`, as BF-Net's own is, so it is bound to a name of ours rather
    than put on ``sys.path``; only `model` is imported, because its siblings reach for a training
    stack nothing here installs.
    """
    stage = source.package("automorph_av", CODE.obtain() / AV_STAGE / "scripts", modules=["model"])
    return stage.model


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
