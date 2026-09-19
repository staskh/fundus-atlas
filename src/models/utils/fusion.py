# ABOUTME: BF-Net's binary-to-multi fusion, shared by the two catalogued models built on it: an
# ABOUTME: artery branch and a vein branch feed a main generator, whose four classes are read as two.

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch
from PIL import Image

from .outlines import Outlines

#: The grid the published weights were trained and are run at, from `Define_image_size(uniform=True)`
#: in both repositories. Square, and the photograph is resized to it with the aspect ratio ignored —
#: which the store's photographs already are, being cropped to the field of view.
GRID = 720

#: What the four output channels are, in the order the network emits them. The fourth is named
#: `uncertainty` in the authors' own evaluation, and on the annotations they trained it on it is
#: exactly the crossings: measured against HRF, it matches this repository's crossing layer pixel
#: for pixel, with nothing left over.
CLASSES = ("background", "artery", "vein", "crossing")

#: What the architecture is asked for, from `test.py` in BF-Net and `test_outside.py` in AutoMorph.
INPUT_CHANNELS = 3
FILTERS = 32
BILINEAR = False

#: The three checkpoints one seed is: two branch generators and the main one they are fused into.
CHECKPOINTS = {
    "artery": "CP_best_F1_A.pth",
    "vein": "CP_best_F1_V.pth",
    "main": "CP_best_F1_all.pth",
}


@dataclass
class Seed:
    """One training run: a main generator and the two branch generators that feed it."""

    main: object
    artery: object
    vein: object


def prepare(pixels: np.ndarray) -> torch.Tensor:
    """The upstream's own preparation: resize to its grid, then scale by the photograph's own pixels.

    Their expression is ``(image - mean) / 1.0 * std``, whose precedence multiplies by the standard
    deviation rather than dividing by it. It is reproduced rather than corrected because both of
    their dataset classes carry it, so the weights were trained through it; a corrected version
    would hand the networks something they have never seen. The statistics are over the pixels with
    any red in them, which on a photograph cropped to the field of view is the lit circle.
    """
    resized = np.array(Image.fromarray(pixels).resize((GRID, GRID)))
    lit = resized[resized[..., 0] > 0]
    if not lit.size:
        return torch.zeros((INPUT_CHANNELS, GRID, GRID), dtype=torch.float32)
    scaled = (resized - np.mean(lit, axis=0)) * np.std(lit, axis=0)
    return torch.from_numpy(scaled.transpose(2, 0, 1).copy()).float()


def seeds(architecture: object, folders: list[Path], device: str) -> list[Seed]:
    """Load one seed per folder, each folder holding the three checkpoints above."""
    loaded = []
    for folder in folders:
        parts = {}
        for part, filename in CHECKPOINTS.items():
            network = (
                architecture.Generator_main if part == "main" else architecture.Generator_branch
            )(
                input_channels=INPUT_CHANNELS,
                n_filters=FILTERS,
                n_classes=len(CLASSES),
                bilinear=BILINEAR,
            )
            network.load_state_dict(torch.load(folder / filename, map_location=device))
            parts[part] = network.to(device).eval()
        loaded.append(Seed(**parts))
    return loaded


def probabilities(loaded: list[Seed], batch: torch.Tensor, device: str = "cpu") -> np.ndarray:
    """Every seed's own softmax, averaged — which is not the same as averaging their logits.

    Each seed segments arteries and veins separately first, and it is the **fusion** map of each
    branch, rather than its segmentation, that the main generator is conditioned on.
    """
    images = batch.to(device, dtype=torch.float32)
    averaged = None
    with torch.no_grad():
        for seed in loaded:
            _, artery = seed.artery(images)
            _, vein = seed.vein(images)
            emitted, *_ = seed.main(images, artery.detach(), vein.detach())
            found = torch.softmax(emitted, dim=1).cpu()
            averaged = found if averaged is None else averaged + found
    return (averaged / len(loaded)).numpy()


def vessels(found: np.ndarray, sides: list[int]) -> list[Outlines]:
    """Four exclusive classes read as two vessels that share their crossings.

    :param found: one ``(4, H, W)`` map of probabilities per photograph, background first.
    """
    artery, vein, crossing = (CLASSES.index(name) for name in ("artery", "vein", "crossing"))
    return [
        Outlines.from_probabilities(
            {
                "artery": one[artery] + one[crossing],
                "vein": one[vein] + one[crossing],
            },
            side=side,
        )
        for one, side in zip(found, sides, strict=True)
    ]
