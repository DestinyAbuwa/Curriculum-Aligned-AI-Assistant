import os
import re

import streamlit as st
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage, SystemMessage
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
    st.warning("⚠️ No API key found in your environment! Please add OPENAI_API_KEY to your .env file.")
    st.stop()

# ==========================================
# DEV MENU: Sidebar Controls
# ==========================================
st.sidebar.header("⚙️ Dev Menu")

# Chunking Method Dropdown
chunking_method = st.sidebar.selectbox(
    "Chunking Method",
    options=[
        "Recursive Character (1500)",
        "Semantic",
        "Recursive Character (600)",
        "Cloud Hybrid (LlamaParse)",
    ],
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
# 2. Cached Function to Load, Chunk, and Index PDFs
# ==========================================
@st.cache_resource(show_spinner="Processing documents & generating embeddings...")
def process_pdfs(uploaded_files, key, method):
    all_chunks = []

    # Loop through every uploaded file
    for uploaded_file in uploaded_files:
        temp_path = f"temp_{uploaded_file.name}"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getvalue())

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
        elif method == "Cloud Hybrid (LlamaParse)":
            from chunkers import cloud_hybrid_chunker

            chunks = cloud_hybrid_chunker(temp_path)

        all_chunks.extend(chunks)

    # After the loop finishes extending all_chunks:
    if not all_chunks:
        st.error("No chunks were generated. The chunker failed or the PDFs are empty.")
        st.stop()

    # Embeddings & Vector Store
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large", api_key=key)

    # Create a safe collection name based on file count and method
    method_safe = re.sub(r"[^a-zA-Z0-9]", "_", method).lower()
    collection_name = f"corpus_{len(uploaded_files)}_docs_{method_safe}".strip("_")

    vector_store = Chroma.from_documents(all_chunks, embeddings, collection_name=collection_name)
    return vector_store, all_chunks


# ==========================================
# 3. Upload Documents
# ==========================================
# Added accept_multiple_files=True
uploaded_files = st.file_uploader("Upload course PDFs to test:", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    vector_store, chunks = process_pdfs(uploaded_files, api_key, chunking_method)

    st.success(
        f"Loaded **{len(uploaded_files)} documents** using **{chunking_method}** ({len(chunks)} total chunks ready)!"
    )

    # with st.expander("View Document Chunks"):
    #     for i, chunk in enumerate(chunks):
    #         st.markdown(f"**Chunk {i + 1}** *(Source: {chunk.metadata.get('source', 'Unknown')})*")
    #         content = chunk.page_content if hasattr(chunk, "page_content") else chunk
    #         st.text(content)
    #         st.divider()

    # ==========================================
    # 4. Query Form
    # ==========================================
    with st.form("query_form", clear_on_submit=True):
        user_query = st.text_input("Ask a question about this document:")
        submitted = st.form_submit_button("Ask")

    if submitted and user_query:
        with st.spinner("Searching ChromaDB and generating answer..."):
            matching_docs_with_scores = vector_store.similarity_search_with_score(user_query, k=k_value)
            context_text = "\n\n---\n\n".join([doc.page_content for doc, score in matching_docs_with_scores])

            llm = ChatOpenAI(model="gpt-6-luna", api_key=api_key)

            # Define the strict behavior
            system_instruction = (
                "You are an accurate, objective Medical Curriculum AI Assistant for "
                "preclinical medical students at UICOM-Peoria. Your role is clear, "
                "educational, and encouraging.\n\n"
                "1. Curriculum-First Grounding & Fallback:\n"
                "- Answer user questions using the provided curriculum documents "
                "first.\n"
                "- Only fall back to general external medical knowledge when the answer "
                "cannot be found in the provided curriculum documents.\n"
                "- When providing information from outside the curriculum, explicitly "
                "begin your answer with: \"This isn't covered in your course materials, "
                'but..."\n\n'
                "2. Practice Question Generation (ONLY when explicitly requested):\n"
                "- If the user explicitly asks for practice questions or MCQs, format "
                "them using the NBME Item-Writing Guide:\n"
                "  - Rule 1 (Focus): Focus each item on a single, important testing point.\n"
                "  - Rule 2 (Vignette): Test application of knowledge using a Clinical "
                "Vignette (Age/Sex -> Site of Care -> Chief Complaint -> History -> "
                "Vitals/Exam -> Labs/Imaging).\n"
                "  - Rule 3 (Lead-In): Use a focused, closed lead-in that passes the "
                '"cover-the-options" rule. Never use negative phrasing (e.g., EXCEPT/NOT).\n'
                "  - Rule 4 (Options): Provide 4-5 homogeneous, plausible options (A-E). "
                'Never use "All of the above" or "None of the above".\n'
                "  - Rule 5 (No Flaws): Ensure options are parallel in length/structure "
                "and free of grammatical cues."
            )

            # Combine context and question for the human message
            human_input = f"Context:\n{context_text}\n\nQuestion: {user_query}"

            # Invoke the model with structured messages
            messages = [
                SystemMessage(content=system_instruction),
                HumanMessage(content=human_input),
            ]

            # 2. Stream the response directly to the UI, filtering out <think> and markers
            st.write("### **Answer:**")

            def generate_filtered_stream():
                in_think_block = False
                for chunk in llm.stream(messages):
                    token = chunk.content

                    # Filter out the hidden reasoning tags
                    if "<think>" in token:
                        in_think_block = True
                        token = token.replace("<think>", "")
                    if "</think>" in token:
                        in_think_block = False
                        token = token.replace("</think>", "")
                        continue  # Skip yielding the closing tag

                    # Filter out specific backend markers
                    if "NOT_FOUND" in token:
                        token = token.replace("NOT_FOUND", "")

                    # Only yield tokens if we are not inside a <think> block
                    if not in_think_block and token:
                        yield token

            # st.write_stream prints progressively and returns the final cleaned string
            full_response = st.write_stream(generate_filtered_stream)

            # 3. Save to QA history after streaming completes
            st.session_state.qa_history.append(
                {
                    "query": user_query,
                    "answer": full_response,
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

            with st.expander(f"🔍 View Retrieved Chunks for Query #{len(st.session_state.qa_history) - item_idx}"):
                for idx, (doc, score) in enumerate(item["retrieved"]):
                    st.markdown(f"**Chunk {idx + 1}** — *Distance Score:* `{score:.4f}`")
                    st.info(doc.page_content)
            st.divider()
