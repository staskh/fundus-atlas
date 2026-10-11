# ABOUTME: A small store on disk, so loader tests run against the real layout rather than a mock.
# ABOUTME: Nothing here downloads anything: the photographs are a handful of coloured squares.

import csv
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from datasets.utils import manifest


def write_store(
    root: Path,
    slug: str,
    rows: list[dict[str, str]],
    readings: list[dict[str, str]] | None = None,
) -> Path:
    """Write a manifest, optional labels and one photograph per row, as large as its crop."""
    store = root / slug
    store.mkdir(parents=True, exist_ok=True)
    with open(store / "manifest.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(manifest.CORE_COLUMNS), restval="")
        writer.writeheader()
        writer.writerows(rows)
    if readings:
        with open(store / "labels.csv", "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["key", "field", "reader", "value"])
            writer.writeheader()
            writer.writerows(readings)
    images = store / "crop" / "images"
    images.mkdir(parents=True, exist_ok=True)
    for index, row in enumerate(rows):
        side = int(row["crop_side"])
        pixels = np.full((side, side, 3), (index * 10) % 256, dtype=np.uint8)
        Image.fromarray(pixels).save(images / f"{row['key']}.png")
    return store


def row(key: str, **overrides: str) -> dict[str, str]:
    """One manifest row with the columns the loaders read, and blanks elsewhere."""
    record = {
        "key": key,
        "subset": "main",
        "split": "train",
        "crop_side": "1024",
        "pad_fraction": "0.0000",
        "quality": "good",
        "quality_source": "published",
        "maps": "fov",
    }
    record.update(overrides)
    return record


@pytest.fixture
def store(tmp_path: Path) -> Path:
    return tmp_path / "store"


def write_contours(
    store: Path,
    key: str,
    drawn: dict[tuple[str, str], list[tuple[float, float]]],
) -> None:
    """One photograph's outlines, in the crop frame the store keeps them in."""
    where = store / "crop" / "contours"
    where.mkdir(parents=True, exist_ok=True)
    with open(where / f"{key}.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["structure", "reader", "node", "x", "y"])
        for (structure, reader), nodes in drawn.items():
            for index, (x, y) in enumerate(nodes):
                writer.writerow([structure, reader, index, x, y])


def write_masks(
    store: Path,
    key: str,
    drawn: dict[str, np.ndarray],
) -> None:
    """One photograph's binary annotations, in the crop frame the annotator drew in."""
    for structure, mask in drawn.items():
        where = store / "crop" / structure
        where.mkdir(parents=True, exist_ok=True)
        Image.fromarray(np.asarray(mask, dtype=bool)).save(where / f"{key}.png")
