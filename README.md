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

Prerequisites: a `.env` with `OPENAI_API_KEY` and `TAVILY_API_KEY` (or Ollama running with the
`qwen3:8b` model if you set `LLM_PROVIDER=ollama`), and the Chroma index built by
`discovery/embedding-retrieval-prototype/build_index.py`.

```
uv run ask-hybrid      # answers using the hybrid-chunked index
uv run ask-semantic    # answers using the semantic-chunked index
```

Both programs run the same agent; only the chunking differs.

By default the agent uses the OpenAI API, so `OPENAI_API_KEY` must be set in `.env`
(`OPENAI_MODEL` is optional). To use the local Ollama model instead, set `LLM_PROVIDER=ollama`.

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
