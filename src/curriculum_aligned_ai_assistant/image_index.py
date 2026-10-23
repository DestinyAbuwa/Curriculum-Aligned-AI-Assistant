"""Pure helpers for building image chunks and index-time text cleaning."""

import re
from collections import defaultdict
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass

MIN_SIDE_PX = 150
DECORATIVE = "DECORATIVE"
IMAGE_MARKER = "<!-- image -->"
CONTEXT_CHARS = 600

_BLANK_RUNS = re.compile(r"\n\s*\n+")


@dataclass(frozen=True)
class ImageRecord:
    source: str
    page: int
    heading: str
    caption: str
    file: str  # image path relative to the repo root, forward slashes
    context: str = ""  # same-page slide text around the picture


@dataclass(frozen=True)
class IndexedChunk:
    id: str
    text: str
    metadata: dict[str, str | int]


def is_usable_size(width: int, height: int, min_side: int = MIN_SIDE_PX) -> bool:
    return min(width, height) >= min_side


def _nearest_first(items: Sequence[str], max_chars: int) -> list[str]:
    """Keep whole items from the front of `items` while they fit; cut the first if too long."""
    kept: list[str] = []
    used = 0
    for item in items:
        text = item.strip()
        if not text:
            continue
        if not kept and len(text) > max_chars:
            return [text[:max_chars]]
        if used + len(text) > max_chars:
            break
        kept.append(text)
        used += len(text)
    return kept


def build_context(
    before: Sequence[str], after: Sequence[str], max_chars_each: int = CONTEXT_CHARS
) -> str:
    """Join the text just before and just after a picture, nearest items first within budget.

    `before` is in document order (nearest last); `after` is in document order (nearest first).
    """
    before_part = "\n".join(reversed(_nearest_first(list(reversed(before)), max_chars_each)))
    after_part = "\n".join(_nearest_first(after, max_chars_each))
    return "\n".join(p for p in (before_part, after_part) if p).strip()


def describe_all(
    records: Sequence[ImageRecord],
    describe: Callable[[str], str],
    cache: Mapping[str, str],
) -> dict[str, str]:
    """Describe every record, calling the model only for files missing from the cache."""
    result: dict[str, str] = {}
    for record in records:
        if record.file in cache:
            result[record.file] = cache[record.file]
        elif record.file not in result:
            result[record.file] = describe(record.file)
    return result


def build_image_chunks(
    records: Sequence[ImageRecord], descriptions: Mapping[str, str]
) -> list[IndexedChunk]:
    counters: defaultdict[tuple[str, int], int] = defaultdict(int)
    chunks: list[IndexedChunk] = []
    for record in records:
        description = descriptions.get(record.file, "").strip()
        if not description or description == DECORATIVE:
            continue
        key = (record.source, record.page)
        n = counters[key]
        counters[key] += 1
        chunk_id = f"fig-p{record.page}-{n}"
        parts = [p.strip() for p in (record.heading, record.caption, description)]
        chunks.append(
            IndexedChunk(
                id=f"{record.source}_{chunk_id}",
                text="\n".join(p for p in parts if p),
                metadata={
                    "source": record.source,
                    "chunk_id": chunk_id,
                    "kind": "image",
                    "image_path": record.file,
                },
            )
        )
    return chunks


def clean_semantic_text(text: str) -> str:
    without_markers = text.replace(IMAGE_MARKER, "")
    return _BLANK_RUNS.sub("\n\n", without_markers).strip()


def text_chunks_for_index(
    chunks: Sequence[Mapping[str, object]], source: str, clean: bool
) -> list[IndexedChunk]:
    result: list[IndexedChunk] = []
    for chunk in chunks:
        raw = str(chunk["text"])
        text = clean_semantic_text(raw) if clean else raw.strip()
        if not text:
            continue
        chunk_id = chunk["id"]
        assert isinstance(chunk_id, int)
        result.append(
            IndexedChunk(
                id=f"{source}_{chunk_id}",
                text=text,
                metadata={"source": source, "chunk_id": chunk_id, "kind": "text"},
            )
        )
    return result
