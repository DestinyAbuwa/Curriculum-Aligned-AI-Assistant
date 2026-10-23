import os
import re

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import (
    MarkdownTextSplitter,
    RecursiveCharacterTextSplitter,
)


def _clean_docs(docs):
    """Helper function to strip URLs and university headers across all chunkers."""
    for doc in docs:
        doc.page_content = re.sub(r"http[s]?://\S+", "", doc.page_content)
        doc.page_content = re.sub(
            r"THE UNIVERSITY OF ILLINOIS COLLEGE OF MEDICINE",
            "",
            doc.page_content,
            flags=re.IGNORECASE,
        )
    return docs


def semantic_chunker(file_path):
    """
    Semantic Chunker (API-powered version):
    Uses OpenAIEmbeddings for detecting semantic boundary shifts,
    and a tiktoken CharacterTextSplitter to cap chunk size.
    """
    try:
        loader = PyPDFLoader(file_path)
        docs = _clean_docs(loader.load())
    except Exception as e:
        print(f"Skipping corrupted file {file_path}: {e}")
        return []

    full_text = "\n".join([doc.page_content for doc in docs])

    openai_embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    semantic_splitter = SemanticChunker(openai_embeddings)
    semantic_chunks = semantic_splitter.create_documents([full_text])

    token_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=512, chunk_overlap=0)
    final_chunks = token_splitter.split_documents(semantic_chunks)

    for chunk in final_chunks:
        chunk.metadata["source"] = file_path

    return final_chunks


def recursive_baseline_chunker(file_path):
    """
    Recursive Character Chunker (Baseline - 1500 chars):
    Splits PDF text into large blocks with overlap.
    """
    try:
        loader = PyPDFLoader(file_path)
        docs = _clean_docs(loader.load())
    except Exception as e:
        print(f"Skipping corrupted file {file_path}: {e}")
        return []

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=250,
        separators=["\n\n\n", "\n\n", "\n", " ", ""],
    )
    chunks = text_splitter.split_documents(docs)

    for chunk in chunks:
        chunk.metadata["source"] = file_path

    return chunks


def recursive_alternative_chunker(file_path):
    """
    Recursive Character Chunker (Structural - 600 chars):
    Splits PDF text into smaller layout-sized blocks.
    """
    try:
        loader = PyPDFLoader(file_path)
        docs = _clean_docs(loader.load())
    except Exception as e:
        print(f"Skipping corrupted file {file_path}: {e}")
        return []

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=100,
        separators=["\n\n\n", "\n\n", "\n", " ", ""],
    )
    chunks = text_splitter.split_documents(docs)

    for chunk in chunks:
        chunk.metadata["source"] = file_path

    return chunks


def cloud_hybrid_chunker(file_path):
    """
    Hybrid Cloud Chunker:
    Uses LlamaCloud v2 API to extract layout-aware Markdown (tables/headers),
    then splits structurally based on Markdown syntax.
    """
    try:
        from pathlib import Path

        from llama_cloud import LlamaCloud

        # 1. Initialize the v2 LlamaCloud client
        client = LlamaCloud(api_key=os.getenv("LLAMA_CLOUD_API_KEY"))

        # Upload the file to the cloud
        uploaded = client.files.create(file=Path(file_path), purpose="parse")

        # Request a parse job and wait for the markdown output
        result = client.parsing.parse(
            file_id=uploaded.id,
            tier="agentic",
            version="latest",
            expand=["markdown_full"],
            agentic_options={
                "custom_prompt": (
                    "Provide detailed, precise descriptions for all medical figures, "
                    "diagrams, anatomical illustrations, CT scans, and MRIs in markdown."
                )
            },
        )

        # FIX: result.markdown_full is already a string, no need to loop through .pages!
        full_markdown_text = result.markdown_full or ""

        # 2. Split structurally using LangChain's Markdown headings
        markdown_splitter = MarkdownTextSplitter(chunk_size=1500, chunk_overlap=250)

        texts = markdown_splitter.split_text(full_markdown_text)

        # 3. Convert back to LangChain Document objects
        final_chunks = [Document(page_content=t, metadata={"source": file_path}) for t in texts]

        return final_chunks
    except Exception as e:
        print(f"Skipping corrupted file {file_path} in Cloud Hybrid: {e}")
        return []
