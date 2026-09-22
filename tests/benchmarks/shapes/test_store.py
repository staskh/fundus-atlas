# ABOUTME: Tests for the synthetic store: what a generated rendering is written as, and the rule
# ABOUTME: that what is read back is exactly what was drawn.

import csv
from pathlib import Path

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


def test_a_mask_read_back_survives_being_walked(tmp_path) -> None:
    """Reading it correctly is not enough: it has to be usable by what measures it.

    A one-bit PNG opens as a mode `1` image, and handing that straight to NumPy gives an array that
    compares equal to the mask written and yet whose memory is not what it claims — anything walking
    it in C reads past the buffer and the process dies with no exception to catch. Every measurement
    downstream skeletonises these masks, so that is what this asserts.
    """
    from skimage.morphology import skeletonize

    a_store(tmp_path, rotations=(0.0,))
    drawn = library.build("straight", side=SIDE, um_per_px=10.0)

    read = store.load(tmp_path / "av", "straight-1024-000")

    assert int(skeletonize(read.artery).sum()) == int(skeletonize(drawn.artery).sum())
    assert int(skeletonize(read.vein).sum()) > 0


def test_the_committed_store_and_the_library_settle_the_same_quantities() -> None:
    """The store is drawn from the library, and nothing keeps them in step but this.

    `ground_truth.csv` holds one column per catalogued name some shape settles, and the library is
    where those values come from. They can drift apart for ordinary reasons — a shape gains a value
    and the store is not redrawn, or the store is drawn with different parameters — and nothing
    would say so: the benchmark's configuration page reports what the *library* settles, while a
    run that reads the store measures what the *store* settles. This is what notices.

    It compares at the store's own parameters, read from its manifest, so it is a test of agreement
    rather than a test that the store was drawn with the settings the benchmark happens to declare.
    """
    from benchmarks.shapes import library

    where = Path(library.__file__).resolve().parents[3] / store.STORE
    manifest = store.read(where)
    assert manifest, f"no synthetic store at {where} — draw one with `python -m benchmarks.shapes`"

    side = int(manifest[0]["side"])
    um_per_px = float(manifest[0]["um_per_px"])
    families = list(dict.fromkeys(row["family"] for row in manifest))

    with (where / "ground_truth.csv").open() as handle:
        stored = {name for name in next(csv.reader(handle)) if name != "key"}
    drawn = {
        name
        for family in families
        for name in library.build(family, side=side, um_per_px=um_per_px).theory
    }

    assert stored == drawn, (
        f"the store and the library disagree — redraw it with `python -m benchmarks.shapes`.\n"
        f"only in the store:   {sorted(stored - drawn)}\n"
        f"only in the library: {sorted(drawn - stored)}"
    )
