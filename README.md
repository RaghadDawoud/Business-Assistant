# Business Assistant

A conversational agent (Arabic + English) for small Saudi retail/service businesses.
Answers policy questions from documents (RAG), sales questions from a CSV (pandas),
and remembers conversation context (SQLite).

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # then add your GROQ_API_KEY
python scripts/build_vector_db.py   # index the documents in data/documents/
python app.py                       # launch the Gradio chat UI
```

## Project structure

```
business-assistant/
├── config.py                  # all settings/paths in one place
├── app.py                     # Gradio UI entry point
├── requirements.txt
├── .env.example
├── data/
│   ├── documents/              # policy/FAQ files (.txt/.pdf/.docx) -> RAG source
│   ├── sales/sample_sales.csv  # sales data -> pandas analysis source
│   ├── chroma_db/               # generated: vector store (after build_vector_db.py)
│   └── memory.db                # generated: conversation + preference history
├── scripts/
│   └── build_vector_db.py      # (re)index documents into ChromaDB
└── src/
    ├── rag/
    │   ├── ingest.py           # load docs -> chunk -> embed -> store
    │   └── retriever.py        # similarity search over stored chunks
    ├── analysis/
    │   └── sales_functions.py  # safe, predefined pandas queries
    ├── memory/
    │   └── memory_store.py     # SQLite: conversation history + preferences
    └── agent/
        ├── llm_client.py       # Groq API wrapper
        ├── router.py           # tool schemas + dispatcher (the "routing" logic)
        └── agent.py            # orchestrates: history -> LLM -> tools -> answer
```

See the chat response for a suggested reading/build order.
