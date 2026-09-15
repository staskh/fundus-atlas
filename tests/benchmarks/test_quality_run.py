# ABOUTME: Tests for the quality benchmark itself: what it scores, what it keeps, and its promise
# ABOUTME: that a re-run measures only what has actually changed.

from pathlib import Path

import numpy as np
import torch
from conftest import row, write_store

from benchmarks import quality, runs
from benchmarks.loaders.base import Unit
from models.utils.grading import BAD, GOOD, Grade


class Brightness:
    """A stand-in model: it calls a bright photograph good and a dark one bad.

    It is a real adapter rather than a mock — the benchmark calls it exactly as it calls the
    catalogued four — so what these tests exercise is the run, not a rehearsal of one.
    """

    slug = "brightness"
    purpose = "quality"
    grid = 512

    def __init__(self, weights: str = "one") -> None:
        self.weights = weights

    def declare(self) -> dict[str, object]:
        return {"slug": self.slug, "purpose": self.purpose, "grid": self.grid, "network_grid": 512}

    def identity(self) -> str:
        return self.weights

    def prepare(self, pixels: np.ndarray) -> torch.Tensor:
        return torch.from_numpy(pixels.transpose(2, 0, 1).copy()).float() / 255.0

    def grade(self, images: torch.Tensor, keys: list[str]) -> list[Grade]:
        confidence = images.mean(dim=(1, 2, 3))
        return [
            Grade(key, verdict=GOOD if value > 0.05 else BAD, gradeable=float(value))
            for key, value in zip(keys, confidence, strict=True)
        ]


def a_store(tmp_path: Path) -> Path:
    write_store(
        tmp_path / "data",
        "fives",
        [row("dark", quality="bad"), row("light", quality="good")],
    )
    return tmp_path / "data"


def test_a_run_scores_every_photograph_of_the_unit(tmp_path: Path) -> None:
    unit = Unit("fives", "main", "train")

    results = quality.run(
        [Brightness()], [unit], results=tmp_path / "results", root=a_store(tmp_path)
    )

    assert results[0]["summary"]["photographs"] == 2
    assert results[0]["summary"]["coverage"] == 1.0
    assert results[0]["reused"] is False


def test_the_per_image_evidence_is_kept_beside_the_summary(tmp_path: Path) -> None:
    unit = Unit("fives", "main", "train")
    quality.run([Brightness()], [unit], results=tmp_path / "results", root=a_store(tmp_path))

    evidence = list(runs.rows(tmp_path / "results", quality.NAME, "brightness", unit))

    assert [entry["key"] for entry in evidence] == ["dark", "light"]
    assert evidence[0]["grade"] == "bad"
    assert evidence[0]["outcome"] == "graded"


def test_a_result_carries_the_mark_that_says_what_it_is_worth(tmp_path: Path) -> None:
    results = quality.run(
        [Brightness()],
        [Unit("fives", "main", "train")],
        results=tmp_path / "results",
        root=a_store(tmp_path),
    )

    assert results[0]["contamination"] == "unknown", "no page, so nothing is cleared"


def test_a_second_run_measures_nothing_that_has_not_changed(tmp_path: Path) -> None:
    unit = Unit("fives", "main", "train")
    store = a_store(tmp_path)
    quality.run([Brightness()], [unit], results=tmp_path / "results", root=store)

    again = quality.run([Brightness()], [unit], results=tmp_path / "results", root=store)

    assert again[0]["reused"] is True


def test_changed_weights_are_measured_again(tmp_path: Path) -> None:
    unit = Unit("fives", "main", "train")
    store = a_store(tmp_path)
    quality.run([Brightness()], [unit], results=tmp_path / "results", root=store)

    again = quality.run(
        [Brightness(weights="retrained")], [unit], results=tmp_path / "results", root=store
    )

    assert again[0]["reused"] is False


def test_a_forced_run_measures_everything_again(tmp_path: Path) -> None:
    unit = Unit("fives", "main", "train")
    store = a_store(tmp_path)
    quality.run([Brightness()], [unit], results=tmp_path / "results", root=store)

    again = quality.run(
        [Brightness()], [unit], results=tmp_path / "results", root=store, force=True
    )

    assert again[0]["reused"] is False


