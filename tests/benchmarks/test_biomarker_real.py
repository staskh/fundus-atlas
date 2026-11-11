# ABOUTME: Tests for the real-segmentation biomarker benchmark: a small store, a model's kept masks,
# ABOUTME: and a real adapter that measures area — never a downloaded store, never a real program.

import csv
import json
from pathlib import Path

import numpy as np
import pytest

from benchmarks import biomarker_real, runs
from benchmarks.loaders.biomarker_real import NO_CLASSES, NO_DISC, BiomarkerLoader

from conftest import row, write_masks, write_store

SIDE = 600


class Area:
    """A real biomarker adapter, small: the artery and vein areas, and their ratio.

    It satisfies the interface the catalogued adapters do, so what these tests exercise is the run
    rather than a rehearsal of one. Areas are in pixels², as an adapter reports them.
    """

    slug = "area"
    needs = ("artery", "vein", "disc")

    def declare(self) -> dict[str, object]:
        return {
            "slug": self.slug,
            "needs": list(self.needs),
            "keys": list(self.keys()),
            "units": {"artery_area": "px²", "vein_area": "px²"},
            "names": {
                "artery_area": "density/area/artery",
                "vein_area": "density/area/vein",
                "ratio": None,
            },
            "upstream": {"commit": "0" * 40},
        }

    def identity(self) -> str:
        return "area-1"

    def keys(self) -> tuple[str, ...]:
        return ("artery_area", "vein_area", "ratio")

    def measure(self, artery, vein, fov, disc, um_per_px) -> dict[str, float | None]:
        a, v = float(artery.sum()), float(vein.sum())
        return {"artery_area": a, "vein_area": v, "ratio": a / v if v else None}


def _vessels(width_a: int, width_v: int) -> dict[str, np.ndarray]:
    artery = np.zeros((SIDE, SIDE), dtype=bool)
    vein = np.zeros((SIDE, SIDE), dtype=bool)
    artery[100 : 100 + width_a, 50:550] = True
    vein[300 : 300 + width_v, 50:550] = True
    return {"artery": artery, "vein": vein, "fov": np.ones((SIDE, SIDE), dtype=bool)}


