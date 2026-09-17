# ABOUTME: Tests for the native resolution a manifest records: a published value, one derived from a
# ABOUTME: stated field angle per image, the honest absence of one, and an inferred camera scale.

import csv
import json

import pytest

from datasets.utils import manifest, resolution


def test_a_field_angle_is_a_resolution_per_image_rather_than_per_dataset():
    declared = resolution.Declared(
        um_per_px=None, source="field_angle", degrees=30, note="a 30 degree camera"
    )

    # 300 microns to the degree, over a field 900 pixels across.
    assert declared.for_field(450.0) == pytest.approx(300 * 30 / 900)


def test_a_declared_value_ignores_the_field_it_is_given():
    declared = resolution.Declared(um_per_px=4.0, source="published", note="stated by the authors")

    assert declared.for_field(450.0) == pytest.approx(4.0)


def test_an_unknown_resolution_stays_unknown_whatever_the_field():
    declared = resolution.Declared(um_per_px=None, source="unknown", note="nothing published")

    assert declared.for_field(450.0) is None


def test_a_field_angle_without_the_angle_is_refused():
    with pytest.raises(ValueError, match="degrees"):
        resolution.Declared(um_per_px=None, source="field_angle", note="a camera")


def a_store(tmp_path, rows, builder_version=6):
    """A store with a manifest and a build record, as a build leaves them."""
    store = tmp_path / "chaksu"
    store.mkdir(parents=True, exist_ok=True)
    with open(store / manifest.MANIFEST, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(manifest.CORE_COLUMNS), restval="")
        writer.writeheader()
        writer.writerows(rows)
    (store / "build.json").write_text(json.dumps({"builder_version": builder_version}))
    return store


def a_row(key, **overrides):
    record = {
        "key": key,
        "subset": "bosch",
        "native_width": "1920",
        "native_height": "1440",
        "crop_side": "1400",
        "um_per_px": "",
        "resolution_source": "unknown",
    }
    record.update(overrides)
    return record


def an_inference(tmp_path, groups, builder_version=6):
    directory = tmp_path / "um_resolution"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "chaksu.json").write_text(
        json.dumps({"dataset": "chaksu", "builder_version": builder_version, "groups": groups})
    )
    return directory


def a_group(**overrides):
    group = {
        "subset": "bosch",
        "native_width": 1920,
        "native_height": 1440,
        "accepted": True,
        "um_per_px": 8.61,
        "note": "",
    }
    group.update(overrides)
    return group


def test_an_inferred_scale_is_copied_into_the_rows_it_was_measured_from(tmp_path) -> None:
    store = a_store(tmp_path, [a_row("a"), a_row("b")])

    stamped = resolution.stamp(store, "chaksu", an_inference(tmp_path, [a_group()]))

    rows = list(manifest.read(store))
    assert stamped == 2
    assert [row["um_per_px"] for row in rows] == ["8.610000", "8.610000"]
    assert [row["resolution_source"] for row in rows] == ["disc_anchored", "disc_anchored"]


def test_a_published_scale_is_never_overwritten_by_an_inferred_one(tmp_path) -> None:
    """An author's measurement beats our assumption about how big a disc usually is."""
    store = a_store(tmp_path, [a_row("a", um_per_px="6.000000", resolution_source="published")])

    stamped = resolution.stamp(store, "chaksu", an_inference(tmp_path, [a_group()]))

    row = next(iter(manifest.read(store)))
    assert stamped == 0
    assert row["um_per_px"] == "6.000000"
    assert row["resolution_source"] == "published"


def test_a_photograph_of_another_camera_is_left_alone(tmp_path) -> None:
    store = a_store(tmp_path, [a_row("a"), a_row("b", subset="forus", native_width="2048")])

    resolution.stamp(store, "chaksu", an_inference(tmp_path, [a_group()]))

    rows = {row["key"]: row for row in manifest.read(store)}
    assert rows["a"]["um_per_px"] == "8.610000"
    assert rows["b"]["um_per_px"] == ""
    assert rows["b"]["resolution_source"] == "unknown"


def test_a_group_that_failed_its_gate_stamps_nothing(tmp_path) -> None:
    store = a_store(tmp_path, [a_row("a")])
    refused = a_group(accepted=False, note="its discs disagree by more than a tenth")
    refused.pop("um_per_px")

    stamped = resolution.stamp(store, "chaksu", an_inference(tmp_path, [refused]))

    assert stamped == 0
    assert next(iter(manifest.read(store)))["um_per_px"] == ""


def test_a_scale_measured_on_another_store_is_refused(tmp_path) -> None:
    """A crop rule that changed since the discs were measured changes the discs."""
    store = a_store(tmp_path, [a_row("a")], builder_version=7)

    try:
        resolution.stamp(store, "chaksu", an_inference(tmp_path, [a_group()], builder_version=6))
    except ValueError as refused:
        assert "builder" in str(refused)
    else:
        raise AssertionError("a scale measured on a differently built store must not be stamped")


def test_a_dataset_with_no_inference_is_left_as_it_is(tmp_path) -> None:
    store = a_store(tmp_path, [a_row("a")])

    stamped = resolution.stamp(store, "chaksu", tmp_path / "um_resolution")

    assert stamped == 0
    assert next(iter(manifest.read(store)))["resolution_source"] == "unknown"


def test_a_photograph_a_few_pixels_off_its_camera_is_still_that_camera(tmp_path) -> None:
    """Field-of-view detection moves the native size by a few pixels on one device.

    The group that was measured tolerates 10%; the stamp has to tolerate the same, or the rows
    that made the measurement possible are the ones left without it.
    """
    rows = [a_row("a"), a_row("b", native_width="1907", native_height="1433")]
    store = a_store(tmp_path, rows)

    stamped = resolution.stamp(store, "chaksu", an_inference(tmp_path, [a_group()]))

    assert stamped == 2
    assert all(row["um_per_px"] == "8.610000" for row in manifest.read(store))


def test_a_photograph_between_two_cameras_takes_the_nearer_one(tmp_path) -> None:
    store = a_store(tmp_path, [a_row("a", native_width="2100", native_height="1500")])
    two = [a_group(), a_group(native_width=2200, native_height=1560, um_per_px=7.5)]

    resolution.stamp(store, "chaksu", an_inference(tmp_path, two))

    assert next(iter(manifest.read(store)))["um_per_px"] == "7.500000"
