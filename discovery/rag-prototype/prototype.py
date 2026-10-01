import os
import re

import streamlit as st
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

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


# 2. Cached Function to Load, Clean, Chunk, and Index PDF
@st.cache_resource(show_spinner="Processing document & generating embeddings...")
def process_pdf(file_bytes, filename, key):
    temp_path = f"temp_{filename}"
    with open(temp_path, "wb") as f:
        f.write(file_bytes)

    # Load PDF
    loader = PyPDFLoader(temp_path)
    docs = loader.load()

    # Clean text before splitting
    for doc in docs:
        doc.page_content = re.sub(r"http[s]?://\S+", "", doc.page_content)
        doc.page_content = re.sub(
            r"THE UNIVERSITY OF ILLINOIS COLLEGE OF MEDICINE",
            "",
            doc.page_content,
            flags=re.IGNORECASE,
        )

    # Chunking
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=250)
    chunks = text_splitter.split_documents(docs)

    # Embeddings & Vector Store
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=key)

    # Safe collection name (alphanumeric and underscores only)
    safe_name = re.sub(r"[^a-zA-Z0-9]", "_", filename).strip("_")
    collection_name = f"pdf_{safe_name[:30]}"

    vector_store = Chroma.from_documents(chunks, embeddings, collection_name=collection_name)

    return vector_store, chunks


# 3. Upload Document
uploaded_file = st.file_uploader("Upload a course PDF to test:", type=["pdf"])

if uploaded_file:
    # Read bytes once for caching key
    file_bytes = uploaded_file.getvalue()

    vector_store, chunks = process_pdf(file_bytes, uploaded_file.name, api_key)

    st.success(f"Loaded **{uploaded_file.name}** ({len(chunks)} chunks ready)!")

    with st.expander("View Document Chunks"):
        for i, chunk in enumerate(chunks):
            st.markdown(f"**Chunk {i + 1}:**")
            content = chunk.page_content if hasattr(chunk, "page_content") else chunk
            st.text(content)
            st.divider()

    # 4. Query Form
    with st.form("query_form", clear_on_submit=True):
        user_query = st.text_input("Ask a question about this document:")
        submitted = st.form_submit_button("Ask")

    if submitted and user_query:
        with st.spinner("Searching ChromaDB and generating answer..."):
            # Fetch top 5 docs + similarity scores
            matching_docs_with_scores = vector_store.similarity_search_with_score(user_query, k=5)
            context_text = "\n\n---\n\n".join(
                [doc.page_content for doc, score in matching_docs_with_scores]
            )

            # Call LLM
            llm = ChatOpenAI(model="gpt-4o-mini", api_key=api_key, temperature=0)
            prompt = (
                f"Answer the question using ONLY the context below. If unknown, say so.\n\n"
                f"Context:\n{context_text}\n\n"
                f"Question: {user_query}"
            )

            response = llm.invoke(prompt)

            # Store query, answer, and retrieved chunks in session history
            st.session_state.qa_history.append(
                {
                    "query": user_query,
                    "answer": response.content,
                    "retrieved": matching_docs_with_scores,
                }
            )

    # 5. Render Q&A History
    if st.session_state.qa_history:
        st.write("---")
        st.subheader("💬 Query History")

        # Display newest items first
        for item_idx, item in enumerate(reversed(st.session_state.qa_history)):
            st.markdown(f"### **Q: {item['query']}**")
            st.write(f"**Answer:** {item['answer']}")

            with st.expander(
                f"🔍 View Retrieved Chunks for Query #{len(st.session_state.qa_history) - item_idx}"
            ):
                for idx, (doc, score) in enumerate(item["retrieved"]):
                    st.markdown(f"**Chunk {idx + 1}** — *Distance Score:* `{score:.4f}`")
                    st.info(doc.page_content)
            st.divider()
