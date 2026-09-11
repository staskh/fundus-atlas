# ABOUTME: Tests for finding the field of view in a photograph and for the square crop around it.
# ABOUTME: Synthetic circles only — never a downloaded image.

import numpy as np
import pytest

from datasets.utils import crop, fov


def disc(height, width, cx, cy, r, value=200):
    yy, xx = np.mgrid[0:height, 0:width]
    image = np.zeros((height, width, 3), dtype=np.uint8)
    image[(xx - cx) ** 2 + (yy - cy) ** 2 <= r**2] = value
    return image


def test_detects_a_circle_that_fits_inside_the_frame():
    found = fov.detect(disc(400, 500, cx=250, cy=200, r=150))
    assert found.cx == pytest.approx(250, abs=2)
    assert found.cy == pytest.approx(200, abs=2)
    assert found.r == pytest.approx(150, abs=2)
    assert found.source == "detected"


def test_recovers_the_radius_of_a_circle_cut_off_left_and_right():
    # The common fundus case: the camera's circle is wider than the sensor, so the disc runs off
    # both sides and its true width is not visible anywhere in the image.
    found = fov.detect(disc(400, 260, cx=130, cy=200, r=170))
    assert found.r == pytest.approx(170, abs=4)
    assert found.cx == pytest.approx(130, abs=3)


def test_ignores_a_bright_speck_outside_the_field():
    image = disc(400, 500, cx=250, cy=200, r=150)
    image[10:16, 480:486] = 255
    found = fov.detect(image)
    assert found.r == pytest.approx(150, abs=3)


def test_a_frame_with_no_dark_border_is_the_whole_frame():
    image = np.full((300, 400, 3), 180, dtype=np.uint8)
    found = fov.detect(image)
    assert found.source == "assumed_full_frame"
    assert (found.cx, found.cy) == (200.0, 150.0)
    assert found.r == pytest.approx(200, abs=1)


def test_the_mask_is_the_pixels_that_are_there_not_a_redrawn_circle():
    image = disc(400, 500, cx=250, cy=200, r=150)
    image[195:205, 245:255] = 0  # a dead patch inside the field
    mask = fov.mask_of(image)
    assert mask[200, 250] == 0
    assert mask[200, 150] == 255


def test_the_square_is_the_circle_bounding_box():
    square = crop.square_around(fov.Circle(cx=250, cy=200, r=150, source="detected"))
    assert (square.x0, square.y0, square.side) == (100, 50, 300)


def test_a_square_may_start_outside_the_image():
    square = crop.square_around(fov.Circle(cx=130, cy=200, r=170, source="detected"))
    assert square.x0 == -40
    assert square.side == 340


def test_source_is_pasted_into_the_square_rather_than_sliced_from_it():
    image = disc(400, 260, cx=130, cy=200, r=170)
    square = crop.square_around(fov.Circle(cx=130, cy=200, r=170, source="detected"))
    out = crop.apply(image, square)
    assert out.shape == (340, 340, 3)
    assert out[:, 0].max() == 0  # the invented left margin
    assert out[170, 170].max() > 0  # the centre of the field


def test_pad_fraction_counts_the_canvas_that_has_no_photograph_behind_it():
    square = crop.square_around(fov.Circle(cx=130, cy=200, r=170, source="detected"))
    # 40 invented columns on the left and 40 on the right, out of a 340-wide square.
    assert crop.pad_fraction(square, height=400, width=260) == pytest.approx(80 / 340)


def test_nothing_is_padded_when_the_square_fits():
    square = crop.square_around(fov.Circle(cx=250, cy=200, r=150, source="detected"))
    assert crop.pad_fraction(square, height=400, width=500) == 0.0


def test_a_very_dark_photograph_keeps_its_whole_field():
    # Exposure varies by more than an order of magnitude across a screening dataset. A field that
    # is dim everywhere is still a field, and must not be cropped to the part that was well lit.
    bright = disc(400, 500, cx=250, cy=200, r=150, value=200)
    dim = disc(400, 500, cx=250, cy=200, r=150, value=14)
    assert fov.detect(dim).r == pytest.approx(fov.detect(bright).r, abs=2)


def test_the_line_between_surround_and_retina_follows_the_exposure():
    assert fov.dark_level(disc(400, 500, 250, 200, 150, value=200)) == pytest.approx(10, abs=1)
    assert fov.dark_level(disc(400, 500, 250, 200, 150, value=20)) == fov.MIN_DARK
