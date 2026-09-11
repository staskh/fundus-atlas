# ABOUTME: End-to-end test of a build, on a synthetic two-image dataset written to disk.
# ABOUTME: Real files, real PNGs, real manifest — the only thing not real is the retina.

import json
import shutil

import numpy as np
import pytest
from PIL import Image

from datasets.utils import build, cli, fov, manifest, quality, resolution


def a_dataset(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()
    for key, cx in (("a", 150), ("b", 160)):
        yy, xx = np.mgrid[0:300, 0:300]
        image = np.zeros((300, 300, 3), dtype=np.uint8)
        image[(xx - cx) ** 2 + (yy - 150) ** 2 <= 100**2] = 180
        Image.fromarray(image).save(raw / f"{key}.png")
        vessels = np.zeros((300, 300), dtype=np.uint8)
        vessels[145:155, 100:200] = 255
        Image.fromarray(vessels).save(raw / f"{key}_vessels.png")
    return raw


def discover(raw):
    return [
        build.SourceRecord(
            key=key,
            image=raw / f"{key}.png",
            maps={"vessels": raw / f"{key}_vessels.png"},
            patient=f"p{key}",
            eye="od",
            extras={"artifact": "0"},
        )
        for key in ("a", "b")
    ]


def build_it(tmp_path, *argv):
    args = cli.parse("synthetic", ["--data-root", str(tmp_path / "store"), "--sizes", "64", *argv])
    build.run(
        slug="synthetic",
        sources=[],
        discover=discover,
        resolution_of=resolution.Declared(5.0, "published", "stated in the paper"),
        args=args,
        fov_strategy=fov.DETECT,
        quality_rule=quality.FromComponents({"artifact": "0"}),
        extra_columns=[manifest.Column("artifact", "0 is best")],
        skipped=["an ultra-wide-field split"],
    )
    return tmp_path / "store" / "synthetic"


def test_every_layer_is_written_at_native_and_at_each_size(tmp_path):
    store = build_it(tmp_path, "--raw", str(a_dataset(tmp_path)))
    for size in ("native", "64"):
        for layer in ("images", "vessels", "fov"):
            assert (store / size / layer / "a.png").exists()


def test_a_size_is_square_and_native_is_the_crop(tmp_path):
    store = build_it(tmp_path, "--raw", str(a_dataset(tmp_path)))
    assert Image.open(store / "64" / "images" / "a.png").size == (64, 64)
    # Native is the field's bounding box, to within the pixel the circle fit can resolve.
    assert Image.open(store / "native" / "images" / "a.png").size[0] == pytest.approx(200, abs=1)


def test_the_manifest_describes_the_crop_it_made(tmp_path):
    store = build_it(tmp_path, "--raw", str(a_dataset(tmp_path)))
    row = next(iter(manifest.read(store)))
    assert row["key"] == "a"
    assert int(row["crop_side"]) == pytest.approx(200, abs=1)
    assert row["maps"] == "vessels;fov"
    assert row["patient"] == "pa"
    assert row["um_per_px"] == "5"


def test_the_quality_rule_runs_over_the_dataset_s_own_columns(tmp_path):
    store = build_it(tmp_path, "--raw", str(a_dataset(tmp_path)))
    row = next(iter(manifest.read(store)))
    assert (row["quality"], row["quality_source"]) == ("good", "derived")
    assert row["artifact"] == "0"


def test_a_skipped_subcollection_is_recorded_rather_than_forgotten(tmp_path):
    store = build_it(tmp_path, "--raw", str(a_dataset(tmp_path)))
    record = json.loads((store / "build.json").read_text())
    assert record["warnings"] == ["not built: an ultra-wide-field split"]
    assert record["partial"] is False
    assert record["images"] == 2


def test_a_limited_build_says_it_is_partial(tmp_path):
    store = build_it(tmp_path, "--raw", str(a_dataset(tmp_path)), "--limit", "1")
    record = json.loads((store / "build.json").read_text())
    assert record["partial"] is True
    assert record["images"] == 1


def test_a_raw_tree_the_caller_supplied_is_never_deleted(tmp_path):
    raw = a_dataset(tmp_path)
    build_it(tmp_path, "--raw", str(raw))
    assert (raw / "a.png").exists()


def test_a_second_run_rebuilds_nothing(tmp_path):
    raw = a_dataset(tmp_path)
    store = build_it(tmp_path, "--raw", str(raw))
    before = (store / "native" / "images" / "a.png").stat().st_mtime_ns
    build_it(tmp_path, "--raw", str(raw))
    assert (store / "native" / "images" / "a.png").stat().st_mtime_ns == before


def test_force_rebuilds_anyway(tmp_path):
    raw = a_dataset(tmp_path)
    store = build_it(tmp_path, "--raw", str(raw))
    before = (store / "native" / "images" / "a.png").stat().st_mtime_ns
    build_it(tmp_path, "--raw", str(raw), "--force")
    assert (store / "native" / "images" / "a.png").stat().st_mtime_ns != before


def test_a_new_size_is_built_from_native_with_no_archive_in_reach(tmp_path):
    raw = a_dataset(tmp_path)
    store = build_it(tmp_path, "--raw", str(raw))
    shutil.rmtree(raw)  # the archive is gone; native must be enough
    args = cli.parse("synthetic", ["--data-root", str(tmp_path / "store"), "--sizes", "32,64"])
    build.run(
        slug="synthetic",
        sources=[],
        discover=discover,
        resolution_of=resolution.Declared(5.0, "published", "stated in the paper"),
        args=args,
    )
    assert Image.open(store / "32" / "images" / "a.png").size == (32, 32)
    assert Image.open(store / "32" / "vessels" / "a.png").size == (32, 32)
    assert json.loads((store / "build.json").read_text())["sizes"] == [32, 64]


def test_an_interrupted_build_continues_rather_than_starting_over(tmp_path):
    raw = a_dataset(tmp_path)
    store = build_it(tmp_path, "--raw", str(raw), "--limit", "1")
    assert json.loads((store / "build.json").read_text())["partial"] is True
    before = (store / "native" / "images" / "a.png").stat().st_mtime_ns

    build_it(tmp_path, "--raw", str(raw))
    record = json.loads((store / "build.json").read_text())
    assert record["images"] == 2
    assert record["partial"] is False
    assert (store / "native" / "images" / "a.png").stat().st_mtime_ns == before
