# ABOUTME: Tests for the quality benchmark's run: what it scores, what it keeps, what it finishes
# ABOUTME: rather than repeats, and what it steps over when a dataset or a model is not there.

from pathlib import Path

import numpy as np
import pytest
import torch
from conftest import row, write_store

from benchmarks import quality, runs
from models.utils.grading import BAD, GOOD, Grade


class Brightness:
    """A stand-in model: it calls a bright photograph good and a dark one bad.

    It is a real adapter rather than a mock — the benchmark calls it exactly as it calls the
    catalogued models — so what these tests exercise is the run, not a rehearsal of one.
    """

    slug = "brightness"
    purpose = "quality"
    grid = 512

    def __init__(self, weights: str = "one") -> None:
        self.weights = weights
        self.scored: list[str] = []

    def declare(self) -> dict[str, object]:
        return {"slug": self.slug, "purpose": self.purpose, "grid": self.grid, "network_grid": 512}

    def identity(self) -> str:
        return self.weights

    def prepare(self, pixels: np.ndarray) -> torch.Tensor:
        return torch.from_numpy(pixels.transpose(2, 0, 1).copy()).float() / 255.0

    def grade(self, images: torch.Tensor, keys: list[str]) -> list[Grade]:
        self.scored.extend(keys)
        confidence = images.mean(dim=(1, 2, 3))
        return [
            Grade(key, verdict=GOOD if value > 0.05 else BAD, gradeable=float(value))
            for key, value in zip(keys, confidence, strict=True)
        ]


def a_store(tmp_path: Path, keys: str = "abc") -> Path:
    write_store(
        tmp_path / "data",
        "fives",
        [row(key, quality="good" if index else "bad") for index, key in enumerate(keys)],
    )
    return tmp_path / "data"


def test_a_run_scores_every_photograph_of_the_dataset(tmp_path: Path) -> None:
    scored = quality.run(
        [Brightness()], ["fives"], results=tmp_path / "results", root=a_store(tmp_path)
    )

    assert scored[0]["summary"]["photographs"] == 3
    assert scored[0]["counts"] == {
        "processed": 3,
        "total": 3,
        "complete": True,
        "excluded": {},
    }


def test_the_per_image_evidence_carries_where_each_photograph_came_from(tmp_path: Path) -> None:
    quality.run([Brightness()], ["fives"], results=tmp_path / "results", root=a_store(tmp_path))

    evidence = runs.rows(tmp_path / "results", quality.NAME, "brightness", "fives")

    assert [entry["key"] for entry in evidence] == ["a", "b", "c"]
    assert evidence[0]["subset"] == "main"
    assert evidence[0]["split"] == "train"
    assert evidence[0]["grade"] == "bad"


def test_a_second_run_scores_nothing_that_is_already_complete(tmp_path: Path) -> None:
    store = a_store(tmp_path)
    quality.run([Brightness()], ["fives"], results=tmp_path / "results", root=store)

    adapter = Brightness()
    quality.run([adapter], ["fives"], results=tmp_path / "results", root=store)

    assert adapter.scored == [], "a complete result is never re-run"


def test_a_sampled_run_is_finished_rather_than_repeated(tmp_path: Path) -> None:
    store = a_store(tmp_path)
    quality.run([Brightness()], ["fives"], results=tmp_path / "results", root=store, max_samples=1)

    adapter = Brightness()
    scored = quality.run([adapter], ["fives"], results=tmp_path / "results", root=store)

    assert adapter.scored == ["b", "c"], "only what was missing"
    assert scored[0]["counts"]["processed"] == 3
    assert scored[0]["counts"]["complete"] is True


def test_a_sample_never_truncates_what_is_already_there(tmp_path: Path) -> None:
    store = a_store(tmp_path)
    quality.run([Brightness()], ["fives"], results=tmp_path / "results", root=store)

    scored = quality.run(
        [Brightness()], ["fives"], results=tmp_path / "results", root=store, max_samples=1
    )

    assert scored[0]["counts"]["processed"] == 3, "asking for one leaves three alone"
    assert len(runs.rows(tmp_path / "results", quality.NAME, "brightness", "fives")) == 3


def test_a_sampled_run_says_it_is_not_complete(tmp_path: Path) -> None:
    scored = quality.run(
        [Brightness()],
        ["fives"],
        results=tmp_path / "results",
        root=a_store(tmp_path),
        max_samples=2,
    )

    assert scored[0]["counts"] == {
        "processed": 2,
        "total": 3,
        "complete": False,
        "excluded": {},
    }


