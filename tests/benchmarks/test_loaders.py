# ABOUTME: Tests for what a benchmark is run on: a whole dataset, the exclusions that take
# ABOUTME: photographs out of it and say why, the sampling, and what one sample carries.

from pathlib import Path

import pytest
import torch
from conftest import row, write_store

from benchmarks.loaders import base, quality


def test_a_store_that_was_never_built_is_not_available(tmp_path: Path) -> None:
    assert base.available("hrf", root=tmp_path) is False


def test_a_built_store_is_available(store: Path) -> None:
    write_store(store.parent, "fives", [row("a")])

    assert base.available("fives", root=store.parent) is True


def test_a_dataset_is_loaded_whole(store: Path) -> None:
    write_store(
        store.parent,
        "mshf",
        [
            row("a", subset="cfp", split="train"),
            row("b", subset="cfp", split="test"),
            row("c", subset="portable", split="train"),
        ],
    )

    loader = base.Photographs("mshf", size=512, root=store.parent)

    assert [sample["key"] for sample in loader] == ["a", "b", "c"], "one pass, every split"


def test_the_subset_and_split_travel_with_the_photograph(store: Path) -> None:
    write_store(store.parent, "mshf", [row("a", subset="portable", split="test")])

    sample = base.Photographs("mshf", size=512, root=store.parent)[0]

    assert (sample["subset"], sample["split"]) == ("portable", "test")


def test_a_field_under_the_floor_is_excluded_and_counted(store: Path) -> None:
    write_store(store.parent, "mshf", [row("big", crop_side="512"), row("small", crop_side="511")])

    loader = base.Photographs("mshf", size=512, root=store.parent)

    assert [sample["key"] for sample in loader] == ["big"]
    assert loader.excluded == {base.BELOW_THE_FLOOR: 1}
    assert loader.total == 1


def test_a_finding_against_a_photograph_is_excluded_and_counted(
    store: Path, tmp_path: Path
) -> None:
    write_store(store.parent, "fqs", [row("sound"), row("broken")])
    findings = tmp_path / "exclusions"
    findings.mkdir()
    (findings / "fqs.json").write_text(
        '{"exclusions": [{"key": "broken", "maps": "*", "reason": "image-corrupt",'
        ' "detail": "truncated", "evidence": "the archive", "found": "2026-09-15"}]}'
    )

    loader = base.Photographs("fqs", size=512, root=store.parent, findings=findings)

    assert [sample["key"] for sample in loader] == ["sound"]
    assert loader.excluded == {base.A_RECORDED_FINDING: 1}


def test_a_dataset_of_crops_is_refused_whole(store: Path) -> None:
    write_store(store.parent, "riga", [row("a")])

    with pytest.raises(ValueError, match="crops"):
        base.Photographs("riga", size=512, root=store.parent)


def test_the_first_photographs_are_taken_when_a_run_asks_for_a_sample(store: Path) -> None:
    write_store(store.parent, "fives", [row("c"), row("a"), row("b")])

    loader = base.Photographs("fives", size=512, root=store.parent, max_samples=2)

    assert [sample["key"] for sample in loader] == ["a", "b"], "the first two, in the store's order"
    assert loader.total == 3, "the dataset still holds three"
    assert loader.sampled is True


def test_a_random_sample_is_the_same_sample_twice_from_one_seed(store: Path) -> None:
    write_store(store.parent, "fives", [row(letter) for letter in "abcdefgh"])
    taken = [
        [
            sample["key"]
            for sample in base.Photographs(
                "fives", size=512, root=store.parent, max_samples=3, random_samples=True, seed=7
            )
        ]
        for _ in range(2)
    ]

    assert taken[0] == taken[1]
    assert len(taken[0]) == 3
    assert taken[0] != ["a", "b", "c"], "a random sample is not the first three"


def test_asking_for_more_than_the_dataset_holds_is_not_a_sample(store: Path) -> None:
    write_store(store.parent, "fives", [row("a"), row("b")])

    loader = base.Photographs("fives", size=512, root=store.parent, max_samples=99)

    assert loader.sampled is False


def test_a_run_can_restrict_itself_to_the_photographs_it_still_needs(store: Path) -> None:
    write_store(store.parent, "fives", [row("a"), row("b"), row("c")])
    loader = base.Photographs("fives", size=512, root=store.parent)

    loader.restrict({"b", "c"})

    assert [row["key"] for row in loader.rows] == ["b", "c"]
    assert loader.total == 3, "restricting is about work left, not about the dataset"


def test_the_photograph_is_prepared_by_the_model_that_asked_for_it(store: Path) -> None:
    write_store(store.parent, "fqs", [row("a")])

    loader = base.Photographs(
        "fqs", size=512, root=store.parent, prepare=lambda image: torch.zeros(3, 8, 8)
    )

    assert loader[0]["image"].shape == (3, 8, 8)
    assert base.Photographs("fqs", size=512, root=store.parent)[0]["image"].shape == (3, 512, 512)


def test_quality_yields_the_datasets_own_grade(store: Path) -> None:
    write_store(store.parent, "fives", [row("a", quality="usable")])

    assert quality.QualityLoader("fives", size=512, root=store.parent)[0]["grade"] == "usable"


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

    loader = quality.QualityLoader("mshf", size=512, root=store.parent)

    assert loader[0]["readers"] == {"annotator1": "good", "annotator2": "usable"}


def test_a_photograph_with_no_grade_is_excluded_with_its_own_reason(store: Path) -> None:
    write_store(store.parent, "mshf", [row("graded"), row("ungraded", quality="")])

    loader = quality.QualityLoader("mshf", size=512, root=store.parent)

    assert [sample["key"] for sample in loader] == ["graded"]
    assert loader.excluded == {quality.NO_REFERENCE: 1}
    assert loader.total == 1


def test_a_batch_stacks_the_photographs_and_lists_everything_else(store: Path) -> None:
    write_store(store.parent, "fives", [row("a"), row("b", quality="bad", split="test")])
    loader = quality.QualityLoader("fives", size=512, root=store.parent)

    batch = base.collate([loader[0], loader[1]])

    assert batch["image"].shape == (2, 3, 512, 512)
    assert batch["key"] == ["a", "b"]
    assert batch["grade"] == ["good", "bad"]
    assert batch["split"] == ["train", "test"]
    assert batch["readers"] == [{}, {}]
