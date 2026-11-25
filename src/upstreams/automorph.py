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
VESSEL_STAGE = "M2_Vessel_seg"

#: The measurement stage, which is where AutoMorph's biomarkers are computed. It holds no model:
#: it reads the masks the M2 stages wrote and turns them into numbers, which is why it is reached
#: by the biomarker adapter rather than by any model adapter.
FEATURE_STAGE = "M3_feature_whole_pic"
FEATURE_ZONE_STAGE = "M3_feature_zone"

CODE = source.Checkout(
    "automorph",
    "https://github.com/rmaphoh/AutoMorph",
    "9a953e5edfa419b454e9fb7b06235eb413828d05",
    subtrees=[QUALITY_STAGE, DISC_STAGE, AV_STAGE, VESSEL_STAGE, FEATURE_STAGE, FEATURE_ZONE_STAGE],
    imports_from=QUALITY_STAGE,
)

#: Where the eight seeds of each ensemble live inside the checkout. The disc-and-cup folder is
#: named for a resolution nothing in the shipped inference runs at: every one of its configurations
#: says 512.
QUALITY_WEIGHTS = f"{QUALITY_STAGE}/Retinal_quality/EyePACS_quality/efficientnet"
DISC_WEIGHTS = f"{DISC_STAGE}/experiments/wnet_All_three_1024_disc_cup"
AV_WEIGHTS = f"{AV_STAGE}/ALL-AV"
VESSEL_WEIGHTS = f"{VESSEL_STAGE}/Saved_model/train_on_ALL-SIX"

#: The three checkpoints each artery/vein seed is, in the order `test_outside.py` loads them.
AV_CHECKPOINTS = ("CP_best_F1_A.pth", "CP_best_F1_V.pth", "CP_best_F1_all.pth")

#: The ten seeds of the vessel ensemble, as `test_outside_integrated.py` names them — every even
#: number from 24 to 42, each a folder of its own holding one checkpoint.
VESSEL_SEEDS = tuple(range(24, 44, 2))

#: What every vessel seed folder is called, and the one checkpoint inside it.
VESSEL_JOB = "20210630_uniform_thres40_ALL-SIX"
VESSEL_CHECKPOINT = "G_best_F1_epoch.pth"


def measurements():
    """`retipy.tortuosity_measures` and `retipy.retina` from the whole-picture stage.

    AutoMorph's measuring is retipy's, vendored into the stage rather than installed, so it is
    reached by putting the stage's own `retipy` package on the path and importing it by name.
    """
    import sys

    tree = CODE.obtain()
    entry = str(tree / FEATURE_STAGE / "retipy")
    if entry not in sys.path:
        sys.path.insert(0, entry)
    from retipy import retina, tortuosity_measures

    return tortuosity_measures, retina


def retipy_config() -> dict[str, float]:
    """The thresholds in the feature stages' `resources/retipy.config`, read by retipy's own
    `Configuration`, as every driver reads them."""
    import importlib

    measurements()
    configuration = importlib.import_module("retipy.configuration")
    read = configuration.Configuration(
        str(CODE.obtain() / FEATURE_STAGE / "retipy" / "resources" / "retipy.config")
    )
    return {
        "pixels_per_window": read.pixels_per_window,
        "sampling_size": read.sampling_size,
        "r_2_threshold": read.r_2_threshold,
    }


#: The top-level module names the two feature stages both own. Each stage vendors its own
#: `retipy`, and its modules import each other by that absolute name, so the zone stage's copy can
#: only be imported with the whole-picture copy's modules out of the way.
_STAGE_MODULES = ("retipy", "function_")

_ZONE: tuple | None = None


def zone_measurements():
    """`retipy.tortuosity_measures` and `retipy.retina` from the **zone** stage.

    It is a second copy of retipy whose `evaluate_window` returns thirteen values rather than six —
    the same six, then the Hubbard and Knudtson equivalents — and whose width sampling multiplies
    by the image's scale. Both stages call it `retipy`, so it is imported with the other copy's
    modules set aside, and those are put back afterwards: each stage's functions keep the modules
    they were imported with, so both live in one process.
    """
    global _ZONE
    if _ZONE is not None:
        return _ZONE
    import importlib
    import sys

    entry = str(CODE.obtain() / FEATURE_ZONE_STAGE / "retipy")
    saved = _set_aside(_STAGE_MODULES)
    sys.path.insert(0, entry)
    try:
        measures = importlib.import_module("retipy.tortuosity_measures")
        retina = importlib.import_module("retipy.retina")
    finally:
        sys.path.remove(entry)
        _set_aside(_STAGE_MODULES)
        sys.modules.update(saved)
    _ZONE = (measures, retina)
    return _ZONE


