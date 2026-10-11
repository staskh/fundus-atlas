# ABOUTME: Tests for the camera scale inferred from the typical optic disc: how photographs are
# ABOUTME: grouped, what the gate refuses, and what is written down — against discs of known size.

import csv
import json
from pathlib import Path

import numpy as np
import pytest
import torch
from PIL import Image

from datasets import fetch_disc_estimation as estimation
from datasets import fetch_um_resolution as inference
from datasets.utils import manifest, resolution
from models.utils.outlines import Outlines


class Disc:
    """A stand-in disc model that draws a circle of the size it was told, in the crop frame."""

    slug = "a-disc-model"
    grid = 512
    structures = ("disc",)

    def __init__(self, diameters: dict[str, float] | float = 200.0) -> None:
        self.diameters = diameters
        self.asked: list[str] = []

    def declare(self) -> dict[str, object]:
        return {"slug": self.slug, "grid": self.grid, "structures": list(self.structures)}

    def identity(self) -> str:
        return "one-set-of-weights"

    def prepare(self, pixels: np.ndarray) -> torch.Tensor:
        return torch.from_numpy(pixels.transpose(2, 0, 1).copy()).float()

    def _diameter(self, key: str) -> float:
        return self.diameters[key] if isinstance(self.diameters, dict) else self.diameters

    def outline(self, images: torch.Tensor, sides: list[int], keys: list[str]) -> list[Outlines]:
        drawn = []
        for side, key in zip(sides, keys, strict=True):
            self.asked.append(key)
            radius = self._diameter(key) / 2
            ys, xs = np.ogrid[:side, :side]
            mask = (xs - side / 2) ** 2 + (ys - side / 2) ** 2 <= radius**2
            drawn.append(Outlines(masks={"disc": mask}, resampling="drawn for a test"))
        return drawn


def a_store(tmp_path: Path, rows: list[dict[str, str]], slug: str = "chaksu") -> Path:
    store = tmp_path / slug
    (store / "crop" / "images").mkdir(parents=True, exist_ok=True)
    with open(store / manifest.MANIFEST, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(manifest.CORE_COLUMNS), restval="")
        writer.writeheader()
        writer.writerows(rows)
    (store / "build.json").write_text(json.dumps({"builder_version": 6}))
    for row in rows:
        side = int(row["crop_side"])
        pixels = np.zeros((side, side, 3), dtype=np.uint8)
        Image.fromarray(pixels).save(store / "crop" / "images" / f"{row['key']}.png")
    return store


def a_row(key: str, **overrides: str) -> dict[str, str]:
    record = {
        "key": key,
        "subset": "bosch",
        "split": "train",
        "raw_width": "1920",
        "raw_height": "1440",
        "crop_side": "1400",
        "um_per_px": "",
        "resolution_source": "unknown",
        "maps": "fov",
    }
    record.update(overrides)
    return record


def test_photographs_of_one_camera_at_one_size_are_one_group() -> None:
    rows = [a_row("a"), a_row("b", raw_width="1900", raw_height="1450")]

    found = inference.groups(rows)

    assert len(found) == 1
    assert [row["key"] for row in found[0].rows] == ["a", "b"]


def test_a_size_more_than_a_tenth_away_is_another_camera() -> None:
    rows = [a_row("a"), a_row("b", raw_width="2400")]

    found = inference.groups(rows)

    assert len(found) == 2


def test_two_subsets_are_two_groups_at_the_same_size() -> None:
    """A 30° disc-centred subset and a 50° one are different magnifications, not one camera."""
    rows = [a_row("a"), a_row("b", subset="forus")]

    assert len(inference.groups(rows)) == 2


def test_the_scale_is_the_typical_disc_over_the_median_measured_one(tmp_path: Path) -> None:
    store = a_store(tmp_path, [a_row(key) for key in "abcdefghijklmnopqrstuvwxyz"])

    written = inference.measure(store, "chaksu", Disc(diameters=200.0), sample=16)

    group = written["groups"][0]
    assert group["median_disc_px"] == pytest.approx(200, abs=2)
    assert group["accepted"] is True
    assert group["um_per_px"] == pytest.approx(resolution.DISC_MICRONS / group["median_disc_px"])
    assert group["n_measured"] == 16, "the sample, not the whole group"


