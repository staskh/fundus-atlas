# ABOUTME: Tests for identifying the weights a run actually loaded, and for refusing a download
# ABOUTME: that is not the file we pinned.

from pathlib import Path

import pytest

from upstreams.utils import weights


def test_one_ensembles_weights_have_one_identity(tmp_path: Path) -> None:
    (tmp_path / "a.pth").write_bytes(b"first member")
    (tmp_path / "b.pth").write_bytes(b"second member")

    identity = weights.digest([tmp_path / "a.pth", tmp_path / "b.pth"])

    assert len(identity) == 64
    assert identity == weights.digest([tmp_path / "b.pth", tmp_path / "a.pth"]), (
        "the order the files were listed in is not part of what was loaded"
    )


def test_a_changed_member_changes_the_identity(tmp_path: Path) -> None:
    (tmp_path / "a.pth").write_bytes(b"first member")
    before = weights.digest([tmp_path / "a.pth"])

    (tmp_path / "a.pth").write_bytes(b"retrained")

    assert weights.digest([tmp_path / "a.pth"]) != before


def test_a_file_that_is_not_what_was_pinned_is_refused(tmp_path: Path) -> None:
    path = tmp_path / "classifier.pkl"

    def hand_over(url: str, into: Path) -> None:
        into.write_bytes(b"something else entirely")

    with pytest.raises(ValueError, match="sha256"):
        weights.fetch("https://example.invalid/classifier.pkl", path, "0" * 64, fetch=hand_over)
    assert not path.exists(), "a file that is not what was pinned is not left on disk"


def test_a_pinned_file_is_fetched_once(tmp_path: Path) -> None:
    path = tmp_path / "classifier.pkl"
    calls = []

    def hand_over(url: str, into: Path) -> None:
        calls.append(url)
        into.write_bytes(b"the classifier")

    pinned = weights.digest_of(b"the classifier")
    weights.fetch("https://example.invalid/classifier.pkl", path, pinned, fetch=hand_over)
    weights.fetch("https://example.invalid/classifier.pkl", path, pinned, fetch=hand_over)

    assert calls == ["https://example.invalid/classifier.pkl"]
    assert path.read_bytes() == b"the classifier"
