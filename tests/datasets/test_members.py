# ABOUTME: Tests for reading a dataset's files where they lie: on disk, or inside a zip unopened.
# ABOUTME: Chaksu's per-expert masks are 70 GB extracted and a tenth of that left in the archive.

import zipfile

from datasets.utils import archives


def a_zip(tmp_path):
    path = tmp_path / "d.zip"
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("Train/1.0_Original/a.jpg", b"photograph")
        zf.writestr("Train/3.0_Masks/Expert 1/a.tif", b"mask")
    return path


def test_a_file_inside_a_zip_is_read_without_extracting_it(tmp_path):
    member = archives.Member(a_zip(tmp_path), "Train/1.0_Original/a.jpg")
    with member.open() as f:
        assert f.read() == b"photograph"
    assert not (tmp_path / "Train").exists()


def test_a_member_names_itself_by_its_path_inside_the_archive(tmp_path):
    member = archives.Member(a_zip(tmp_path), "Train/1.0_Original/a.jpg")
    assert member.label == "d.zip!Train/1.0_Original/a.jpg"


def test_members_can_be_listed_by_prefix(tmp_path):
    found = archives.members(a_zip(tmp_path), under="Train/3.0_Masks/")
    assert [m.name for m in found] == ["Train/3.0_Masks/Expert 1/a.tif"]


def test_listing_skips_the_rubbish_a_mac_leaves_in_an_archive(tmp_path):
    path = tmp_path / "mac.zip"
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("Train/a.jpg", b"x")
        zf.writestr("__MACOSX/Train/._a.jpg", b"junk")
        zf.writestr("Train/.DS_Store", b"junk")
    assert [m.name for m in archives.members(path)] == ["Train/a.jpg"]


def test_a_file_on_disk_reads_the_same_way(tmp_path):
    (tmp_path / "a.jpg").write_bytes(b"photograph")
    handle = archives.File(tmp_path / "a.jpg", root=tmp_path)
    with handle.open() as f:
        assert f.read() == b"photograph"
    assert handle.label == "a.jpg"
