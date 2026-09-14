# ABOUTME: Tests for what a benchmark is run on: the evaluation unit, the two exclusion rules of
# ABOUTME: the plan, and the photograph and ground truth one sample carries.

from pathlib import Path

import pytest
import torch
from conftest import row, write_store

from benchmarks.loaders import base, quality


def test_a_unit_is_a_dataset_a_subset_and_a_split() -> None:
    unit = base.Unit("fqs", "main", "unspecified")

    assert unit.name == "fqs/main/unspecified"
    assert unit.filename == "fqs-main-unspecified"


def test_only_the_units_own_rows_are_loaded(store: Path) -> None:
    write_store(
        store.parent,
        "mshf",
        [
            row("a", subset="cfp", split="train"),
            row("b", subset="cfp", split="test"),
            row("c", subset="portable", split="train"),
        ],
    )

    loader = base.Photographs(base.Unit("mshf", "cfp", "train"), size=512, root=store.parent)

    assert [sample["key"] for sample in loader] == ["a"]


def test_a_field_under_the_floor_is_excluded(store: Path) -> None:
    write_store(
        store.parent,
        "mshf",
        [row("big", crop_side="512"), row("small", crop_side="511")],
    )

    loader = base.Photographs(base.Unit("mshf", "main", "train"), size=512, root=store.parent)

    assert [sample["key"] for sample in loader] == ["big"]


def test_a_dataset_of_crops_is_refused_whole(store: Path) -> None:
    write_store(store.parent, "riga", [row("a")])

    with pytest.raises(ValueError, match="crops"):
        base.Photographs(base.Unit("riga", "main", "train"), size=512, root=store.parent)


def test_a_finding_against_a_photograph_keeps_it_out(store: Path, tmp_path: Path) -> None:
    write_store(store.parent, "fqs", [row("good_one"), row("broken")])
    findings = tmp_path / "exclusions"
    findings.mkdir()
    (findings / "fqs.json").write_text(
        '{"exclusions": [{"key": "broken", "maps": "*", "reason": "image-corrupt",'
        ' "detail": "truncated", "evidence": "the archive", "found": "2026-09-14"}]}'
    )

    loader = base.Photographs(
        base.Unit("fqs", "main", "train"), size=512, root=store.parent, findings=findings
    )

    assert [sample["key"] for sample in loader] == ["good_one"]


def test_the_key_travels_with_the_photograph(store: Path) -> None:
    write_store(store.parent, "fqs", [row("second"), row("first")], sizes=(512,))

    loader = base.Photographs(base.Unit("fqs", "main", "train"), size=512, root=store.parent)

    assert [sample["key"] for sample in loader] == ["first", "second"], "sorted by key"
    assert loader[0]["image"].shape == (3, 512, 512)


def test_the_photograph_is_prepared_by_the_model_that_asked_for_it(store: Path) -> None:
    write_store(store.parent, "fqs", [row("a")])

    loader = base.Photographs(
        base.Unit("fqs", "main", "train"),
        size=512,
        root=store.parent,
        prepare=lambda image: torch.zeros(3, 8, 8),
    )

    assert loader[0]["image"].shape == (3, 8, 8)


def test_quality_yields_the_datasets_own_grade(store: Path) -> None:
    write_store(store.parent, "fives", [row("a", quality="usable")])

    loader = quality.QualityLoader(base.Unit("fives", "main", "train"), size=512, root=store.parent)

    assert loader[0]["grade"] == "usable"


def test_quality_yields_every_readers_grade_where_the_dataset_keeps_them_apart(
    store: Path,
) -> None:
    write_store(
        store.parent,
        "mshf",
        [row("a", quality="good", multi_reader="quality")],
        readings=[
            {"key": "a", "field": "quality", "reader": "annotator1", "value": "good"},
            {"key": "a", "field": "quality", "reader": "annotator2", "value": "usable"},
            {"key": "a", "field": "clarity", "reader": "annotator1", "value": "good"},
        ],
    )

    loader = quality.QualityLoader(base.Unit("mshf", "main", "train"), size=512, root=store.parent)

    assert loader[0]["readers"] == {"annotator1": "good", "annotator2": "usable"}


def test_a_photograph_with_no_grade_is_not_part_of_a_quality_benchmark(store: Path) -> None:
    write_store(store.parent, "mshf", [row("graded"), row("ungraded", quality="")])

    loader = quality.QualityLoader(base.Unit("mshf", "main", "train"), size=512, root=store.parent)

    assert [sample["key"] for sample in loader] == ["graded"]
    assert loader.without_reference == ["ungraded"]


def test_a_batch_stacks_the_photographs_and_lists_everything_else(store: Path) -> None:
    write_store(store.parent, "fives", [row("a"), row("b", quality="bad")])
    loader = quality.QualityLoader(base.Unit("fives", "main", "train"), size=512, root=store.parent)

    batch = base.collate([loader[0], loader[1]])

    assert batch["image"].shape == (2, 3, 512, 512)
    assert batch["key"] == ["a", "b"]
    assert batch["grade"] == ["good", "bad"]
    assert batch["readers"] == [{}, {}]


def test_the_units_a_store_holds_are_read_from_its_manifest(store: Path) -> None:
    write_store(
        store.parent,
        "mshf",
        [
            row("a", subset="cfp", split="train"),
            row("b", subset="cfp", split="test"),
            row("c", subset="portable", split="train"),
        ],
    )

    found = base.units("mshf", root=store.parent)

    assert [unit.name for unit in found] == [
        "mshf/cfp/test",
        "mshf/cfp/train",
        "mshf/portable/train",
    ]
