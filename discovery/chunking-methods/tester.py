import json
from pathlib import Path

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from langchain_experimental.text_splitter import SemanticChunker
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import SentenceTransformersTokenTextSplitter

# Safety cap: SemanticChunker has no built-in max chunk size and can emit an
# unsplit chunk spanning an entire document section if no breakpoint is found
# (seen in practice on dense academic PDFs with reference lists/tables, which
# skew the similarity statistic the chunker relies on). 512 tokens is both a
# sensible RAG retrieval-quality size and well clear of bge-m3's 8,192-token
# limit, so any oversized chunk gets force-split rather than ever reaching the
# embedder.
MAX_TOKENS = 512

pipeline_options = PdfPipelineOptions(do_ocr=False)
converter = DocumentConverter(
    format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}
)
emb = HuggingFaceEmbeddings(model_name="BAAI/bge-m3", model_kwargs={"device": "cpu"})
splitter = SemanticChunker(
    emb,
    breakpoint_threshold_type="standard_deviation",
    breakpoint_threshold_amount=1.25,
)
fallback_splitter = SentenceTransformersTokenTextSplitter(
    model_name="BAAI/bge-m3",
    tokens_per_chunk=MAX_TOKENS,
    chunk_overlap=50,
    model_kwargs={"device": "cpu"},
)


def chunk_with_cap(text: str) -> list[str]:
    capped_chunks = []
    for chunk in splitter.split_text(text):
        if fallback_splitter.count_tokens(text=chunk) > MAX_TOKENS:
            capped_chunks.extend(fallback_splitter.split_text(chunk))
        else:
            capped_chunks.append(chunk)
    return capped_chunks

BASE_DIR = Path(__file__).parent
out_dir = BASE_DIR / "semanticresults"
out_dir.mkdir(exist_ok=True)

for path in (BASE_DIR / "sample_pdfs").glob("*.*"):
    if path.suffix.lower() not in {".pdf", ".docx", ".pptx", ".html"}:
        continue

    text = converter.convert(path).document.export_to_markdown()
    chunks = chunk_with_cap(text)

    # JSON: one entry per chunk
    (out_dir / f"{path.stem}_semantic.json").write_text(
        json.dumps(
            [{"id": i, "text": c.strip()} for i, c in enumerate(chunks)],
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    # Plain text: easy to eyeball where the cuts lannded
    (out_dir / f"{path.stem}_semantic.txt").write_text(
        "\n\n--- CHUNK BREAK ---\n\n".join(c.strip() for c in chunks),
        encoding="utf-8",
    )

    print(f"\n=== {path.name}: {len(chunks)} chunks ===")
    for i, c in enumerate(chunks):
        print(f"[{i}] {c.strip()[:200]}...\n")