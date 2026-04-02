# dev-archive

RAG pipeline for querying and analyzing software engineering case studies. Locally hosted with a FastAPI backend, React frontend, Pinecone vector DB, and SQLite for chat history.

---

## Prerequisites

- Python + [Poetry](https://python-poetry.org/)
- Node.js + npm
- Pinecone account
- OpenAI API key

## Environment Variables

Create a `.env` file in the project root:

```
OPENAI_API_KEY=[insert key]
PINECONE_API_KEY=[insert key]
PINECONE_INDEX_NAME=dev-archive
PINECONE_INDEX_NAMESPACE=case-studies
```

---

## Server (FastAPI · port 8000)

```bash
cd server
pipx install poetry        # skip if already installed
poetry config virtualenvs.in-project true
poetry install
eval $(poetry env activate)
fastapi dev
```

## Client (React · port 5173)

```bash
cd client
npm install
npm run dev
```

Open `http://localhost:5173` — API requests proxy automatically to port 8000.

---

## Pinecone Setup

1. Create a Pinecone index named `dev-archive`
2. Create a namespace `case-studies`
3. Run the ingestion script to embed and upsert chunks:

```bash
cd server
eval $(poetry env activate)
python ingestion/embed_upsert.py   # reads from ingestion/chunks.json
```

---

## Storage

| Store | Details |
|-------|---------|
| **Pinecone** | Vector embeddings for semantic search (`llama-text-embed-v2`, top-10 retrieval) |
| **SQLite** | Chat thread history saved to `server/history/chat_history.db` |
