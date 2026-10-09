import re

from langchain_community.document_loaders import PyPDFLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter


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
    loader = PyPDFLoader(file_path)
    docs = _clean_docs(loader.load())

    full_text = "\n".join([doc.page_content for doc in docs])

    openai_embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    semantic_splitter = SemanticChunker(openai_embeddings)
    semantic_chunks = semantic_splitter.create_documents([full_text])

    token_splitter = CharacterTextSplitter.from_tiktoken_encoder(chunk_size=512, chunk_overlap=0)
    final_chunks = token_splitter.split_documents(semantic_chunks)

    for chunk in final_chunks:
        chunk.metadata["source"] = file_path

    return final_chunks


def recursive_baseline_chunker(file_path):
    """
    Recursive Character Chunker (Baseline - 1500 chars):
    Splits PDF text into large blocks with overlap.
    """
    loader = PyPDFLoader(file_path)
    docs = _clean_docs(loader.load())

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
    loader = PyPDFLoader(file_path)
    docs = _clean_docs(loader.load())

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=100,
        separators=["\n\n\n", "\n\n", "\n", " ", ""],
    )
    chunks = text_splitter.split_documents(docs)

    for chunk in chunks:
        chunk.metadata["source"] = file_path

    return chunks
