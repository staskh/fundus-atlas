# ABOUTME: Which processor a model runs on, chosen once so every adapter answers the same way.
# ABOUTME: Recorded in the run, because a number produced on one is not always bit-identical.

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
