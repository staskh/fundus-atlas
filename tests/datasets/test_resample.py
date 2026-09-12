# ABOUTME: Tests for resizing a native frame to a built size, and for the resolution that follows.
# ABOUTME: Photographs are interpolated; masks and labels never are.

import numpy as np
import pytest

from datasets.utils import resample, resolution


def test_a_photograph_is_resized_to_the_requested_square():
    out = resample.photograph(np.zeros((300, 300, 3), dtype=np.uint8), 128)
    assert out.shape == (128, 128, 3)


def test_a_mask_keeps_only_the_values_it_arrived_with():
    mask = np.zeros((300, 300), dtype=np.uint8)
    mask[100:200, 100:200] = 255
    out = resample.mask(mask, 128)
    assert out.shape == (128, 128)
    assert set(np.unique(out)) <= {0, 255}


def test_a_label_map_does_not_invent_a_class_between_two_others():
    labels = np.zeros((300, 300), dtype=np.uint8)
    labels[:, :150] = 1
    labels[:, 150:] = 3
    out = resample.mask(labels, 64)
    assert set(np.unique(out)) == {1, 3}


def test_microns_per_pixel_grows_as_the_grid_gets_coarser():
    assert resolution.um_per_px_at(5.0, crop_side=2048, size=1024) == pytest.approx(10.0)
    assert resolution.um_per_px_at(5.0, crop_side=2048, size=2048) == pytest.approx(5.0)


def test_an_unknown_resolution_stays_unknown_at_every_size():
    assert resolution.um_per_px_at(None, crop_side=2048, size=512) is None


def test_a_declared_resolution_carries_its_derivation():
    declared = resolution.Declared(um_per_px=None, source="unknown", note="no field angle stated")
    assert declared.um_per_px is None
    assert declared.source == "unknown"


def test_a_declared_source_must_be_one_the_skill_recognises():
    with pytest.raises(ValueError, match="guessed"):
        resolution.Declared(um_per_px=5.0, source="guessed", note="")


def test_a_resolution_without_a_source_is_refused():
    with pytest.raises(ValueError, match="unknown"):
        resolution.Declared(um_per_px=5.0, source="unknown", note="")


def test_from_a_field_angle_a_degree_is_three_hundred_microns():
    assert resolution.from_field_angle(degrees=45, fov_diameter_px=1500) == pytest.approx(9.0)


def test_from_an_anchored_disc_the_disc_is_eighteen_hundred_microns():
    assert resolution.from_disc(disc_diameter_px=180) == pytest.approx(10.0)
