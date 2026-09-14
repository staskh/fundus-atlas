# ABOUTME: Tests for pinning third-party code: a clone at a commit, a patch applied to it, and the
# ABOUTME: provenance a run records about both, against real git repositories and real packages.

import subprocess
import sys
from pathlib import Path

import pytest

from upstreams.utils import source


def git(*args: str, cwd: Path) -> str:
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
    ).stdout


@pytest.fixture
def origin(tmp_path: Path) -> Path:
    """A two-commit repository standing in for somebody's published code."""
    repo = tmp_path / "origin"
    repo.mkdir()
    git("init", "-q", "-b", "main", cwd=repo)
    git("config", "user.email", "test@example.com", cwd=repo)
    git("config", "user.name", "Test", cwd=repo)
    (repo / "grader.py").write_text("VERDICT = 'good'\n")
    git("add", "grader.py", cwd=repo)
    git("commit", "-qm", "first", cwd=repo)
    return repo


def head_of(repo: Path) -> str:
    return git("rev-parse", "HEAD", cwd=repo).strip()


def test_checkout_clones_at_the_pinned_commit(origin: Path, tmp_path: Path) -> None:
    pinned = head_of(origin)
    (origin / "grader.py").write_text("VERDICT = 'moved on'\n")
    git("commit", "-qam", "second", cwd=origin)

    checkout = source.Checkout("grader", str(origin), pinned)
    tree = checkout.obtain(root=tmp_path / "code")

    assert (tree / "grader.py").read_text() == "VERDICT = 'good'\n"


def test_checkout_is_obtained_once(origin: Path, tmp_path: Path) -> None:
    checkout = source.Checkout("grader", str(origin), head_of(origin))
    first = checkout.obtain(root=tmp_path / "code")
    (first / "scratch.txt").write_text("left behind")

    again = checkout.obtain(root=tmp_path / "code")

    assert again == first
    assert (again / "scratch.txt").exists(), "the tree was cloned a second time"


def test_checkout_records_its_provenance(origin: Path, tmp_path: Path) -> None:
    pinned = head_of(origin)
    checkout = source.Checkout("grader", str(origin), pinned)
    checkout.obtain(root=tmp_path / "code")

    assert checkout.provenance() == {
        "slug": "grader",
        "repo": str(origin),
        "commit": pinned,
        "patches": {},
    }


def test_a_patch_is_applied_to_the_checkout(origin: Path, tmp_path: Path) -> None:
    patches = tmp_path / "patches" / "grader"
    patches.mkdir(parents=True)
    (patches / "001-verdict.patch").write_text(
        "--- a/grader.py\n+++ b/grader.py\n@@ -1 +1 @@\n-VERDICT = 'good'\n+VERDICT = 'usable'\n"
    )
    checkout = source.Checkout("grader", str(origin), head_of(origin), patches=patches.parent)

    tree = checkout.obtain(root=tmp_path / "code")

    assert (tree / "grader.py").read_text() == "VERDICT = 'usable'\n"


def test_a_patch_is_applied_once_and_named_by_its_content(origin: Path, tmp_path: Path) -> None:
    patches = tmp_path / "patches" / "grader"
    patches.mkdir(parents=True)
    (patches / "001-verdict.patch").write_text(
        "--- a/grader.py\n+++ b/grader.py\n@@ -1 +1 @@\n-VERDICT = 'good'\n+VERDICT = 'usable'\n"
    )
    checkout = source.Checkout("grader", str(origin), head_of(origin), patches=patches.parent)
    tree = checkout.obtain(root=tmp_path / "code")
    checkout.obtain(root=tmp_path / "code")

    assert (tree / "grader.py").read_text() == "VERDICT = 'usable'\n"
    recorded = checkout.provenance()["patches"]
    assert list(recorded) == ["001-verdict.patch"]
    assert len(recorded["001-verdict.patch"]) == 64, "a patch is fingerprinted by its content"


def test_a_checkout_can_be_imported_from(origin: Path, tmp_path: Path) -> None:
    checkout = source.Checkout("grader", str(origin), head_of(origin))
    tree = checkout.obtain(root=tmp_path / "code")

    try:
        checkout.on_path(root=tmp_path / "code")
        assert str(tree) in sys.path
        import grader

        assert grader.VERDICT == "good"
    finally:
        sys.path.remove(str(tree))
        sys.modules.pop("grader", None)


def test_an_installed_upstream_reports_the_version_that_is_actually_there() -> None:
    import numpy

    installed = source.Installed("numpy")

    assert installed.provenance()["version"] == numpy.__version__


def test_an_installed_upstream_at_the_wrong_version_is_refused() -> None:
    installed = source.Installed("numpy", version="0.0.0-not-a-real-release")

    with pytest.raises(RuntimeError, match="numpy"):
        installed.provenance()


def test_an_upstream_that_is_not_installed_says_how_to_install_it() -> None:
    installed = source.Installed("no-such-distribution")

    with pytest.raises(RuntimeError, match="uv sync"):
        installed.provenance()


def test_a_checkout_can_be_imported_from_a_subdirectory(origin: Path, tmp_path: Path) -> None:
    git("mv", "grader.py", "stage.py", cwd=origin)
    (origin / "module").mkdir()
    git("mv", "stage.py", "module/grader.py", cwd=origin)
    git("commit", "-qam", "into a module", cwd=origin)
    checkout = source.Checkout("staged", str(origin), head_of(origin), imports_from="module")

    tree = checkout.on_path(root=tmp_path / "code")

    try:
        assert str(tree / "module") in sys.path
        import grader

        assert grader.VERDICT == "good"
    finally:
        sys.path.remove(str(tree / "module"))
        sys.modules.pop("grader", None)


def test_an_upstream_installed_from_a_repository_reports_the_commit_it_came_from() -> None:
    from upstreams import fit

    assert fit.CODE.provenance()["commit"] == fit.CODE.commit


def test_an_upstream_installed_from_a_release_reports_no_commit() -> None:
    assert "commit" not in source.Installed("numpy").provenance()
