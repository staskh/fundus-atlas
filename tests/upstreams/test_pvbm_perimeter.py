# ABOUTME: Tests for the PVBM upstream: that the four lines transcribed out of its deprecated
# ABOUTME: analysis class still compute what that class computed.

import pytest


def test_the_transcribed_perimeter_matches_the_class_it_replaced() -> None:
    """`GeometryAnalysis` exposes no perimeter, so four lines of the deprecated class live in
    `upstreams.pvbm.perimeter`. A transcription that drifts from its original is worse than none,
    so this runs both and requires them to agree.

    The deprecated class is imported **here and nowhere else**: a test may touch it to prove an
    equivalence, and the adapter may not, because constructing it warns that it goes in version 3.0
    and the point of the transcription is not to construct it.
    """
    import warnings

    import numpy as np

    from upstreams import pvbm

    mask = np.zeros((128, 128), dtype=np.float64)
    mask[30:60, 20:100] = 1.0  # a bar
    mask[70:78, 40:90] = 1.0  # and a thinner one, so the border is not one rectangle

    ours, outline = pvbm.perimeter(mask)

    pvbm.CODE.on_path()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        from PVBM.GeometricalAnalysis import GeometricalVBMs as Deprecated

        theirs, their_outline = Deprecated().compute_perimeter(mask.copy())

    assert ours == pytest.approx(theirs), "the transcription no longer matches what it replaced"
    assert np.array_equal(outline, their_outline), "and the border it returns must match too"
    assert mask.sum() == 30 * 80 + 8 * 50, "the mask must survive: the helper empties what it walks"
