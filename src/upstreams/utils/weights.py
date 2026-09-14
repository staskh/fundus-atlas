# ABOUTME: Fetching a published weight file and checking it is the one we pinned, and naming the
# ABOUTME: weights a run actually loaded so a score cannot outlive them.

import hashlib
from collections.abc import Callable, Iterable
from pathlib import Path

from datasets.utils import archives


def digest(paths: Iterable[Path]) -> str:
    """One identity for the weights a model loaded, whether that is one file or ten.

    The files are hashed in the order of their own digests rather than of their names, so the
    identity describes what was loaded and not how the caller happened to list it.
    """
    members = sorted(hashlib.sha256(Path(path).read_bytes()).hexdigest() for path in paths)
    return hashlib.sha256("".join(members).encode()).hexdigest()


def digest_of(content: bytes) -> str:
    """The digest of one file's content, for pinning it."""
    return hashlib.sha256(content).hexdigest()


def fetch(
    url: str,
    path: Path,
    sha256: str,
    fetch: Callable[[str, Path], None] | None = None,
) -> Path:
    """Download a weight file once, and refuse anything that is not what was pinned.

    :raises ValueError: if the download does not match, leaving nothing behind — some of these
        files are pickles, and loading a pickle runs the code inside it.
    """
    if path.exists() and digest_of(path.read_bytes()) == sha256:
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    (fetch or _download)(url, path)
    found = digest_of(path.read_bytes())
    if found != sha256:
        path.unlink()
        raise ValueError(f"{url} is sha256 {found}, not the pinned {sha256}")
    return path


def _download(url: str, into: Path) -> None:
    archives.download(url, into)