def test_discs_that_disagree_too_much_are_not_one_camera(tmp_path: Path) -> None:
    keys = list("abcdefghijklmnopqrst")
    wild = {key: (120.0 if index % 2 else 300.0) for index, key in enumerate(keys)}
    store = a_store(tmp_path, [a_row(key) for key in keys])

    written = inference.measure(store, "chaksu", Disc(diameters=wild), sample=20)

    group = written["groups"][0]
    assert group["accepted"] is False
    assert "spread" in group["note"]
    assert "um_per_px" not in group


def test_too_few_discs_to_settle_a_median_are_refused(tmp_path: Path) -> None:
    store = a_store(tmp_path, [a_row(key) for key in "abc"])

    written = inference.measure(store, "chaksu", Disc(), sample=32)

    group = written["groups"][0]
    assert group["accepted"] is False
    assert "too-few" in group["note"]


def test_what_is_written_names_the_photographs_it_was_measured_from(tmp_path: Path) -> None:
    store = a_store(tmp_path, [a_row(key) for key in "abcdefghijklmnopqrst"])

    written = inference.measure(store, "chaksu", Disc(), sample=16)

    group = written["groups"][0]
    assert len(group["keys"]) == 16
    assert set(group["keys"]) <= set("abcdefghijklmnopqrst")
    assert written["typical_disc_um"] == resolution.DISC_MICRONS
    assert written["builder_version"] == 6, "the store these discs were measured on"


def test_the_run_commits_the_scale_and_stamps_the_manifest(tmp_path: Path) -> None:
    store = a_store(tmp_path, [a_row(key) for key in "abcdefghijklmnopqrst"])

    inference.run(
        ["chaksu"],
        root=tmp_path,
        directory=tmp_path / "um_resolution",
        estimates=tmp_path / "disc_estimation",
        adapter=Disc(),
        sample=16,
    )

    committed = json.loads((tmp_path / "um_resolution" / "chaksu.json").read_text())
    assert committed["groups"][0]["accepted"] is True
    rows = list(manifest.read(store))
    assert all(row["resolution_source"] == "disc_anchored" for row in rows)
    assert all(row["um_per_px"] for row in rows)


def test_a_dataset_that_published_a_scale_is_left_alone(tmp_path: Path) -> None:
    """Replacing an author's measurement with our assumption is the error this command avoids."""
    rows = [a_row(key, um_per_px="6.000000", resolution_source="published") for key in "abcdefgh"]
    a_store(tmp_path, rows)
    adapter = Disc()

    inference.run(
        ["chaksu"],
        root=tmp_path,
        directory=tmp_path / "um_resolution",
        estimates=tmp_path / "disc_estimation",
        adapter=adapter,
        sample=8,
    )

    assert adapter.asked == [], "a published scale is not re-measured"
    assert not (tmp_path / "um_resolution" / "chaksu.json").exists()


class Patchy(Disc):
    """A model that finds nothing on some photographs, as a real one does."""

    def __init__(self, blind: set[str]) -> None:
        super().__init__()
        self.blind = blind

    def outline(self, images: torch.Tensor, sides: list[int], keys: list[str]):
        drawn = super().outline(images, sides, keys)
        return [
            Outlines(masks={}, resampling="found nothing") if key in self.blind else found
            for key, found in zip(keys, drawn, strict=True)
        ]


def test_a_photograph_the_model_misses_is_replaced_from_the_rest(tmp_path: Path) -> None:
    """A sample of 32 that measures 21 is a wobblier median than one that measures 32.

    The first MSHF portable group failed its spread gate on a draw where eleven photographs came
    back without a disc; the same discs pooled sat well inside the gate. Replacement is what keeps
    the gate measuring the camera rather than the draw.
    """
    keys = [f"k{index:02d}" for index in range(40)]
    store = a_store(tmp_path, [a_row(key) for key in keys])
    blind = set(keys[:10])

    written = inference.measure(store, "chaksu", Patchy(blind), sample=16)

    group = written["groups"][0]
    assert group["n_measured"] == 16, "the sample is filled, not merely attempted"
    assert group["n_drawn"] > 16, "it took more than sixteen draws to measure sixteen"
    assert not (set(group["keys"]) & blind)


def test_a_group_too_small_to_fill_the_sample_uses_what_it_has(tmp_path: Path) -> None:
    keys = [f"k{index:02d}" for index in range(20)]
    store = a_store(tmp_path, [a_row(key) for key in keys])

    written = inference.measure(store, "chaksu", Patchy(set(keys[:2])), sample=32)

    group = written["groups"][0]
    assert group["n_measured"] == 18
    assert group["n_drawn"] == 20, "every photograph in the group was tried"


