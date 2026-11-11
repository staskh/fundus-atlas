# ABOUTME: Tests for the paired agreement statistics, against cases whose answer is arithmetic and
# ABOUTME: against a published worked example of the two intraclass correlations.

import math

import numpy as np
import pytest

from benchmarks.metrics import agreement


def test_identical_maps_agree_perfectly_and_have_no_noise() -> None:
    values = [1.0, 2.0, 3.0, 5.0, 8.0]

    found = agreement.summary(values, values)

    assert found["icc_agreement"] == pytest.approx(1.0)
    assert found["icc_consistency"] == pytest.approx(1.0)
    assert found["snr"] == math.inf
    assert found["bias"] == 0.0


def test_a_constant_offset_is_forgiven_by_consistency_and_not_by_agreement() -> None:
    expert = [1.0, 2.0, 3.0, 4.0, 5.0]
    model = [value + 2.0 for value in expert]

    found = agreement.summary(expert, model)

    assert found["icc_consistency"] == pytest.approx(1.0)
    assert found["icc_agreement"] < 0.6
    assert found["bias"] == pytest.approx(2.0)
    assert found["relative_bias"] == pytest.approx(2.0 / 3.0)
    assert found["snr"] == math.inf  # an offset is bias, not noise


def test_the_two_iccs_match_a_worked_example() -> None:
    """Shrout and Fleiss (1979), Table 2, first two judges: six subjects rated by two judges.

    For two raters both forms have a closed form in the sample moments, which is independent of the
    analysis of variance the code uses: ICC(C,1) = 2·cov / (var₁ + var₂), and ICC(A,1) adds the
    squared mean difference to that denominator, less the residual's share (var₁ + var₂ − 2·cov) / n. Here var₁ = 8/3, var₂ = 2.7,
    cov = 2 and the means differ by 31/6.
    """
    pairs = np.array([[9, 2], [6, 1], [8, 4], [7, 1], [10, 5], [6, 2]], dtype=float)
    v1, v2, cov, gap, n = 8 / 3, 2.7, 2.0, 31 / 6, 6

    assert agreement.icc_consistency(pairs) == pytest.approx(2 * cov / (v1 + v2))
    assert agreement.icc_agreement(pairs) == pytest.approx(
        2 * cov / (v1 + v2 + gap**2 - (v1 + v2 - 2 * cov) / n)
    )


def test_noise_as_large_as_the_signal_gives_a_ratio_near_one() -> None:
    rng = np.random.default_rng(0)
    expert = rng.normal(0, 1, 20000)
    model = expert + rng.normal(0, 1, 20000)

    found = agreement.summary(list(expert), list(model))

    assert found["snr"] == pytest.approx(1.0, abs=0.03)
    # 2·cov / (var₁ + var₂) with cov = 1, var₁ = 1 and var₂ = 2.
    assert found["icc_consistency"] == pytest.approx(2 / 3, abs=0.02)


def test_a_photograph_only_one_map_answered_is_counted_and_left_out() -> None:
    found = agreement.summary([1.0, 2.0, 3.0, None, 5.0], [1.0, 2.0, 3.0, 4.0, None])

    assert found["n"] == 3
    assert found["expert_only"] == 1
    assert found["model_only"] == 1


def test_too_few_photographs_report_coverage_and_nothing_else() -> None:
    found = agreement.summary([1.0, 2.0], [1.0, 2.0])

    assert found == {"n": 2, "expert_only": 0, "model_only": 0}


def test_no_spread_between_photographs_has_no_signal_to_speak_of() -> None:
    found = agreement.summary([3.0, 3.0, 3.0], [3.0, 3.1, 2.9])

    assert found["snr"] is None
