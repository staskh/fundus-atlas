# ABOUTME: LUNet v2's optic disc model: one ONNX file with no repository of its own, pinned by the
# ABOUTME: digest of the copy AutoMorphalyzer republished under a fixed release tag.

from pathlib import Path

from .utils import paths, weights

#: Where the file is fetched from. PVBM fetches the same model from an unversioned Google Drive
#: link, which can change without notice; AutoMorphalyzer's copy sits behind a release tag, so that
#: is what is pinned here — and the digest below is what makes the two interchangeable or not.
PUBLISHED = (
    "https://github.com/jaburke166/AutoMorphalyzer/releases/download/v1.0_PVBM/lunetv2_odc.onnx"
)

#: What that file is. No licence accompanies it; its stated ancestor is CC BY-NC 4.0.
SHA256 = "f72f6c9ea2ade798b80539de77fa610bb6553bb0fd7fcb78d1e841982cae0b5f"

#: The library that runs it, which is the whole of its published code.
RUNNER = "onnxruntime"


def model_file() -> Path:
    """The ONNX file, fetched once and checked against the digest above."""
    return weights.fetch(PUBLISHED, paths.weights("lunetv2") / "lunetv2_odc.onnx", SHA256)


def session(device: str = "cpu") -> object:
    """A loaded inference session. Only the CPU provider is asked for, because that is the one
    every machine running this has, and the file is small enough that it costs little."""
    import onnxruntime

    return onnxruntime.InferenceSession(str(model_file()), providers=["CPUExecutionProvider"])


def provenance() -> dict[str, object]:
    import onnxruntime

    return {
        "slug": "lunetv2-odc",
        "repo": PUBLISHED,
        "commit": SHA256,
        "runner": {"distribution": RUNNER, "version": onnxruntime.__version__},
        "patches": {},
    }
