# ABOUTME: How far one biomarker moves when the expert's vessel map is replaced by a model's: the
# ABOUTME: intraclass correlations, the signal-to-noise ratio and the bias, over paired photographs.

import math
from collections.abc import Sequence

import numpy as np

#: Fewer paired photographs than this and no statistic is reported. Three is the least for which a
#: two-way analysis of variance has a residual at all; below it every number here is undefined
#: rather than merely noisy.
FEWEST = 3


def paired(expert: Sequence[float | None], model: Sequence[float | None]) -> np.ndarray:
    """The photographs both maps produced a finite value for, as an n × 2 array."""
    rows = [
        (float(e), float(m))
        for e, m in zip(expert, model, strict=True)
        if e is not None and m is not None and math.isfinite(float(e)) and math.isfinite(float(m))
    ]
    return np.asarray(rows, dtype=float).reshape(-1, 2)


def _mean_squares(pairs: np.ndarray) -> tuple[float, float, float]:
    """The two-way analysis of variance behind both ICCs: photographs, maps, and what is left.

    Rows are photographs (the subjects), columns the two maps (the raters). Returns the mean squares
    for rows, columns and error, as McGraw and Wong (1996) name them MSR, MSC and MSE.
    """
    n, k = pairs.shape
    grand = pairs.mean()
    rows = k * ((pairs.mean(axis=1) - grand) ** 2).sum() / (n - 1)
    columns = n * ((pairs.mean(axis=0) - grand) ** 2).sum() / (k - 1)
    residual = pairs - pairs.mean(axis=1, keepdims=True) - pairs.mean(axis=0, keepdims=True) + grand
    error = (residual**2).sum() / ((n - 1) * (k - 1))
    return rows, columns, error


def icc_agreement(pairs: np.ndarray) -> float | None:
    """ICC(A,1): two-way, absolute agreement, one measurement — a constant offset counts against it.

    `None` where it is undefined: too few photographs, or no spread between them at all.
    """
    if len(pairs) < FEWEST:
        return None
    n, k = pairs.shape
    msr, msc, mse = _mean_squares(pairs)
    denominator = msr + (k - 1) * mse + k * (msc - mse) / n
    return None if denominator <= 0 else float((msr - mse) / denominator)


def icc_consistency(pairs: np.ndarray) -> float | None:
    """ICC(C,1): two-way, consistency, one measurement — a constant offset is forgiven."""
    if len(pairs) < FEWEST:
        return None
    k = pairs.shape[1]
    msr, _msc, mse = _mean_squares(pairs)
    denominator = msr + (k - 1) * mse
    return None if denominator <= 0 else float((msr - mse) / denominator)


def signal_to_noise(pairs: np.ndarray) -> float | None:
    """How much eyes differ, over how much swapping the map moves the number.

    Signal is the standard deviation across photographs of the expert-map value; noise is the
    standard deviation of the paired difference, model minus expert, so a constant offset is not
    noise — it is reported as the bias instead. Infinite where the two maps agree exactly, `None`
    where there is no signal to speak of.
    """
    if len(pairs) < FEWEST:
        return None
    signal = float(np.std(pairs[:, 0], ddof=1))
    noise = float(np.std(pairs[:, 1] - pairs[:, 0], ddof=1))
    if signal == 0:
        return None
    return math.inf if noise == 0 else signal / noise


def summary(expert: Sequence[float | None], model: Sequence[float | None]) -> dict[str, object]:
    """Everything reported about one biomarker under one model, on the photographs given.

    Coverage is counted on its own and never folded into the statistics: `expert_only` and
    `model_only` are photographs where one map produced a value and the other did not.
    """
    pairs = paired(expert, model)
    has_expert = sum(e is not None and math.isfinite(float(e)) for e in expert)
    has_model = sum(m is not None and math.isfinite(float(m)) for m in model)
    n = len(pairs)
    found: dict[str, object] = {
        "n": n,
        "expert_only": has_expert - n,
        "model_only": has_model - n,
    }
    if n < FEWEST:
        return found
    difference = pairs[:, 1] - pairs[:, 0]
    expert_mean = float(pairs[:, 0].mean())
    bias = float(difference.mean())
    found |= {
        "expert_mean": expert_mean,
        "expert_sd": float(np.std(pairs[:, 0], ddof=1)),
        "model_mean": float(pairs[:, 1].mean()),
        "bias": bias,
        "relative_bias": bias / abs(expert_mean) if expert_mean else None,
        "sd_difference": float(np.std(difference, ddof=1)),
        "icc_agreement": icc_agreement(pairs),
        "icc_consistency": icc_consistency(pairs),
        "snr": signal_to_noise(pairs),
    }
    return found
