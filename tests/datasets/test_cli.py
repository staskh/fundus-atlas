# ABOUTME: Tests for the command-line contract every fetcher shares, and for where a store lives.
# ABOUTME: One contract, so a person who has run one fetcher has run all of them.

import pytest

from datasets.utils import cli, paths


def test_there_is_no_size_to_ask_for():
    """Every size a model needs is made from the crop when it is read, never stored."""
    with pytest.raises(SystemExit):
        cli.parse("hrf", ["--sizes", "512"])


def test_raw_is_deleted_unless_asked_for():
    assert cli.parse("hrf", []).keep_raw is False
    assert cli.parse("hrf", ["--keep-raw"]).keep_raw is True


def test_a_partial_build_must_be_asked_for_explicitly():
    assert cli.parse("hrf", []).limit is None
    assert cli.parse("hrf", ["--limit", "5"]).limit == 5


def test_the_store_root_can_be_moved(tmp_path):
    args = cli.parse("hrf", ["--data-root", str(tmp_path)])
    assert paths.store(args) == tmp_path / "hrf"


def test_the_store_root_defaults_to_a_hidden_directory_in_the_repository():
    args = cli.parse("hrf", [])
    assert paths.store(args).name == "hrf"
    assert paths.store(args).parent.name == ".atlas_data"


def test_an_environment_variable_moves_every_store(tmp_path, monkeypatch):
    monkeypatch.setenv(paths.ENV_VAR, str(tmp_path))
    assert paths.store(cli.parse("hrf", [])) == tmp_path / "hrf"


def test_every_layer_lives_in_the_crop(tmp_path):
    store = tmp_path / "hrf"
    assert paths.layer(store, "vessels") == store / "crop" / "vessels"
