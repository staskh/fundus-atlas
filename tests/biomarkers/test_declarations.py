# ABOUTME: Tests every biomarker adapter holds to: what it must declare about the code it runs, so
# ABOUTME: the synthetic benchmark can tell a stored result from a stale one.

import pytest

from biomarkers.utils import catalogue


@pytest.mark.parametrize("slug", catalogue.slugs())
def test_every_implementation_declares_the_code_it_runs(slug: str) -> None:
    """The benchmark fingerprints `upstream`, so leaving it out would keep a stale result."""
    upstream = catalogue.load(slug).declare()["upstream"]

    assert upstream["commit"]
