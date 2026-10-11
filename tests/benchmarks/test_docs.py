# ABOUTME: Tests for the configuration-page renderer: every table is built from what a benchmark
# ABOUTME: reports about itself, and nothing a person wrote between the blocks is touched.

import pytest

from benchmarks import docs


def a_config() -> dict[str, object]:
    return {
        "asks": "Whether it works.",
        "unit_of_work": {"singular": "photograph", "plural": "photographs"},
        "subjects": {
            "label": "model",
            "fields": ["Pinned at", "Grid"],
            "declared": [
                {
                    "slug": "one",
                    "page": "../models/one.md",
                    "facts": {"Pinned at": "`abc`", "Grid": "512²"},
                    "ran": True,
                    "note": "gates on its own verdict",
                },
                {"slug": "two", "page": "../models/two.md", "ran": False, "why_not": "no weights"},
            ],
        },
        "material": {
            "label": "dataset",
            "fields": ["Photographs"],
            "declared": [
                {"slug": "here", "page": "../datasets/here.md", "facts": {"Photographs": 12}},
                {"slug": "gone", "available": False, "why_not": "no store built"},
            ],
            "wanted": [{"slug": "gone", "settles": "a held-out test", "cost": "direct"}],
        },
        "exclusions": {"below the size floor": "a field under 512 pixels"},
    }


def rendered(block: str) -> str:
    page = f"<!-- generated: {block} -->\n<!-- /generated -->\n"
    return docs.render(page, a_config())


def test_a_subject_table_takes_its_headings_from_the_config() -> None:
    written = rendered("subjects")

    assert "| Model | Pinned at | Grid | Took part |" in written
    assert "| [one](../models/one.md) | `abc` | 512² | yes |" in written


def test_a_subject_that_did_not_take_part_says_why_and_invents_no_facts() -> None:
    assert "| [two](../models/two.md) | — | — | **no** — no weights |" in rendered("subjects")


def test_material_without_a_page_is_named_rather_than_linked() -> None:
    written = rendered("material")

    assert "| Dataset | Photographs | Available |" in written
    assert "| [here](../datasets/here.md) | 12 | yes |" in written
    assert "| `gone` | — | **no** — no store built |" in written


def test_what_a_subject_does_with_its_answer_is_listed_only_where_it_said() -> None:
    written = rendered("subject_notes")

    assert "- **one** — gates on its own verdict" in written
    assert "two" not in written


def test_what_is_worth_fetching_is_a_table_of_its_own() -> None:
    written = rendered("worth_fetching")

    assert "| Dataset | What it would settle | Cost |" in written
    assert "| [gone](../datasets/gone.md) | a held-out test | direct |" in written


def test_every_exclusion_rule_is_named() -> None:
    assert "- **Below the size floor** — a field under 512 pixels" in rendered("exclusions")


def test_written_prose_around_a_block_is_left_alone() -> None:
    page = "Prose before.\n\n<!-- generated: asks -->\nstale\n<!-- /generated -->\n\nProse after.\n"

    assert docs.render(page, a_config()) == (
        "Prose before.\n\n<!-- generated: asks -->\nWhether it works.\n<!-- /generated -->\n\n"
        "Prose after.\n"
    )


def test_a_block_nothing_renders_is_an_error() -> None:
    with pytest.raises(ValueError, match="nothing renders"):
        docs.render("<!-- generated: nonsense -->\n<!-- /generated -->\n", a_config())