def test_the_run_records_what_produced_it(tmp_path: Path) -> None:
    quality.run(
        [Brightness()],
        [Unit("fives", "main", "train")],
        results=tmp_path / "results",
        root=a_store(tmp_path),
        record=tmp_path / "runs",
    )

    record = next((tmp_path / "runs").rglob("run.json"))

    assert "brightness" in record.read_text()
    assert "builder_version" in record.read_text()


class Fickle(Brightness):
    """A model that answers for one photograph and crashes on the other."""

    slug = "fickle"

    def grade(self, images, keys):
        from models.utils.grading import FAILED, Grade

        return [
            Grade(key, outcome=FAILED, note="broke")
            if index == 0
            else Grade(key, verdict=GOOD, gradeable=0.8, classes={GOOD: 0.8, BAD: 0.2})
            for index, key in enumerate(keys)
        ]


def test_a_photograph_the_model_failed_on_keeps_the_same_columns(tmp_path: Path) -> None:
    unit = Unit("fives", "main", "train")
    quality.run([Fickle()], [unit], results=tmp_path / "results", root=a_store(tmp_path))

    evidence = list(runs.rows(tmp_path / "results", quality.NAME, "fickle", unit))

    assert list(evidence[0]) == list(evidence[1])
    assert evidence[0]["outcome"] == "failed"
    assert evidence[0]["good"] == ""


def test_a_model_is_let_go_of_once_its_units_are_done(tmp_path: Path) -> None:
    """Five ensembles held at once is how a run gets killed for memory."""

    class Heavy(Brightness):
        slug = "heavy"

        def __init__(self) -> None:
            super().__init__()
            self.released = 0

        def release(self) -> None:
            self.released += 1

    adapter = Heavy()
    quality.run(
        [adapter],
        [Unit("fives", "main", "train")],
        results=tmp_path / "results",
        root=a_store(tmp_path),
    )

    assert adapter.released == 1


def test_a_model_with_nothing_to_let_go_of_is_left_alone(tmp_path: Path) -> None:
    quality.run(
        [Brightness()],
        [Unit("fives", "main", "train")],
        results=tmp_path / "results",
        root=a_store(tmp_path),
    )


def test_a_reworded_declaration_does_not_throw_away_hours_of_measurement(tmp_path: Path) -> None:
    """Prose is not a fact about the numbers."""

    class Reworded(Brightness):
        def declare(self) -> dict[str, object]:
            return {**super().declare(), "gate": "a longer explanation of the same rule"}

    unit = Unit("fives", "main", "train")
    store = a_store(tmp_path)
    quality.run([Brightness()], [unit], results=tmp_path / "results", root=store)

    again = quality.run([Reworded()], [unit], results=tmp_path / "results", root=store)

    assert again[0]["reused"] is True


def test_a_changed_grid_is_measured_again(tmp_path: Path) -> None:
    class Finer(Brightness):
        def declare(self) -> dict[str, object]:
            return {**super().declare(), "network_grid": 1024}

    unit = Unit("fives", "main", "train")
    store = a_store(tmp_path)
    quality.run([Brightness()], [unit], results=tmp_path / "results", root=store)

    again = quality.run([Finer()], [unit], results=tmp_path / "results", root=store)

    assert again[0]["reused"] is False


def test_a_changed_gate_threshold_is_measured_again(tmp_path: Path) -> None:
    """A number the model acts on is a fact, even though the rule around it is prose."""

    class Stricter(Brightness):
        def declare(self) -> dict[str, object]:
            return {**super().declare(), "gate_threshold": 0.1}

    unit = Unit("fives", "main", "train")
    store = a_store(tmp_path)
    quality.run([Brightness()], [unit], results=tmp_path / "results", root=store)

    again = quality.run([Stricter()], [unit], results=tmp_path / "results", root=store)

    assert again[0]["reused"] is False
