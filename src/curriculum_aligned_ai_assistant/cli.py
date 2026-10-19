from collections.abc import Callable

from curriculum_aligned_ai_assistant.bootstrap import build_agent
from curriculum_aligned_ai_assistant.errors import AgentStartupError, LlmUnavailableError

QUIT_WORDS = {"quit", "exit"}


def run_cli(
    collection_name: str,
    input_fn: Callable[[str], str] = input,
    output_fn: Callable[[str], None] = print,
) -> int:
    try:
        graph, warnings = build_agent(collection_name)
    except AgentStartupError as exc:
        output_fn(f"Cannot start: {exc}")
        return 1
    for warning in warnings:
        output_fn(f"Warning: {warning}")
    output_fn(f"Ask about your course materials ({collection_name}). Type 'quit' to stop.")

    while True:
        question = input_fn("\n> ").strip()
        if not question:
            continue
        if question.lower() in QUIT_WORDS:
            return 0
        try:
            answer = graph.invoke({"question": question})["answer"]
        except LlmUnavailableError as exc:
            output_fn(str(exc))
            continue
        output_fn(f"\n[{answer.source_type}] {answer.text}")
        if answer.citations:
            output_fn("Sources:")
            for citation in answer.citations:
                output_fn(f"  - {citation}")
