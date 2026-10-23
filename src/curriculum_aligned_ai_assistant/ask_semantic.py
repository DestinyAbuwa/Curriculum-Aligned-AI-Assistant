import sys

from curriculum_aligned_ai_assistant.cli import collection_for, run_cli


def main() -> None:
    raise SystemExit(run_cli(collection_for("semantic", sys.argv[1:])))
