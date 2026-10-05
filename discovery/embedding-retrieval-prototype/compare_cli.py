from pathlib import Path

import chromadb
import ollama
from sentence_transformers import SentenceTransformer

BASE_DIR = Path(__file__).parent
TOP_K = 3
WIDTH = 88
LLM_MODEL = "qwen3:8b"

SYSTEM_PROMPT = (
    "You are a study assistant for preclinical medical students. Answer the "
    "student's question using ONLY the provided context below, as a clean, "
    "natural answer a student would actually want to read. Do not mention "
    "chunks, sources, or where the information came from — just answer the "
    "question directly, as if you already know it. If the context does not "
    "contain enough information to answer, say so explicitly rather than "
    "guessing or using outside knowledge."
)

print("Loading embedding model (bge-m3)...")
model = SentenceTransformer("BAAI/bge-m3", device="cpu")
client = chromadb.PersistentClient(path=str(BASE_DIR / "chroma_db"))
semantic = client.get_collection("semantic_chunks")
hybrid = client.get_collection("hybrid_chunks")


def print_results(label: str, results: dict) -> None:
    print(f"\n--- {label}: retrieved chunks (top {TOP_K}) ---")
    docs = results["documents"][0]
    metas = results["metadatas"][0]
    dists = results["distances"][0]
    if not docs:
        print("  (no results)")
        return
    for rank, (doc, meta, dist) in enumerate(zip(docs, metas, dists), start=1):
        similarity = 1 - dist
        print(f"\n[{rank}] similarity={similarity:.3f}  source={meta['source']}  chunk#{meta['chunk_id']}")
        print("-" * WIDTH)
        print(doc.strip())
    print()


def build_context(results: dict) -> str:
    # Deliberately unlabeled (no "Chunk N" markers) so the model has nothing
    # chunk-shaped to echo back in its answer — see print_results() for the
    # labeled view used to inspect what was actually retrieved.
    docs = results["documents"][0]
    return "\n\n---\n\n".join(doc.strip() for doc in docs)


def generate_answer(question: str, results: dict) -> str:
    context = build_context(results)
    if not context:
        return "(no retrieved context to answer from)"
    user_prompt = f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer using only the context above."
    response = ollama.chat(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response["message"]["content"].strip()


def print_generated(label: str, answer: str) -> None:
    print(f"\n--- {label}: generated answer ({LLM_MODEL}) ---")
    print(answer)
    print()


def ask(question: str) -> None:
    q_embedding = model.encode([question], normalize_embeddings=True).tolist()
    semantic_results = semantic.query(query_embeddings=q_embedding, n_results=TOP_K)
    hybrid_results = hybrid.query(query_embeddings=q_embedding, n_results=TOP_K)

    print("\n" + "=" * WIDTH)
    print(f"Q: {question}")
    print("=" * WIDTH)

    print_results("SEMANTIC CHUNKER", semantic_results)
    print_results("HYBRID CHUNKER", hybrid_results)

    print("Generating answers...")
    semantic_answer = generate_answer(question, semantic_results)
    hybrid_answer = generate_answer(question, hybrid_results)

    print("\n" + "=" * WIDTH)
    print("GENERATED ANSWERS")
    print("=" * WIDTH)
    print_generated("SEMANTIC CHUNKER", semantic_answer)
    print_generated("HYBRID CHUNKER", hybrid_answer)


def main() -> None:
    print("Chunking comparison CLI — ask a question, see both chunkers' top")
    print("matches AND the LLM's generated answer from each.")
    print("Type 'quit' or 'exit' to stop.\n")
    while True:
        try:
            question = input("Ask a question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break
        if not question:
            continue
        if question.lower() in {"quit", "exit", "q"}:
            print("Exiting.")
            break
        ask(question)


if __name__ == "__main__":
    main()
