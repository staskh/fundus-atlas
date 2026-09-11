# ABOUTME: Tests for the command-line contract every fetcher shares, and for where a store lives.
# ABOUTME: One contract, so a person who has run one fetcher has run all of them.

import pytest

from datasets.utils import cli, paths


def test_the_default_sizes_are_the_two_most_models_use():
    assert cli.parse("hrf", []).sizes == [512, 1024]


def test_sizes_are_a_comma_separated_list():
    assert cli.parse("hrf", ["--sizes", "256,512,1472"]).sizes == [256, 512, 1472]


def test_sizes_are_sorted_and_deduplicated():
    assert cli.parse("hrf", ["--sizes", "1024,512,1024"]).sizes == [512, 1024]


def test_a_size_that_is_not_a_positive_number_is_refused():
    with pytest.raises(SystemExit):
        cli.parse("hrf", ["--sizes", "0"])


def test_raw_is_deleted_unless_asked_for():
    assert cli.parse("hrf", []).keep_raw is False
    assert cli.parse("hrf", ["--keep-raw"]).keep_raw is True


def test_a_partial_build_must_be_asked_for_explicitly():
    assert cli.parse("hrf", []).limit is None
    assert cli.parse("hrf", ["--limit", "5"]).limit == 5


def test_the_store_root_can_be_moved(tmp_path):
    args = cli.parse("hrf", ["--data-root", str(tmp_path)])
    assert paths.store(args) == tmp_path / "hrf"


def test_the_store_root_defaults_to_the_repository_data_directory():
    args = cli.parse("hrf", [])
    assert paths.store(args).name == "hrf"
    assert paths.store(args).parent.name == "data"


def test_an_environment_variable_moves_every_store(tmp_path, monkeypatch):
    monkeypatch.setenv(paths.ENV_VAR, str(tmp_path))
    assert paths.store(cli.parse("hrf", [])) == tmp_path / "hrf"


def test_each_size_is_its_own_directory_beside_native(tmp_path):
    store = tmp_path / "hrf"
    assert paths.frame(store, "native") == store / "native"
    assert paths.frame(store, 512) == store / "512"
    assert paths.layer(store, 512, "vessels") == store / "512" / "vessels"
