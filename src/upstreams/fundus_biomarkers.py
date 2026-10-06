# ABOUTME: fundus-biomarkers, Pheno's proprietary reference implementation of the canonical
# ABOUTME: biomarkers: cloned at a pinned commit from its private remote, never installed.

from .utils import source

#: The commit a result here is attributable to. The library's constants live in its code, so this
#: one id fingerprints all of them (`PLAN-BIOMARKER.md` §5.5).
COMMIT = "29dea9c2c945646320f84e11215386d2137c0071"

#: **Cloned, never installed** (`PLAN-BIOMARKER.md` §5.4): the private code never enters this
#: repository's dependency graph, and a clone of the atlas without access to the remote can read
#: every number this column produced but cannot re-run it. Its package lives under `src/`.
CODE = source.Checkout(
    "fundus-biomarkers",
    "git@github.com:PhenoAI/fundus-biomarkers.git",
    COMMIT,
    imports_from="src",
)


def library() -> object:
    """The library's entry points: `measure(retina)`, `names()` and the `Retina` record."""
    CODE.on_path()
    from fundus_biomarkers import measure, retina

    return measure, retina


def provenance() -> dict[str, object]:
    return CODE.provenance()
