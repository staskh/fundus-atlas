# ABOUTME: Tests that AutoMorph's stages are declared as this atlas reads them — the vessel
# ABOUTME: ensemble's ten seeds, and the single checkpoint each of them is.

from upstreams import automorph


def test_every_stage_this_atlas_reads_is_checked_out() -> None:
    """A stage left out of the subtrees is a stage whose weights are silently absent."""
    for stage in (
        automorph.QUALITY_STAGE,
        automorph.DISC_STAGE,
        automorph.AV_STAGE,
        automorph.VESSEL_STAGE,
    ):
        assert stage in automorph.CODE.subtrees


def test_the_vessel_ensemble_is_ten_seeds_of_one_training_set() -> None:
    """Ten random seeds, two apart, all trained on the set AutoMorph calls ALL-SIX."""
    assert automorph.VESSEL_SEEDS == tuple(range(24, 44, 2))
    assert len(automorph.VESSEL_SEEDS) == 10
    assert "ALL-SIX" in automorph.VESSEL_WEIGHTS


def test_a_vessel_seed_folder_is_named_for_its_seed() -> None:
    """The folder name carries the seed, so a missing seed is a missing folder rather than a
    silently shorter ensemble."""
    named = automorph.vessel_folder(24)
    assert named.endswith("randomseed_24")
    assert automorph.VESSEL_WEIGHTS in named
