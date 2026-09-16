# ABOUTME: Tests for the disc and cup measurements, against shapes whose answer is arithmetic
# ABOUTME: rather than another program's output.

import numpy as np
import pytest

from benchmarks.metrics import disc


def circle(side: int, cx: float, cy: float, r: float) -> np.ndarray:
    yy, xx = np.mgrid[0:side, 0:side]
    return (xx - cx) ** 2 + (yy - cy) ** 2 <= r**2


def test_two_identical_shapes_overlap_completely() -> None:
    shape = circle(200, 100, 100, 50)

    assert disc.dice(shape, shape) == pytest.approx(1.0)


def test_shapes_that_do_not_touch_overlap_not_at_all() -> None:
    assert disc.dice(circle(200, 50, 50, 20), circle(200, 150, 150, 20)) == pytest.approx(0.0)


def test_overlap_is_twice_the_shared_area_over_the_two_areas() -> None:
    # A circle and a copy of itself shifted so that they share exactly half of each.
    one, other = circle(400, 200, 200, 100), circle(400, 200, 200, 100)
    shared = (one & other).sum()
    assert disc.dice(one, other) == pytest.approx(2 * shared / (one.sum() + other.sum()))


def test_nothing_predicted_against_something_is_no_overlap_rather_than_an_error() -> None:
    assert disc.dice(circle(100, 50, 50, 20), np.zeros((100, 100), bool)) == pytest.approx(0.0)


def test_two_empty_shapes_have_no_overlap_to_measure() -> None:
    assert disc.dice(np.zeros((10, 10), bool), np.zeros((10, 10), bool)) is None


def test_a_centre_is_where_the_shape_is() -> None:
    found = disc.centre(circle(200, 60, 140, 30))

    assert found == pytest.approx((60, 140), abs=0.5)


def test_a_shifted_shape_is_offset_by_the_shift() -> None:
    offset = disc.centre_offset(circle(200, 100, 100, 30), circle(200, 110, 100, 30))

    assert offset == pytest.approx(10, abs=0.5)


def test_the_extent_of_a_circle_is_its_diameter_in_both_directions() -> None:
    width, height = disc.extent(circle(300, 150, 150, 40))

    assert width == pytest.approx(80, abs=2)
    assert height == pytest.approx(80, abs=2)


def test_the_equivalent_radius_of_a_circle_is_its_own_radius() -> None:
    assert disc.equivalent_radius(circle(400, 200, 200, 75)) == pytest.approx(75, abs=1)


def test_a_cup_of_half_the_height_is_a_vertical_ratio_of_one_half() -> None:
    cup, optic_disc = circle(400, 200, 200, 40), circle(400, 200, 200, 80)

    assert disc.vertical_ratio(cup, optic_disc) == pytest.approx(0.5, abs=0.02)


def test_a_cup_of_half_the_radius_covers_a_quarter_of_the_area() -> None:
    cup, optic_disc = circle(400, 200, 200, 40), circle(400, 200, 200, 80)

    assert disc.area_ratio(cup, optic_disc) == pytest.approx(0.25, abs=0.02)


def test_a_ratio_needs_a_disc_to_be_a_ratio_of() -> None:
    assert disc.vertical_ratio(circle(100, 50, 50, 10), np.zeros((100, 100), bool)) is None


def test_a_cup_outside_its_disc_is_reported_rather_than_repaired() -> None:
    cup, optic_disc = circle(300, 60, 150, 25), circle(300, 200, 150, 50)

    assert disc.outside_its_disc(cup, optic_disc) == pytest.approx(1.0)
    assert disc.outside_its_disc(circle(300, 200, 150, 25), optic_disc) == pytest.approx(0.0)


def test_a_polygon_becomes_the_mask_it_encloses() -> None:
    square = np.array([[10.0, 10.0], [10.0, 40.0], [40.0, 40.0], [40.0, 10.0]])

    mask = disc.mask_of(square, (60, 60))

    assert mask.sum() == pytest.approx(31 * 31, rel=0.05)
    assert mask[25, 25] and not mask[5, 5]


def test_every_measurement_of_one_pair_comes_back_together() -> None:
    truth = {"disc": circle(300, 150, 150, 60), "cup": circle(300, 150, 150, 30)}
    said = {"disc": circle(300, 155, 150, 60), "cup": circle(300, 155, 150, 36)}

    found = disc.measure(said, truth)

    assert found["disc_dice"] > 0.9
    assert found["disc_centre_offset"] == pytest.approx(5, abs=0.5)
    assert found["cup_vertical_ratio_error"] == pytest.approx(0.1, abs=0.02)
    assert found["truth_vertical_ratio"] == pytest.approx(0.5, abs=0.02)
