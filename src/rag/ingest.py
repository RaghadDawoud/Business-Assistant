"""
One-time / repeatable pipeline: read raw documents -> chunk -> embed -> store in ChromaDB.
Run this via scripts/build_vector_db.py whenever you add or update documents.
"""
import os
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

import config


def load_documents(docs_dir: str):
    """Read every supported file in docs_dir and return raw LangChain Document objects."""
    documents = []
    for filename in os.listdir(docs_dir):
        path = os.path.join(docs_dir, filename)
        if filename.endswith(".pdf"):
            loader = PyPDFLoader(path)
        elif filename.endswith(".docx"):
            loader = Docx2txtLoader(path)
        elif filename.endswith(".txt"):
            loader = TextLoader(path, encoding="utf-8")
        else:
            continue  # skip unsupported file types
        documents.extend(loader.load())
    return documents


def build_vector_store():
    """Chunk documents and persist them into a local ChromaDB collection."""
    documents = load_documents(config.DOCS_DIR)
    if not documents:
        print(f"No documents found in {config.DOCS_DIR}. Add .pdf/.docx/.txt files first.")
        return None

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
    )
    chunks = splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL)

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=config.CHROMA_DIR,
    )
    print(f"Indexed {len(chunks)} chunks from {len(documents)} documents.")
    return vector_store
