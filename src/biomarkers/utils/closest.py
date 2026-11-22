# ABOUTME: The nearest canonical name to a column the catalogue cannot name, and what keeps it from
# ABOUTME: being that name — a pointer for a reader of a project page, never a mapping.

import re

#: One rule: a pattern matched against the whole of a column's own name, the canonical name it is
#: nearest to (`None` where nothing is near), and why it is not that name. Both strings may use the
#: pattern's named groups, each translated through the adapter's own words for that group.
Rule = tuple[str, str | None, str]


def nearest(
    own: str, rules: tuple[Rule, ...], words: dict[str, dict[str, str]]
) -> tuple[str | None, str] | None:
    """The first rule matching `own`, filled in: `(canonical name or None, why)`. `None` where no
    rule matches, which a page renders as nothing near and nothing said."""
    for pattern, template, why in rules:
        found = re.fullmatch(pattern, own)
        if found is None:
            continue
        filled = {
            group: words.get(group, {}).get(value or "", value or "")
            for group, value in found.groupdict().items()
        }
        return (template.format(**filled) if template else None), why.format(**filled)
    return None
