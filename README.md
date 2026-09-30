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

*(Application entry points will be added as backend and API routes are implemented.)*

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
