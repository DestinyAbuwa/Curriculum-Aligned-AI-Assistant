from typing import Protocol

from curriculum_aligned_ai_assistant.state import Chunk, WebResult


class Retriever(Protocol):
    def search(self, question: str, k: int) -> list[Chunk]: ...


class WebSearcher(Protocol):
    def search(self, question: str) -> list[WebResult]: ...


class Llm(Protocol):
    def invoke(self, prompt: str) -> str: ...
