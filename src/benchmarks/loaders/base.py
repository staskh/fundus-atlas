# ABOUTME: What a benchmark is run on: a whole dataset, the rules that take photographs out of it,
# ABOUTME: and the PyTorch dataset that hands one photograph at a time to a model.

import random
from collections.abc import Callable
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from torch.utils.data import Dataset

from datasets.utils import exclusions, manifest, paths

#: Photographs whose field of view is smaller than this are excluded, measured on the field's own
#: size rather than the frame's: below it, a model's grid is finer than the evidence.
FLOOR = 512

#: Why a photograph was excluded. The words are the reader's, not the code's: they appear in the
#: generated documents as they are written here.
BELOW_THE_FLOOR = "below the size floor"
A_RECORDED_FINDING = "a finding recorded against the image"

#: Datasets whose images are crops of a photograph rather than photographs, and the evidence for
#: saying so. Measuring pixels on a crop of a resized photograph relates to nothing, and no size
#: floor catches it, because a crop can be large. Declared per dataset rather than inferred per
#: image: one photograph whose retina fills the frame is ordinary, a dataset where that is true of
#: every one is not.
CROPS = {
    "riga": "744 of 744 rows have no findable field boundary",
}


def available(slug: str, root: Path | None = None) -> bool:
    """Whether this dataset's store has been built.

    A benchmark names the datasets it wants, not the ones that happen to exist, so asking is
    ordinary: an unbuilt store is something to warn about and step over, not to raise on.
    """
    return ((root or paths.root()) / slug / manifest.MANIFEST).exists()


class Photographs(Dataset):
    """One dataset's photographs, at one model's grid.

    The whole dataset is loaded in a single pass and each photograph carries the subset and split
    it came from, so that grouping stays a question for the analysis rather than one the run has to
    be told in advance.

    Batching is only possible once photographs are on a common grid, which is what the store's
    ``512/`` and ``1024/`` directories are for. Ground truth that needs full resolution is read at
    native by the scorer, not stacked into the batch.

    :param size: the store grid to read, which is the grid the model asked for.
    :param prepare: the model adapter's own preparation, applied per photograph so that a batch
        arrives at the model in the form its upstream expects.
    :param max_samples: score at most this many photographs, for a development run.
    :param random_samples: choose those at random rather than taking the first of the manifest.
    :param findings: where the repository's exclusions live, for tests.
    """

    def __init__(
        self,
        slug: str,
        size: int,
        root: Path | None = None,
        prepare: Callable[[np.ndarray], torch.Tensor] | None = None,
        floor: int = FLOOR,
        findings: Path | None = None,
        max_samples: int | None = None,
        random_samples: bool = False,
        seed: int = 0,
    ) -> None:
        if slug in CROPS:
            raise ValueError(
                f"{slug} is excluded whole: its images are crops rather than photographs "
                f"({CROPS[slug]}), and a measurement in pixels on a crop relates to nothing"
            )
        self.slug = slug
        self.size = size
        self.store = (root or paths.root()) / slug
        self.prepare = prepare
        self.excluded: dict[str, int] = {}
        self.rows = self._rows(floor, findings)
        #: How many photographs the benchmark would ask about, before any sampling.
        self.total = len(self.rows)
        self.sampled = max_samples is not None and max_samples < self.total
        if self.sampled:
            self.rows = self._sample(max_samples, random_samples, seed)

    def _rows(self, floor: int, findings: Path | None) -> list[dict[str, str]]:
        """Every row the benchmark will ask about, counting what the rules took out on the way."""
        published = list(manifest.read(self.store))
        usable = list(exclusions.usable_rows(self.store, findings=_findings(self.slug, findings)))
        self._exclude(A_RECORDED_FINDING, len(published) - len(usable))

        kept = [row for row in usable if int(row["crop_side"]) >= floor]
        self._exclude(BELOW_THE_FLOOR, len(usable) - len(kept))
        return sorted(self._with_reference(kept), key=lambda row: row["key"])

    def _with_reference(self, rows: list[dict[str, str]]) -> list[dict[str, str]]:
        """The rows this benchmark has something to score against; every row, by default."""
        return rows

    def _exclude(self, reason: str, count: int) -> None:
        if count:
            self.excluded[reason] = self.excluded.get(reason, 0) + count

    def _sample(self, how_many: int, at_random: bool, seed: int) -> list[dict[str, str]]:
        """A development-sized slice, reproducible either way it is chosen."""
        if not at_random:
            return self.rows[:how_many]
        chosen = random.Random(seed).sample(range(len(self.rows)), how_many)
        return [self.rows[index] for index in sorted(chosen)]

    @property
    def padding(self) -> float:
        """How much of the square the store built is canvas rather than photograph, at the median.

        A fundus cut off at top and bottom leaves black bands in a square crop, and a model judges
        the square it is handed.
        """
        pads = sorted(float(row["pad_fraction"]) for row in self.rows if row["pad_fraction"])
        return pads[len(pads) // 2] if pads else 0.0

    def restrict(self, keys: set[str]) -> None:
        """Keep only the photographs named — the ones a resumed run still has to score.

        This is about work left, not about the dataset, so :attr:`total` is untouched.
        """
        self.rows = [row for row in self.rows if row["key"] in keys]

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, index: int) -> dict[str, object]:
        row = self.rows[index]
        return {
            "key": row["key"],
            "subset": row["subset"],
            "split": row["split"],
            "image": self._image(row["key"]),
        }

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
