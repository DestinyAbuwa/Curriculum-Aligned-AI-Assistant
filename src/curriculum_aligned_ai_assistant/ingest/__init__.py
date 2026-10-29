"""Offline pipeline that turns course PDFs into the Chroma collections the agent searches.

Steps, in order: chunk the PDFs, extract their figures, describe the figures, build the index.
Run them with `uv run --group ingest ingest` (see `cli.py`).
"""
