# ABOUTME: AutoMorph's optic disc and cup model: eight seeds of a little W-Net whose averaged
# ABOUTME: softmax separates background, the disc ring and the cup it encloses.

import numpy as np
import torch

from upstreams import automorph
from upstreams.utils import weights

from .utils.device import forget, pick
from .utils.outlines import Outlines

#: The store grid this reads, and the grid the networks see. AutoMorph reaches it by resizing its
#: own 912-diameter preprocessed image; the store's photographs are already cropped to the field of
#: view and square, which is the same thing arrived at by a different route.
GRID = 512

#: The network's three exclusive classes, in the order it emits them.
BACKGROUND, RING, CUP = 0, 1, 2

#: What the architecture is asked for, and with how many outputs, as `test_outside.sh` asks for it.
ARCHITECTURE = "wnet"
CLASSES = 3


class AutoMorphDiscCup:
    """Eight W-Net seeds, their softmax outputs averaged, read as two nested structures.

    The three classes are **exclusive**: a pixel the network calls cup is not in its disc class,
    while the disc an ophthalmologist draws contains the cup. So the disc measured here is the
    ring and the cup together, which is the region the expert outlined. AutoMorph's own pipeline
    never does this — it takes the bounding box of the ring, which spans the same height — so the
    difference shows in area and overlap rather than in the cup-to-disc ratio.

    AutoMorph then deletes specks from the argmaxed masks, under 100 pixels of disc and 50 of cup.
    That is done to a thresholded mask and cannot be done to a probability, so it is not applied
    here: the benchmark measures what the network said, and a stray speck is reported by
    `cup_outside_its_disc` rather than repaired out of sight.
    """

    slug = "automorph-disc-cup"
    purpose = "disc/cup"
    grid = GRID
    structures = ("disc", "cup")

    def __init__(self, device: str | None = None) -> None:
        self.device = pick(device)
        self._ensemble: list | None = None

    def declare(self) -> dict[str, object]:
        return {
            "slug": self.slug,
            "purpose": self.purpose,
            "grid": self.grid,
            "network_grid": GRID,
            "structures": list(self.structures),
            "emits_probabilities": True,
            "resampling": "probabilities to native, bilinear, thresholded there",
            "threshold": 0.5,
            "ensemble": 8,
            "device": self.device,
            "upstream": automorph.provenance(),
        }

    def identity(self) -> str:
        return weights.digest(automorph.disc_weights())

    def prepare(self, pixels: np.ndarray) -> torch.Tensor:
        """The upstream's own preparation: the photograph at 512, scaled to 0 to 1, nothing else."""
        return torch.from_numpy(pixels.transpose(2, 0, 1).copy()).float() / 255.0

    def outline(self, images: torch.Tensor, sides: list[int]) -> list[Outlines]:
        batch = images.to(self.device, dtype=torch.float32)
        with torch.no_grad():
            members = []
            for member in self._loaded():
                _, emitted = member(batch)
                members.append(torch.softmax(emitted, dim=1).cpu().numpy())
        return self.interpret(np.mean(members, axis=0), sides)

    @staticmethod
    def interpret(probabilities: np.ndarray, sides: list[int]) -> list[Outlines]:
        """The eight seeds' mean softmax, read as a disc containing a cup.

        :param probabilities: one ``(3, H, W)`` map per photograph, background first.
        """
        return [
            Outlines.from_probabilities(
                {
                    "disc": found[RING] + found[CUP],
                    "cup": found[CUP],
                },
                side=side,
            )
            for found, side in zip(probabilities, sides, strict=True)
        ]

    def _loaded(self) -> list:
        if self._ensemble is None:
            architecture = automorph.disc_architecture()
            self._verified()
            self._ensemble = []
            for checkpoint in automorph.disc_weights():
                member = architecture(ARCHITECTURE, n_classes=CLASSES)
                member.load_state_dict(
                    torch.load(checkpoint, map_location=self.device)["model_state_dict"]
                )
                self._ensemble.append(member.to(self.device).eval())
        return self._ensemble

    def _verified(self) -> None:
        """Check the seeds were trained at the grid and architecture this adapter assumes."""
        for seed in automorph.disc_configuration():
            if seed["model_name"] != ARCHITECTURE or int(seed["im_size"]) != GRID:
                raise RuntimeError(
                    f"a seed was trained as {seed['model_name']} at {seed['im_size']}, not as "
                    f"{ARCHITECTURE} at {GRID}; read the configuration before changing either"
                )

    def release(self) -> None:
        """Give back what this model loaded, for a run that has finished with it."""
        self._ensemble = None
        forget()


def model(**arguments: object) -> AutoMorphDiscCup:
    return AutoMorphDiscCup(**arguments)
