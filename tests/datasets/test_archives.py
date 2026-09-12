# ABOUTME: Tests for obtaining a dataset: a real local git repository, a real zip, no mocks.
# ABOUTME: Also the rule that a licence needing a human is never automated around.

import subprocess
import zipfile

import pytest

from datasets.utils import archives


def a_repository(tmp_path):
    repo = tmp_path / "upstream"
    (repo / "images").mkdir(parents=True)
    (repo / "images" / "a.txt").write_text("a")
    (repo / "elsewhere").mkdir()
    (repo / "elsewhere" / "b.txt").write_text("b")
    run = lambda *a: subprocess.run(["git", "-C", str(repo), *a], check=True, capture_output=True)
    run("init", "-q")
    run("add", "-A")
    run("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "data")
    head = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"], check=True, capture_output=True, text=True
    ).stdout.strip()
    return repo, head


def test_a_repository_is_checked_out_at_the_pinned_commit(tmp_path):
    repo, head = a_repository(tmp_path)
    source = archives.GitSource(layer="d", repo=str(repo), commit=head)
    tree, record = source.obtain(tmp_path / "raw")
    assert (tree / "images" / "a.txt").read_text() == "a"
    assert record["commit"] == head


def test_only_the_subtrees_asked_for_are_checked_out(tmp_path):
    repo, head = a_repository(tmp_path)
    source = archives.GitSource(layer="d", repo=str(repo), commit=head, paths=["images"])
    tree, _ = source.obtain(tmp_path / "raw")
    assert (tree / "images" / "a.txt").exists()
    assert not (tree / "elsewhere").exists()


def test_a_commit_that_is_not_the_pinned_one_is_an_error(tmp_path):
    repo, head = a_repository(tmp_path)
    archives.GitSource(layer="d", repo=str(repo), commit=head).obtain(tmp_path / "raw")
    wrong = archives.GitSource(layer="d", repo=str(repo), commit="0" * 40)
    with pytest.raises(ValueError, match="pinned"):
        wrong.obtain(tmp_path / "raw")


def test_a_source_needing_a_human_is_never_downloaded(tmp_path):
    source = archives.Source(layer="d", url="https://example.invalid/x.zip", manual=True)
    with pytest.raises(PermissionError, match="--archive"):
        source.obtain(tmp_path)


def test_a_checksum_that_does_not_match_stops_the_build(tmp_path):
    payload = tmp_path / "x.zip"
    with zipfile.ZipFile(payload, "w") as zf:
        zf.writestr("a.txt", "a")
    source = archives.Source(layer="d", url=payload.as_uri(), sha256="0" * 64)
    with pytest.raises(ValueError, match="not the archive"):
        source.obtain(tmp_path / "raw")


def test_a_zip_is_unpacked(tmp_path):
    payload = tmp_path / "x.zip"
    with zipfile.ZipFile(payload, "w") as zf:
        zf.writestr("a.txt", "a")
    tree = archives.extract(payload, tmp_path / "out")
    assert (tree / "a.txt").read_text() == "a"


def test_an_archive_can_be_kept_packed_and_read_in_place(tmp_path):
    payload = tmp_path / "big.zip"
    with zipfile.ZipFile(payload, "w") as zf:
        zf.writestr("Train/a.tif", b"mask")
    source = archives.Source(layer="d", url=payload.as_uri(), extract_it=False)
    where, record = source.obtain(tmp_path / "raw")
    assert where.suffix == ".zip"
    assert not (tmp_path / "raw" / "d").exists()
    assert record["sha256"]


def test_a_download_can_be_named_where_the_url_does_not_name_it(tmp_path):
    payload = tmp_path / "x.zip"
    with zipfile.ZipFile(payload, "w") as zf:
        zf.writestr("a.txt", b"a")
    # Figshare and friends serve files from a numeric id with no filename in the path.
    source = archives.Source(layer="d", url=payload.as_uri(), filename="Named.zip")
    source.obtain(tmp_path / "raw")
    assert (tmp_path / "raw" / "Named.zip").exists()


def test_an_archive_that_yields_nothing_is_an_error(tmp_path):
    # FIVES and GRAPE publish RAR5, which the Python standard library cannot read. bsdtar reads it
    # — and, handed a broken one, exits successfully having produced no files at all. An empty
    # directory named after the dataset looks like an extracted dataset, which is worse than a
    # failure, so emptiness is the thing to check for whatever the format.
    fake = tmp_path / "x.rar"
    fake.write_bytes(b"Rar!\x1a\x07\x01\x00" + b"not really a rar")
    with pytest.raises(RuntimeError, match="no files"):
        archives.extract(fake, tmp_path / "out")
    assert not (tmp_path / "out").exists()
