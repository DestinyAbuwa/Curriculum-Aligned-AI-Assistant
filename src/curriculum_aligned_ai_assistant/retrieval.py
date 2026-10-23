from collections.abc import Callable, Mapping, Sequence
from functools import cache

import chromadb
from chromadb.api.models.Collection import Collection
from sentence_transformers import SentenceTransformer

from curriculum_aligned_ai_assistant.config import Settings
from curriculum_aligned_ai_assistant.errors import AgentStartupError
from curriculum_aligned_ai_assistant.state import Chunk

Embedder = Callable[[str], list[float]]


def _image_path(metadata: Mapping[str, object]) -> str | None:
    path = metadata.get("image_path")
    if metadata.get("kind") == "image" and isinstance(path, str) and path:
        return path
    return None


class ChromaRetriever:
    def __init__(self, collection: Collection, embed: Embedder) -> None:
        self._collection = collection
        self._embed = embed

    def search(self, question: str, k: int) -> list[Chunk]:
        query: list[Sequence[float] | Sequence[int]] = [self._embed(question)]
        result = self._collection.query(query_embeddings=query, n_results=k)
        documents = (result["documents"] or [[]])[0]
        metadatas = (result["metadatas"] or [[]])[0]
        distances = (result["distances"] or [[]])[0]
        return [
            Chunk(
                text=document,
                source=str(metadata["source"]),
                chunk_id=str(metadata["chunk_id"]),
                distance=float(distance),
                image_path=_image_path(metadata),
            )
            for document, metadata, distance in zip(documents, metadatas, distances, strict=True)
        ]


@cache
def _load_model(model_name: str) -> SentenceTransformer:
    return SentenceTransformer(model_name, device="cpu")


def open_retriever(
    settings: Settings, collection_name: str, model_name: str = "BAAI/bge-m3"
) -> ChromaRetriever:
    script = (
        "discovery/image-parsing/build_image_index.py"
        if collection_name.endswith("_images")
        else "discovery/embedding-retrieval-prototype/build_index.py"
    )
    rebuild_hint = f"Build it with {script}."
    if not settings.chroma_path.exists():
        raise AgentStartupError(f"No Chroma index at {settings.chroma_path}. {rebuild_hint}")
    client = chromadb.PersistentClient(path=str(settings.chroma_path))
    try:
        collection = client.get_collection(collection_name)
    except Exception as exc:  # chromadb raises different error types across versions
        raise AgentStartupError(
            f"Collection '{collection_name}' not found in {settings.chroma_path}. {rebuild_hint}"
        ) from exc
    if collection.count() == 0:
        raise AgentStartupError(
            f"Collection '{collection_name}' in {settings.chroma_path} is empty. {rebuild_hint}"
        )

    def embed(text: str) -> list[float]:
        vector = _load_model(model_name).encode([text], normalize_embeddings=True)[0]
        return [float(x) for x in vector]

    return ChromaRetriever(collection, embed)
