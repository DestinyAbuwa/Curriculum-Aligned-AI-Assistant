from dataclasses import dataclass
from typing import Literal, TypedDict

SourceType = Literal["course", "web", "none"]


@dataclass(frozen=True)
class Chunk:
    text: str
    source: str
    chunk_id: str
    distance: float
    image_path: str | None = None


@dataclass(frozen=True)
class WebResult:
    title: str
    url: str
    content: str


@dataclass(frozen=True)
class Answer:
    text: str
    source_type: SourceType
    citations: list[str]
    images: tuple[str, ...] = ()


class AgentState(TypedDict, total=False):
    question: str
    chunks: list[Chunk]
    relevant: bool
    course_answer: str
    web_results: list[WebResult]
    answer: Answer
