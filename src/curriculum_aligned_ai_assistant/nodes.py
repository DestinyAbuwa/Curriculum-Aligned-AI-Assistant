import logging
import re
from typing import Literal

from curriculum_aligned_ai_assistant.messages import NOT_FOUND_MESSAGE, WEB_LABEL
from curriculum_aligned_ai_assistant.ports import Llm, Retriever, WebSearcher
from curriculum_aligned_ai_assistant.state import AgentState, Answer, Chunk, WebResult

logger = logging.getLogger(__name__)

NOT_FOUND_MARKER = "NOT_FOUND"
# Models sometimes append a note such as "**NOT_FOUND** (nothing more in the excerpts)" after a
# real answer. Drop the marker and the rest of its line, keep the answer before it.
_MARKER_TAIL = re.compile(rf"\*{{0,2}}{NOT_FOUND_MARKER}\*{{0,2}}.*$", re.IGNORECASE | re.MULTILINE)

GRADE_PROMPT = """You are checking whether course excerpts can answer a student's question.

Question: {question}

Excerpts:
{excerpts}

Do the excerpts contain the information needed to answer the question? Reply with only YES or NO."""

COURSE_PROMPT = """Answer the student's question using ONLY the course excerpts below.
Be concise and accurate. If the excerpts do not contain the answer, reply with exactly NOT_FOUND.

Question: {question}

Excerpts:
{excerpts}"""

WEB_PROMPT = """Answer the student's question using ONLY the web results below.
Be concise and accurate. If the results do not contain the answer, reply with exactly NOT_FOUND.

Question: {question}

Web results:
{results}"""


def format_excerpts(chunks: list[Chunk]) -> str:
    return "\n\n".join(
        f"[{i}] ({c.source} #{c.chunk_id})\n{'Figure: ' if c.image_path else ''}{c.text}"
        for i, c in enumerate(chunks, start=1)
    )


def returned_images(chunks: list[Chunk], max_distance: float, margin: float) -> tuple[str, ...]:
    """Image paths of retrieved image chunks to return with a course answer.

    An image chunk qualifies if its distance is at or below max_distance. Of those, only the ones
    within margin of the closest qualifying image are kept. Deduplicated, in retrieval order.
    """
    qualifying = [c for c in chunks if c.image_path and c.distance <= max_distance]
    if not qualifying:
        return ()
    cutoff = min(c.distance for c in qualifying) + margin
    paths = (c.image_path for c in qualifying if c.distance <= cutoff and c.image_path)
    return tuple(dict.fromkeys(paths))


def format_web_results(results: list[WebResult]) -> str:
    return "\n\n".join(
        f"[{i}] {r.title} ({r.url})\n{r.content}" for i, r in enumerate(results, start=1)
    )


def is_clear_yes(reply: str) -> bool:
    return reply.strip().strip("*`\"' ").upper().startswith("YES")


def usable_reply(reply: str) -> str | None:
    """The reply with any stray NOT_FOUND note removed, or None if there is no real answer."""
    if reply.strip().strip("*`\"' ").upper().startswith(NOT_FOUND_MARKER):
        return None
    return _MARKER_TAIL.sub("", reply).strip() or None


def _none_answer() -> AgentState:
    return {"answer": Answer(text=NOT_FOUND_MESSAGE, source_type="none", citations=[])}


class Nodes:
    def __init__(
        self,
        retriever: Retriever,
        web_searcher: WebSearcher | None,
        llm: Llm,
        k: int,
        max_distance: float,
        image_max_distance: float = 0.45,
        image_margin: float = 0.05,
    ) -> None:
        self._retriever = retriever
        self._web_searcher = web_searcher
        self._llm = llm
        self._k = k
        self._max_distance = max_distance
        self._image_max_distance = image_max_distance
        self._image_margin = image_margin

    def retrieve(self, state: AgentState) -> AgentState:
        return {"chunks": self._retriever.search(state["question"], self._k)}

    def grade(self, state: AgentState) -> AgentState:
        chunks = state.get("chunks", [])
        if not chunks or chunks[0].distance > self._max_distance:
            return {"relevant": False}
        prompt = GRADE_PROMPT.format(question=state["question"], excerpts=format_excerpts(chunks))
        return {"relevant": is_clear_yes(self._llm.invoke(prompt))}

    def web_search(self, state: AgentState) -> AgentState:
        if self._web_searcher is None:
            return {"web_results": []}
        try:
            return {"web_results": self._web_searcher.search(state["question"])}
        except Exception:
            logger.exception("Web search failed")
            return {"web_results": []}

    def generate(self, state: AgentState) -> AgentState:
        question = state["question"]
        if state.get("relevant"):
            chunks = state["chunks"]
            reply = self._llm.invoke(
                COURSE_PROMPT.format(question=question, excerpts=format_excerpts(chunks))
            )
            text = usable_reply(reply)
            if text is None:
                return _none_answer()
            citations = [f"{c.source} #{c.chunk_id}" for c in chunks]
            images = returned_images(chunks, self._image_max_distance, self._image_margin)
            return {
                "answer": Answer(
                    text=text, source_type="course", citations=citations, images=images
                )
            }

        results = state.get("web_results", [])
        if not results:
            return _none_answer()
        reply = self._llm.invoke(
            WEB_PROMPT.format(question=question, results=format_web_results(results))
        )
        text = usable_reply(reply)
        if text is None:
            return _none_answer()
        return {
            "answer": Answer(
                text=f"{WEB_LABEL}\n\n{text}",
                source_type="web",
                citations=[r.url for r in results],
            )
        }


def route_after_grade(state: AgentState) -> Literal["generate", "web_search"]:
    return "generate" if state.get("relevant") else "web_search"
