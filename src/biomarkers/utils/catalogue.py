# ABOUTME: Loading a biomarker adapter by the slug of the project page it belongs to, from a file
# ABOUTME: whose name may carry hyphens and therefore cannot be imported.

import importlib.util
from pathlib import Path

#: Where the adapters live, one per implementation.
DIRECTORY = Path(__file__).resolve().parents[1]


def slugs() -> list[str]:
    """Every implementation with an adapter, by the slug of its project page."""
    return sorted(
        path.stem
        for path in DIRECTORY.glob("*.py")
        if path.stem not in {"__init__", "canonical", "naming"}
    )


def load(slug: str, **arguments: object):
    """One adapter, loaded from its path because a slug may carry a hyphen."""
    path = DIRECTORY / f"{slug}.py"
    if not path.exists():
        raise LookupError(f"no biomarker adapter at src/biomarkers/{slug}.py")
    spec = importlib.util.spec_from_file_location(f"biomarkers_{slug.replace('-', '_')}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.implementation(**arguments)
