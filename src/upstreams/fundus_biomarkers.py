# ABOUTME: fundus-biomarkers, Pheno's proprietary reference implementation of the canonical
# ABOUTME: biomarkers: cloned at a pinned commit from its private remote, never installed.

from .utils import source

#: The commit a result here is attributable to. The library's constants live in its code, so this
#: one id fingerprints all of them (`PLAN-BIOMARKER.md` §5.5).
COMMIT = "571bc8114241d6bacd08af3153476cc7f5733ee5"

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
    """The library's entry points: the `Retina` record, whose `biomarkers` are everything it
    measures, and the `Disc` it roots its tracing at."""
    CODE.on_path()
    from fundus_biomarkers import Disc, Retina

    return Retina, Disc


def provenance() -> dict[str, object]:
    return CODE.provenance()
