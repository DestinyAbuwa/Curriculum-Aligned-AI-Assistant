import json
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

BASE_DIR = Path(__file__).parent
CHUNKING_DIR = BASE_DIR.parent / "chunking-methods"

model = SentenceTransformer("BAAI/bge-m3", device="cpu")
client = chromadb.PersistentClient(path=str(BASE_DIR / "chroma_db"))


def build_collection(name: str, results_dir: Path, suffix: str) -> None:
    collection = client.get_or_create_collection(name=name, metadata={"hnsw:space": "cosine"})
    if collection.count():
        collection.delete(ids=collection.get()["ids"])

    ids: list[str] = []
    documents: list[str] = []
    metadatas: list[dict] = []

    json_paths = sorted(results_dir.glob(f"*{suffix}.json"))
    for json_path in json_paths:
        source = json_path.stem.removesuffix(f"_{suffix}")
        chunks = json.loads(json_path.read_text(encoding="utf-8"))
        for chunk in chunks:
            text = chunk["text"].strip()
            if not text:
                continue
            ids.append(f"{source}_{chunk['id']}")
            documents.append(text)
            metadatas.append({"source": source, "chunk_id": chunk["id"]})

    embeddings = model.encode(documents, normalize_embeddings=True, show_progress_bar=True).tolist()
    collection.add(ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings)
    print(f"{name}: indexed {len(ids)} chunks from {len(json_paths)} documents")


if __name__ == "__main__":
    build_collection("semantic_chunks", CHUNKING_DIR / "semanticresults", "semantic")
    build_collection("hybrid_chunks", CHUNKING_DIR / "hybridresults", "hybrid")
