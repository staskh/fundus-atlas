# ABOUTME: The photographs of an artery/vein benchmark, with every annotator's arteries and veins in
# ABOUTME: the native frame they were drawn in.

import numpy as np
from PIL import Image

from datasets.utils import exclusions, paths

from .base import Photographs

#: Why a photograph is excluded from an artery/vein benchmark though the dataset published it.
NOTHING_SEGMENTED = "no artery/vein annotation to score against"

#: The maps the store holds for one of these datasets, and which of them a model is scored on. The
#: vessel map is read as the dataset published it and **also** derived from the two classes, because
#: in several datasets those are the same annotation and the page has to be able to say so.
STRUCTURES = ("artery", "vein", "vessels")


class ArteryVeinLoader(Photographs):
    """One dataset's photographs and the vessels drawn on them.

    The masks stay in **native** coordinates whatever grid the model asked for: that is where the
    annotator drew and where every score is computed. A photograph nobody annotated is excluded with
    its own reason — there is nothing to score against, which is not a failure of the model.

    These datasets publish one annotation each; the reader column exists so that one which keeps its
    annotators apart can be added without changing the evidence's shape.
    """

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.findings = exclusions.load(self.slug)

    def _with_reference(self, rows: list[dict[str, str]]) -> list[dict[str, str]]:
        annotated = [row for row in rows if {"artery", "vein"} <= set(row["maps"].split(";"))]
        self._exclude(NOTHING_SEGMENTED, len(rows) - len(annotated))
        return annotated

    def masks_of(self, key: str) -> dict[str, np.ndarray]:
        """Every vessel mask drawn on one photograph, less any a finding condemns."""
        condemned = {
            name
            for finding in self.findings
            if finding.key == key
            for name in (STRUCTURES if finding.maps == exclusions.EVERYTHING else finding.maps)
        }
        found = {}
        for structure in STRUCTURES:
            if structure in condemned:
                continue
            path = paths.layer(self.store, paths.NATIVE, structure) / f"{key}.png"
            if path.exists():
                with Image.open(path) as drawn:
                    found[structure] = np.asarray(drawn) > 0
        return found

    def readers_of(self, key: str) -> list[str]:
        """Who annotated this photograph. One unnamed annotator, in every dataset built so far."""
        readers = [
            reader for reader in self.rows_by_key(key).get("readers", "").split(";") if reader
        ]
        return readers or ["expert"]

    def rows_by_key(self, key: str) -> dict[str, str]:
        for row in self.rows:
            if row["key"] == key:
                return row
        return {}

    def __getitem__(self, index: int) -> dict[str, object]:
        row = self.rows[index]
        sample = super().__getitem__(index)
        sample["masks"] = self.masks_of(row["key"])
        sample["reader"] = self.readers_of(row["key"])[0]
        sample["native_side"] = int(row["crop_side"])
        return sample
