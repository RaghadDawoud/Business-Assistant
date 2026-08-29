"""
Central configuration for the app.
All other files import from here.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# LLM (Groq) 
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(BASE_DIR, "data", "documents")
SALES_CSV = os.path.join(BASE_DIR, "data", "sales", "sample_sales.csv")
CHROMA_DIR = os.path.join(BASE_DIR, "data", "chroma_db")
MEMORY_DB = os.path.join(BASE_DIR, "data", "memory.db") # SQLite

# RAG settings 
EMBEDDING_MODEL = "intfloat/multilingual-e5-small"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
TOP_K = 3  # how many chunks to retrieve per query 
