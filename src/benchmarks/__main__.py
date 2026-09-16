# ABOUTME: The one command every benchmark is run from: `python -m benchmarks --benchmark <name>`.
# ABOUTME: One entry point, so that running a new benchmark needs no new instructions.

import argparse
import importlib
from argparse import Namespace

#: The benchmarks that exist, by the name they are known by everywhere else — in `results/`, in
#: `docs/benchmarks/`, and in the module that implements them.
BENCHMARKS = ("quality", "disc")


def parse(argv: list[str] | None = None) -> Namespace:
    """Read the command line."""
    parser = argparse.ArgumentParser(
        prog="python -m benchmarks",
        description="Score catalogued models against what experts annotated.",
    )
    parser.add_argument(
        "--benchmark", required=True, choices=BENCHMARKS, help="which benchmark to run"
    )
    parser.add_argument("--model", help="one model slug, or several separated by commas")
    parser.add_argument("--dataset", help="one dataset slug, or several separated by commas")
    parser.add_argument("--device", help="cuda, mps or cpu; the fastest available by default")
    parser.add_argument("--batch", type=int, help="how many photographs go to the model at once")
    parser.add_argument(
        "--max-samples",
        type=int,
        help="score at most this many photographs of each dataset, for a development run",
    )
    parser.add_argument(
        "--random-samples",
        action="store_true",
        help="choose those photographs at random rather than taking the first of the manifest",
    )
    parser.add_argument("--seed", type=int, default=0, help="the seed a random sample uses")
    parser.add_argument("--data-root", help="override the store root")
    parser.add_argument(
        "--force", action="store_true", help="discard what is stored and measure it all again"
    )
    parser.add_argument(
        "--no-report", dest="report", action="store_false", help="skip the generated documents"
    )
    return parser.parse_args(argv)


def named(value: str | None) -> list[str] | None:
    """One name, or several separated by commas, or nothing at all."""
    if not value:
        return None
    return [name.strip() for name in value.split(",") if name.strip()]


def main(argv: list[str] | None = None) -> None:
    asked = parse(argv)
    benchmark = importlib.import_module(f"benchmarks.{asked.benchmark}")
    benchmark.main(asked)


if __name__ == "__main__":
    main()
