# ABOUTME: Tests for finding the field of view in a photograph and for the square crop around it.
# ABOUTME: Synthetic circles only — never a downloaded image.

import numpy as np
import pytest

from datasets.utils import crop, fov


def disc(height, width, cx, cy, r, value=200, background=0):
    """A filled circle on a uniform surround, which is what a fundus photograph is."""
    yy, xx = np.mgrid[0:height, 0:width]
    image = np.full((height, width, 3), background, dtype=np.uint8)
    image[(xx - cx) ** 2 + (yy - cy) ** 2 <= r**2] = value
    return image


def test_detects_a_circle_that_fits_inside_the_frame():
    found = fov.detect(disc(400, 500, cx=250, cy=200, r=150))
    assert found.cx == pytest.approx(250, abs=2)
    assert found.cy == pytest.approx(200, abs=2)
    assert found.r == pytest.approx(150, abs=2)
    assert found.source == "detected"


def test_a_white_surround_is_a_surround_too():
    # Some cameras write the area outside the field white rather than black. Nothing about it is
    # retina, and a brightness test would call the entire frame field of view.
    found = fov.detect(disc(400, 500, cx=250, cy=200, r=150, value=90, background=255))
    assert found.r == pytest.approx(150, abs=2)
    assert found.source == "detected"


def test_a_grey_surround_is_a_surround_too():
    found = fov.detect(disc(400, 500, cx=250, cy=200, r=150, value=200, background=128))
    assert found.r == pytest.approx(150, abs=2)


def test_a_white_surround_is_outside_the_mask():
    mask = fov.mask_of(disc(400, 500, cx=250, cy=200, r=150, value=90, background=255))
    assert mask[200, 250] == 255
    assert mask[5, 5] == 0


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


def test_a_frame_with_no_surround_at_all_is_the_whole_frame():
    image = np.full((300, 400, 3), 180, dtype=np.uint8)
    found = fov.detect(image)
    assert found.source == "assumed_full_frame"
    assert (found.cx, found.cy) == (200.0, 150.0)
    assert found.r == pytest.approx(200, abs=1)


def test_a_dead_patch_inside_the_field_is_still_inside_the_field():
    # The mask says where the camera's field was, not where the photograph came out well. A patch
    # of no signal in the middle of the retina is still within the field of view; only the
    # surround — uniform and reaching the frame's edge — is outside it.
    image = disc(400, 500, cx=250, cy=200, r=150)
    image[195:205, 245:255] = 0
    mask = fov.mask_of(image)
    assert mask[200, 250] == 255
    assert mask[200, 150] == 255
    assert mask[5, 5] == 0


def test_a_very_dark_photograph_keeps_its_whole_field():
    # Exposure varies by more than an order of magnitude across a screening dataset. A field that
    # is dim everywhere is still a field, and must not be cropped to the part that was well lit.
    bright = disc(400, 500, cx=250, cy=200, r=150, value=200)
    dim = disc(400, 500, cx=250, cy=200, r=150, value=14)
    assert fov.detect(dim).r == pytest.approx(fov.detect(bright).r, abs=2)


def test_an_unlit_sector_does_not_shrink_the_circle():
    # A photograph can be so underexposed on one side that the rim there is indistinguishable from
    # the surround. The mask then has a bite taken out of it, and edge points along that bite lie
    # well inside the true field: fitting to them would crop away retina that is present.
    image = disc(400, 500, cx=250, cy=200, r=150)
    yy, xx = np.mgrid[0:400, 0:500]
    image[(xx > 330) & (yy > 120) & (yy < 280)] = 0
    assert fov.detect(image).r == pytest.approx(150, abs=3)


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


def test_a_burnt_in_label_out_in_the_surround_is_not_part_of_the_field():
    # Several cameras stamp an index or a timestamp in the corner. It is not surround-coloured, so
    # a colour test keeps it; it is also not the field, and a consumer masking with it would carry
    # a patch of text into an analysis.
    image = disc(400, 500, cx=250, cy=200, r=150, value=90, background=255)
    image[8:14, 8:30] = 40
    mask = fov.mask_of(image)
    assert mask[10, 20] == 0
    assert mask[200, 250] == 255


def test_a_circle_that_cannot_be_this_photograph_s_field_is_refused():
    # A photograph cropped so that only a straight-looking sliver of the field edge is in frame.
    # Any radius fits a nearly straight arc, and RIGA+ produced circles 36 and 13,646 pixels across
    # on 800-pixel images that way. A circle must at least be the size of the region it came from.
    image = np.full((800, 800, 3), 150, dtype=np.uint8)
    image[:, :24] = 0  # enough surround to look findable, too little to shape a circle
    found = fov.detect(image)
    assert found.source == "assumed_full_frame"
    assert found.r == pytest.approx(400, abs=1)


def test_a_photograph_with_no_field_to_find_can_be_taken_whole():
    # RIGA+ publishes crops of photographs rather than photographs. There is no field of view in
    # them to find, and a fetcher says so rather than having one invented.
    image = np.full((300, 400, 3), 150, dtype=np.uint8)
    found = fov.whole(image)
    assert found.source == "assumed_full_frame"
    assert (found.cx, found.cy) == (200.0, 150.0)


def test_a_frame_that_is_all_retina_is_all_field():
    # Every pixel resembles the border, because the border is retina too. Reading that as surround
    # would hand back a mask saying the photograph contains no retina at all.
    assert fov.mask_of(np.full((300, 400, 3), 150, dtype=np.uint8)).min() == 255


def test_a_real_field_is_still_detected_at_the_same_size():
    found = fov.detect(disc(400, 500, cx=250, cy=200, r=150))
    assert found.source == "detected"
    assert found.r == pytest.approx(150, abs=2)


def test_a_field_much_smaller_than_its_frame_is_still_a_field():
    # A photograph with wide margins is not the same thing as a failed fit.
    found = fov.detect(disc(1000, 1000, cx=500, cy=500, r=260))
    assert found.source == "detected"
    assert found.r == pytest.approx(260, abs=3)
