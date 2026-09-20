# ABOUTME: Betti matching: the reference C++ implementation of the topological metric, cloned at a
# ABOUTME: pinned commit and built once into the checkout, because nothing publishes it as a wheel.

import subprocess
import sys
from pathlib import Path

from .utils import source

#: The reference implementation, by the authors of the method. MIT licensed, and not published on
#: PyPI in any form — neither the 2D nor the 3D repository — so it is cloned and built rather than
#: installed.
CODE = source.Checkout(
    "betti-matching",
    "https://github.com/nstucki/Betti-Matching-3D",
    "db623be7456ae451beb422af3bbcea94e9863a8f",
)

#: Where the build goes, inside the checkout, and what it produces. The module is a pybind11
#: extension named for the Python it was built against, so a checkout built by one interpreter is
#: not read by another.
BUILD = "build"
MODULE = "betti_matching"

#: What the build needs, which the upstream does not declare and this repository pins in the
#: `benchmarks` extra of pyproject.toml: cmake to configure it and pybind11 to link against. Both
#: are Python packages here rather than system tools, so that a machine with no Homebrew cmake can
#: still build this.
BUILD_REQUIREMENTS = ("cmake", "pybind11")


def module():
    """The built extension, building it first if this checkout has not been built yet.

    Imported by its own name from inside the build directory, as a pybind11 module must be.
    """
    built = _built()
    if str(built.parent) not in sys.path:
        sys.path.insert(0, str(built.parent))
    import betti_matching

    return betti_matching


def provenance() -> dict[str, object]:
    """What a run records: the pin, and the toolchain that turned it into something importable."""
    return {
        **CODE.provenance(),
        "built_with": {name: _version(name) for name in BUILD_REQUIREMENTS},
        "python": f"{sys.version_info.major}.{sys.version_info.minor}",
    }


def _built(root: Path | None = None) -> Path:
    """The compiled extension, built on first use and reused afterwards."""
    tree = CODE.obtain(root)
    directory = tree / BUILD
    existing = sorted(directory.glob(f"{MODULE}*.so")) + sorted(directory.glob(f"{MODULE}*.pyd"))
    if existing:
        return existing[0]
    _build(directory)
    made = sorted(directory.glob(f"{MODULE}*.so")) + sorted(directory.glob(f"{MODULE}*.pyd"))
    if not made:
        raise RuntimeError(
            f"the Betti matching build produced no extension module in {directory}; "
            f"the build log is beside it"
        )
    return made[0]


def _build(directory: Path) -> None:
    """Configure and compile, with cmake pointed at this environment rather than the system.

    The upstream's own instructions assume a cmake and a pybind11 on the machine. Here both come
    from the virtual environment, so both are named explicitly: otherwise cmake finds neither, or
    finds a pybind11 built against another Python.
    """
    import pybind11

    directory.mkdir(parents=True, exist_ok=True)
    cmake = Path(sys.executable).parent / "cmake"
    configure = [
        str(cmake),
        "-DCMAKE_BUILD_TYPE=Release",
        f"-Dpybind11_DIR={pybind11.get_cmake_dir()}",
        f"-DPython_EXECUTABLE={sys.executable}",
        "..",
    ]
    # An Apple machine defaults to building for whatever the compiler prefers, which on a machine
    # running an x86 Python under Rosetta is not the architecture the extension has to load into.
    if sys.platform == "darwin":
        configure.insert(1, f"-DCMAKE_OSX_ARCHITECTURES={_architecture()}")
    for command in (configure, [str(cmake), "--build", ".", "-j", "8"]):
        finished = subprocess.run(command, cwd=directory, capture_output=True, text=True)
        (directory / "atlas-build.log").write_text(finished.stdout + finished.stderr)
        if finished.returncode != 0:
            raise RuntimeError(
                f"building Betti matching failed: {' '.join(command)}\n"
                f"{finished.stderr[-2000:]}"
            )


def _architecture() -> str:
    """What this interpreter is, which is what the extension has to match."""
    import platform

    return "arm64" if platform.machine() == "arm64" else "x86_64"


def _version(package: str) -> str:
    from importlib import metadata

    try:
        return metadata.version(package)
    except metadata.PackageNotFoundError:  # pragma: no cover — only on a machine that cannot build
        return "not installed"
