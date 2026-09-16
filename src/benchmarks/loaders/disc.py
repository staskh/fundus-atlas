# ABOUTME: The photographs of a disc-and-cup benchmark, with every reader's outline of every
# ABOUTME: structure, in the native frame the expert drew in.

from pathlib import Path

import numpy as np

from datasets.utils import contours, exclusions, paths

from .base import Photographs

#: Why a photograph is excluded from a disc-and-cup benchmark though the dataset published it.
NOTHING_OUTLINED = "no outline to score against"


class DiscCupLoader(Photographs):
    """One dataset's photographs and the outlines drawn on them.

    The outlines stay in **native** coordinates whatever grid the model asked for: that is where
    the expert drew, and it is where every measurement is made. A photograph nobody outlined is
    excluded with its own reason — there is nothing to score against, which is not a failure of the
    model.

    Multi-reader is the ordinary case here, not the exception: Chákṣu publishes five outlines per
    structure and PAPILA two, so the outlines travel as a dictionary keyed by structure and reader
    and the collate function keeps them as a list.
    """

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.findings = exclusions.load(self.slug)

    def _with_reference(self, rows: list[dict[str, str]]) -> list[dict[str, str]]:
        outlined = [row for row in rows if {"disc", "cup"} & set(row["maps"].split(";"))]
        self._exclude(NOTHING_OUTLINED, len(rows) - len(outlined))
        return outlined

    def outlines_of(self, key: str) -> dict[tuple[str, str], np.ndarray]:
        """Every outline drawn on one photograph, less any a finding condemns."""
        path = paths.layer(self.store, paths.NATIVE, "contours") / f"{key}.csv"
        if not path.exists():
            return {}
        return exclusions.trusted_outlines(key, contours.read(path), findings=self.findings)

    def readers_of(self, key: str) -> list[str]:
        return sorted({reader for _, reader in self.outlines_of(key)})

    def __getitem__(self, index: int) -> dict[str, object]:
        row = self.rows[index]
        sample = super().__getitem__(index)
        sample["outlines"] = self.outlines_of(row["key"])
        sample["native_side"] = int(row["crop_side"])
        return sample
