"""Chunk the course PDFs two ways and write one JSON (and one .txt to eyeball) per document.

- semantic: LangChain `SemanticChunker` on Docling markdown, with a token cap.
- hybrid: Docling's structure-aware `HybridChunker`, keeping each chunk's headings.

Output: data/chunks/<kind>/<pdf stem>_<kind>.json, a list of {"id", "text"[, "headings"]}.
"""

import json
from pathlib import Path
from typing import Any

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.transforms.chunker.hybrid_chunker import HybridChunker
from langchain_experimental.text_splitter import SemanticChunker
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import SentenceTransformersTokenTextSplitter

from curriculum_aligned_ai_assistant.config import CHUNKS_DIR, EMBEDDING_MODEL, PDF_DIR

# Safety cap: SemanticChunker has no built-in max chunk size and can emit an
# unsplit chunk spanning an entire document section if no breakpoint is found
# (seen in practice on dense academic PDFs with reference lists/tables, which
# skew the similarity statistic the chunker relies on). 512 tokens is both a
# sensible RAG retrieval-quality size and well clear of bge-m3's 8,192-token
# limit, so any oversized chunk gets force-split rather than ever reaching the
# embedder.
MAX_TOKENS = 512
SUPPORTED_SUFFIXES = {".pdf", ".docx", ".pptx", ".html"}
CHUNK_BREAK = "\n\n--- CHUNK BREAK ---\n\n"


def source_documents(pdf_dir: Path = PDF_DIR) -> list[Path]:
    return sorted(p for p in pdf_dir.glob("*.*") if p.suffix.lower() in SUPPORTED_SUFFIXES)


def _write(out_dir: Path, stem: str, kind: str, chunks: list[dict[str, Any]], text: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"{stem}_{kind}.json").write_text(
        json.dumps(chunks, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    # Plain text: easy to eyeball where the cuts landed
    (out_dir / f"{stem}_{kind}.txt").write_text(text, encoding="utf-8")


class SemanticChunking:
    def __init__(self) -> None:
        options = PdfPipelineOptions(do_ocr=False)
        self._converter = DocumentConverter(
            format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=options)}
        )
        embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL, model_kwargs={"device": "cpu"}
        )
        self._splitter = SemanticChunker(
            embeddings,
            breakpoint_threshold_type="standard_deviation",
            breakpoint_threshold_amount=1.25,
        )
        self._fallback_splitter = SentenceTransformersTokenTextSplitter(
            model_name=EMBEDDING_MODEL,
            tokens_per_chunk=MAX_TOKENS,
            chunk_overlap=50,
            model_kwargs={"device": "cpu"},
        )

    def split(self, text: str) -> list[str]:
        capped: list[str] = []
        for chunk in self._splitter.split_text(text):
            if self._fallback_splitter.count_tokens(text=chunk) > MAX_TOKENS:
                capped.extend(self._fallback_splitter.split_text(chunk))
            else:
                capped.append(chunk)
        return capped

    def chunk_document(self, path: Path, out_dir: Path) -> int:
        text = self._converter.convert(path).document.export_to_markdown()
        chunks = [c.strip() for c in self.split(text)]
        _write(
            out_dir,
            path.stem,
            "semantic",
            [{"id": i, "text": c} for i, c in enumerate(chunks)],
            CHUNK_BREAK.join(chunks),
        )
        return len(chunks)


class HybridChunking:
    def __init__(self) -> None:
        self._converter = DocumentConverter()
        self._chunker = HybridChunker()

    def chunk_document(self, path: Path, out_dir: Path) -> int:
        doc = self._converter.convert(path).document
        chunks: list[dict[str, Any]] = []
        for i, chunk in enumerate(self._chunker.chunk(dl_doc=doc)):
            headings = getattr(chunk.meta, "headings", None) or []
            chunks.append({"id": i, "headings": headings, "text": chunk.text.strip()})
        _write(
            out_dir,
            path.stem,
            "hybrid",
            chunks,
            CHUNK_BREAK.join(
                (f"[{' > '.join(c['headings'])}]\n" if c["headings"] else "") + c["text"]
                for c in chunks
            ),
        )
        return len(chunks)


def chunk_all(pdf_dir: Path = PDF_DIR, chunks_dir: Path = CHUNKS_DIR) -> None:
    documents = source_documents(pdf_dir)
    for kind, chunker in (("semantic", SemanticChunking()), ("hybrid", HybridChunking())):
        for path in documents:
            count = chunker.chunk_document(path, chunks_dir / kind)
            print(f"{kind}: {path.name}: {count} chunks", flush=True)
