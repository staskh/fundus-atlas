# ABOUTME: Which processor a model runs on, chosen once so every adapter answers the same way.
# ABOUTME: Recorded in the run, because a number produced on one is not always bit-identical.

import gc

import torch


def pick(preferred: str | None = None) -> str:
    """The fastest processor available, or the one asked for."""
    if preferred:
        return preferred
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def forget() -> None:
    """Give back whatever a model left on the processor, once nothing needs it."""
    gc.collect()
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
