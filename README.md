# 💬 Business Assistant

A conversational AI agent (Arabic + English) built for small retail/service businesses.
It answers three kinds of questions through a single chat interface:
policy/FAQ questions from your documents (RAG), sales and performance questions from
your data (pandas analysis), and it remembers context across the conversation (SQLite).

Instead of hardcoded logic deciding which question goes where, the LLM itself picks
the right tool for each query via function-calling — that's the "agent" part.

## Tech Stack

| Purpose | Tool |
|---|---|
| LLM inference | [Groq API](https://console.groq.com) |
| Agent orchestration / tool-calling | LangChain |
| Vector database (RAG) | ChromaDB |
| Embeddings | Hugging Face `sentence-transformers` (multilingual, for Arabic support) |
| Document parsing | `pypdf`, `python-docx`, `unstructured` |
| Sales data analysis | pandas |
| Conversation memory / preferences | SQLite |
| Chat interface | Gradio |

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env                # then add your GROQ_API_KEY
python scripts/build_vector_db.py   # index the documents in data/documents/
python app.py                       # launch the Gradio chat UI
```

## Project Structure

business-assistant/
├── config.py # all settings/paths in one place
├── app.py # Gradio UI entry point
├── requirements.txt
├── .env.example
├── data/
│ ├── documents/ # policy/FAQ files (.txt/.pdf/.docx) -> RAG source
│ ├── sales/sample_sales.csv # sales data -> pandas analysis source
│ ├── chroma_db/ # generated: vector store (after build_vector_db.py)
│ └── memory.db # generated: conversation + preference history
├── scripts/
│ └── build_vector_db.py # (re)index documents into ChromaDB
└── src/
├── rag/
│ ├── ingest.py # load docs -> chunk -> embed -> store (LangChain + ChromaDB)
│ └── retriever.py # similarity search over stored chunks
├── analysis/
│ └── sales_functions.py # safe, predefined pandas queries
├── memory/
│ └── memory_store.py # SQLite: conversation history + preferences
└── agent/
├── llm_client.py # Groq API wrapper
├── router.py # tool schemas + dispatcher (the "routing" logic)
└── agent.py # orchestrates: history -> LLM -> tools -> answer


## How It Works

1. A user message comes in through the Gradio chat.
2. The agent (`src/agent/agent.py`) sends it to Groq along with a list of available tools.
3. The LLM decides — via function-calling, not keyword matching — whether it needs to
   search documents, query sales data, both, or neither.
4. Chosen tool run, their results go back to the LLM, which composes the final answer.
5. The exchange is logged to SQLite so future turns have conversation context.


## How to Run

1. **Clone or download the project**, then open a terminal inside the `business-assistant` folder.

2. **Create and activate a virtual environment**

   Windows (PowerShell):

    python -m venv venv
    venv\Scripts\activate


   Mac/Linux:

    python3 -m venv venv
    source venv/bin/activate

3. **Install dependencies**

    pip install -r requirements.txt

    
4. **Set up your API key**

   > **Note:** `.env` is intentionally not included in this repo (it would contain a private
   > API key). You must create your own local copy from the provided template:

    cp .env.example .env

    Then open `.env` and add your Groq API key (get one free at [console.groq.com](https://console.groq.com)):

    GROQ_API_KEY= your_actual_key_here
    GROQ_MODEL= openai/gpt-oss-120b

5. **Build the document index** (run once, and again whenever you update files in `data/documents/`)

    python scripts/build_vector_db.py

6. **Launch the app**

    python app.py

    Open the local URL it prints (usually `http://127.0.0.1:7860`) in your browser.