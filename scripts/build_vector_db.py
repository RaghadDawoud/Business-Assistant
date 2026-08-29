"""
Run this once, and again whenever you add or update documents in
data/documents/, to (re)build the ChromaDB vector store.

Usage: python scripts/build_vector_db.py
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rag.ingest import build_vector_store

if __name__ == "__main__":
    build_vector_store()
