"""`uv run --group ingest ingest [step ...]`: run the pipeline steps in order.

With no steps, runs all of them. `describe` calls the OpenAI API only for images that are not
already in data/descriptions.json.
"""

import argparse
from collections.abc import Callable, Sequence

STEPS = ("chunk", "extract", "describe", "index")


def _chunk() -> None:
    from curriculum_aligned_ai_assistant.ingest.chunking import chunk_all

    chunk_all()


def _extract() -> None:
    from curriculum_aligned_ai_assistant.ingest.extract_images import main

    main()


def _describe() -> None:
    from curriculum_aligned_ai_assistant.ingest.describe_images import main

    main()


def _index() -> None:
    from curriculum_aligned_ai_assistant.ingest.indexing import build_all

    build_all()


# Imported per step so `index` and `describe` work without the Docling `ingest` group installed.
RUNNERS: dict[str, Callable[[], None]] = {
    "chunk": _chunk,
    "extract": _extract,
    "describe": _describe,
    "index": _index,
}


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="ingest", description=__doc__)
    parser.add_argument("steps", nargs="*", choices=STEPS, metavar="step", help=", ".join(STEPS))
    selected = set(parser.parse_args(argv).steps or STEPS)
    for step in STEPS:
        if step in selected:
            print(f"== {step}", flush=True)
            RUNNERS[step]()
