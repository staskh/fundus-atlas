# ABOUTME: Tests for the quality grade: a published grade mapped, or one derived from components.
# ABOUTME: Covers the three-value vocabulary and the "best value differs per component" rule.

import pytest

from datasets.utils import quality


def test_published_grade_is_mapped_to_the_common_vocabulary():
    rule = quality.Published({"1": "good", "0": "bad"})
    assert rule.grade({"overall_quality": "1"}) == ("good", "published")
    assert rule.grade({"overall_quality": "0"}) == ("bad", "published")


def test_published_grade_absent_from_the_row_is_empty_not_guessed():
    rule = quality.Published({"1": "good", "0": "bad"})
    assert rule.grade({"overall_quality": ""}) == ("", "published")


def test_published_grade_outside_the_declared_mapping_is_an_error():
    rule = quality.Published({"1": "good", "0": "bad"})
    with pytest.raises(ValueError, match="7"):
        rule.grade({"overall_quality": "7"})


def test_published_mapping_may_only_produce_the_three_words():
    with pytest.raises(ValueError, match="excellent"):
        quality.Published({"1": "excellent"})


def test_all_components_at_their_best_is_good():
    rule = quality.FromComponents({"artifact": "0", "clarity": "10", "field_definition": "10"})
    row = {"artifact": "0", "clarity": "10", "field_definition": "10"}
    assert rule.grade(row) == ("good", "derived")


def test_best_is_not_always_the_highest_number():
    rule = quality.FromComponents({"artifact": "0", "clarity": "10"})
    assert rule.grade({"artifact": "10", "clarity": "10"}) == ("usable", "derived")


def test_exactly_one_component_short_of_best_is_usable():
    rule = quality.FromComponents({"artifact": "0", "clarity": "10", "field_definition": "10"})
    row = {"artifact": "0", "clarity": "8", "field_definition": "10"}
    assert rule.grade(row) == ("usable", "derived")


def test_two_components_short_of_best_is_bad():
    rule = quality.FromComponents({"artifact": "0", "clarity": "10", "field_definition": "10"})
    row = {"artifact": "4", "clarity": "8", "field_definition": "10"}
    assert rule.grade(row) == ("bad", "derived")


def test_an_unrated_component_counts_as_short_of_best():
    rule = quality.FromComponents({"artifact": "0", "clarity": "10"})
    assert rule.grade({"artifact": "0", "clarity": ""}) == ("usable", "derived")


def test_a_missing_component_column_is_an_error_not_a_silent_bad():
    rule = quality.FromComponents({"artifact": "0", "clarity": "10"})
    with pytest.raises(KeyError, match="clarity"):
        rule.grade({"artifact": "0"})


def test_no_rule_means_no_grade_and_no_source():
    assert quality.grade_of(None, {"anything": "1"}) == ("", "")