def driver(stage: str, filename: str, names: tuple[str, ...], **settings: object) -> dict:
    """Functions from one of AutoMorph's driver scripts, exactly as its source has them.

    The functions that turn a segmentation into what the feature stage reads — `filter_frag`, which
    cleans and skeletonises the M2 maps, and `optic_disc_centre`, which measures the disc and cup
    and cuts zones B and C — live in scripts whose top level imports the segmentation networks and
    parses a command line. So the script is not imported: its source is parsed, and only the named
    functions are executed, with those of its own import lines that they use. The text that runs is
    upstream's, at the pinned commit; nothing is rewritten. A module the script imports from its
    own folder (`FD_cal`) is imported from that folder and set aside again afterwards, because two
    stages ship modules under one name.

    :param settings: module-level names the functions read, such as `AUTOMORPH_DATA`.
    """
    import ast
    import sys

    folder = CODE.obtain() / stage
    tree = ast.parse((folder / filename).read_text())
    wanted = [node for node in tree.body if isinstance(node, ast.FunctionDef)]
    wanted = [node for node in wanted if node.name in names]
    if {node.name for node in wanted} != set(names):
        raise LookupError(
            f"{filename} defines none of {sorted(set(names) - {n.name for n in wanted})}"
        )
    used = {node.id for fn in wanted for node in ast.walk(fn) if isinstance(node, ast.Name)}
    imports = [
        node
        for node in tree.body
        if isinstance(node, ast.Import | ast.ImportFrom)
        and any((alias.asname or alias.name).split(".")[0] in used for alias in node.names)
    ]
    local = tuple(
        path.stem if path.suffix == ".py" else path.name
        for path in folder.iterdir()
        if path.suffix == ".py" or path.is_dir()
    )
    namespace: dict = {"__name__": f"automorph_{stage}_{filename}", **settings}
    saved = _set_aside(local)
    sys.path.insert(0, str(folder))
    try:
        exec(  # noqa: S102 — upstream's own function source, at the pinned commit
            compile(ast.Module(body=imports + wanted, type_ignores=[]), filename, "exec"), namespace
        )
    finally:
        sys.path.remove(str(folder))
        _set_aside(local)
        sys.modules.update(saved)
    return namespace


def _set_aside(names: tuple[str, ...]) -> dict:
    """Remove every loaded module under these top-level names, and return what was removed."""
    import sys

    return {key: sys.modules.pop(key) for key in list(sys.modules) if key.split(".")[0] in names}


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


def vessel_folder(seed: int) -> str:
    """Where one seed of the vessel ensemble lives, inside the checkout."""
    return f"{VESSEL_WEIGHTS}/{VESSEL_JOB}_savebest_randomseed_{seed}"


def vessel_weights() -> list[Path]:
    """The ten checkpoints of the vessel ensemble, one per seed, committed in the repository."""
    tree = CODE.obtain()
    checkpoints = [tree / vessel_folder(seed) / VESSEL_CHECKPOINT for seed in VESSEL_SEEDS]
    missing = [path for path in checkpoints if not path.exists()]
    if missing:
        raise RuntimeError(
            f"expected the ten seeds of the vessel ensemble under {tree / VESSEL_WEIGHTS}; "
            f"{len(missing)} are missing, the first being {missing[0]}"
        )
    return checkpoints


def vessel_architecture() -> object:
    """The stage's own `Segmenter`, a U-Net emitting one logit per pixel.

    Its module is called `model`, which the quality stage also owns, so it is bound to a name of
    ours rather than reached through ``sys.path``.
    """
    stage = source.package(
        "automorph_vessel", CODE.obtain() / VESSEL_STAGE, modules=["model", "utils"]
    )
    return stage.model.Segmenter


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
