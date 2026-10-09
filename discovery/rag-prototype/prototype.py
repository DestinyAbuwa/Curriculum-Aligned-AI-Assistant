import os
import re

import streamlit as st
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

st.set_page_config(page_title="UICOMP Assistant Prototype", page_icon="🩺")
st.title("🩺 UICOMP AI Assistant — Baseline Prototype")

# Load variables from .env file
load_dotenv()

# Initialize UI session history if it doesn't exist yet
if "qa_history" not in st.session_state:
    st.session_state.qa_history = []

# 1. Check API Key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.warning(
        "⚠️ No API key found in your environment! Please add OPENAI_API_KEY to your .env file."
    )
    st.stop()

# ==========================================
# DEV MENU: Sidebar Controls
# ==========================================
st.sidebar.header("⚙️ Dev Menu")

# Chunking Method Dropdown
chunking_method = st.sidebar.selectbox(
    "Chunking Method",
    options=["Recursive Character (1500)", "Semantic", "Recursive Character (600)"],
    help="Select how the PDF is split into pieces before vectorizing.",
)

# K-Value Slider
k_value = st.sidebar.slider(
    "Retrieved Chunks (k)",
    min_value=1,
    max_value=10,
    value=5,
    help="Number of chunks to retrieve for the LLM context.",
)

st.sidebar.divider()
st.sidebar.info("Upload a new PDF or change the chunking method to rebuild the vector database.")


# ==========================================
# 2. Cached Function to Load, Chunk, and Index PDF
# ==========================================
@st.cache_resource(show_spinner="Processing document & generating embeddings...")
def process_pdf(file_bytes, filename, key, method):
    temp_path = f"temp_{filename}"
    with open(temp_path, "wb") as f:
        f.write(file_bytes)

    # Apply Selected Chunking Method from chunkers.py
    if method == "Recursive Character (1500)":
        from chunkers import recursive_baseline_chunker

        chunks = recursive_baseline_chunker(temp_path)

    elif method == "Semantic":
        from chunkers import semantic_chunker

        chunks = semantic_chunker(temp_path)

    elif method == "Recursive Character (600)":
        from chunkers import recursive_alternative_chunker

        chunks = recursive_alternative_chunker(temp_path)

    # Embeddings & Vector Store
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=key)

    # Safe collection name based on filename AND full method string so collections don't mix
    safe_name = re.sub(r"[^a-zA-Z0-9]", "_", filename).strip("_")
    method_safe = re.sub(r"[^a-zA-Z0-9]", "_", method).lower()  # e.g., 'recursive_character_1500'
    collection_name = f"pdf_{safe_name[:20]}_{method_safe[:20]}".strip("_")

    vector_store = Chroma.from_documents(chunks, embeddings, collection_name=collection_name)
    return vector_store, chunks


# ==========================================
# 3. Upload Document
# ==========================================
uploaded_file = st.file_uploader("Upload a course PDF to test:", type=["pdf"])

if uploaded_file:
    file_bytes = uploaded_file.getvalue()
    vector_store, chunks = process_pdf(file_bytes, uploaded_file.name, api_key, chunking_method)

    st.success(
        f"Loaded **{uploaded_file.name}** using **{chunking_method}** ({len(chunks)} chunks ready)!"
    )

    with st.expander("View Document Chunks"):
        for i, chunk in enumerate(chunks):
            st.markdown(f"**Chunk {i + 1}:**")
            content = chunk.page_content if hasattr(chunk, "page_content") else chunk
            st.text(content)
            st.divider()

    # ==========================================
    # 4. Query Form
    # ==========================================
    with st.form("query_form", clear_on_submit=True):
        user_query = st.text_input("Ask a question about this document:")
        submitted = st.form_submit_button("Ask")

    if submitted and user_query:
        with st.spinner("Searching ChromaDB and generating answer..."):
            matching_docs_with_scores = vector_store.similarity_search_with_score(
                user_query, k=k_value
            )
            context_text = "\n\n---\n\n".join(
                [doc.page_content for doc, score in matching_docs_with_scores]
            )

            llm = ChatOpenAI(model="gpt-4o-mini", api_key=api_key, temperature=0)
            prompt = (
                f"Answer the question using ONLY the context below. If unknown, say so.\n\n"
                f"Context:\n{context_text}\n\n"
                f"Question: {user_query}"
            )
            response = llm.invoke(prompt)

            st.session_state.qa_history.append(
                {
                    "query": user_query,
                    "answer": response.content,
                    "retrieved": matching_docs_with_scores,
                    "k_used": k_value,
                    "method_used": chunking_method,
                }
            )

    # ==========================================
    # 5. Render Q&A History
    # ==========================================
    if st.session_state.qa_history:
        st.write("---")
        st.subheader("💬 Query History")

        for item_idx, item in enumerate(reversed(st.session_state.qa_history)):
            st.markdown(f"### **Q: {item['query']}**")
            st.write(f"**Answer:** {item['answer']}")

            st.caption(f"⚙️ *Tested with: {item['method_used']} | k={item['k_used']}*")

            with st.expander(
                f"🔍 View Retrieved Chunks for Query #{len(st.session_state.qa_history) - item_idx}"
            ):
                for idx, (doc, score) in enumerate(item["retrieved"]):
                    st.markdown(f"**Chunk {idx + 1}** — *Distance Score:* `{score:.4f}`")
                    st.info(doc.page_content)
            st.divider()
