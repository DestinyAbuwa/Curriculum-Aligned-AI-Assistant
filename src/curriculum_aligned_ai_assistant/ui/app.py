"""Prototype page for seeing the figures the agent returns with an answer."""

from dataclasses import replace
from time import perf_counter

import streamlit as st

from curriculum_aligned_ai_assistant.bootstrap import build_agent
from curriculum_aligned_ai_assistant.config import REPO_ROOT, Settings
from curriculum_aligned_ai_assistant.errors import AgentStartupError, LlmUnavailableError
from curriculum_aligned_ai_assistant.graph import AgentGraph

COLLECTIONS = ["semantic_chunks", "hybrid_chunks", "semantic_images", "hybrid_images"]


@st.cache_resource(show_spinner="Loading the selected language model...")
def cached_agent(collection_name: str, provider: str) -> tuple[AgentGraph, list[str]]:
    settings = replace(Settings.from_env(), llm_provider=provider)
    return build_agent(collection_name, settings)


st.title("Curriculum assistant: figure prototype")
collection = st.selectbox("Collection", COLLECTIONS, index=COLLECTIONS.index("semantic_images"))
default_provider = Settings.from_env().llm_provider
provider = st.radio(
    "Language model",
    options=["openai", "mlx"],
    index=1 if default_provider == "mlx" else 0,
    format_func=lambda value: "OpenAI API · GPT" if value == "openai" else "MLX · MedGemma 4B",
    horizontal=True,
)

try:
    graph, warnings = cached_agent(collection, provider)
except AgentStartupError as exc:
    st.error(f"Cannot start: {exc}")
    st.stop()

for warning in warnings:
    st.warning(warning)

with st.form("ask"):
    question = st.text_input("Question")
    submitted = st.form_submit_button("Ask")

if submitted and question.strip():
    try:
        started = perf_counter()
        answer = graph.invoke({"question": question.strip()})["answer"]
        elapsed = perf_counter() - started
    except LlmUnavailableError as exc:
        st.error(str(exc))
        st.stop()
    st.caption(f"End-to-end time: {elapsed:.2f} seconds · {provider}")
    st.caption(f"Source: {answer.source_type}")
    st.write(answer.text)
    for citation in answer.citations:
        st.markdown(f"- {citation}")
    for path in answer.images:
        image_file = (REPO_ROOT / path).resolve()
        if image_file.is_relative_to(REPO_ROOT.resolve()) and image_file.is_file():
            st.image(image_file, caption=path)
        else:
            st.warning(f"Image unavailable (missing or outside the repo): {path}")
