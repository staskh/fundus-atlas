# ABOUTME: Tests for the disc-and-cup benchmark's run: one row per reader, what it keeps rather
# ABOUTME: than repeats, and the pages it generates before and after measuring.

import json
from pathlib import Path

import numpy as np
import pytest
import torch
from conftest import row, write_contours, write_store
from PIL import Image

from benchmarks import disc, report, runs
from models.utils.outlines import Outlines


class Circles:
    """A stand-in model that outlines a circle of its own, at the centre of the photograph.

    A real adapter rather than a mock: the benchmark calls it exactly as it calls the catalogued
    ones, so these tests exercise the run rather than a rehearsal of it.
    """

    slug = "circles"
    purpose = "disc/cup"
    grid = 512
    structures = ("disc", "cup")

    def __init__(self, radius: float = 0.2, fails: bool = False) -> None:
        self.radius = radius
        self.fails = fails
        self.outlined: list[str] = []

    def declare(self) -> dict[str, object]:
        return {
            "slug": self.slug,
            "purpose": self.purpose,
            "grid": self.grid,
            "network_grid": 512,
            "structures": list(self.structures),
            "emits_probabilities": True,
            "resampling": "probabilities to native, bilinear, then thresholded",
            "threshold": 0.5,
            "ensemble": 1,
        }

    def identity(self) -> str:
        return f"circles-{self.radius}"

    def prepare(self, pixels: np.ndarray) -> torch.Tensor:
        return torch.from_numpy(pixels.transpose(2, 0, 1).copy()).float() / 255.0

    def outline(self, images: torch.Tensor, sides: list[int]) -> list[Outlines]:
        if self.fails:
            raise RuntimeError("the network fell over")
        answers = []
        for side in sides:
            grid = np.linspace(-0.5, 0.5, self.grid)
            distance = np.hypot(*np.meshgrid(grid, grid))
            answers.append(
                Outlines.from_probabilities(
                    {
                        "disc": (distance <= self.radius).astype(np.float32),
                        "cup": (distance <= self.radius / 2).astype(np.float32),
                    },
                    side,
                )
            )
        return answers

    def release(self) -> None:
        self.outlined.append("released")


def circle(radius: float, side: int = 1024, nodes: int = 64) -> list[tuple[float, float]]:
    angles = np.linspace(0, 2 * np.pi, nodes, endpoint=False)
    return [
        (side / 2 + radius * side * np.cos(angle), side / 2 + radius * side * np.sin(angle))
        for angle in angles
    ]


def a_store(tmp_path: Path, keys: str = "ab") -> Path:
    root = tmp_path / "data"
    store = write_store(
        root, "papila", [row(key, maps="fov;disc;cup", readers="expert1;expert2") for key in keys]
    )
    (root / "papila" / "build.json").write_text(json.dumps({"builder_version": 6}))
    for key in keys:
        write_contours(
            store,
            key,
            {
                ("disc", "expert1"): circle(0.2),
                ("cup", "expert1"): circle(0.1),
                ("disc", "expert2"): circle(0.22),
                ("cup", "expert2"): circle(0.1),
            },
        )
    return root


def test_a_run_scores_every_photograph_against_every_reader(tmp_path: Path) -> None:
    scored = disc.run([Circles()], ["papila"], results=tmp_path / "results", root=a_store(tmp_path))

    assert scored[0]["summary"]["photographs"] == 2
    assert scored[0]["summary"]["outlines"] == 4, "two photographs, two readers each"
    assert scored[0]["counts"] == {"processed": 2, "total": 2, "complete": True, "excluded": {}}


def test_the_evidence_names_the_reader_each_row_is_scored_against(tmp_path: Path) -> None:
    disc.run([Circles()], ["papila"], results=tmp_path / "results", root=a_store(tmp_path))

    evidence = runs.rows(tmp_path / "results", disc.NAME, "circles", "papila")

    assert [(entry["key"], entry["reader"]) for entry in evidence] == [
        ("a", "expert1"),
        ("a", "expert2"),
        ("b", "expert1"),
        ("b", "expert2"),
    ]
    assert float(evidence[0]["disc_dice"]) > 0.95, "the same circle the expert drew"
    assert float(evidence[1]["disc_dice"]) < float(evidence[0]["disc_dice"]), "a wider disc"


def test_the_measurements_are_made_in_the_frame_the_expert_drew_in(tmp_path: Path) -> None:
    disc.run([Circles()], ["papila"], results=tmp_path / "results", root=a_store(tmp_path))

    evidence = runs.rows(tmp_path / "results", disc.NAME, "circles", "papila")

    assert evidence[0]["native_side"] == "1024", "not the 512 grid the model read"
    assert abs(float(evidence[0]["cup_vertical_ratio_error"])) < 0.05
    assert float(evidence[0]["cup_outside_its_disc"]) == 0.0


def test_a_model_that_falls_over_is_recorded_rather_than_dropped(tmp_path: Path) -> None:
    scored = disc.run(
        [Circles(fails=True)], ["papila"], results=tmp_path / "results", root=a_store(tmp_path)
    )

    evidence = runs.rows(tmp_path / "results", disc.NAME, "circles", "papila")

    assert scored[0]["summary"]["failed"] == 4
    assert all(entry["outcome"] == "failed" for entry in evidence)
    assert "fell over" in evidence[0]["note"]