def estimated(
    tmp_path: Path,
    store: Path,
    diameters: dict[str, float | None],
    model: str = estimation.MODEL,
    builder_version: int = 6,
) -> Path:
    """Disc estimates for every photograph of a store, as `fetch_disc_estimation` commits them."""
    where = tmp_path / "disc_estimation"
    where.mkdir(exist_ok=True)
    slug = store.name
    with open(where / f"{slug}.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(estimation.COLUMNS), restval="")
        writer.writeheader()
        for key, diameter in diameters.items():
            if diameter is None:
                writer.writerow({"key": key, "outcome": estimation.NO_DISC})
            else:
                writer.writerow(
                    {
                        "key": key,
                        "outcome": "graded",
                        "disc_cx": "700",
                        "disc_cy": "700",
                        "disc_r": f"{diameter / 2:.2f}",
                    }
                )
    sidecar = {
        "dataset": slug,
        "model": model,
        "builder_version": builder_version,
        "frame": estimation.FRAME,
        "fingerprint": "estimated-for-a-test",
    }
    (where / f"{slug}.json").write_text(json.dumps(sidecar))
    return where


def test_the_scale_is_inferred_with_the_model_that_estimates_each_disc() -> None:
    """One disc model for both, so a reused estimate and a fresh one are the same measurement."""
    assert inference.MODEL == estimation.MODEL == "segformer-disc-cup"


def test_estimated_discs_are_read_rather_than_measured_again(tmp_path: Path) -> None:
    keys = [f"k{index:02d}" for index in range(40)]
    store = a_store(tmp_path, [a_row(key) for key in keys])
    where = estimated(tmp_path, store, {key: 180.0 for key in keys})
    adapter = Disc(diameters=400.0)

    written = inference.measure(store, "chaksu", adapter, estimates=where)

    group = written["groups"][0]
    assert adapter.asked == [], "no photograph was segmented again"
    assert group["median_disc_px"] == pytest.approx(180)
    assert written["discs"] == "disc_estimation"


def test_every_estimated_disc_counts_not_a_sample(tmp_path: Path) -> None:
    keys = [f"k{index:02d}" for index in range(40)]
    store = a_store(tmp_path, [a_row(key) for key in keys])
    where = estimated(tmp_path, store, {key: (None if key < "k05" else 180.0) for key in keys})

    written = inference.measure(store, "chaksu", None, estimates=where)

    group = written["groups"][0]
    assert group["n_measured"] == 35, "every photograph with a disc, not the first 32"
    assert group["n_estimated"] == 40
    assert len(group["keys"]) == 35


def test_the_run_needs_no_model_where_every_disc_is_estimated(tmp_path: Path) -> None:
    keys = [f"k{index:02d}" for index in range(20)]
    store = a_store(tmp_path, [a_row(key) for key in keys])
    where = estimated(tmp_path, store, {key: 180.0 for key in keys})

    inference.run(["chaksu"], root=tmp_path, directory=tmp_path / "um_resolution", estimates=where)

    committed = json.loads((tmp_path / "um_resolution" / "chaksu.json").read_text())
    assert committed["groups"][0]["um_per_px"] == pytest.approx(10.0)
    assert committed["model"] == estimation.MODEL


@pytest.mark.parametrize(
    "stale",
    [{"builder_version": 5}, {"model": "another-disc-model"}],
    ids=["another-build", "another-model"],
)
def test_an_estimate_that_is_not_of_this_store_is_measured_again(
    tmp_path: Path, stale: dict[str, object]
) -> None:
    keys = [f"k{index:02d}" for index in range(20)]
    store = a_store(tmp_path, [a_row(key) for key in keys])
    where = estimated(tmp_path, store, {key: 180.0 for key in keys}, **stale)
    adapter = Disc(diameters=200.0)

    written = inference.measure(store, "chaksu", adapter, sample=16, estimates=where)

    assert adapter.asked, "the stale estimate was not trusted"
    assert written["discs"] == "sample"
    assert written["groups"][0]["median_disc_px"] == pytest.approx(200, abs=2)


def test_an_estimate_missing_a_photograph_of_the_store_is_measured_again(tmp_path: Path) -> None:
    keys = [f"k{index:02d}" for index in range(20)]
    store = a_store(tmp_path, [a_row(key) for key in keys])
    where = estimated(tmp_path, store, {key: 180.0 for key in keys[:-1]})
    adapter = Disc(diameters=200.0)

    written = inference.measure(store, "chaksu", adapter, sample=16, estimates=where)

    assert written["discs"] == "sample"
