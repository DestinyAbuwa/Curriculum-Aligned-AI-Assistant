"""Describe each extracted figure with a vision model, caching results on disk.

Reads data/images.json and writes data/descriptions.json (image path -> description).
The file is rewritten after every successful call, so an interrupted run resumes where it
stopped.
"""

import base64
import json
import os

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from curriculum_aligned_ai_assistant.config import (
    DESCRIPTIONS_JSON,
    IMAGES_JSON,
    REPO_ROOT,
    Settings,
)
from curriculum_aligned_ai_assistant.ingest.image_index import DECORATIVE, ImageRecord, describe_all

PROMPT = (
    "You are indexing images from preclinical medical course materials so students can "
    "find them by search. Describe this image in 2 to 4 sentences: what it shows, any "
    "labels, axis titles and key text read exactly, and the concept it teaches. Describe "
    "only what is visible plus what the nearby text states. If nearby text from the same "
    "page is given, you may use it to identify what the image shows (for example that "
    "a diagram's caption on the slide names the structure it shows) and to read terms "
    "correctly. Read numbers, units and measurements exactly as printed on the image; if a "
    "figure is hard to read, say it is unclear instead of guessing. "
    "Never add a diagnosis or medical claim that neither the image nor the "
    "nearby text states. For an unlabeled medical image whose nearby text does not "
    "identify it, say it is unlabeled and describe its appearance; never speculate about a "
    "condition. "
    f"Reply with exactly {DECORATIVE} and nothing else for a decorative icon, logo, stock "
    "photo or other picture with no teaching content, or for a title or section slide "
    "that has no text beyond its title. A slide that contains a table, list, data or any "
    "informational text is NOT decorative: transcribe and describe it. A generic icon, "
    "silhouette or clip-art graphic is decorative even if the slide has a title or the "
    "nearby text asks a question about a topic."
)


def build_prompt(context: str) -> str:
    if not context.strip():
        return PROMPT
    return f"{PROMPT}\n\nText near the image on the same page:\n{context.strip()}"


def save(descriptions: dict[str, str]) -> None:
    temp = DESCRIPTIONS_JSON.with_suffix(".json.tmp")
    temp.write_text(json.dumps(descriptions, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(temp, DESCRIPTIONS_JSON)


def main() -> None:
    llm = ChatOpenAI(model=Settings.from_env().openai_model)
    records = [ImageRecord(**r) for r in json.loads(IMAGES_JSON.read_text(encoding="utf-8"))]
    cache: dict[str, str] = (
        json.loads(DESCRIPTIONS_JSON.read_text(encoding="utf-8"))
        if DESCRIPTIONS_JSON.exists()
        else {}
    )
    completed = dict(cache)
    contexts = {r.file: r.context for r in records}
    calls = 0

    def describe(path: str) -> str:
        nonlocal calls
        calls += 1
        encoded = base64.b64encode((REPO_ROOT / path).read_bytes()).decode()
        message = HumanMessage(
            content=[
                {"type": "text", "text": build_prompt(contexts.get(path, ""))},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded}"}},
            ]
        )
        try:
            reply = llm.invoke([message]).text.strip()
        except Exception as exc:
            raise RuntimeError(f"Vision call failed for {path}: {exc}") from exc
        if not reply:
            raise RuntimeError(f"Model returned an empty description for {path}")
        completed[path] = reply
        save(completed)
        print(f"[{calls}] described {path}", flush=True)
        return reply

    descriptions = describe_all(records, describe, cache)
    save(descriptions)
    decorative = sum(1 for text in descriptions.values() if text == DECORATIVE)
    print(
        f"{len(descriptions)} images: {len(descriptions) - decorative} described, "
        f"{decorative} {DECORATIVE}; {calls} model calls"
    )


if __name__ == "__main__":
    main()
