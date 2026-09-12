# ABOUTME: Getting a dataset onto disk: downloads, checksums, and repositories pinned to a commit.
# ABOUTME: Never works around a human step — a licence that asks for one is not an inconvenience.

import hashlib
import shutil
import subprocess
import tarfile
import time
import urllib.request
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import BinaryIO

#: How much to ask for at a time. Large archives are fetched in ranged pieces rather than one
#: long connection: figshare and its S3 backend will accept a connection for a ten-gigabyte file,
#: deliver a few gigabytes and then go quiet indefinitely, while ranged requests to the same file
#: run at full speed. Small enough to lose little on a retry, large enough not to be chatty.
CHUNK = 64 << 20

#: How many times a chunk is retried before the download is called off.
ATTEMPTS = 6

#: Seconds between attempts.
PAUSE = 3


def download(
    url: str,
    path: Path,
    fetch=None,
    size_of=None,
    chunk: int = CHUNK,
    attempts: int = ATTEMPTS,
    pause: float = PAUSE,
) -> None:
    """Fetch a URL to a file, in chunks, resuming whatever is already there.

    :param fetch: how to get one range, for tests; by default an HTTP range request.
    :param size_of: how to learn the total size, for tests.
    :raises OSError: if the server stops sending before the file is complete, rather than waiting
        on it for ever.
    """
    fetch = fetch or _range
    size_of = size_of or _size
    total = size_of(url)
    have = path.stat().st_size if path.exists() else 0
    if have > total:
        raise ValueError(
            f"{path} is {have} bytes, larger than the {total} the server reports: it is not a "
            f"partial copy of this file. Delete it and start again."
        )
    if have == total:
        return

    with open(path, "ab") as f:
        wrote = 0
        while have < total:
            end = min(have + chunk, total) - 1
            piece = _with_retries(fetch, url, have, end, attempts, pause)
            if not piece:
                raise OSError(f"{url} stopped sending at {have} of {total} bytes")
            f.write(piece)
            f.flush()
            have += len(piece)
            wrote += len(piece)
            if wrote > total:
                raise ValueError(f"{url} sent more than the {total} bytes it reported")


def _with_retries(fetch, url: str, start: int, end: int, attempts: int, pause: float) -> bytes:
    for attempt in range(attempts):
        try:
            return fetch(url, start, end)
        except OSError:
            if attempt == attempts - 1:
                raise
            time.sleep(pause)
    return b""


def _range(url: str, start: int, end: int) -> bytes:
    request = urllib.request.Request(url, headers={"Range": f"bytes={start}-{end}"})
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.read()


def _size(url: str) -> int:
    with urllib.request.urlopen(urllib.request.Request(url, method="HEAD"), timeout=60) as r:
        length = r.headers.get("Content-Length")
    if length:
        return int(length)
    request = urllib.request.Request(url, headers={"Range": "bytes=0-0"})
    with urllib.request.urlopen(request, timeout=60) as r:
        return int(r.headers["Content-Range"].split("/")[-1])


#: Files a Mac leaves inside an archive that are not part of the dataset.
MAC_RUBBISH = ("__MACOSX/", "._", ".DS_Store")


@dataclass(frozen=True)
class File:
    """A dataset file on disk.

    :param root: the extracted tree, so the file can name itself by where it sits inside it.
    """

    path: Path
    root: Path | None = None

    @property
    def label(self) -> str:
        if self.root is None:
            return str(self.path)
        try:
            return str(self.path.resolve().relative_to(self.root.resolve()))
        except ValueError:
            return str(self.path)

    def open(self) -> BinaryIO:
        return open(self.path, "rb")


@dataclass(frozen=True)
class Member:
    """A dataset file inside a zip, read where it lies.

    Some archives are far larger unpacked than packed, and unpacking them is work done twice:
    Chakshu's per-expert masks are uncompressed TIFFs, 70 GB extracted against 11 GB in the
    archive, and every one of them is read once and turned into a polygon. Reading members
    directly keeps the archive as the only copy.
    """

    archive: Path
    name: str

    @property
    def label(self) -> str:
        return f"{self.archive.name}!{self.name}"

    def open(self) -> BinaryIO:
        return _opened(self.archive).open(self.name)


Handle = File | Member


def members(archive: Path, under: str = "") -> list[Member]:
    """Every real file in a zip, in archive order.

    :param under: keep only members beneath this path inside the archive.
    """
    return [
        Member(archive, name)
        for name in _opened(archive).namelist()
        if name.startswith(under)
        and not name.endswith("/")
        and not any(part in name for part in MAC_RUBBISH)
    ]