def _world(tmp_path: Path, keys: list[str], with_disc: list[str] | None = None):
    """A store of `keys`, the expert's maps, one model's kept masks and the disc estimates."""
    root = tmp_path / "stores"
    rows = [
        row(k, crop_side=str(SIDE), maps="artery;vein;vessels;fov", um_per_px="10.0") for k in keys
    ]
    store = write_store(root, "toy", rows)
    kept = tmp_path / "runs" / "av" / "model-a" / "toy"
    kept.mkdir(parents=True)
    (kept / "fingerprint.txt").write_text("drawn-1\n")
    for index, key in enumerate(keys):
        write_masks(store, key, _vessels(10 + index, 14 + 2 * index))
        model = _vessels(11 + index, 14 + 2 * index)
        from PIL import Image

        for name in ("artery", "vein"):
            Image.fromarray(model[name]).save(kept / f"{key}-{name}.png")
    discs = tmp_path / "discs"
    discs.mkdir()
    with open(discs / "toy.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["key", "outcome", "disc_cx", "disc_cy", "disc_r"])
        for key in with_disc if with_disc is not None else keys:
            writer.writerow([key, "graded", 300, 300, 40])
    (discs / "toy.json").write_text(json.dumps({"fingerprint": "disc-1"}))
    sources = {"toy": ({"model-a": {"directory": kept, "drawing": "drawn-1"}}, {})}
    return root, discs, sources


def _run(tmp_path: Path, root: Path, discs: Path, sources, **kwargs):
    return biomarker_real.run(
        [Area()],
        ["toy"],
        results=tmp_path / "results",
        root=root,
        workers=1,
        kept=tmp_path / "runs",
        sources=sources,
        discs=discs,
        **kwargs,
    )


def _evidence(tmp_path: Path) -> list[dict[str, str]]:
    return runs.rows(tmp_path / "results", biomarker_real.NAME, "area", "toy")


def test_every_photograph_is_measured_on_the_expert_map_and_the_models(tmp_path: Path) -> None:
    root, discs, sources = _world(tmp_path, ["a", "b", "c", "d"])

    _run(tmp_path, root, discs, sources)

    evidence = _evidence(tmp_path)
    assert sorted((r["key"], r["source"]) for r in evidence) == sorted(
        (k, s) for k in "abcd" for s in ("expert", "model-a")
    )
    first = next(r for r in evidence if r["key"] == "a" and r["source"] == "expert")
    assert float(first["said_artery_area"]) == 10 * 500
    assert first["disc_r"] == "40.00"


def test_agreement_is_written_in_microns_for_a_named_length_and_as_returned_otherwise(
    tmp_path: Path,
) -> None:
    root, discs, sources = _world(tmp_path, ["a", "b", "c", "d"])

    _run(tmp_path, root, discs, sources)

    path = tmp_path / "results" / biomarker_real.NAME / "area" / "agreement" / "toy.csv"
    table = {r["column"]: r for r in csv.DictReader(path.open())}
    artery = table["artery_area"]
    assert artery["unit"] == "µm²"
    # The model's artery is one row of 500 pixels wider on every photograph: 500 px² × 100 µm²/px².
    assert float(artery["bias"]) == pytest.approx(50000)
    assert float(artery["icc_consistency"]) == pytest.approx(1.0)
    assert table["ratio"]["unit"] == "as returned"
    assert table["vein_area"]["snr"] == "inf"  # the model drew every vein exactly
    assert (path.parent / "pooled.csv").exists()


def test_a_photograph_without_a_disc_is_excluded_and_counted(tmp_path: Path) -> None:
    root, discs, sources = _world(tmp_path, ["a", "b", "c"], with_disc=["a", "b"])

    scored = _run(tmp_path, root, discs, sources)

    assert {r["key"] for r in _evidence(tmp_path)} == {"a", "b"}
    assert scored[0]["counts"]["excluded"] == {NO_DISC: 1}


def test_a_photograph_without_both_classes_is_excluded(tmp_path: Path) -> None:
    root = tmp_path / "stores"
    write_store(root, "toy", [row("a", maps="vessels;fov"), row("b", maps="artery;vein;fov")])
    discs = tmp_path / "discs"
    discs.mkdir()
    (discs / "toy.csv").write_text("key,outcome,disc_cx,disc_cy,disc_r\na,graded,1,1,1\nb,graded,1,1,1\n")

    loader = BiomarkerLoader("toy", root=root, discs_from=discs)

    assert [r["key"] for r in loader.rows] == ["b"]
    assert loader.excluded == {NO_CLASSES: 1}


def test_a_partial_run_is_finished_rather_than_repeated(tmp_path: Path) -> None:
    root, discs, sources = _world(tmp_path, ["a", "b", "c", "d"])
    _run(tmp_path, root, discs, sources, max_samples=2)
    assert not json.loads(
        (tmp_path / "results" / biomarker_real.NAME / "area" / "toy.json").read_text()
    )["summary"]["complete"]
    before = {(r["key"], r["source"]): r["seconds"] for r in _evidence(tmp_path)}

    scored = _run(tmp_path, root, discs, sources)

    after = {(r["key"], r["source"]): r["seconds"] for r in _evidence(tmp_path)}
    assert len(after) == 8
    assert all(after[k] == v for k, v in before.items())  # kept, not measured again
    assert scored[0]["counts"]["complete"]


def test_a_redrawn_model_is_measured_again_and_the_expert_is_not(tmp_path: Path) -> None:
    root, discs, sources = _world(tmp_path, ["a", "b", "c"])
    _run(tmp_path, root, discs, sources)
    usable, refused = sources["toy"]
    redrawn = {"toy": ({"model-a": usable["model-a"] | {"drawing": "drawn-2"}}, refused)}

    _run(tmp_path, root, discs, redrawn)

    evidence = _evidence(tmp_path)
    assert {r["drawing"] for r in evidence if r["source"] == "model-a"} == {"drawn-2"}
    assert len(evidence) == 6


def test_a_model_with_no_kept_masks_is_refused_with_the_command_that_fixes_it(
    tmp_path: Path,
) -> None:
    usable, refused = biomarker_real.masks("toy", kept=tmp_path)

    assert usable == {}
    assert set(refused) == set(biomarker_real.SEGMENTERS)
    assert all("--benchmark av" in why for why in refused.values())


def test_every_column_of_the_evidence_and_the_agreement_is_explained(tmp_path: Path) -> None:
    root, discs, sources = _world(tmp_path, ["a", "b", "c"])
    _run(tmp_path, root, discs, sources)

    evidence = _evidence(tmp_path)
    explained = set(biomarker_real.COLUMNS)
    for column in evidence[0]:
        assert column in explained or column.startswith("said_"), f"`{column}` is not explained"
    path = tmp_path / "results" / biomarker_real.NAME / "area" / "agreement" / "toy.csv"
    assert list(next(csv.DictReader(path.open()))) == list(biomarker_real.AGREEMENT_COLUMNS)


def test_the_committed_configuration_page_is_current() -> None:
    """A stale page fails the suite rather than sitting wrong in a public reference."""
    from benchmarks import docs

    page = Path(docs.DIRECTORY) / f"{biomarker_real.NAME}-docs.md"
    current = page.read_text()

    assert docs.render(current, biomarker_real.config()) == current, (
        f"{page} is stale — refresh it with "
        f"`python -m benchmarks --benchmark {biomarker_real.NAME} --docs`"
    )
