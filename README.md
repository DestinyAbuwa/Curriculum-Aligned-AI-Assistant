# Curriculum-Aligned AI Assistant

A retrieval-augmented generation (RAG) assistant designed for preclinical medical students at UICOMP. This tool indexes course materials — such as lecture slides, syllabi, and clinical guides — to provide accurate, grounded answers with direct source citations to aid medical study and exam preparation.

---

## Prerequisites

- **Python**: `^3.11` (or Python 3.10+)
- **Package Manager**: [`uv`](https://astral.sh/uv/)

---

## Setup & Installation

1. **Clone the repository:**
   ```
   git clone [https://github.com/DestinyAbuwa/Curriculum-Aligned-AI-Assistant.git](https://github.com/DestinyAbuwa/Curriculum-Aligned-AI-Assistant.git)
   cd Curriculum-Aligned-AI-Assistant
   ```




2. **Install dependencies using `uv`:**
    ```
    uv sync
    ```


3. **Set up pre-commit hooks (One-time setup for contributors):**
    ```
    uv run pre-commit install
    ```


---

## Environment Variables

Copy the example environment file to create your local `.env` configuration:

```
cp .env.example .env
```

Open `.env` and add your specific API credentials as needed:

* `OPENAI_API_KEY`: API key for OpenAI model access.
* `ANTHROPIC_API_KEY`: API key for Anthropic Claude model access.
* `GROK_API_KEY`: API key for X.AI Grok endpoint (if applicable).

---

## Running the Project

Prerequisites: a `.env` with `OPENAI_API_KEY` and `TAVILY_API_KEY` (or Apple Silicon with the
MLX dependencies installed if you set `LLM_PROVIDER=mlx`), and the Chroma index in `data/chroma_db/`
(see [Building the index](#building-the-index)).

```
uv run ask-hybrid      # answers using the hybrid-chunked index
uv run ask-semantic    # answers using the semantic-chunked index
```

Both programs run the same agent; only the chunking differs.

A small Streamlit page shows the figures the agent returns with an answer. It is a prototype for
seeing those figures, not the final frontend:

```
uv run streamlit run src/curriculum_aligned_ai_assistant/ui/app.py
```

### Figures from the course PDFs

`--images` makes the agent search the `semantic_images` / `hybrid_images` collections, which hold
figures as their own chunks (a text description plus the image file). Without the flag the
programs use the original `*_chunks` collections.

```
uv run ask-semantic --images
uv run ask-hybrid --images
```

A figure is returned with a course answer only if its distance is at most `IMAGE_MAX_DISTANCE`
(0.45) and within `IMAGE_MARGIN` (0.05) of the closest such figure, so unrelated or merely
neighbouring figures are left out.

### Building the index

The ingestion pipeline lives in `src/curriculum_aligned_ai_assistant/ingest/` and reads and writes
everything under `data/`:

| Step | Module | Reads | Writes |
| --- | --- | --- | --- |
| `chunk` | `chunking.py` | `data/pdfs/` | `data/chunks/semantic/`, `data/chunks/hybrid/` |
| `extract` | `extract_images.py` | `data/pdfs/` | `data/images/`, `data/images.json` |
| `describe` | `describe_images.py` | `data/images.json` | `data/descriptions.json` |
| `index` | `indexing.py` | chunks, images.json, descriptions.json | `data/chroma_db/` (all four collections) |

```
uv run --group ingest ingest                 # all steps, in order
uv run --group ingest ingest chunk extract   # only some steps
uv run ingest index                          # rebuild the index from the committed chunks
```

`chunk` and `extract` need the `ingest` dependency group (Docling). `describe` needs
`OPENAI_API_KEY` and costs a few cents; it skips images already in `descriptions.json`, which is
committed along with the chunks. `data/images/` and `data/chroma_db/` are generated and
git-ignored, so on a fresh clone run `uv run --group ingest ingest extract index` first; until then
the Streamlit page shows "Image unavailable".

By default the agent uses the OpenAI API, so `OPENAI_API_KEY` must be set in `.env`
(`OPENAI_MODEL` is optional). To use local MedGemma through MLX-VLM on Apple Silicon, set
`LLM_PROVIDER=mlx`. The default checkpoint is `mlx-community/medgemma-4b-it-4bit`; override it
with `MLX_MODEL`. Before the first run, request access to MedGemma and accept Google's Health AI
Developer Foundations terms on Hugging Face. If Hugging Face requires authentication, set
`HF_TOKEN` in `.env`. The Streamlit prototype also has an OpenAI/MLX selector and reports
generation time for each answer so both engines can be compared on the same question.

### Viewing the agent graph

```
uv run langgraph dev
```

This opens LangGraph Studio with two graphs, `hybrid` and `semantic`. Studio draws the graph from
the code and shows each node running with the state at every step, so it stays current as nodes are
added. It needs a free LangSmith API key in `.env` as `LANGSMITH_API_KEY`; keep
`LANGSMITH_TRACING=false` so runs are not sent to LangSmith.

---

## Testing & Quality Assurance

* **Run unit tests:**
    ```
    uv run pytest
    ```


* **Run linter checks:**
    ```
    uv run ruff check .
    ```


* **Format code:**
    ```
    uv run ruff format .
    ```
