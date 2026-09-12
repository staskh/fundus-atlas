# ABOUTME: Tests for tracing disc and cup outlines from masks, and for the contour CSV.
# ABOUTME: Synthetic shapes only; the fidelity check is what guards a real trace.

import numpy as np
import pytest
from PIL import Image

from datasets.utils import contours


def circle_mask(height, width, cx, cy, r):
    yy, xx = np.mgrid[0:height, 0:width]
    return np.where((xx - cx) ** 2 + (yy - cy) ** 2 <= r**2, 255, 0).astype(np.uint8)


def test_a_traced_outline_encloses_what_the_mask_enclosed():
    # The ceiling is about 0.988, not 1.0: the outline runs along the 0.5 level, half a pixel
    # inside the mask's filled edge, which costs (r - 0.5)**2 / r**2 of the area on a disc this
    # size. Anything much below this is a trace that has gone wrong.
    mask = circle_mask(400, 400, 200, 200, 80)
    polygon = contours.trace(mask)
    assert contours.fidelity(mask, polygon) > 0.98


def test_an_outline_is_a_few_dozen_nodes_not_a_pixel_chain():
    polygon = contours.trace(circle_mask(400, 400, 200, 200, 80))
    assert 10 < len(polygon) < 120


def test_nodes_are_x_then_y():
    polygon = contours.trace(circle_mask(400, 600, cx=450, cy=100, r=50))
    assert polygon[:, 0].mean() == pytest.approx(450, abs=3)
    assert polygon[:, 1].mean() == pytest.approx(100, abs=3)


def test_only_the_largest_shape_is_traced():
    mask = circle_mask(400, 400, 200, 200, 80)
    mask |= circle_mask(400, 400, 30, 30, 10)
    polygon = contours.trace(mask)
    assert polygon[:, 0].min() > 100


def test_a_mask_nobody_drew_on_traces_to_nothing():
    assert len(contours.trace(np.zeros((100, 100), dtype=np.uint8))) == 0


def test_native_keeps_floats_so_every_size_comes_from_one_trace(tmp_path):
    drawn = {("disc", "expert1"): np.array([[10.5, 20.25], [30.5, 40.75]])}
    contours.write(tmp_path / "k.csv", drawn)
    rows = (tmp_path / "k.csv").read_text().splitlines()
    assert rows[0] == "structure,reader,node,x,y"
    assert rows[1] == "disc,expert1,0,10.5,20.25"


def test_a_size_is_the_native_trace_scaled_and_rounded(tmp_path):
    drawn = {("disc", "expert1"): np.array([[100.0, 200.0], [300.0, 400.0]])}
    contours.write(tmp_path / "k.csv", drawn, scale=0.5)
    assert (tmp_path / "k.csv").read_text().splitlines()[1:] == [
        "disc,expert1,0,50,100",
        "disc,expert1,1,150,200",
    ]


def test_a_node_outside_the_frame_is_kept_rather_than_clipped(tmp_path):
    drawn = {("cup", "consensus"): np.array([[-12.0, 5.0]])}
    contours.write(tmp_path / "k.csv", drawn, scale=0.5)
    assert (tmp_path / "k.csv").read_text().splitlines()[1] == "cup,consensus,0,-6,2"


def test_every_structure_and_reader_shares_one_file_per_image(tmp_path):
    drawn = {
        ("disc", "expert1"): np.array([[1.0, 1.0]]),
        ("cup", "expert1"): np.array([[2.0, 2.0]]),
        ("disc", "expert2"): np.array([[3.0, 3.0]]),
    }
    contours.write(tmp_path / "k.csv", drawn)
    assert len((tmp_path / "k.csv").read_text().splitlines()) == 4


def test_a_shared_mask_names_the_values_each_structure_is_made_of(tmp_path):
    # RIGA+ packs both structures into one file: the cup is 128 and the disc is the cup plus the
    # 255 ring around it. Tracing the file as a whole would give one shape where there are two.
    from datasets.utils import archives, contours as c

    path = tmp_path / "m.tif"
    mask = circle_mask(300, 300, 150, 150, 80) // 255 * 255
    mask[circle_mask(300, 300, 150, 150, 40) > 0] = 128
    Image.fromarray(mask).save(path)

    disc = c.Layer(archives.File(path), values=(128, 255))
    cup = c.Layer(archives.File(path), values=(128,))

    def width(nodes):
        return nodes[:, 0].max() - nodes[:, 0].min()

    assert width(c.trace(disc.mask_from(mask))) == pytest.approx(160, abs=3)
    assert width(c.trace(cup.mask_from(mask))) == pytest.approx(80, abs=3)
