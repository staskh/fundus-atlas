# ABOUTME: LUNet: a Keras model committed in its own repository, read through the Keras 2
# ABOUTME: compatibility layer because a current Keras cannot deserialise a 2.11 layer config.

import os
from pathlib import Path

from .utils import source

#: Reading a Keras 2 checkpoint needs the compatibility implementation rather than Keras 3, and this
#: is how TensorFlow is told so. Set before anything imports keras, which is why it sits here.
os.environ.setdefault("TF_USE_LEGACY_KERAS", "1")

#: The repository, which holds the weights as well as the code — 80 MB of `.h5` committed in git, so
#: the commit pins the model as exactly as a checksum would.
CODE = source.Checkout(
    "lunet",
    "https://github.com/aim-lab/LUNet",
    "0b0f383ea215b35576df41822778c2838c8744ad",
    imports_from="",
)

#: The checkpoint inside it.
CHECKPOINT = "lunet_modelbest.h5"

#: The grid the model was built at, from `final_shape = 1472` in its `main.py` — the largest of any
#: model in this catalogue, and the point of it: arterioles a coarser grid cannot resolve.
GRID = 1472

#: What its own pinned requirements ask for, and why this repository does not install that.
DECLINED_PIN = (
    "LUNet pins tensorflow==2.14.0 and numpy<2.0, which no other upstream in this environment can "
    "live with. Its checkpoint is a Keras 2.11 functional model of standard layers — no "
    "tensorflow_addons custom objects — so tensorflow 2.21 reads it through tf-keras, the Keras 2 "
    "compatibility package, with numpy 2.5 unchanged. Verified by loading it: 19,782,782 "
    "parameters, input (1472, 1472, 3), output (1472, 1472, 3)."
)


def model_file() -> Path:
    """The checkpoint, from the pinned checkout rather than a download."""
    tree = CODE.obtain()
    found = tree / CHECKPOINT
    if not found.exists():
        raise FileNotFoundError(
            f"{CHECKPOINT} is not in {tree}; the checkout is not what was pinned"
        )
    return found


def loaded(path: Path | None = None):
    """The model, deserialised by the Keras that wrote it."""
    import tf_keras

    return tf_keras.models.load_model(path or model_file(), compile=False)


def provenance() -> dict[str, object]:
    return CODE.provenance()
