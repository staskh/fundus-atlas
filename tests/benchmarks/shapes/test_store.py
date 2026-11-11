# ABOUTME: Tests for the synthetic store: what a generated rendering is written as, and the rule
# ABOUTME: that what is read back is exactly what was drawn.

import csv
from pathlib import Path

import numpy as np
import pytest

from benchmarks.shapes import library, render, scene, store

SIDE = 512


def a_store(tmp_path, families=("straight",), rotations=(0.0, 90.0)):
    return store.write(tmp_path / "av", families=families, side=SIDE, rotations=rotations)


def test_it_writes_a_manifest_a_ground_truth_its_kinds_and_three_masks(tmp_path) -> None:
    written = a_store(tmp_path)

    for name in ("manifest.csv", "ground_truth.csv", "ground_truth_kind.csv"):
        assert (tmp_path / "av" / name).exists(), name
    assert len(written) == 2, "one rendering per rotation"
    for row in written:
        for which in ("artery", "vein", "fov"):
            assert (tmp_path / "av" / row[which]).exists(), f"{which} was not written"


def test_a_rendering_is_keyed_by_its_family_its_grid_and_its_angle(tmp_path) -> None:
    """The key is the name of the picture, so a row and a file cannot drift apart."""
    written = a_store(tmp_path, rotations=(0.0, 15.0, 90.0))

    keys = [row["key"] for row in written]
    assert keys == ["straight-512-000", "straight-512-015", "straight-512-090"]
    assert written[1]["artery"] == "straight-512-015-artery.png"


def test_what_is_read_back_is_exactly_what_was_drawn(tmp_path) -> None:
    """A mask that changed on its way through a file would move every measurement after it."""
    a_store(tmp_path, rotations=(30.0,))
    drawn = library.build("straight", side=SIDE, rotation=30.0)

    read = store.load(tmp_path / "av", "straight-512-030")

    assert np.array_equal(read.artery, drawn.artery)
    assert np.array_equal(read.vein, drawn.vein)
    assert np.array_equal(read.fov, drawn.fov)
    assert read.disc == pytest.approx(drawn.disc, abs=1e-4)
    assert read.um_per_px == pytest.approx(drawn.um_per_px)


def test_the_manifest_records_the_scale_the_disc_and_the_widths(tmp_path) -> None:
    """A measurement needs the disc in pixels; a reader needs to know what size that is."""
    a_store(tmp_path, rotations=(0.0,))

    with (tmp_path / "av" / "manifest.csv").open() as handle:
        row = next(iter(csv.DictReader(handle)))

    um = render.um_per_px(SIDE)
    assert float(row["um_per_px"]) == pytest.approx(um)
    assert float(row["disc_r"]) == pytest.approx(scene.DISC_RADIUS_UM / um, abs=1e-4)
    assert float(row["disc_diameter_um"]) == pytest.approx(scene.DISC_DIAMETER_UM)
    assert float(row["artery_width_um"]) == pytest.approx(scene.ARTERY_UM)
    assert float(row["vein_width_um"]) == pytest.approx(scene.VEIN_UM)
    # Pixel i's centre is at i, so the frame's centre is half a pixel short of side / 2.
    assert float(row["fov_cx"]) == pytest.approx(SIDE / 2 - 0.5)


def test_the_ground_truth_carries_every_value_the_shape_settles(tmp_path) -> None:
    """Under canonical names, so a measurement can be compared without a translation step."""
    a_store(tmp_path, rotations=(0.0,))
    drawn = library.build("straight", side=SIDE)

    read = store.truth(tmp_path / "av")["straight-512-000"]

    assert set(read) == set(drawn.theory)
    for name, value in drawn.theory.items():
        if isinstance(value, str):
            assert read[name] == value
        else:
            assert read[name] == pytest.approx(value, rel=1e-9, abs=1e-12), name


def test_a_category_is_kept_as_the_word_it_is(tmp_path) -> None:
    a_store(tmp_path, families=("spokes-disc-centred",), rotations=(0.0,))
    assert (
        store.truth(tmp_path / "av")["spokes-disc-centred-512-000"]["landmarks/centring"] == "disc"
    )


def test_how_each_value_is_known_is_written_beside_it(tmp_path) -> None:
    a_store(tmp_path, families=("koch",), rotations=(0.0,))
    kinds = store.kinds(tmp_path / "av")["koch-512-000"]
    assert kinds["density/box-counting/artery"] == "asymptotic"
    assert kinds["density/sparsity/artery/mean"] == "numerical"
    assert kinds["tortuosity/hart-tau1/artery/mean"] == "exact"


