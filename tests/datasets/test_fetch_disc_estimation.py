# ABOUTME: Tests for the per-photograph optic disc and cup estimate: where the centre and radius
# ABOUTME: land in the native crop, what an empty answer records, and when a run is skipped.

import csv
import json
from pathlib import Path

import numpy as np
import pytest
import torch
from PIL import Image

from datasets import fetch_disc_estimation as estimation
from datasets.utils import manifest
from models.utils.outlines import Outlines


class DiscCup:
    """A stand-in disc-and-cup model drawing circles at known places in the native crop."""

    slug = "a-disc-cup-model"
    grid = 64
    structures = ("disc", "cup")

    def __init__(self, circles: dict[str, tuple[float, float, float, float]] | None = None) -> None:
        #: key → (centre x, centre y, disc radius, cup radius), in native crop pixels.
        self.circles = circles or {}
        self.shapes: list[tuple[int, ...]] = []

    def identity(self) -> str:
        return "one-set-of-weights"

    def prepare(self, pixels: np.ndarray) -> torch.Tensor:
        self.shapes.append(pixels.shape)
        return torch.from_numpy(pixels.transpose(2, 0, 1).copy()).float()

    def outline(self, images: torch.Tensor, sides: list[int], keys: list[str]) -> list[Outlines]:
        drawn = []
        for side, key in zip(sides, keys, strict=True):
            if key not in self.circles:
                drawn.append(Outlines(masks={"disc": np.zeros((side, side), bool)}))
                continue
            cx, cy, disc, cup = self.circles[key]
            ys, xs = np.ogrid[:side, :side]
            distance = (xs - cx) ** 2 + (ys - cy) ** 2
            drawn.append(Outlines(masks={"disc": distance <= disc**2, "cup": distance <= cup**2}))
        return drawn


def a_store(tmp_path: Path, keys: list[str], side: int = 300, slug: str = "hrf") -> Path:
    store = tmp_path / slug
    (store / "native" / "images").mkdir(parents=True)
    rows = [
        {
            "key": key,
            "subset": "main",
            "native_width": "400",
            "native_height": "260",
            "crop_x0": "50",
            "crop_y0": "-20",
            "crop_side": str(side),
        }
        for key in keys
    ]
    with open(store / manifest.MANIFEST, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(manifest.CORE_COLUMNS), restval="")
        writer.writeheader()
        writer.writerows(rows)
    (store / "build.json").write_text(json.dumps({"builder_version": 6}))
    for key in keys:
        pixels = np.full((side, side, 3), 90, dtype=np.uint8)
        Image.fromarray(pixels).save(store / "native" / "images" / f"{key}.png")
    return store


def read(directory: Path, slug: str = "hrf") -> dict[str, dict[str, str]]:
    with open(directory / f"{slug}.csv", newline="") as f:
        return {row["key"]: row for row in csv.DictReader(f)}


def test_the_centre_and_radius_are_in_the_native_crop(tmp_path: Path) -> None:
    a_store(tmp_path, ["a"])
    model = DiscCup({"a": (210.0, 120.0, 40.0, 15.0)})

    estimation.run(["hrf"], root=tmp_path, directory=tmp_path / "out", adapter=model)

    row = read(tmp_path / "out")["a"]
    assert row["outcome"] == "graded"
    assert float(row["disc_cx"]) == pytest.approx(210, abs=0.5)
    assert float(row["disc_cy"]) == pytest.approx(120, abs=0.5)
    assert float(row["disc_r"]) == pytest.approx(40, abs=0.5)
    assert float(row["cup_cx"]) == pytest.approx(210, abs=0.5)
    assert float(row["cup_r"]) == pytest.approx(15, abs=0.5)


def test_the_model_is_handed_the_native_photograph_resized_to_its_grid(tmp_path: Path) -> None:
    a_store(tmp_path, ["a"], side=300)
    model = DiscCup({"a": (150.0, 150.0, 40.0, 15.0)})

    estimation.run(["hrf"], root=tmp_path, directory=tmp_path / "out", adapter=model)

    assert model.shapes == [(64, 64, 3)]