def test_changed_weights_throw_away_what_was_measured(tmp_path: Path) -> None:
    store = a_store(tmp_path)
    quality.run([Brightness()], ["fives"], results=tmp_path / "results", root=store)

    adapter = Brightness(weights="retrained")
    quality.run([adapter], ["fives"], results=tmp_path / "results", root=store)

    assert adapter.scored == ["a", "b", "c"]


def test_a_forced_run_measures_everything_again(tmp_path: Path) -> None:
    store = a_store(tmp_path)
    quality.run([Brightness()], ["fives"], results=tmp_path / "results", root=store)

    adapter = Brightness()
    quality.run([adapter], ["fives"], results=tmp_path / "results", root=store, force=True)

    assert adapter.scored == ["a", "b", "c"]


def test_a_dataset_with_no_store_is_stepped_over_and_recorded(tmp_path: Path) -> None:
    scored = quality.run(
        [Brightness()],
        ["fives", "eyeq"],
        results=tmp_path / "results",
        root=a_store(tmp_path),
    )

    assert [entry["dataset"] for entry in scored] == ["fives"]
    assert quality.missing_datasets(["fives", "eyeq"], root=a_store(tmp_path)) == {
        "eyeq": "no store built"
    }


def test_a_dataset_excluded_whole_is_recorded_as_that_rather_than_as_missing(
    tmp_path: Path,
) -> None:
    assert quality.missing_datasets(["riga"], root=a_store(tmp_path)) == {
        "riga": "excluded whole: its images are crops rather than photographs"
    }


def test_a_model_with_no_adapter_is_stepped_over_and_recorded() -> None:
    adapters, missing = quality.adapters(["quickqual", "no-such-model"], device="cpu")

    assert [adapter.slug for adapter in adapters] == ["quickqual"]
    assert missing == {"no-such-model": "no adapter written"}


def test_a_run_with_nothing_available_is_an_error(tmp_path: Path) -> None:
    try:
        quality.run([Brightness()], ["eyeq"], results=tmp_path / "results", root=tmp_path)
    except RuntimeError as refused:
        assert "nothing" in str(refused)
    else:
        raise AssertionError("a run with nothing to measure should refuse to write a report")


def test_the_run_records_what_produced_it(tmp_path: Path) -> None:
    quality.run(
        [Brightness()],
        ["fives"],
        results=tmp_path / "results",
        root=a_store(tmp_path),
        record=tmp_path / "runs",
    )

    record = next((tmp_path / "runs").rglob("run.json")).read_text()

    assert "brightness" in record
    assert "builder_version" in record
    assert "processed" in record


def test_the_configuration_is_known_before_anything_is_measured(tmp_path: Path) -> None:
    """The page describing a run must not need the run to have happened."""
    adapter = Brightness()

    configured = quality.configuration([adapter], ["fives"], root=a_store(tmp_path))

    assert adapter.scored == [], "reading a manifest is not scoring a photograph"
    assert configured["models"] == [{"slug": "brightness", "declared": adapter.declare()}]
    assert configured["datasets"] == [
        {
            "slug": "fives",
            "total": 3,
            "excluded": {},
            "grade_source": ["published"],
            "padding": 0.0,
        }
    ]


def test_a_dataset_with_no_store_is_left_out_of_the_configuration(tmp_path: Path) -> None:
    configured = quality.configuration([Brightness()], ["fives", "eyeq"], root=a_store(tmp_path))

    assert [entry["slug"] for entry in configured["datasets"]] == ["fives"]


class Stopped(Brightness):
    """A model the machine stops part-way through, as an out-of-memory kill does."""

    def __init__(self, after: int = 1) -> None:
        super().__init__()
        self.after = after
        self.batches = 0

    def grade(self, images: torch.Tensor, keys: list[str]) -> list[Grade]:
        self.batches += 1
        if self.batches > self.after:
            raise KeyboardInterrupt("the machine ran out of memory")
        return super().grade(images, keys)


def test_a_run_stopped_part_way_keeps_what_it_had_scored(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(runs, "CHECKPOINT", 1)
    store = a_store(tmp_path)

    with pytest.raises(KeyboardInterrupt):
        quality.run(
            [Stopped(after=1)], ["fives"], results=tmp_path / "results", root=store, batch=1
        )

    stored = runs.read(tmp_path / "results", quality.NAME, "brightness", "fives")
    assert stored["summary"]["processed"] == 1
    assert stored["summary"]["complete"] is False

    finished = quality.run([Brightness()], ["fives"], results=tmp_path / "results", root=store)
    assert finished[0]["measured"] == 2, "only what the kill never reached"
