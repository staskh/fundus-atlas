# ABOUTME: OCULAR: the repository behind OCULARNet, cloned at a pinned commit for its architecture
# ABOUTME: factory, with the weights published separately on an anonymous review account.

from pathlib import Path

from .utils import paths, source, weights

#: The repository the catalogue describes. Only its `utils/` is needed: the architecture is built by
#: `segmentation_models_pytorch` from a name, and the weights are published elsewhere.
CODE = source.Checkout(
    "ocular",
    "https://github.com/GonzaloPlaaza/OCULAR",
    "34b1ecc3a31a211987d5b05ed7643278b525d1ff",
    imports_from="",
)

#: Where the weights are published, and what they are. The account is an **anonymous review
#: account**, which the model's page warns may be renamed when a paper appears — so the digest below
#: is what says whether the file that arrives is the one this atlas measured.
PUBLISHED = "https://huggingface.co/Anon-User-Retina/OCULARNet/resolve/main/OCULARNet.pth"
SHA256 = "88eec1d78ec9328927c0159fbd99c21acc613628a1b46286e644d792f3f1df75"

#: The nano variant's five folds were published on the same account and **are gone**: the URLs its
#: page records answer 401, and the account now holds one repository. Recorded here rather than in a
#: comment somewhere, because a benchmark that declares the model needs to say why it cannot run it.
NANO_WITHDRAWN = (
    "OCULARNet-nano's five checkpoints were published on the same anonymous account and are no "
    "longer served: nano_f1.pth through nano_f5.pth answer HTTP 401, and the account now holds only "
    "OCULARNet. Checked 2026-09-17."
)

#: The architecture name its own inference script passes, and the classes it emits.
ARCHITECTURE = "base_unet_repvgg_b3"
CLASSES = ("background", "artery", "vein", "crossing")


def model_file() -> Path:
    """The checkpoint, fetched once and checked against the digest above."""
    return weights.fetch(PUBLISHED, paths.weights("ocular") / "OCULARNet.pth", SHA256)


def architecture(classes: int = len(CLASSES)):
    """The network its own factory builds, called rather than transcribed.

    `base_unet_repvgg_b3` with three input channels and four classes is what `inference.py` asks
    for. Building it here from the repository's `get_model` means a checkpoint that stops loading is
    a change in their code rather than a mistake in my reading of it — and the folder is imported
    under a name of ours, since `utils` is what half of Python calls something.
    """
    factory = source.package("ocular_utils", CODE.obtain() / "utils", modules=["get_model"])
    return factory.get_model.get_model(ARCHITECTURE, num_classes=classes, in_c=3)


def provenance() -> dict[str, object]:
    return {**CODE.provenance(), "weights": {"url": PUBLISHED, "sha256": SHA256}}


def geometry():
    """OCULAR's `GeometricalVBMs`: PVBM's measuring code as this project modified it.

    The class imports PVBM's helpers at runtime, so PVBM must be installed for it to load — which
    is the whole point of cataloguing the two together.

    **Loaded by path, under a name of its own.** It lives in a package called `utils`, and so does
    AutoMorphalyzer's measuring code; whichever upstream is imported first takes that name for the
    process. Reaching this one through the bare name therefore returns the wrong module once both
    are in play, and it does so **silently** — the class still loads and still measures, and only
    the numbers change. That was caught here by a test comparing OCULAR's tortuosity with PVBM's,
    which it imports and must agree with.
    """
    import importlib.util
    import sys

    name = "ocular_geometrical_vbms"
    loaded = sys.modules.get(name)
    if loaded is None:
        source_file = CODE.obtain() / "utils" / "GeometricalVBMs.py"
        spec = importlib.util.spec_from_file_location(name, source_file)
        loaded = importlib.util.module_from_spec(spec)
        sys.modules[name] = loaded
        spec.loader.exec_module(loaded)
    return loaded.GeometricalVBMs
