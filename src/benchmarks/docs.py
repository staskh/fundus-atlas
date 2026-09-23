# ABOUTME: The configuration page every benchmark has: rendering the JSON a benchmark reports about
# ABOUTME: itself into marked blocks, and leaving everything a person wrote exactly as they wrote it.

import json
from collections.abc import Iterable
from pathlib import Path

#: Where the pages live.
DIRECTORY = Path("docs/benchmarks")

#: What separates what is generated from what is written. A marker rather than a section number,
#: because numbers shift the moment somebody inserts a section, and a page that renumbered itself
#: would overwrite the wrong prose without anybody noticing.
OPEN = "<!-- generated: {name} -->"
CLOSE = "<!-- /generated -->"


def config_of(benchmark) -> dict[str, object]:
    """What a benchmark reports about itself, as data.

    Prose is not allowed across this boundary. A benchmark that described itself in finished
    sentences would have its sentences applied to pages it knows nothing about — which is exactly
    how a page came to tell readers that a benchmark with no weights hashed its weights.
    """
    return benchmark.config()


def render(page: str, config: dict[str, object]) -> str:
    """The page with every marked block replaced, and everything else untouched.

    :raises ValueError: on a marker naming a block nothing renders, or one never closed. Both are
        mistakes that would otherwise be silent — the first leaves a block permanently stale, the
        second would swallow the rest of the page.
    """
    out: list[str] = []
    rest = page
    while True:
        start = rest.find("<!-- generated: ")
        if start < 0:
            out.append(rest)
            return "".join(out)
        head, rest = rest[:start], rest[start:]
        line_end = rest.find("\n")
        marker = rest[:line_end] if line_end >= 0 else rest
        name = marker[len("<!-- generated: ") :].removesuffix("-->").strip()
        closing = rest.find(CLOSE)
        if closing < 0:
            raise ValueError(f"the `{name}` block is never closed; add `{CLOSE}` after it")
        if name not in BLOCKS:
            known = ", ".join(sorted(BLOCKS))
            raise ValueError(f"nothing renders a `{name}` block; there are {known}")
        out.append(head)
        out.append(marker + "\n")
        body = "\n".join(BLOCKS[name](config)).rstrip("\n")
        out.append(body + "\n" if body else "")
        rest = rest[closing:]
        out.append(CLOSE + "\n")
        rest = rest[len(CLOSE) :].removeprefix("\n")


def write(benchmark: str, config: dict[str, object], into: Path = DIRECTORY) -> Path:
    """Refresh one benchmark's configuration page in place."""
    path = Path(into) / f"{benchmark}-docs.md"
    if not path.exists():
        raise FileNotFoundError(
            f"{path} does not exist. The prose comes first and the blocks fill in: write the page "
            f"with empty marked blocks, then refresh it (see the `document-benchmark` skill)."
        )
    path.write_text(render(path.read_text(), config))
    return path


def _asks(config) -> Iterable[str]:
    yield str(config["asks"])


def _subjects(config) -> Iterable[str]:
    """Every declared subject, **including those that did not take part**, with the reason."""
    subjects = config["subjects"]
    yield f"| {subjects['label'].title()} | Pinned at | Columns it returns | Took part |"
    yield "| --- | --- | --- | --- |"
    for entry in subjects["declared"]:
        name = f"[{entry['slug']}]({entry['page']})" if entry.get("page") else f"`{entry['slug']}`"
        took = "yes" if entry.get("ran", True) else f"**no** — {entry.get('why_not', 'unknown')}"
        yield f"| {name} | {entry.get('pinned', '—')} | {entry.get('columns', '—')} | {took} |"


def _material(config) -> Iterable[str]:
    material = config["material"]
    yield f"| {material['label'].title()} | {material['describes']} | Available |"
    yield "| --- | --- | --- |"
    for entry in material["declared"]:
        available = (
            "yes" if entry.get("available", True) else f"**no** — {entry.get('why_not', '')}"
        )
        yield f"| `{entry['slug']}` | {entry.get('detail', '—')} | {available} |"


def _running(config) -> Iterable[str]:
    """The command, and **only the flags this benchmark honours**."""
    yield "```bash"
    for line in config["running"]["examples"]:
        yield line
    yield "```"
    yield ""
    yield "| Flag | What it does |"
    yield "| --- | --- |"
    for flag, meaning in config["running"]["flags"].items():
        yield f"| `{flag}` | {meaning} |"


def _columns(config) -> Iterable[str]:
    unit = config["unit_of_work"]
    yield f"`{config['evidence']}` holds one row per {unit['singular']}:"
    yield ""
    yield "| Column | Meaning |"
    yield "| --- | --- |"
    for column, meaning in config["columns"].items():
        yield f"| `{column}` | {meaning} |"


def _fingerprint(config) -> Iterable[str]:
    """Built from what this benchmark actually fingerprints, never from what benchmarks usually do."""
    unit = config["unit_of_work"]
    yield (
        "A stored result is kept only while everything it depends on is unchanged. This benchmark "
        "fingerprints:"
    )
    yield ""
    for item in config["fingerprint"]:
        yield f"- {item}"
    yield ""
    yield (
        f"A fingerprint that differs means the stored result describes something that no longer "
        f"exists, and it is measured again from nothing. **How much was done is not part of it**, "
        f"because that does not change what any {unit['singular']} scored: a complete result is "
        f"never re-run, and a partial one is finished rather than restarted."
    )


def _counts(config) -> Iterable[str]:
    yield "| Count | What it answers |"
    yield "| --- | --- |"
    for count, meaning in config["counts"].items():
        yield f"| `{count}` | {meaning} |"


def _biomarkers(config) -> Iterable[str]:
    """Every catalogued name an implementation may answer under, grouped by biomarker.

    Names are written with `<structure>` where one definition applies to several: an implementation
    that measures arteries and veins separately reports one column per structure. Whether a shape
    here settles a value is part of the table, because a name nothing settles is a gap in the
    shapes rather than a verdict on anybody's code.
    """
    structures = ", ".join(f"`{name}`" for name in config["structures"])
    settled = sum(1 for entry in config["biomarkers"] if entry["settled"])
    yield (
        f"{len(config['biomarkers'])} definitions, each applying to one or more structures "
        f"({structures}). **{settled} of them have a ground truth here** — a value computed from "
        f"the geometry of at least one synthetic image, which is what an implementation's answer "
        f"is compared against. The rest are measured and stored, and compared against nothing."
    )
    family = None
    for entry in config["biomarkers"]:
        if entry["biomarker"] != family:
            family = entry["biomarker"]
            yield ""
            yield f"**[{family}](../biomarkers/{family}.md)**"
            yield ""
            yield "| Canonical name | What it measures | Ground truth here |"
            yield "| --- | --- | --- |"
        yield (f"| `{entry['name']}` | {entry['means']} | {'yes' if entry['settled'] else '—'} |")


def _reports(config) -> Iterable[str]:
    for label, stem in config["reports"]:
        yield f"- **{label}** — [{stem}-results.md]({stem}-results.md)"


#: Every block a page may mark, and what fills it. A marker naming anything else is an error.
BLOCKS = {
    "asks": _asks,
    "subjects": _subjects,
    "material": _material,
    "running": _running,
    "columns": _columns,
    "fingerprint": _fingerprint,
    "counts": _counts,
    "biomarkers": _biomarkers,
    "reports": _reports,
}


def as_json(config: dict[str, object]) -> str:
    """What `--config` prints."""
    return json.dumps(config, indent=2, ensure_ascii=False)
