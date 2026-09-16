# ABOUTME: Tests for what a disc-and-cup benchmark is run on: the photograph, and every reader's
# ABOUTME: outline of every structure, in the frame the expert drew in.

from pathlib import Path

from benchmarks.loaders import disc
from conftest import row, write_contours, write_store


def a_store(tmp_path: Path, readers=("expert1", "expert2")) -> Path:
    root = tmp_path / "data"
    write_store(root, "papila", [row("a", maps="fov;disc;cup", readers=";".join(readers))])
    square = [(10.0, 10.0), (10.0, 90.0), (90.0, 90.0), (90.0, 10.0)]
    inner = [(30.0, 30.0), (30.0, 70.0), (70.0, 70.0), (70.0, 30.0)]
    write_contours(
        root / "papila",
        "a",
        {("disc", reader): square for reader in readers}
        | {("cup", reader): inner for reader in readers},
    )
    return root


def test_the_outlines_come_back_per_reader_and_per_structure(tmp_path: Path) -> None:
    loader = disc.DiscCupLoader("papila", size=512, root=a_store(tmp_path))

    sample = loader[0]

    assert set(sample["outlines"]) == {
        ("disc", "expert1"),
        ("disc", "expert2"),
        ("cup", "expert1"),
        ("cup", "expert2"),
    }
    assert loader.readers_of("a") == ["expert1", "expert2"]


def test_the_outlines_are_in_the_frame_the_expert_drew_in(tmp_path: Path) -> None:
    loader = disc.DiscCupLoader("papila", size=512, root=a_store(tmp_path))

    nodes = loader[0]["outlines"][("disc", "expert1")]

    assert nodes.max() == 90.0, "native coordinates, not the model's grid"


def test_a_photograph_nobody_outlined_is_excluded_with_its_own_reason(tmp_path: Path) -> None:
    root = a_store(tmp_path)
    write_store(
        root,
        "papila",
        [
            row("a", maps="fov;disc;cup", readers="expert1;expert2"),
            row("b", maps="fov", readers=""),
        ],
    )
    write_contours(
        root / "papila",
        "a",
        {("disc", "expert1"): [(10.0, 10.0), (10.0, 90.0), (90.0, 90.0)]},
    )

    loader = disc.DiscCupLoader("papila", size=512, root=root)

    assert [sample["key"] for sample in loader] == ["a"]
    assert loader.excluded == {disc.NOTHING_OUTLINED: 1}


def test_the_photograph_is_prepared_by_the_model_that_asked_for_it(tmp_path: Path) -> None:
    import torch

    loader = disc.DiscCupLoader(
        "papila", size=512, root=a_store(tmp_path), prepare=lambda pixels: torch.zeros(3, 8, 8)
    )

    assert loader[0]["image"].shape == (3, 8, 8)


def test_a_batch_keeps_the_outlines_as_a_list(tmp_path: Path) -> None:
    from benchmarks.loaders.base import collate

    loader = disc.DiscCupLoader("papila", size=512, root=a_store(tmp_path))

    batch = collate([loader[0], loader[0]])

    assert batch["image"].shape[0] == 2
    assert isinstance(batch["outlines"], list) and len(batch["outlines"]) == 2