def test_only_the_largest_patch_is_the_disc(tmp_path: Path) -> None:
    """A stray speck elsewhere must not drag the centre off the disc."""

    class Speckled(DiscCup):
        def outline(self, images, sides, keys):
            drawn = super().outline(images, sides, keys)
            drawn[0].masks["disc"][5:8, 5:8] = True
            return drawn

    a_store(tmp_path, ["a"])
    estimation.run(
        ["hrf"],
        root=tmp_path,
        directory=tmp_path / "out",
        adapter=Speckled({"a": (200.0, 200.0, 30.0, 10.0)}),
    )

    row = read(tmp_path / "out")["a"]
    assert float(row["disc_cx"]) == pytest.approx(200, abs=0.5)
    assert float(row["disc_r"]) == pytest.approx(30, abs=0.5)


def test_a_photograph_with_no_disc_keeps_its_row_and_says_why(tmp_path: Path) -> None:
    a_store(tmp_path, ["a", "b"])

    estimation.run(
        ["hrf"],
        root=tmp_path,
        directory=tmp_path / "out",
        adapter=DiscCup({"a": (150.0, 150.0, 40.0, 15.0)}),
    )

    rows = read(tmp_path / "out")
    assert list(rows) == ["a", "b"]
    assert rows["b"]["outcome"] == "no-disc"
    assert rows["b"]["disc_cx"] == "" and rows["b"]["cup_r"] == ""


def test_the_sidecar_records_what_the_numbers_were_measured_with(tmp_path: Path) -> None:
    a_store(tmp_path, ["a", "b"])

    estimation.run(
        ["hrf"],
        root=tmp_path,
        directory=tmp_path / "out",
        adapter=DiscCup({"a": (150.0, 150.0, 40.0, 15.0)}),
    )

    sidecar = json.loads((tmp_path / "out" / "hrf.json").read_text())
    assert sidecar["dataset"] == "hrf"
    assert sidecar["model"] == "a-disc-cup-model"
    assert sidecar["builder_version"] == 6
    assert sidecar["frame"] == "native crop"
    assert sidecar["n_images"] == 2
    assert sidecar["n_disc"] == 1
    assert sidecar["fingerprint"]


def test_an_unchanged_run_measures_nothing_again(tmp_path: Path) -> None:
    a_store(tmp_path, ["a"])
    first = DiscCup({"a": (150.0, 150.0, 40.0, 15.0)})
    estimation.run(["hrf"], root=tmp_path, directory=tmp_path / "out", adapter=first)

    second = DiscCup({"a": (150.0, 150.0, 40.0, 15.0)})
    estimation.run(["hrf"], root=tmp_path, directory=tmp_path / "out", adapter=second)

    assert second.shapes == []


def test_force_measures_again(tmp_path: Path) -> None:
    a_store(tmp_path, ["a"])
    estimation.run(
        ["hrf"],
        root=tmp_path,
        directory=tmp_path / "out",
        adapter=DiscCup({"a": (150.0, 150.0, 40.0, 15.0)}),
    )

    again = DiscCup({"a": (150.0, 150.0, 40.0, 15.0)})
    estimation.run(["hrf"], root=tmp_path, directory=tmp_path / "out", adapter=again, force=True)

    assert again.shapes == [(64, 64, 3)]


def test_a_store_with_a_photograph_added_is_measured_again(tmp_path: Path) -> None:
    a_store(tmp_path, ["a"])
    estimation.run(
        ["hrf"],
        root=tmp_path,
        directory=tmp_path / "out",
        adapter=DiscCup({"a": (150.0, 150.0, 40.0, 15.0)}),
    )
    a_store(tmp_path / "rebuilt", ["a", "b"])

    again = DiscCup({"a": (150.0, 150.0, 40.0, 15.0)})
    estimation.run(["hrf"], root=tmp_path / "rebuilt", directory=tmp_path / "out", adapter=again)

    assert list(read(tmp_path / "out")) == ["a", "b"]
