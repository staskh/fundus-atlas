# ABOUTME: Tests for the AV-WIDE fetcher: REYIA's ultra-wide-field subset, built from the same archive
# ABOUTME: as REYIA but into a store of its own, so a 200-degree photograph is never pooled with 45.

from pathlib import Path

from test_reyia import an_archive

from datasets import av_wide, reyia
from datasets.utils import fov


def records(tmp_path: Path):
    found = av_wide.discover({av_wide.SLUG: an_archive(tmp_path)})
    return {record.key: record for record in found}


def test_only_the_ultra_wide_field_subset_is_built(tmp_path: Path) -> None:
    found = records(tmp_path)

    assert sorted(found) == ["avwide_w01"]
    assert {record.subset for record in found.values()} == {"avwide"}


def test_it_is_read_as_reyia_reads_it(tmp_path: Path) -> None:
    """One archive, one palette: the same label map must not mean two things in two stores."""
    (record,) = records(tmp_path).values()

    assert av_wide.PALETTE is reyia.PALETTE
    assert set(record.maps) == {"av"}
    assert record.extras["source_dataset"] == "AVWIDE"


def test_the_archive_is_reyias_and_needs_a_human(tmp_path: Path) -> None:
    (source,) = av_wide.SOURCES

    assert source.manual and source.filename == reyia.SOURCES[0].filename


def test_reyia_says_where_its_ultra_wide_field_subset_went() -> None:
    assert any(av_wide.SLUG in note for note in reyia.SKIPPED)


def test_the_whole_frame_is_kept_since_an_ultra_wide_field_has_no_circle() -> None:
    """A circle fitted to an Optos frame's edge is not a field of view: it pushed photographs off
    centre and padded a third of the square with nothing."""
    assert av_wide.FIELD == fov.WHOLE
