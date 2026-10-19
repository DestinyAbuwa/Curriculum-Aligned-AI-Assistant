import re
from typing import Any

from langchain_ollama import ChatOllama

from curriculum_aligned_ai_assistant.errors import LlmUnavailableError

_CLOSED_THINK = re.compile(r"<think>.*?</think>", re.DOTALL)
_OPEN_THINK = re.compile(r"<think>.*\Z", re.DOTALL)


def strip_thinking(text: str) -> str:
    """Remove Qwen3 reasoning blocks, including one that was cut off before closing."""
    text = _CLOSED_THINK.sub("", text)
    text = _OPEN_THINK.sub("", text)
    return text.strip()


class OllamaLlm:
    def __init__(self, model: str, client: Any | None = None) -> None:
        self._model = model
        self._client = client if client is not None else ChatOllama(model=model, temperature=0)

    def invoke(self, prompt: str) -> str:
        try:
            message = self._client.invoke(prompt)
        except Exception as exc:  # any failure talking to Ollama is reported the same way
            raise LlmUnavailableError(
                f"Could not get a reply from Ollama model '{self._model}'. "
                "Start the server with `ollama serve` and check `ollama list` for the model."
            ) from exc
        content = message.content
        return strip_thinking(content) if isinstance(content, str) else ""