def _opened(archive: Path) -> zipfile.ZipFile:
    """One open handle per archive, since a build reads thousands of members from each."""
    key = str(archive)
    if key not in _OPEN:
        _OPEN[key] = zipfile.ZipFile(archive)
    return _OPEN[key]


_OPEN: dict[str, zipfile.ZipFile] = {}


@dataclass(frozen=True)
class Source:
    """One download making up a dataset.

    :param layer: what this supplies — the photographs, or an annotation published separately.
    :param url: where it comes from, or empty for a source that must be obtained by hand.
    :param sha256: the archive's checksum, or empty where the host does not serve stable bytes.
    :param manual: `True` where the licence requires a person to accept terms or sign for it. Such
        a source is never downloaded: the fetcher requires `--archive` and prints the page's route.
    """

    layer: str
    url: str = ""
    sha256: str = ""
    licence: str = ""
    optional: bool = False
    manual: bool = False
    filename: str = ""
    extract_it: bool = True

    def obtain(self, into: Path, verify: bool = True) -> tuple[Path, dict[str, str]]:
        """Download, and unpack unless this archive is meant to be read in place.

        :return: the extracted tree — or the archive itself, for a source declaring
            ``extract_it=False`` — and what to record about where it came from.
        """
        if self.manual or not self.url:
            raise PermissionError(
                f"{self.layer} must be obtained by hand and passed with --archive; "
                f"see the dataset page for the route"
            )
        into.mkdir(parents=True, exist_ok=True)
        archive = into / (self.filename or Path(self.url).name)
        download(self.url, archive)
        digest = _sha256(archive)
        if self.sha256 and verify and digest != self.sha256:
            raise ValueError(f"{archive.name} is not the archive recorded for {self.layer}")
        record = {"layer": self.layer, "url": self.url, "sha256": digest}
        if not self.extract_it:
            return archive, record
        return extract(archive, into / self.layer), record


@dataclass(frozen=True)
class GitSource:
    """A dataset published as a repository rather than an archive.

    The commit, not a checksum, is the anchor: a host's generated tarball is not byte-stable, but
    a commit names exactly one tree for ever.

    :param paths: the subtrees to check out, for a repository holding more than the atlas builds.
    """

    layer: str
    repo: str
    commit: str
    paths: list[str] = field(default_factory=list)
    licence: str = ""
    optional: bool = False
    manual: bool = False

    def obtain(self, into: Path, verify: bool = True) -> tuple[Path, dict[str, str]]:
        """Clone at the pinned commit, fetching only the subtrees asked for."""
        tree = into / self.layer
        if not (tree / ".git").exists():
            into.mkdir(parents=True, exist_ok=True)
            sparse = ["--sparse"] if self.paths else []
            _git(["clone", "--filter=blob:none", *sparse, "--no-checkout", self.repo, str(tree)])
            if self.paths:
                _git(["-C", str(tree), "sparse-checkout", "set", *self.paths])
            _git(["-C", str(tree), "checkout", self.commit])
        at = _git(["-C", str(tree), "rev-parse", "HEAD"]).strip()
        if verify and at != self.commit:
            raise ValueError(f"{tree} is at {at}, not the pinned {self.commit}")
        return tree, {"layer": self.layer, "repo": self.repo, "commit": at}


def extract(archive: Path, into: Path) -> Path:
    """Unpack a zip or tar, or return a directory that was passed instead of an archive."""
    if archive.is_dir():
        return archive
    if into.exists():
        return into
    into.mkdir(parents=True)
    if zipfile.is_zipfile(archive):
        with zipfile.ZipFile(archive) as zf:
            zf.extractall(into)
    elif tarfile.is_tarfile(archive):
        with tarfile.open(archive) as tf:
            tf.extractall(into, filter="data")
    else:
        shutil.copy2(archive, into / archive.name)
    return into


def _sha256(path: Path) -> str:
    with open(path, "rb") as f:
        return _digest(f)


def _digest(stream: BinaryIO) -> str:
    digest = hashlib.sha256()
    for block in iter(lambda: stream.read(1 << 20), b""):
        digest.update(block)
    return digest.hexdigest()


def sha256_of(source: "Handle | Path") -> str:
    """The checksum of one file, recorded per image so a row can be traced to its bytes."""
    if isinstance(source, (File, Member)):
        with source.open() as f:
            return _digest(f)
    return _sha256(Path(source))


def _git(argv: list[str]) -> str:
    return subprocess.run(["git", *argv], check=True, capture_output=True, text=True).stdout
