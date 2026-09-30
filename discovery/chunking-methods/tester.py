import json
from pathlib import Path

from docling.document_converter import DocumentConverter
from langchain_experimental.text_splitter import SemanticChunker
from langchain_huggingface import HuggingFaceEmbeddings

converter = DocumentConverter()
emb = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
splitter = SemanticChunker(emb, breakpoint_threshold_type="percentile")

out_dir = Path("chunks_out")
out_dir.mkdir(exist_ok=True)

for path in Path("docs").glob("*.*"):
    if path.suffix.lower() not in {".pdf", ".docx", ".pptx", ".html"}:
        continue

    text = converter.convert(path).document.export_to_markdown()
    chunks = splitter.split_text(text)

    # JSON: one entry per chunk
    (out_dir / f"{path.stem}_chunks.json").write_text(
        json.dumps(
            [{"id": i, "text": c.strip()} for i, c in enumerate(chunks)],
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    # Plain text: easy to eyeball where the cuts landed
    (out_dir / f"{path.stem}_chunks.txt").write_text(
        "\n\n--- CHUNK BREAK ---\n\n".join(c.strip() for c in chunks),
        encoding="utf-8",
    )

    print(f"\n=== {path.name}: {len(chunks)} chunks ===")
    for i, c in enumerate(chunks):
        print(f"[{i}] {c.strip()[:200]}...\n")