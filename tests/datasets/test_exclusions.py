# ABOUTME: Tests for exclusions: findings recorded in the repository, applied when a store is read.
# ABOUTME: A store always holds what the dataset published, including the images we distrust.

import json

import pytest

from datasets.utils import exclusions, manifest


def write_store(tmp_path, rows):
    manifest.write(tmp_path, rows, extra_columns=[])
    return tmp_path


def write_findings(tmp_path, entries):
    path = tmp_path / "fives.json"
    path.write_text(json.dumps({"dataset": "fives", "exclusions": entries}))
    return path


def test_a_dataset_with_no_findings_loses_nothing(tmp_path):
    store = write_store(tmp_path, [{"key": "a"}, {"key": "b"}])
    rows = list(exclusions.usable_rows(store, findings=[]))
    assert [row["key"] for row in rows] == ["a", "b"]


def test_an_image_excluded_outright_is_not_returned(tmp_path):
    store = write_store(tmp_path, [{"key": "a"}, {"key": "b"}])
    found = [exclusions.Exclusion("a", "*", "image-corrupt", "truncated", "issue 4", "2026-09-11")]
    assert [row["key"] for row in exclusions.usable_rows(store, findings=found)] == ["b"]


def test_an_image_with_one_bad_map_keeps_its_good_ones(tmp_path):
    store = write_store(tmp_path, [{"key": "a", "maps": "vessels;av;fov"}])
    found = [
        exclusions.Exclusion("a", ["av"], "annotation-incomplete", "half", "eye", "2026-09-11")
    ]
    row = next(iter(exclusions.usable_rows(store, findings=found)))
    assert row["maps"] == "vessels;fov"


def test_the_store_itself_still_holds_every_image(tmp_path):
    store = write_store(tmp_path, [{"key": "a"}, {"key": "b"}])
    assert len(list(manifest.read(store))) == 2


def test_inspecting_a_finding_can_ask_for_the_excluded_rows(tmp_path):
    store = write_store(tmp_path, [{"key": "a"}, {"key": "b"}])
    found = [
        exclusions.Exclusion("a", "*", "not-a-fundus", "a slit lamp photo", "eye", "2026-09-11")
    ]
    rows = list(exclusions.usable_rows(store, findings=found, include_excluded=True))
    assert [row["key"] for row in rows] == ["a", "b"]


def test_a_reason_outside_the_vocabulary_is_refused(tmp_path):
    write_findings(
        tmp_path,
        [
            {
                "key": "a",
                "maps": "*",
                "reason": "looks odd",
                "detail": "d",
                "evidence": "e",
                "found": "2026-09-11",
            }
        ],
    )
    with pytest.raises(ValueError, match="looks odd"):
        exclusions.load("fives", directory=tmp_path)


def test_findings_are_read_from_the_repository(tmp_path):
    write_findings(
        tmp_path,
        [
            {
                "key": "a",
                "maps": ["av"],
                "reason": "mismatched-pair",
                "detail": "d",
                "evidence": "e",
                "found": "2026-09-11",
            }
        ],
    )
    found = exclusions.load("fives", directory=tmp_path)
    assert found[0].key == "a"
    assert found[0].maps == ["av"]


def test_a_dataset_with_no_findings_file_has_no_findings(tmp_path):
    assert exclusions.load("hrf", directory=tmp_path) == []


def test_one_readers_bad_outline_does_not_discard_the_others(tmp_path):
    # Chaksu's Image145 has five experts' discs; one of them is a broken mask. Excluding "disc"
    # for that image would throw away four good outlines to be rid of one bad one.
    finding = exclusions.Exclusion(
        "a",
        ["disc"],
        "annotation-incomplete",
        "fragments",
        "notes",
        "2026-09-12",
        readers=["expert2"],
    )
    drawn = {
        ("disc", "expert1"): "good",
        ("disc", "expert2"): "broken",
        ("cup", "expert2"): "good",
    }
    kept = exclusions.trusted_outlines("a", drawn, findings=[finding])
    assert set(kept) == {("disc", "expert1"), ("cup", "expert2")}


def test_a_reader_scoped_finding_leaves_the_row_and_its_maps_alone(tmp_path):
    store = write_store(tmp_path, [{"key": "a", "maps": "fov;disc;cup"}])
    finding = exclusions.Exclusion(
        "a",
        ["disc"],
        "annotation-incomplete",
        "fragments",
        "notes",
        "2026-09-12",
        readers=["expert2"],
    )
    row = next(iter(exclusions.usable_rows(store, findings=[finding])))
    assert row["maps"] == "fov;disc;cup"


def test_a_finding_naming_no_reader_covers_every_reader(tmp_path):
    finding = exclusions.Exclusion(
        "a", ["disc"], "ground-truth-wrong", "wrong eye", "notes", "2026-09-12"
    )
    drawn = {("disc", "expert1"): "x", ("cup", "expert1"): "y"}
    assert set(exclusions.trusted_outlines("a", drawn, findings=[finding])) == {("cup", "expert1")}


def test_outlines_of_an_image_nobody_flagged_are_untouched(tmp_path):
    drawn = {("disc", "expert1"): "x"}
    assert exclusions.trusted_outlines("b", drawn, findings=[]) == drawn


def test_the_findings_recorded_for_chaksu_load_and_name_real_readers():
    found = exclusions.load("chaksu")
    assert len(found) >= 3
    assert all(f.maps == ["disc"] for f in found)
    assert all(f.readers != exclusions.EVERYTHING for f in found)
