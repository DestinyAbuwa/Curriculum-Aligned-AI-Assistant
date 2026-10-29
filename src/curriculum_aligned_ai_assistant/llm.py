import re
from functools import lru_cache
from typing import Any

from langchain_openai import ChatOpenAI

from curriculum_aligned_ai_assistant.config import Settings
from curriculum_aligned_ai_assistant.errors import AgentStartupError, LlmUnavailableError
from curriculum_aligned_ai_assistant.ports import Llm

# Measured MedGemma 4B answers top out around 750 tokens (5 NBME questions with explanations);
# 2048 leaves room for longer requests and stops a repetition loop after ~35 s on an M2 Pro.
MLX_MAX_TOKENS = 2048


@lru_cache(maxsize=2)
def _load_mlx_model(model_id: str) -> tuple[Any, Any]:
    from mlx_vlm import load

    return load(model_id)


class MlxLlm:
    """Run MedGemma locally through MLX-VLM on Apple Silicon."""

    def __init__(
        self, model_id: str, model: Any | None = None, processor: Any | None = None
    ) -> None:
        self._model_id = model_id
        if model is None or processor is None:
            try:
                model, processor = _load_mlx_model(model_id)
            except Exception as exc:
                raise AgentStartupError(
                    f"Could not load MLX model '{model_id}'. Install the Apple Silicon MLX "
                    "dependencies with `uv sync`; confirm Hugging Face access to MedGemma and "
                    "set HF_TOKEN if prompted."
                ) from exc
        self._model = model
        self._processor = processor

    def invoke(self, prompt: str) -> str:
        try:
            from mlx_vlm import generate
            from mlx_vlm.prompt_utils import apply_chat_template

            formatted_prompt = apply_chat_template(
                self._processor,
                self._model.config,
                prompt,
                num_images=0,
            )
            result = generate(
                self._model,
                self._processor,
                formatted_prompt,
                max_tokens=MLX_MAX_TOKENS,
                temperature=0.0,
                verbose=False,
            )
        except Exception as exc:
            raise LlmUnavailableError(
                f"Could not get a reply from MLX model '{self._model_id}'. "
                "Check that this Mac has Apple Silicon and enough memory for MedGemma."
            ) from exc
        content = getattr(result, "text", result)
        return content.strip() if isinstance(content, str) else ""


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
    """Build the language model chosen by LLM_PROVIDER."""
    if settings.llm_provider == "mlx":
        return MlxLlm(settings.mlx_model)
    if settings.llm_provider == "openai":
        if not settings.openai_api_key:
            raise AgentStartupError(
                "LLM_PROVIDER is 'openai' but OPENAI_API_KEY is not set. Add it to .env."
            )
        return OpenAiLlm(settings.openai_model, api_key=settings.openai_api_key)
    raise AgentStartupError(
        f"LLM_PROVIDER '{settings.llm_provider}' is not recognised. Use 'mlx' or 'openai'."
    )
