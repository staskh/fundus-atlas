# ABOUTME: The photographs of the real-segmentation biomarker benchmark: those carrying both an
# ABOUTME: artery and a vein map, and an optic disc estimate every map of them is measured with.

import csv
from pathlib import Path

import numpy as np
from PIL import Image

from datasets.utils import exclusions, paths

from .av import ArteryVeinLoader

#: Where every photograph's optic disc was estimated, once, by the SegFormer disc-and-cup model.
DISCS = Path(__file__).resolve().parents[3] / "results" / "disc_estimation"

#: Why a photograph is excluded though the dataset published it. The words are the reader's.
NO_CLASSES = "no artery and vein annotation"
CONDEMNED = "a finding condemns its artery or vein map"
NO_DISC = "no optic disc estimate"


def discs(slug: str, directory: Path = DISCS) -> dict[str, tuple[float, float, float]]:
    """Every graded disc estimate for one dataset, as `(x, y, radius)` in crop pixels."""
    path = directory / f"{slug}.csv"
    if not path.exists():
        return {}
    with open(path, newline="") as f:
        return {
            row["key"]: (float(row["disc_cx"]), float(row["disc_cy"]), float(row["disc_r"]))
            for row in csv.DictReader(f)
            if row["outcome"] == "graded" and row["disc_r"]
        }


def disc_fingerprint(slug: str, directory: Path = DISCS) -> str | None:
    """What estimated the discs, so a re-estimate re-measures everything that used them."""
    path = directory / f"{slug}.json"
    if not path.exists():
        return None
    import json

    return json.loads(path.read_text()).get("fingerprint")


class BiomarkerLoader(ArteryVeinLoader):
    """One dataset's photographs that every implementation can be run on twice — expert and model.

    That needs both classes, uncondemned, and a disc: every implementation here measures in zones
    counted in disc radii, and handing the expert's map and the model's map one disc is what makes
    a difference between their numbers a difference between the maps.

    It never reads a photograph. A biomarker is measured from masks, so the image a model saw is
    not this benchmark's business, and reading it would cost seconds per photograph for nothing.
    """

    def __init__(self, *args: object, discs_from: Path = DISCS, **kwargs: object) -> None:
        self._discs_from = discs_from
        kwargs.setdefault("size", 0)
        super().__init__(*args, **kwargs)

    def _with_reference(self, rows: list[dict[str, str]]) -> list[dict[str, str]]:
        findings = exclusions.load(self.slug)
        self.discs = discs(self.slug, self._discs_from)
        classed = [row for row in rows if {"artery", "vein"} <= set(row["maps"].split(";"))]
        self._exclude(NO_CLASSES, len(rows) - len(classed))
        condemned = {
            finding.key
            for finding in findings
            if finding.maps == exclusions.EVERYTHING or {"artery", "vein"} & set(finding.maps)
        }
        clean = [row for row in classed if row["key"] not in condemned]
        self._exclude(CONDEMNED, len(classed) - len(clean))
        placed = [row for row in clean if row["key"] in self.discs]
        self._exclude(NO_DISC, len(clean) - len(placed))
        return placed

    def scale_of(self, row: dict[str, str]) -> float | None:
        """Microns per pixel, or `None` where nobody published or inferred one."""
        return float(row["um_per_px"]) if row.get("um_per_px") else None

    def field_of(self, key: str) -> Path:
        return paths.layer(self.store, "fov") / f"{key}.png"

    def expert_of(self, key: str) -> dict[str, Path]:
        return {name: paths.layer(self.store, name) / f"{key}.png" for name in ("artery", "vein")}

    def __getitem__(self, index: int) -> dict[str, object]:
        row = self.rows[index]
        return {
            "key": row["key"],
            "subset": row["subset"],
            "split": row["split"],
            "crop_side": int(row["crop_side"]),
            "um_per_px": self.scale_of(row),
            "disc": self.discs[row["key"]],
        }


def read_mask(path: Path) -> np.ndarray:
    with Image.open(path) as drawn:
        return np.asarray(drawn) > 0
