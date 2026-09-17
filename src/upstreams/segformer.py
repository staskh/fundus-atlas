# ABOUTME: The SegFormer disc-and-cup model: weights published on the Hugging Face hub with no code
# ABOUTME: of its own, so `transformers` is the code and a revision hash is the only version there is.

from pathlib import Path

from .utils import source

#: The model repository, and the revision this atlas describes. The repository publishes no tags,
#: so the commit of its `main` branch as last modified on 2023-09-08 is the only way to pin it.
REPOSITORY = "pamixsun/segformer_for_optic_disc_cup_segmentation"
REVISION = "a0463fb6c2bf184cf398e5fd82a8194e01e66e7f"

#: The library that runs it, which is the whole of its published code.
RUNNER = source.Installed("transformers")


def weights() -> Path:
    """The weight file, downloaded on first use, without loading it."""
    from huggingface_hub import hf_hub_download

    return Path(
        hf_hub_download(repo_id=REPOSITORY, filename="model.safetensors", revision=REVISION)
    )


def segmenter(device: str = "cpu") -> object:
    """The model at the pinned revision, on the device asked for."""
    from transformers import SegformerForSemanticSegmentation

    model = SegformerForSemanticSegmentation.from_pretrained(REPOSITORY, revision=REVISION)
    return model.to(device).eval()


def labels() -> dict[int, str]:
    """What each output channel is, read from the repository's own configuration."""
    from transformers import AutoConfig

    config = AutoConfig.from_pretrained(REPOSITORY, revision=REVISION)
    return {int(index): name for index, name in config.id2label.items()}


def provenance() -> dict[str, object]:
    return {
        "slug": "segformer-disc-cup",
        "repo": f"https://huggingface.co/{REPOSITORY}",
        "commit": REVISION,
        "runner": RUNNER.provenance(),
        "patches": {},
    }
