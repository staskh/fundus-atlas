# ABOUTME: Tests that BF-Net's unversioned weights are pinned by a digest this repository took
# ABOUTME: itself, that a run records which archive it ran, and that a nameless one is not guessed at.

import pytest

from upstreams import bfnet


def test_every_published_archive_is_pinned_by_a_full_digest() -> None:
    """A Google Drive folder carries no version, so the digest is the only pin there is."""
    for name, published in bfnet.PUBLISHED.items():
        assert len(published.sha256) == 64, f"{name} is not pinned by a sha256"
        assert published.folder.startswith(f"{name}/"), f"{name} names its own folder"
        assert published.seed == 42, "each archive holds one seed, and it is this one"


def test_the_archive_the_benchmark_runs_trained_on_none_of_the_stores_it_is_scored_on() -> None:
    assert bfnet.DEFAULT == "DRIVE_AV"
    assert bfnet.DEFAULT in bfnet.PUBLISHED


def test_a_run_records_which_unversioned_archive_it_ran() -> None:
    recorded = bfnet.provenance()

    assert recorded["commit"] == bfnet.CODE.commit
    assert recorded["weights"]["sha256"] == bfnet.PUBLISHED[bfnet.DEFAULT].sha256
    assert recorded["weights"]["fetched"], "a digest with no date behind it dates nothing"
    assert recorded["weights"]["folder"] == bfnet.FOLDER


def test_an_archive_the_folder_does_not_hold_is_not_guessed_at() -> None:
    with pytest.raises(LookupError, match="DRIVE_AV"):
        bfnet.provenance("IOSTAR-AV")