def test_a_second_run_measures_nothing_that_is_already_complete(tmp_path: Path) -> None:
    store = a_store(tmp_path)
    disc.run([Circles()], ["papila"], results=tmp_path / "results", root=store)

    scored = disc.run([Circles()], ["papila"], results=tmp_path / "results", root=store)

    assert scored[0]["measured"] == 0


def test_a_sampled_run_is_finished_rather_than_repeated(tmp_path: Path) -> None:
    store = a_store(tmp_path)
    disc.run([Circles()], ["papila"], results=tmp_path / "results", root=store, max_samples=1)

    scored = disc.run([Circles()], ["papila"], results=tmp_path / "results", root=store)

    assert scored[0]["measured"] == 1, "only the photograph that was missing"
    assert scored[0]["counts"]["complete"] is True


def test_changed_weights_throw_away_what_was_measured(tmp_path: Path) -> None:
    store = a_store(tmp_path)
    disc.run([Circles()], ["papila"], results=tmp_path / "results", root=store)

    scored = disc.run([Circles(radius=0.3)], ["papila"], results=tmp_path / "results", root=store)

    assert scored[0]["measured"] == 2


def test_the_configuration_is_known_before_anything_is_measured(tmp_path: Path) -> None:
    adapter = Circles()

    configured = disc.configuration([adapter], ["papila"], root=a_store(tmp_path))

    assert adapter.outlined == [], "reading contours is not running a network"
    assert configured["datasets"] == [
        {
            "slug": "papila",
            "total": 2,
            "excluded": {},
            "readers": ["expert1", "expert2"],
            "padding": 0.0,
        }
    ]


def test_the_page_saying_how_it_is_run_describes_what_is_measured(tmp_path: Path) -> None:
    written = report.write_docs(
        disc.NAME,
        disc.configuration([Circles()], ["papila"], root=a_store(tmp_path)),
        {"isfa": "no adapter written"},
        {"refuge": "no store built"},
        disc.COLUMNS,
        into=tmp_path / "docs",
    ).read_text()

    assert "Dice" in written
    assert "cup-to-disc ratio" in written
    assert "`disc_dice`" in written
    assert "circles" in written
    assert "isfa" in written and "no adapter written" in written
    assert "refuge" in written and "no store built" in written


def test_the_index_reports_what_a_disc_run_measured(tmp_path: Path) -> None:
    disc.run([Circles()], ["papila"], results=tmp_path / "results", root=a_store(tmp_path))

    written = report.write_index(results=tmp_path / "results", into=tmp_path / "docs").read_text()

    assert "## Disc" in written
    assert "circles" in written
    assert "Disc Dice" in written


def test_a_run_records_how_long_the_model_took_per_photograph(tmp_path: Path) -> None:
    scored = disc.run([Circles()], ["papila"], results=tmp_path / "results", root=a_store(tmp_path))

    assert scored[0]["summary"]["seconds_per_photograph"] > 0
    assert scored[0]["summary"]["timed_photographs"] == 2


def test_a_run_that_measured_nothing_keeps_the_timing_it_had(tmp_path: Path) -> None:
    store = a_store(tmp_path)
    first = disc.run([Circles()], ["papila"], results=tmp_path / "results", root=store)

    again = disc.run([Circles()], ["papila"], results=tmp_path / "results", root=store)

    assert again[0]["summary"]["seconds_per_photograph"] == pytest.approx(
        first[0]["summary"]["seconds_per_photograph"]
    )


def test_the_predicted_masks_are_kept_for_what_comes_after(tmp_path: Path) -> None:
    """The biomarker benchmark's input is these masks, not the scores computed from them."""
    disc.run(
        [Circles()],
        ["papila"],
        results=tmp_path / "results",
        root=a_store(tmp_path),
        record=tmp_path / "runs",
    )

    kept = sorted(
        path.name for path in (tmp_path / "runs" / "disc" / "circles" / "papila").glob("*.png")
    )

    assert kept == ["a-cup.png", "a-disc.png", "b-cup.png", "b-disc.png"]


def test_masks_a_model_no_longer_agrees_with_are_thrown_away(tmp_path: Path) -> None:
    store = a_store(tmp_path)
    disc.run(
        [Circles()], ["papila"], results=tmp_path / "results", root=store, record=tmp_path / "runs"
    )
    where = tmp_path / "runs" / "disc" / "circles" / "papila"
    stale = np.asarray(Image.open(where / "a-disc.png")).sum()

    disc.run(
        [Circles(radius=0.35)],
        ["papila"],
        results=tmp_path / "results",
        root=store,
        record=tmp_path / "runs",
    )

    assert np.asarray(Image.open(where / "a-disc.png")).sum() != stale, (
        "a mask whose fingerprint no longer matches its model is recomputed"
    )


def test_a_kept_mask_is_in_the_frame_the_expert_drew_in(tmp_path: Path) -> None:
    disc.run(
        [Circles()],
        ["papila"],
        results=tmp_path / "results",
        root=a_store(tmp_path),
        record=tmp_path / "runs",
    )

    with Image.open(tmp_path / "runs" / "disc" / "circles" / "papila" / "a-disc.png") as mask:
        assert mask.size == (1024, 1024), "native, not the 512 grid the model read"