def test_a_value_the_geometry_leaves_undefined_is_not_a_blank(tmp_path) -> None:
    """Three different things: a value, no value by definition, and nothing settled at all."""
    a_store(tmp_path, families=("straight", "koch"), rotations=(0.0,))
    stored = tmp_path / "av"

    undefined = store.undefined(stored)
    assert "topology/branching-angle/artery/mean" in undefined["straight-512-000"]
    assert "topology/branching-angle/artery/mean" not in store.truth(stored)["straight-512-000"]
    # A Koch curve's corners make its squared curvature infinite: not settled, so neither.
    assert "tortuosity/hart-tau3/artery/mean" not in undefined["koch-512-000"]
    assert "tortuosity/hart-tau3/artery/mean" not in store.truth(stored)["koch-512-000"]
    assert "tortuosity/hart-tau3/artery/mean" in store.truth(stored)["straight-512-000"]


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
            "--rotations",
            "0,45",
        ]
    )

    rows = store.read(tmp_path / "av")
    assert [row["key"] for row in rows] == [
        "straight-512-000",
        "straight-512-045",
        "disjoint-512-000",
        "disjoint-512-045",
    ]
    assert float(rows[0]["um_per_px"]) == pytest.approx(render.um_per_px(SIDE))


def test_a_mask_read_back_survives_being_walked(tmp_path) -> None:
    """Reading it correctly is not enough: it has to be usable by what measures it.

    A one-bit PNG opens as a mode `1` image, and handing that straight to NumPy gives an array that
    compares equal to the mask written and yet whose memory is not what it claims — anything walking
    it in C reads past the buffer and the process dies with no exception to catch. Every measurement
    downstream skeletonises these masks, so that is what this asserts.
    """
    from skimage.morphology import skeletonize

    a_store(tmp_path, rotations=(0.0,))
    drawn = library.build("straight", side=SIDE)

    read = store.load(tmp_path / "av", "straight-512-000")

    assert int(skeletonize(read.artery).sum()) == int(skeletonize(drawn.artery).sum())
    assert int(skeletonize(read.vein).sum()) > 0


def test_the_committed_store_and_the_library_settle_the_same_quantities() -> None:
    """The store is drawn from the library, and nothing keeps them in step but this.

    They can drift apart for ordinary reasons — a shape gains a value and the store is not redrawn —
    and nothing would say so: the configuration page reports what the *library* settles, while the
    analysis reads what the *store* settles. This is what notices.
    """
    where = Path(library.__file__).resolve().parents[3] / store.STORE
    manifest = store.read(where)
    assert manifest, f"no synthetic store at {where} — draw one with `python -m benchmarks.shapes`"
    families = list(dict.fromkeys(row["family"] for row in manifest))
    assert families == list(library.SHAPES), "redraw the store: its shapes are not the library's"

    stored = store.kinds(where)
    for row in manifest:
        expected = {key: t.kind for key, t in library.truths(row["family"]).items()}
        assert stored[row["key"]] == expected, (
            f"{row['key']}: the store and the library disagree — redraw it with "
            f"`python -m benchmarks.shapes`"
        )


def test_a_digest_covers_one_family_and_not_its_neighbours(tmp_path) -> None:
    """Scoped per shape, so redrawing one does not throw away the measurements of the others."""
    store.write(tmp_path, families=("koch", "arc"), side=256, rotations=(0.0,))
    again = tmp_path / "again"
    store.write(again, families=("koch",), side=256, rotations=(0.0,))

    assert store.digest("koch", tmp_path) != store.digest("arc", tmp_path)
    assert store.digest("koch", again) == store.digest("koch", tmp_path), "the same picture twice"
    assert store.digest("nothing-drawn", tmp_path) == "unbuilt"


def test_a_redrawn_shape_gets_a_different_digest(tmp_path) -> None:
    """Redrawing a shape at another grid must not leave its scores standing."""
    store.write(tmp_path / "a", families=("arc",), side=256, rotations=(0.0,))
    store.write(tmp_path / "b", families=("arc",), side=320, rotations=(0.0,))
    assert store.digest("arc", tmp_path / "a") != store.digest("arc", tmp_path / "b")
