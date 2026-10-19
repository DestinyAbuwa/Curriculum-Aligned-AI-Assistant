# Discovery: Chunking, Embedding & Retrieval

General context for everything under `discovery/` on this branch
(`continued-discovery-chunking-embedding-retrieval-vince`), which continues the
chunking research started on `discovery/chunking-methods-research-vince`. This
is exploratory research toward the RAG pipeline for the Curriculum-Aligned AI
Assistant — not wired into the main app yet.

## Folder map

- **`chunking-methods/`** — compares two chunking strategies against 3 sample
  curriculum PDFs (physiology, pharmacology, pathology lecture decks):
  - `tester.py` — LangChain `SemanticChunker` (sentence-embedding similarity
    breakpoints), output in `semanticresults/`
  - `tester_hybrid.py` — Docling's `HybridChunker` (document-structure-aware,
    no embedding model needed), output in `hybridresults/`
- **`embedding-models/`** — research into which embedding model should power
  the actual retrieval index.
- **`embedding-retrieval-prototype/`** — a working Chroma-based retrieval
  prototype: `build_index.py` embeds both chunkers' output with the chosen
  embedding model into two Chroma collections; `query.py` runs a fixed set of
  test questions against both; `compare_cli.py` is an interactive loop to ask
  ad hoc questions and see both chunkers' top matches side by side.

## Decisions made so far

| Decision | Choice | Why |
| --- | --- | --- |
| Embedding model | `BAAI/bge-m3` | Apache 2.0, 8,192-token context, no license friction. (`Alibaba-NLP/gte-large-en-v1.5` was the original pick but its custom remote code broke against the installed `transformers` version — see below.) |
| Semantic chunker breakpoint type | `standard_deviation`, `breakpoint_threshold_amount=1.25` | Default (`percentile`) threshold was fine; default `standard_deviation` (3σ) was too strict and produced exactly 1 chunk per document — see bug note below. |
| Docling OCR | Disabled (`do_ocr=False`) | PDFs already have a native text layer; OCR was retrying on embedded images and failing, adding ~8 minutes of runtime for no benefit. |
| Vector DB (prototype stage) | Chroma (local, embedded) | Zero infra/signup for a 3-document prototype; not a scale limitation — revisit for production deployment requirements later. |
| Generation LLM | `Qwen3-8B-Instruct` via Ollama | Full writeup: [LLM Generation Model Research & Decision](https://claude.ai/artifact/9zQET7WnNHrJifGqJTL69K) |

## Notable bugs found and fixed

1. **`SemanticChunker` producing 1 chunk per document.** `breakpoint_threshold_type="standard_deviation"` defaults to a 3-standard-deviation threshold, which is so strict that no sentence pair in a modest document ever clears it — every document collapsed into a single chunk. Fixed by setting `breakpoint_threshold_amount=1.25` explicitly.
2. **`gte-large-en-v1.5` incompatible with installed `transformers`.** Its custom remote-code model class calls `get_extended_attention_mask`, a method removed from `transformers`' `PreTrainedModel` API in a recent version. Swapped to `bge-m3`, which uses a standard architecture (no `trust_remote_code` needed) and has the same context length / license.

## Key research findings

- **General-purpose models repeatedly matched or beat domain-specific
  (biomedical) models**, both for embeddings and for the generation LLM.
  Medical-domain fine-tunes often carry real downsides for this project's
  actual content (teaching prose, not research abstracts): short context
  windows, stale base models, abandonment, and — per a 2025 JAMIA study on
  LLMs specifically — *worse* performance than general models on
  summarization/extraction tasks, which is close to what this project's
  generator needs to do.
- **Chunking method comparison (3-question manual test):** hybrid chunking
  tends to produce cleaner, more structurally-bounded chunks (less
  cross-contamination between unrelated adjacent slide content) and roughly
  2x more, smaller chunks than semantic chunking. Semantic chunking's
  finer sentence-level granularity won in the one case where the answer was
  a single sentence buried mid-paragraph rather than at a structural
  boundary. Neither method won outright — see "Next steps."
- **MedGemma** (Google's Gemma-3-based medical model) is a more credible
  domain-specific candidate than older medical LLMs (modern base, 128K
  context, actively maintained), but its strong benchmarks are all QA-style,
  which doesn't necessarily prove it's better at the grounded-synthesis task
  this project actually needs — flagged as worth an empirical A/B test, not
  an assumed win.

## Next steps

- Build a small labeled eval set (~30-50 realistic student questions per doc,
  with known correct source chunks) to get an actual precision/recall score
  per chunking method, rather than manual eyeballing.
- Extend `compare_cli.py`-style tooling to add a generation step: run a
  question through Qwen3-8B, MedGemma-4B, and Gemma-3-4B (via Ollama) on the
  same retrieved context and compare answers side by side.
- Revisit vector DB choice (Chroma vs. managed options) once real
  deployment/scale requirements are known.
