# ABOUTME: What a benchmark is run on: the evaluation unit, the rules that keep photographs out,
# ABOUTME: and the PyTorch dataset that hands one photograph at a time to a model.

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from torch.utils.data import Dataset

from datasets.utils import exclusions, paths

#: Photographs whose field of view is smaller than this are excluded, measured on the field's own
#: size rather than the frame's: below it, a model's grid is finer than the evidence.
FLOOR = 512

#: Datasets whose images are crops of a photograph rather than photographs, and the evidence for
#: saying so. Measuring pixels on a crop of a resized photograph relates to nothing, and no size
#: floor catches it, because a crop can be large. Declared per dataset rather than inferred per
#: image: one photograph whose retina fills the frame is ordinary, a dataset where that is true of
#: every one is not.
CROPS = {
    "riga": "744 of 744 rows have no findable field boundary",
}


@dataclass(frozen=True)
class Unit:
    """One evaluation unit: a dataset's subset and split, scored on its own.

    Contamination is per split and cameras are not interchangeable, so a number over a whole mixed
    dataset hides what a map should show.
    """

    slug: str
    subset: str
    split: str

    @property
    def name(self) -> str:
        return f"{self.slug}/{self.subset}/{self.split}"

    @property
    def filename(self) -> str:
        """The same thing as a path component, for a result file."""
        return f"{self.slug}-{self.subset}-{self.split}"


def units(slug: str, root: Path | None = None, findings: Path | None = None) -> list[Unit]:
    """Every evaluation unit a store holds, in a stable order.

    :raises FileNotFoundError: if the dataset has not been built, saying how to build it.
    """
    store = (root or paths.root()) / slug
    if not (store / "manifest.csv").exists():
        raise FileNotFoundError(
            f"no store for {slug} at {store}; build it with `python -m datasets.{slug}`"
        )
    found = {
        (row["subset"], row["split"])
        for row in exclusions.usable_rows(store, findings=_findings(slug, findings))
    }
    return [Unit(slug, subset, split) for subset, split in sorted(found)]


class Photographs(Dataset):
    """The photographs of one evaluation unit, at one model's grid.

    Batching is only possible once photographs are on a common grid, which is what the store's
    ``512/`` and ``1024/`` directories are for. The ground truth a benchmark scores against is read
    at native by the scorer, not stacked into the batch.

    :param size: the store grid to read, which is the grid the model asked for.
    :param prepare: the model adapter's own preparation, applied per photograph so that a batch
        arrives at the model in the form its upstream expects.
    :param findings: where the repository's exclusions live, for tests.
    """

    def __init__(
        self,
        unit: Unit,
        size: int,
        root: Path | None = None,
        prepare: Callable[[np.ndarray], torch.Tensor] | None = None,
        floor: int = FLOOR,
        findings: Path | None = None,
    ) -> None:
        if unit.slug in CROPS:
            raise ValueError(
                f"{unit.slug} is excluded whole: its images are crops rather than photographs "
                f"({CROPS[unit.slug]}), and a measurement in pixels on a crop relates to nothing"
            )
        self.unit = unit
        self.size = size
        self.store = (root or paths.root()) / unit.slug
        self.prepare = prepare
        self.rows = self._rows(floor, findings)

    def _rows(self, floor: int, findings: Path | None) -> list[dict[str, str]]:
        kept = [
            row
            for row in exclusions.usable_rows(
                self.store, findings=_findings(self.unit.slug, findings)
            )
            if row["subset"] == self.unit.subset
            and row["split"] == self.unit.split
            and int(row["crop_side"]) >= floor
        ]
        return sorted(kept, key=lambda row: row["key"])

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, index: int) -> dict[str, object]:
        row = self.rows[index]
        return {"key": row["key"], "image": self._image(row["key"])}

    def _image(self, key: str) -> torch.Tensor:
        with Image.open(self.store / str(self.size) / "images" / f"{key}.png") as image:
            pixels = np.asarray(image.convert("RGB"))
        if self.prepare is not None:
            return self.prepare(pixels)
        return torch.from_numpy(pixels.transpose(2, 0, 1).copy())


def collate(samples: list[dict[str, object]]) -> dict[str, object]:
    """Stack the photographs and leave everything else a list.

    A multi-reader dataset's ground truth does not stack — five readers' verdicts are not a
    tensor — so it travels as a list, in the same order as the batch.
    """
    batch: dict[str, object] = {}
    for field in samples[0]:
        values = [sample[field] for sample in samples]
        batch[field] = torch.stack(values) if field == "image" else values
    return batch


def _findings(slug: str, directory: Path | None) -> list[exclusions.Exclusion]:
    """The repository's recorded findings for one dataset, so a benchmark applies them too."""
    if directory is None:
        return exclusions.load(slug)
    return exclusions.load(slug, directory)
