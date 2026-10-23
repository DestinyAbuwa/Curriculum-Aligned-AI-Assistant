import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Self

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CHROMA_PATH = REPO_ROOT / "discovery" / "embedding-retrieval-prototype" / "chroma_db"


@dataclass(frozen=True)
class Settings:
    chroma_path: Path = DEFAULT_CHROMA_PATH
    llm_provider: str = "openai"
    ollama_model: str = "qwen3:8b"
    openai_model: str = "gpt-6-luna"
    openai_api_key: str | None = None
    tavily_api_key: str | None = None
    retrieval_k: int = 5
    max_distance: float = 0.50
    image_max_distance: float = 0.45
    image_margin: float = 0.05

    @classmethod
    def from_env(cls, environ: Mapping[str, str] | None = None) -> Self:
        if environ is None:
            load_dotenv()
            environ = os.environ
        retrieval_k = int(environ.get("RETRIEVAL_K", "5"))
        if retrieval_k < 1:
            raise ValueError("RETRIEVAL_K must be at least 1")
        tavily_key = (environ.get("TAVILY_API_KEY") or "").strip() or None
        openai_key = (environ.get("OPENAI_API_KEY") or "").strip() or None
        chroma_path = environ.get("CHROMA_PATH")
        return cls(
            chroma_path=Path(chroma_path) if chroma_path else DEFAULT_CHROMA_PATH,
            llm_provider=(environ.get("LLM_PROVIDER") or "openai").strip().lower(),
            ollama_model=environ.get("OLLAMA_MODEL") or "qwen3:8b",
            openai_model=environ.get("OPENAI_MODEL") or "gpt-6-luna",
            openai_api_key=openai_key,
            tavily_api_key=tavily_key,
            retrieval_k=retrieval_k,
            max_distance=float(environ.get("MAX_DISTANCE", "0.50")),
            image_max_distance=float(environ.get("IMAGE_MAX_DISTANCE", "0.45")),
            image_margin=float(environ.get("IMAGE_MARGIN", "0.05")),
        )
