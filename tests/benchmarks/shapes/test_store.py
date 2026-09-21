# ABOUTME: Tests for the synthetic store: what a generated rendering is written as, and the rule
# ABOUTME: that what is read back is exactly what was drawn.

import csv

import numpy as np
import pytest

from benchmarks.shapes import library, store

SIDE = 1024


def a_store(tmp_path, families=("straight",), rotations=(0.0, 90.0)):
    return store.write(
        tmp_path / "av",
        families=families,
        side=SIDE,
        um_per_px=10.0,
        rotations=rotations,
    )


def test_it_writes_a_manifest_a_ground_truth_and_three_masks_per_rendering(tmp_path) -> None:
    written = a_store(tmp_path)

    assert (tmp_path / "av" / "manifest.csv").exists()
    assert (tmp_path / "av" / "ground_truth.csv").exists()
    assert len(written) == 2, "one rendering per rotation"
    for row in written:
        for which in ("artery", "vein", "fov"):
            assert (tmp_path / "av" / row[which]).exists(), f"{which} was not written"


def test_a_rendering_is_keyed_by_its_family_its_grid_and_its_angle(tmp_path) -> None:
    """The key is the name of the picture, so a row and a file cannot drift apart."""
    written = a_store(tmp_path, rotations=(0.0, 30.0, 60.0, 90.0))

    keys = [row["key"] for row in written]
    assert keys == [
        "straight-1024-000",
        "straight-1024-030",
        "straight-1024-060",
        "straight-1024-090",
    ]
    assert len(set(keys)) == len(keys), "a key identifies one rendering"
    assert written[1]["artery"] == "straight-1024-030-artery.png"


def test_what_is_read_back_is_exactly_what_was_drawn(tmp_path) -> None:
    """A mask that changed on its way through a file would move every measurement after it."""
    a_store(tmp_path, rotations=(30.0,))
    drawn = library.build("straight", side=SIDE, rotation=30.0, um_per_px=10.0)

    read = store.load(tmp_path / "av", "straight-1024-030")

    assert np.array_equal(read.artery, drawn.artery)
    assert np.array_equal(read.vein, drawn.vein)
    assert np.array_equal(read.fov, drawn.fov)
    assert read.disc == pytest.approx(drawn.disc)
    assert read.um_per_px == drawn.um_per_px


def test_the_manifest_records_the_disc_in_pixels_and_in_microns(tmp_path) -> None:
    """A measurement needs the disc in pixels; a reader needs to know what size that is."""
    a_store(tmp_path, rotations=(0.0,))

    with (tmp_path / "av" / "manifest.csv").open() as handle:
        row = next(iter(csv.DictReader(handle)))

    assert float(row["disc_r"]) == pytest.approx(library.DISC_DIAMETER_UM / 2.0 / 10.0)
    assert float(row["disc_diameter_um"]) == pytest.approx(library.DISC_DIAMETER_UM)
    assert float(row["artery_width_um"]) == pytest.approx(library.ARTERY_WIDTH_UM)
    assert float(row["um_per_px"]) == pytest.approx(10.0)


def test_the_ground_truth_carries_every_value_the_shape_pins(tmp_path) -> None:
    """Under canonical names, so a measurement can be compared without a translation step."""
    a_store(tmp_path, rotations=(0.0,))
    drawn = library.build("straight", side=SIDE, um_per_px=10.0)

    with (tmp_path / "av" / "ground_truth.csv").open() as handle:
        row = next(iter(csv.DictReader(handle)))

    assert row["key"] == "straight-1024-000"
    for name, value in drawn.theory.items():
        assert float(row[name]) == pytest.approx(value), f"{name} was not written as it was derived"


def test_a_family_pinning_nothing_for_a_column_leaves_it_empty(tmp_path) -> None:
    """Two families do not pin the same quantities, and a blank is not a zero."""
    a_store(tmp_path, families=("straight", "spokes-disc-centred"), rotations=(0.0,))

    with (tmp_path / "av" / "ground_truth.csv").open() as handle:
        rows = {row["key"]: row for row in csv.DictReader(handle)}

    equivalent = "central-retinal-equivalents/hubbard/artery"
    assert rows["straight-1024-000"][equivalent] == "", "a straight vessel reaches no ring"
    assert float(rows["spokes-disc-centred-1024-000"][equivalent]) > 0


def test_the_command_draws_what_it_was_asked_for(tmp_path) -> None:
    """The utility is the only way a store is made, so it is what has to be right."""
    from benchmarks.shapes import __main__ as command

    command.main(
        [
            "--into",
            str(tmp_path / "av"),
            "--family",
            "straight,disjoint",
            "--side",
            str(SIDE),
            "--um-per-px",
            "10",
            "--rotations",
            "0,45",
        ]
    )

    rows = store.read(tmp_path / "av")
    assert [row["key"] for row in rows] == [
        "straight-1024-000",
        "straight-1024-045",
        "disjoint-1024-000",
        "disjoint-1024-045",
    ]
    assert float(rows[0]["um_per_px"]) == 10.0


def test_naming_no_family_draws_every_one_of_them(tmp_path) -> None:
    """A store missing a family is a benchmark quietly measuring less than it says it does."""
    written = store.write(tmp_path / "av", side=SIDE, um_per_px=10.0, rotations=(0.0,))

    assert {row["family"] for row in written} == set(library.SHAPES)
    assert len(written) == len(library.SHAPES)
