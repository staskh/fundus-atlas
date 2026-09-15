# ABOUTME: Pinning somebody else's code: a clone at a commit, our patches on top, or a pinned
# ABOUTME: distribution already installed — and the provenance a benchmark run records about it.

import hashlib
import json
import subprocess
import sys
from dataclasses import dataclass, field
from importlib import metadata
from pathlib import Path

from datasets.utils import archives

from . import paths

#: Where a patch file lives: ``src/upstreams/patches/<slug>/NNN-what-it-fixes.patch``.
PATCHES = Path(__file__).resolve().parents[1] / "patches"

#: Records which patches a working tree already carries, so obtaining it twice is not applying
#: them twice. Inside ``.git`` because it describes the checkout and never belongs to the upstream.
APPLIED = "atlas-patches.json"


@dataclass(frozen=True)
class Checkout:
    """A repository pinned to a commit, cloned into ``.atlas_code`` and imported from there.

    The commit is the anchor rather than a checksum: a host's generated tarball is not byte-stable,
    but a commit names exactly one tree for ever, so a patch written against it cannot rot.

    :param slug: the directory it is cloned into, and the name its provenance is recorded under.
    :param subtrees: the parts of a large repository to check out, where the rest is not needed.
    :param patches: the directory holding ``<slug>/*.patch``; the repository's own by default.
    :param imports_from: the directory inside the tree whose own modules are imported, where a
        repository is a pipeline of stages rather than a package.
    """

    slug: str
    repo: str
    commit: str
    subtrees: list[str] = field(default_factory=list)
    patches: Path = PATCHES
    imports_from: str = ""

    def obtain(self, root: Path | None = None) -> Path:
        """Clone at the pinned commit if it is not already there, and apply our patches."""
        into = root or paths.root()
        tree, _ = archives.GitSource(
            layer=self.slug, repo=self.repo, commit=self.commit, paths=self.subtrees
        ).obtain(into)
        self._patch(tree)
        return tree

    def on_path(self, root: Path | None = None) -> Path:
        """Obtain the checkout and put it on ``sys.path``, which is how a clone is imported.

        A leading dot is nothing to the import machinery, but it cannot be part of a package name,
        so an upstream fetched this way is reached by its own module names rather than through
        ``.atlas_code``.
        """
        tree = self.obtain(root)
        entry = str(tree / self.imports_from) if self.imports_from else str(tree)
        if entry not in sys.path:
            sys.path.insert(0, entry)
        return tree

    def provenance(self) -> dict[str, object]:
        """What the run records: where the code came from, and what we changed in it."""
        return {
            "slug": self.slug,
            "repo": self.repo,
            "commit": self.commit,
            "patches": {path.name: _digest(path) for path in self._files()},
        }

    def _files(self) -> list[Path]:
        directory = self.patches / self.slug
        return sorted(directory.glob("*.patch")) if directory.exists() else []

    def _patch(self, tree: Path) -> None:
        record = tree / ".git" / APPLIED
        already = json.loads(record.read_text()) if record.exists() else {}
        for path in self._files():
            digest = _digest(path)
            if already.get(path.name) == digest:
                continue
            subprocess.run(
                ["git", "apply", "--whitespace=nowarn", str(path)],
                cwd=tree,
                check=True,
                capture_output=True,
                text=True,
            )
            already[path.name] = digest
        if already:
            record.write_text(json.dumps(already, indent=2, sort_keys=True))


@dataclass(frozen=True)
class Installed:
    """An upstream pinned in ``pyproject.toml`` and installed into the shared environment.

    Nothing here installs anything: the environment is declared in one place and built by ``uv``,
    and this checks that what is actually importable is what was pinned.

    :param version: the release expected, where the pin is a release.
    :param commit: the commit expected, where the pin is a repository.
    """

    distribution: str
    version: str = ""
    commit: str = ""

    def provenance(self) -> dict[str, object]:
        """What the run records, having first checked it is what was asked for.

        :raises RuntimeError: if the distribution is missing, or is not the pinned version.
        """
        try:
            found = metadata.version(self.distribution)
        except metadata.PackageNotFoundError:
            raise RuntimeError(
                f"{self.distribution} is not installed; run "
                f"`uv sync --extra benchmarks` to build the benchmark environment"
            ) from None
        at = self._source()
        if self.version and found != self.version:
            raise RuntimeError(
                f"{self.distribution} is {found}, not the pinned {self.version}; "
                f"run `uv sync --extra benchmarks`"
            )
        if self.commit and at.get("commit") != self.commit:
            raise RuntimeError(
                f"{self.distribution} was installed from {at.get('commit', 'an unknown commit')}, "
                f"not the pinned {self.commit}; run `uv sync --extra benchmarks --reinstall`"
            )
        return {"distribution": self.distribution, "version": found, **at}

    def _source(self) -> dict[str, str]:
        """Where the installer recorded the distribution as coming from, for one from a repository."""
        text = metadata.distribution(self.distribution).read_text("direct_url.json")
        record = json.loads(text) if text else {}
        info = record.get("vcs_info", {})
        if not info:
            return {}
        return {"repo": record.get("url", ""), "commit": info.get("commit_id", "")}


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
