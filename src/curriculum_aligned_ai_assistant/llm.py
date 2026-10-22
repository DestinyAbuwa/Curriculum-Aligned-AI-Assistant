import re
from typing import Any

from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

from curriculum_aligned_ai_assistant.config import Settings
from curriculum_aligned_ai_assistant.errors import AgentStartupError, LlmUnavailableError
from curriculum_aligned_ai_assistant.ports import Llm

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


class OpenAiLlm:
    def __init__(self, model: str, api_key: str | None = None, client: Any | None = None) -> None:
        self._model = model
        # No temperature is sent: some OpenAI models reject anything but their default.
        self._client = (
            client if client is not None else ChatOpenAI(model=model, api_key=api_key)  # type: ignore[arg-type]
        )

    def invoke(self, prompt: str) -> str:
        try:
            message = self._client.invoke(prompt)
        except Exception as exc:  # any failure talking to the API is reported the same way
            raise LlmUnavailableError(
                f"Could not get a reply from OpenAI model '{self._model}'. "
                "Check OPENAI_API_KEY, OPENAI_MODEL and your internet connection."
            ) from exc
        content = message.content
        return content.strip() if isinstance(content, str) else ""


def make_llm(settings: Settings) -> Llm:
    """Build the language model chosen by LLM_PROVIDER (local Ollama by default)."""
    if settings.llm_provider == "ollama":
        return OllamaLlm(settings.ollama_model)
    if settings.llm_provider == "openai":
        if not settings.openai_api_key:
            raise AgentStartupError(
                "LLM_PROVIDER is 'openai' but OPENAI_API_KEY is not set. Add it to .env."
            )
        return OpenAiLlm(settings.openai_model, api_key=settings.openai_api_key)
    raise AgentStartupError(
        f"LLM_PROVIDER '{settings.llm_provider}' is not recognised. Use 'ollama' or 'openai'."
    )
