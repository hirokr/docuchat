# DocuChat Backend

Production-grade FastAPI backend for RAG-based PDF question answering.

## Features

- Anonymous session-based document isolation
- API key authentication (`X-API-Key` header / WebSocket query param)
- PDF upload with background indexing (PyMuPDF → chunk → embed → Pinecone)
- WebSocket chat with typed streaming events
- PostgreSQL metadata + Pinecone vector retrieval filtered by `session_id`
- Groq (LangChain) streaming chat responses with citations and conversation memory

## Requirements

- Python 3.12+
- PostgreSQL 14+
- Pinecone index (dimension **3072** for `text-embedding-3-large`)
- Groq API key (chat) and OpenRouter API key (embeddings)

## Quick Start

### 1. Clone and enter backend

```bash
cd backend
```

### 2. Create virtual environment

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env with your secrets and database URL
```

Required variables:

| Variable | Description |
|---|---|
| `APP_API_KEY` | Shared secret sent as `X-API-Key` |
| `DATABASE_URL` | Local: `postgresql+asyncpg://...` — Neon: paste dashboard URL (`postgresql://...?sslmode=require`) |
| `GROQ_API_KEY` | Groq API key for chat |
| `GROQ_MODEL` | Groq model (default: `llama-3.3-70b-versatile`) |
| `OPENROUTER_API_KEY` | OpenRouter API key for embeddings |
| `OPENROUTER_EMBEDDING_MODEL` | Model id (default: `openai/text-embedding-3-large`) |
| `PINECONE_API_KEY` | Pinecone API key |
| `PINECONE_INDEX_NAME` | Pinecone index name |

### 4. Create PostgreSQL database

```bash
createdb docuchat
```

### 5. Run migrations

```bash
alembic upgrade head
```

### 6. Create Pinecone index

Create an index with:

- **Dimension:** 3072
- **Metric:** cosine
- **Metadata:** enable filtering on `session_id`

### 7. Start the server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or:

```bash
python main.py
```

Health check (no auth): `GET http://localhost:8000/health`

API docs (no auth): `http://localhost:8000/docs`

## API Overview

All REST endpoints require header:

```
X-API-Key: <APP_API_KEY>
```

### Sessions

```http
POST /api/sessions
→ { "sessionId": "uuid" }
```

### Documents

```http
POST /api/documents/upload
Content-Type: multipart/form-data
Fields: session_id, file

GET /api/documents/{session_id}
DELETE /api/documents/{document_id}
```

### WebSocket Chat

```
ws://localhost:8000/ws/chat/{session_id}?api_key=<APP_API_KEY>
```

Send:

```json
{
  "type": "question",
  "content": "What is this document about?",
  "conversation_id": "optional-uuid"
}
```

Receive typed events: `status`, `retrieval`, `thinking`, `token`, `citations`, `complete`, `error`.

## Project Structure

```
app/
├── api/              REST endpoints
├── websocket/        WebSocket chat + connection manager
├── core/             Config, auth, logging, exceptions, middleware
├── db/               SQLAlchemy engine and session
├── models/           ORM models
├── repositories/     Data access layer
├── schemas/          Pydantic request/response models
├── services/         Business logic (RAG, indexing, retrieval)
├── workers/          Background indexing tasks
└── main.py           FastAPI application factory
```

## Development

### Type checking

```bash
mypy app
```

### Linting

```bash
ruff check app
```

## Guardrails

- Max 3 PDFs per session
- Configurable max PDF file size
- PDF MIME and magic-byte validation
- Empty / textless PDF detection
- Session-scoped Pinecone retrieval (no cross-session access)
- WebSocket, Groq, OpenRouter (embeddings), and Pinecone timeouts
- Failed indexing marks document as `FAILED` and cleans up files

## License

Private — DocuChat portfolio project.
