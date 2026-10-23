"""Build the `semantic_images` and `hybrid_images` Chroma collections.

Each collection holds a copy of the text chunks from one chunker plus every image
chunk (built from images.json and descriptions.json), so one search covers both.
The existing `semantic_chunks` and `hybrid_chunks` collections are not touched; only
the two collections created here are deleted and recreated, which makes reruns safe.
"""

import json
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

from curriculum_aligned_ai_assistant.image_index import (
    ImageRecord,
    IndexedChunk,
    build_image_chunks,
    text_chunks_for_index,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
IMAGE_DIR = REPO_ROOT / "discovery" / "image-parsing"
CHUNKING_DIR = REPO_ROOT / "discovery" / "chunking-methods"
CHROMA_PATH = REPO_ROOT / "discovery" / "embedding-retrieval-prototype" / "chroma_db"


def load_image_chunks() -> list[IndexedChunk]:
    records = [
        ImageRecord(**r)
        for r in json.loads((IMAGE_DIR / "images.json").read_text(encoding="utf-8"))
    ]
    descriptions: dict[str, str] = json.loads(
        (IMAGE_DIR / "descriptions.json").read_text(encoding="utf-8")
    )
    return build_image_chunks(records, descriptions)


def load_text_chunks(results_dir: Path, suffix: str, clean: bool) -> list[IndexedChunk]:
    chunks: list[IndexedChunk] = []
    for json_path in sorted(results_dir.glob(f"*_{suffix}.json")):
        source = json_path.stem.removesuffix(f"_{suffix}")
        raw = json.loads(json_path.read_text(encoding="utf-8"))
        chunks.extend(text_chunks_for_index(raw, source, clean))
    return chunks


def build_collection(
    client: chromadb.ClientAPI,
    model: SentenceTransformer,
    name: str,
    text_chunks: list[IndexedChunk],
    image_chunks: list[IndexedChunk],
) -> None:
    if name in [c.name for c in client.list_collections()]:
        client.delete_collection(name)
    collection = client.create_collection(name=name, metadata={"hnsw:space": "cosine"})

    chunks = text_chunks + image_chunks
    documents = [c.text for c in chunks]
    embeddings = model.encode(documents, normalize_embeddings=True, show_progress_bar=True).tolist()
    collection.add(
        ids=[c.id for c in chunks],
        documents=documents,
        metadatas=[dict(c.metadata) for c in chunks],
        embeddings=embeddings,
    )
    print(f"{name}: {len(text_chunks)} text chunks + {len(image_chunks)} image chunks")


def main() -> None:
    model = SentenceTransformer("BAAI/bge-m3", device="cpu")
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    image_chunks = load_image_chunks()
    build_collection(
        client,
        model,
        "semantic_images",
        load_text_chunks(CHUNKING_DIR / "semanticresults", "semantic", clean=True),
        image_chunks,
    )
    build_collection(
        client,
        model,
        "hybrid_images",
        load_text_chunks(CHUNKING_DIR / "hybridresults", "hybrid", clean=False),
        image_chunks,
    )


if __name__ == "__main__":
    main()
