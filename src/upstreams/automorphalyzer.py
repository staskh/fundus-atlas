# ABOUTME: AutoMorphalyzer's measuring code, pinned and reached as a package: its rewritten vessel
# ABOUTME: metrics, the vessel tracer they need, and the zonal masks they are measured inside.

from .utils import source

#: The commit `docs/projects/automorphalyzer.md` §1 describes. Releases exist but hold weights
#: rather than code, so the pin is a commit.
COMMIT = "e68843e2d3bc7f8585b6db34e29e2dfae68c7545"

#: The repository is a package whose modules import each other **flatly** — `measure.py` says
#: `import utils` and `import get_vessel_coords` rather than naming a package — so more than one
#: directory has to be on the path and the modules are imported by their own bare names. That is
#: the same treatment AutoMorph's stages get, and for the same reason.
CODE = source.Checkout(
    "automorphalyzer",
    "https://github.com/jaburke166/AutoMorphalyzer",
    COMMIT,
    imports_from="automorph",
)

#: The directories its flat imports resolve against, in the order they are added.
IMPORT_ROOTS = ("automorph", "automorph/measure")

#: What it needs and what this repository therefore pins. Both are in its own `requirements.txt`
#: at this commit but none is installed by anything else here: `Bottleneck` for the moving windows
#: in its width measurement, `numba` for the depth-first vessel tracer its authors rewrote, and
#: `SimpleITK` because its `utils` imports it at module load to read manual annotations that this
#: benchmark never supplies — needed to import the measuring code at all, not to run it.
REQUIRES = ("Bottleneck==1.4.2", "numba==0.61.0", "SimpleITK==2.4.1")


def _reachable():
    """Put every directory its flat imports need on the path, once."""
    import sys

    tree = CODE.obtain()
    for part in IMPORT_ROOTS:
        entry = str(tree / part)
        if entry not in sys.path:
            sys.path.insert(0, entry)
    return tree


def measure():
    """`automorph.measure.measure`: `vessel_metrics`, and the global metrics it calls."""
    _reachable()
    import measure as module

    return module


def coordinates():
    """`automorph.measure.get_vessel_coords`: the tracer that splits a map into single vessels.

    It is separate from the metrics because the metrics take its output rather than a mask: the
    rewrite of vessel extraction is the change its authors say corrects AutoMorph's tortuosity, so
    an adapter must use it rather than tracing the vessels some other way.
    """
    _reachable()
    import get_vessel_coords as module

    return module


def zones():
    """`automorph.utils`, for `generate_zonal_masks` — the B and C annuli round the disc."""
    _reachable()
    import utils as module

    return module


def provenance() -> dict[str, object]:
    """What a run records about the code that produced the number."""
    return {**CODE.provenance(), "requires": list(REQUIRES)}
