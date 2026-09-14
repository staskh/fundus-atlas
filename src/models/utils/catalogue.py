# ABOUTME: Finding a model adapter by the slug its catalogue page carries, so that a result and
# ABOUTME: the page recording what the model was trained on cannot come apart.

import importlib.util
from pathlib import Path
from types import ModuleType

#: One file per catalogued model, named exactly as ``docs/models/<slug>.md`` is. The slugs carry
#: hyphens, which no module name may, so an adapter is loaded from its path rather than imported.
#: Everything two adapters share lives in ``utils`` beside them, as it does for the fetchers.
DIRECTORY = Path(__file__).resolve().parents[1]

#: The function every adapter module publishes, returning the adapter itself.
ENTRY = "model"


def slugs() -> list[str]:
    """Every model this repository can run, in the order a report should list them."""
    return sorted(
        path.stem for path in DIRECTORY.glob("*.py") if not path.stem.startswith("__")
    )


def load(slug: str, **arguments: object) -> object:
    """The adapter for one catalogued model.

    :raises LookupError: if no adapter has been written for that slug yet.
    """
    path = DIRECTORY / f"{slug}.py"
    if not path.exists():
        raise LookupError(f"no adapter for {slug!r}: src/models/{slug}.py does not exist")
    return getattr(_module(slug, path), ENTRY)(**arguments)


def _module(slug: str, path: Path) -> ModuleType:
    specification = importlib.util.spec_from_file_location(f"models._{slug.replace('-', '_')}", path)
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module
