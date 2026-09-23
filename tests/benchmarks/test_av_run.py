# ABOUTME: Tests for the artery/vein benchmark's run: what it scores, the three masks it keeps for
# ABOUTME: the biomarker benchmark, and what a second run repeats rather than measures again.

import json
from pathlib import Path

import numpy as np
import pytest
import torch
from conftest import row, write_masks, write_store
from PIL import Image

from benchmarks import av, runs
from models.utils.outlines import Outlines

#: The native frame every mask in these tests is drawn in.
SIDE = 1024


def band(side: int, rows: slice, columns: slice) -> np.ndarray:
    """A rectangle of vessel, which is all a Dice score needs to be arithmetic."""
    mask = np.zeros((side, side), dtype=bool)
    mask[rows, columns] = True
    return mask


class Bands:
    """A stand-in model that answers with two rectangles, in the frame it was asked about.

    A real adapter rather than a mock: the benchmark calls it exactly as it calls the catalogued
    ones, so these tests exercise the run rather than a rehearsal of it.
    """

    slug = "bands"
    purpose = "artery/vein"
    grid = 512
    structures = ("artery", "vein")

    def __init__(self, shift: int = 0, fails: bool = False) -> None:
        self.shift = shift
        self.fails = fails
        self.asked = 0
        self.released = 0

    def declare(self) -> dict[str, object]:
        return {
            "slug": self.slug,
            "purpose": self.purpose,
            "grid": self.grid,
            "network_grid": self.grid,
            "structures": list(self.structures),
            "emits_probabilities": True,
            "resampling": "probabilities to native, bilinear, then thresholded",
            "threshold": 0.5,
            "channels": ["background", "artery", "vein"],
            "ensemble": 1,
        }

    def identity(self) -> str:
        return f"bands-{self.shift}"

    def prepare(self, pixels: np.ndarray) -> torch.Tensor:
        return torch.from_numpy(pixels.transpose(2, 0, 1).copy()).float() / 255.0

    def outline(self, images: torch.Tensor, sides: list[int]) -> list[Outlines]:
        if self.fails:
            raise RuntimeError("the network fell over")
        self.asked += len(sides)
        answers = []
        for side in sides:
            quarter = side // 4
            answers.append(
                Outlines(
                    masks={
                        "artery": band(
                            side, slice(quarter + self.shift, 2 * quarter + self.shift), slice(None)
                        ),
                        "vein": band(
                            side,
                            slice(3 * quarter + self.shift, 4 * quarter + self.shift),
                            slice(None),
                        ),
                    },
                    resampling="probabilities to native, bilinear, then thresholded",
                )
            )
        return answers

    def release(self) -> None:
        self.released += 1


def a_store(tmp_path: Path, keys: str = "ab") -> Path:
    """A store of photographs with arteries and veins annotated in the native frame."""
    root = tmp_path / "data"
    store = write_store(
        root,
        "hrf",
        [row(key, maps="fov;artery;vein;vessels", crop_side=str(SIDE)) for key in keys],
    )
    (root / "hrf" / "build.json").write_text(json.dumps({"builder_version": 6}))
    quarter = SIDE // 4
    artery = band(SIDE, slice(quarter, 2 * quarter), slice(None))
    vein = band(SIDE, slice(3 * quarter, 4 * quarter), slice(None))
    for key in keys:
        write_masks(store, key, {"artery": artery, "vein": vein, "vessels": artery | vein})
    return root


def a_run(tmp_path: Path, adapter=None, **arguments: object) -> list[dict[str, object]]:
    return av.run(
        [adapter or Bands()],
        ["hrf"],
        results=tmp_path / "results",
        root=a_store(tmp_path),
        record=tmp_path / "runs",
        **arguments,
    )


def test_a_run_scores_every_photograph_against_its_annotator(tmp_path: Path) -> None:
    scored = a_run(tmp_path)

    assert scored[0]["summary"]["photographs"] == 2
    assert scored[0]["summary"]["segmentations"] == 2, "one annotator each"
    assert scored[0]["counts"] == {"processed": 2, "total": 2, "complete": True, "excluded": {}}


def test_a_model_that_drew_what_the_expert_drew_scores_one(tmp_path: Path) -> None:
    a_run(tmp_path)

    evidence = runs.rows(tmp_path / "results", av.NAME, "bands", "hrf")

    for entry in evidence:
        for structure in ("artery", "vein", "vessels"):
            assert float(entry[f"{structure}_dice"]) == pytest.approx(1.0)
            assert float(entry[f"{structure}_cldice"]) == pytest.approx(1.0)


