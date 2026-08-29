"""
Loads the persisted ChromaDB store and exposes a simple search function
that the agent calls to answer knowledge/policy questions.
"""
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

import config

_embeddings = HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL)
_vector_store = Chroma(
    persist_directory=config.CHROMA_DIR,
    embedding_function=_embeddings,
)


def search_documents(query: str, k: int = None) -> str:
    """Return the top-k most relevant document chunks, concatenated as plain text."""
    k = k or config.TOP_K
    results = _vector_store.similarity_search(query, k=k)
    if not results:
        return "No relevant documents found."
    return "\n\n".join(doc.page_content for doc in results)
