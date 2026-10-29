"""Build the four Chroma collections the agent searches.

- `semantic_chunks` / `hybrid_chunks`: the text chunks from one chunker.
- `semantic_images` / `hybrid_images`: the same text chunks plus every image chunk (built from
  images.json and descriptions.json), so one search covers both. Semantic text is cleaned of
  Docling's image markers here; the `*_chunks` collections keep it as written.

Each collection is deleted and recreated, which makes reruns safe.
"""

import json
from pathlib import Path

import chromadb
from chromadb.api import ClientAPI
from sentence_transformers import SentenceTransformer

from curriculum_aligned_ai_assistant.config import (
    CHUNKS_DIR,
    DEFAULT_CHROMA_PATH,
    DESCRIPTIONS_JSON,
    EMBEDDING_MODEL,
    IMAGES_JSON,
)
from curriculum_aligned_ai_assistant.ingest.image_index import (
    ImageRecord,
    IndexedChunk,
    build_image_chunks,
    text_chunks_for_index,
)


def load_image_chunks() -> list[IndexedChunk]:
    records = [ImageRecord(**r) for r in json.loads(IMAGES_JSON.read_text(encoding="utf-8"))]
    descriptions: dict[str, str] = json.loads(DESCRIPTIONS_JSON.read_text(encoding="utf-8"))
    return build_image_chunks(records, descriptions)


def load_text_chunks(results_dir: Path, suffix: str, clean: bool) -> list[IndexedChunk]:
    chunks: list[IndexedChunk] = []
    for json_path in sorted(results_dir.glob(f"*_{suffix}.json")):
        source = json_path.stem.removesuffix(f"_{suffix}")
        raw = json.loads(json_path.read_text(encoding="utf-8"))
        chunks.extend(text_chunks_for_index(raw, source, clean))
    return chunks


def build_collection(
    client: ClientAPI,
    model: SentenceTransformer,
    name: str,
    chunks: list[IndexedChunk],
) -> None:
    if name in [c.name for c in client.list_collections()]:
        client.delete_collection(name)
    collection = client.create_collection(name=name, metadata={"hnsw:space": "cosine"})

    documents = [c.text for c in chunks]
    embeddings = model.encode(documents, normalize_embeddings=True, show_progress_bar=True).tolist()
    collection.add(
        ids=[c.id for c in chunks],
        documents=documents,
        metadatas=[dict(c.metadata) for c in chunks],
        embeddings=embeddings,
    )
    images = sum(1 for c in chunks if c.metadata.get("kind") == "image")
    print(f"{name}: {len(chunks) - images} text chunks + {images} image chunks")


def build_all(chroma_path: Path = DEFAULT_CHROMA_PATH) -> None:
    model = SentenceTransformer(EMBEDDING_MODEL, device="cpu")
    client = chromadb.PersistentClient(path=str(chroma_path))
    image_chunks = load_image_chunks()
    for kind in ("semantic", "hybrid"):
        results_dir = CHUNKS_DIR / kind
        build_collection(
            client, model, f"{kind}_chunks", load_text_chunks(results_dir, kind, clean=False)
        )
        build_collection(
            client,
            model,
            f"{kind}_images",
            load_text_chunks(results_dir, kind, clean=kind == "semantic") + image_chunks,
        )