def test_the_vessel_score_is_the_union_of_the_two_classes_on_both_sides(tmp_path: Path) -> None:
    """A model that finds the vessels and names them wrongly still scores on the union.

    Its artery is the expert's vein and the reverse, so both class scores are nothing while the
    vessel score is perfect — which is the distinction this benchmark exists to make.
    """
    swapped = Bands()
    swapped.outline = lambda images, sides: [  # noqa: ARG005 — the frame is all it needs
        Outlines(
            masks={
                "artery": band(side, slice(3 * side // 4, side), slice(None)),
                "vein": band(side, slice(side // 4, side // 2), slice(None)),
            },
            resampling="probabilities to native, bilinear, then thresholded",
        )
        for side in sides
    ]

    a_run(tmp_path, adapter=swapped)
    evidence = runs.rows(tmp_path / "results", av.NAME, "bands", "hrf")

    assert float(evidence[0]["artery_dice"]) == pytest.approx(0.0)
    assert float(evidence[0]["vein_dice"]) == pytest.approx(0.0)
    assert float(evidence[0]["vessels_dice"]) == pytest.approx(1.0)


def test_the_three_masks_are_kept_in_the_native_frame(tmp_path: Path) -> None:
    """The biomarker benchmark's input is these files, so it reads them rather than a run's scores."""
    a_run(tmp_path)

    kept = tmp_path / "runs" / av.NAME / "bands" / "hrf"

    assert (kept / "fingerprint.txt").read_text().strip()
    for key in "ab":
        for structure in ("artery", "vein", "vessels"):
            with Image.open(kept / f"{key}-{structure}.png") as mask:
                assert np.asarray(mask).shape == (SIDE, SIDE)
    with Image.open(kept / "a-vessels.png") as vessels:
        assert np.asarray(vessels).sum() == 2 * (SIDE // 4) * SIDE, "the union of the two classes"


def test_the_kept_masks_are_thrown_away_when_they_describe_another_model(tmp_path: Path) -> None:
    root = a_store(tmp_path)
    for shift in (0, 64):
        av.run(
            [Bands(shift=shift)],
            ["hrf"],
            results=tmp_path / "results",
            root=root,
            record=tmp_path / "runs",
        )

    kept = tmp_path / "runs" / av.NAME / "bands" / "hrf"
    with Image.open(kept / "a-artery.png") as mask:
        drawn = np.asarray(mask)

    assert not drawn[SIDE // 4].any(), (
        "the first model's band is gone, not left beside the second's"
    )
    assert drawn[SIDE // 4 + 64].all()


def test_a_model_that_fell_over_is_recorded_as_failed_rather_than_wrong(tmp_path: Path) -> None:
    a_run(tmp_path, adapter=Bands(fails=True))

    evidence = runs.rows(tmp_path / "results", av.NAME, "bands", "hrf")

    assert [entry["outcome"] for entry in evidence] == ["failed", "failed"]
    assert all("fell over" in entry["note"] for entry in evidence)
    assert "artery_dice" not in evidence[0], (
        "a measurement nothing produced is absent rather than blank"
    )


def test_a_second_run_measures_nothing_it_has_already_measured(tmp_path: Path) -> None:
    root = a_store(tmp_path)
    again = Bands()
    for adapter in (Bands(), again):
        av.run(
            [adapter],
            ["hrf"],
            results=tmp_path / "results",
            root=root,
            record=tmp_path / "runs",
        )

    assert again.asked == 0, "the stored scores describe the same model on the same store"


def test_a_rescore_measures_the_kept_masks_without_asking_the_model(tmp_path: Path) -> None:
    root = a_store(tmp_path)
    av.run([Bands()], ["hrf"], results=tmp_path / "results", root=root, record=tmp_path / "runs")

    again = Bands()
    scored = av.run(
        [again],
        ["hrf"],
        results=tmp_path / "results",
        root=root,
        record=tmp_path / "runs",
        rescore=True,
    )

    assert again.asked == 0
    assert scored[0]["summary"]["photographs"] == 2
    evidence = runs.rows(tmp_path / "results", av.NAME, "bands", "hrf")
    assert float(evidence[0]["artery_dice"]) == pytest.approx(1.0)
    assert "kept" in evidence[0]["resampling"]


def test_a_rescore_with_nothing_kept_says_so_rather_than_scoring_nothing(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match="--rescore"):
        a_run(tmp_path, rescore=True)


def test_every_column_of_the_evidence_is_documented(tmp_path: Path) -> None:
    """A column the configuration page does not explain is a bug rather than an omission."""
    a_run(tmp_path)

    evidence = runs.rows(tmp_path / "results", av.NAME, "bands", "hrf")

    assert set(evidence[0]) <= set(av.COLUMNS)


class OnlyVessels:
    """A stand-in model that answers about vessels and says nothing about which vessel it is.

    The vessel reference AutoMorph ships is this shape: one map, no classes. It exists here so the
    run is exercised by a real adapter rather than by a rehearsal of one.
    """

    slug = "only-vessels"
    purpose = "vessels"
    grid = 512
    structures = ("vessels",)

    def declare(self) -> dict[str, object]:
        return {
            "slug": self.slug,
            "purpose": self.purpose,
            "grid": self.grid,
            "network_grid": self.grid,
            "structures": list(self.structures),
            "emits_probabilities": True,
            "resampling": "probabilities to native, bilinear, then thresholded",
            "threshold": 0.2,
            "channels": ["vessel"],
            "ensemble": 1,
        }

    def identity(self) -> str:
        return "only-vessels-1"

    def prepare(self, pixels: np.ndarray) -> torch.Tensor:
        return torch.from_numpy(pixels.transpose(2, 0, 1).copy()).float() / 255.0

    def outline(self, images: torch.Tensor, sides: list[int]) -> list[Outlines]:
        answers = []
        for side in sides:
            quarter = side // 4
            drawn = band(side, slice(quarter, 2 * quarter), slice(None)) | band(
                side, slice(3 * quarter, 4 * quarter), slice(None)
            )
            answers.append(
                Outlines(
                    masks={"vessels": drawn},
                    resampling="probabilities to native, bilinear, then thresholded",
                )
            )
        return answers


def a_vessels_only_store(tmp_path: Path, keys: str = "ab") -> Path:
    """A store annotating vessels and neither class, as FIVES does."""
    root = tmp_path / "data"
    store = write_store(
        root, "fives", [row(key, maps="fov;vessels", crop_side=str(SIDE)) for key in keys]
    )
    (root / "fives" / "build.json").write_text(json.dumps({"builder_version": 6}))
    quarter = SIDE // 4
    drawn = band(SIDE, slice(quarter, 2 * quarter), slice(None)) | band(
        SIDE, slice(3 * quarter, 4 * quarter), slice(None)
    )
    for key in keys:
        write_masks(store, key, {"vessels": drawn})
    return root


def test_a_vessel_only_model_is_scored_on_the_vessel_column_alone(tmp_path: Path) -> None:
    """Its artery and vein columns are empty rather than zero: it was never asked."""
    av.run(
        [OnlyVessels()],
        ["hrf"],
        results=tmp_path / "results",
        root=a_store(tmp_path),
        record=tmp_path / "runs",
    )

    evidence = runs.rows(tmp_path / "results", av.NAME, "only-vessels", "hrf")

    assert float(evidence[0]["vessels_dice"]) == pytest.approx(1.0)
    assert evidence[0]["artery_dice"] == "", "it said nothing about arteries and is scored on none"
    assert evidence[0]["vein_dice"] == ""


def test_a_dataset_annotating_vessels_alone_is_measured_rather_than_excluded(
    tmp_path: Path,
) -> None:
    """FIVES annotates no classes, so every model is scored there on the vessel column only."""
    scored = av.run(
        [Bands()],
        ["fives"],
        results=tmp_path / "results",
        root=a_vessels_only_store(tmp_path),
        record=tmp_path / "runs",
    )

    assert scored[0]["counts"] == {"processed": 2, "total": 2, "complete": True, "excluded": {}}
    evidence = runs.rows(tmp_path / "results", av.NAME, "bands", "fives")
    assert float(evidence[0]["vessels_dice"]) == pytest.approx(1.0), (
        "the model's union against the vessels the dataset published"
    )
    assert evidence[0]["artery_dice"] == "", "there is no artery annotation to be right about"


def test_a_photograph_with_nothing_annotated_is_still_set_aside(tmp_path: Path) -> None:
    """Admitting a vessel-only annotation must not admit a photograph with no annotation at all."""
    root = tmp_path / "data"
    store = write_store(root, "fives", [row("a", maps="fov", crop_side=str(SIDE))])
    (root / "fives" / "build.json").write_text(json.dumps({"builder_version": 6}))
    del store

    scored = av.run(
        [Bands()],
        ["fives"],
        results=tmp_path / "results",
        root=root,
        record=tmp_path / "runs",
    )

    assert scored[0]["counts"]["processed"] == 0
    assert scored[0]["counts"]["excluded"] == {"no vessel annotation to score against": 1}
