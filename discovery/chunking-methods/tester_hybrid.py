import json
from pathlib import Path

from docling.chunking import HybridChunker
from docling.document_converter import DocumentConverter

converter = DocumentConverter()
chunker = HybridChunker()

BASE_DIR = Path(__file__).parent
out_dir = BASE_DIR / "hybridresults"
out_dir.mkdir(exist_ok=True)

for path in (BASE_DIR / "sample_pdfs").glob("*.*"):
    if path.suffix.lower() not in {".pdf", ".docx", ".pptx", ".html"}:
        continue

    doc = converter.convert(path).document

    chunks = []
    for i, chunk in enumerate(chunker.chunk(dl_doc=doc)):
        headings = getattr(chunk.meta, "headings", None) or []
        chunks.append({
            "id": i,
            "headings": headings,
            "text": chunk.text.strip(),
        })

    # JSON: one entry per chunk, with its headings
    (out_dir / f"{path.stem}_hybrid.json").write_text(
        json.dumps(chunks, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    # Plain text: easy to eyeball where the cuts landed
    (out_dir / f"{path.stem}_hybrid.txt").write_text(
        "\n\n--- CHUNK BREAK ---\n\n".join(
            (f"[{' > '.join(c['headings'])}]\n" if c["headings"] else "") + c["text"]
            for c in chunks
        ),
        encoding="utf-8",
    )

    print(f"\n=== {path.name}: {len(chunks)} chunks ===")
    for c in chunks:
        label = " > ".join(c["headings"]) or "(no heading)"
        print(f"[{c['id']}] {label}\n    {c['text'][:200]}...\n")