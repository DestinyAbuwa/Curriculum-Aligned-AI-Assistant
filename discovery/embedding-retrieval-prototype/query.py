from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

BASE_DIR = Path(__file__).parent

model = SentenceTransformer("BAAI/bge-m3", device="cpu")
client = chromadb.PersistentClient(path=str(BASE_DIR / "chroma_db"))

# Grounded in the sample PDFs: each question's answer is known to sit in a
# specific part of the source doc, so we can eyeball whether retrieval found it.
QUESTIONS = [
    "What is the mechanism of action of SGLT2 inhibitors?",
    "What does the GFR mnemonic help remember in adrenal gland anatomy?",
    "What mediates most of the actions of growth hormone on bone growth?",
]


def run() -> None:
    semantic = client.get_collection("semantic_chunks")
    hybrid = client.get_collection("hybrid_chunks")

    for question in QUESTIONS:
        q_embedding = model.encode([question], normalize_embeddings=True).tolist()
        print(f"\n{'=' * 80}\nQ: {question}\n{'=' * 80}")

        for name, collection in [("SEMANTIC", semantic), ("HYBRID", hybrid)]:
            results = collection.query(query_embeddings=q_embedding, n_results=3)
            print(f"\n--- {name} chunker: top 3 ---")
            docs = results["documents"][0]
            metas = results["metadatas"][0]
            dists = results["distances"][0]
            for rank, (doc, meta, dist) in enumerate(zip(docs, metas, dists), start=1):
                snippet = doc[:220].replace("\n", " ")
                print(f"[{rank}] (dist={dist:.4f}) {meta['source']} #{meta['chunk_id']}: {snippet}...")


if __name__ == "__main__":
    run()
