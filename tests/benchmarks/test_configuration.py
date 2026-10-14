# ABOUTME: Tests for what the photograph benchmarks report about themselves: every declared model
# ABOUTME: and dataset, present or not, and a committed configuration page that matches it.

from pathlib import Path

import pytest

from benchmarks import av, disc, docs, photographs, quality

BENCHMARKS = (disc, av, quality)

#: The blocks every photograph benchmark's page carries, so a page with no markers cannot pass as
#: current merely because there is nothing in it to regenerate.
REQUIRED_BLOCKS = (
    "asks",
    "subjects",
    "material",
    "exclusions",
    "running",
    "columns",
    "fingerprint",
    "counts",
)


@pytest.mark.parametrize("benchmark", BENCHMARKS, ids=lambda module: module.NAME)
def test_every_declared_model_is_named_including_those_that_cannot_run(
    benchmark, tmp_path: Path
) -> None:
    subjects = benchmark.config(root=tmp_path)["subjects"]["declared"]

    assert [entry["slug"] for entry in subjects] == list(benchmark.MODELS)
    for entry in subjects:
        assert entry["ran"] or entry["why_not"], f"{entry['slug']} is absent and says nothing"


@pytest.mark.parametrize("benchmark", BENCHMARKS, ids=lambda module: module.NAME)
def test_a_dataset_with_no_store_is_named_and_says_so(benchmark, tmp_path: Path) -> None:
    material = benchmark.config(root=tmp_path)["material"]["declared"]

    assert [entry["slug"] for entry in material] == list(benchmark.DATASETS)
    assert {entry["why_not"] for entry in material} == {"no store built"}
    assert not any(entry["available"] for entry in material)


@pytest.mark.parametrize("benchmark", BENCHMARKS, ids=lambda module: module.NAME)
def test_every_column_of_the_evidence_is_explained(benchmark, tmp_path: Path) -> None:
    assert benchmark.config(root=tmp_path)["columns"] == benchmark.COLUMNS


@pytest.mark.parametrize(
    ("benchmark", "rescores"), [(disc, True), (av, True), (quality, False)], ids=["disc", "av", "q"]
)
def test_only_the_flags_a_benchmark_honours_are_listed(
    benchmark, rescores: bool, tmp_path: Path
) -> None:
    flags = benchmark.config(root=tmp_path)["running"]["flags"]

    assert ("--rescore" in flags) is rescores
    assert "--docs" in flags and "--model" in flags


@pytest.mark.parametrize("benchmark", BENCHMARKS, ids=lambda module: module.NAME)
def test_the_fingerprint_claims_nothing_the_run_does_not_hash(benchmark, tmp_path: Path) -> None:
    """The run hashes the declared facts, the weights, the store and the benchmark — not patches."""
    said = " ".join(benchmark.config(root=tmp_path)["fingerprint"])

    assert "patch" not in said
    assert f"`VERSION` ({benchmark.VERSION})" in said
    assert "builder version" in said


@pytest.mark.parametrize("benchmark", BENCHMARKS, ids=lambda module: module.NAME)
def test_the_committed_configuration_page_is_current(benchmark) -> None:
    """A stale page fails the suite rather than sitting wrong in a public reference.

    Like the store-reading facts it renders, this compares against the stores on the machine that
    runs it: refresh the page with `--docs` after rebuilding a store.
    """
    page = Path(docs.DIRECTORY) / f"{benchmark.NAME}-docs.md"
    current = page.read_text()

    for block in REQUIRED_BLOCKS:
        assert docs.OPEN.format(name=block) in current, f"{page} has no `{block}` block"
    assert docs.render(current, benchmark.config()) == current, (
        f"{page} is stale — refresh it with "
        f"`python -m benchmarks --benchmark {benchmark.NAME} --docs`"
    )


def test_a_store_catalogued_under_another_page_links_to_that_page() -> None:
    """AV-WIDE is a layer of REYIA's page, not a page of its own."""
    (entry,) = photographs.material(["av-wide"], [], {}, [], lambda found: {})["declared"]

    assert entry["page"] == "../datasets/reyia.md"
