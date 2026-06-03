# Technical Architecture Document

# DocuChat — RAG-Based PDF Q&A Assistant (Anonymous, IP-Scoped)

---

# 1. System Overview

DocuChat is a Retrieval-Augmented Generation (RAG) platform that allows **anonymous visitors** to upload up to **three PDFs per client IP address** and ask questions about them using natural language.

There is **no authentication layer**. Tenancy is enforced by **client IP**: documents, vector namespaces, and chat sessions all belong to a normalized IP string resolved on each request.

The system extracts text from uploaded PDFs, creates embeddings, stores them in Pinecone under an IP-specific namespace, retrieves relevant chunks during queries, and uses GPT-4o to generate grounded answers with source citations.

### Core Goals

* Zero-friction anonymous access
* Hard limit of 3 PDFs per IP
* Multi-document knowledge base (within that limit)
* Fast semantic retrieval
* Streaming AI responses
* Source citation tracing
* Conversation memory per IP/session
* Production-ready foundation without user accounts

---

# 2. High-Level Architecture

```text
┌───────────────┐
│   Browser     │
└───────┬───────┘
        │
        ▼
┌────────────────────┐
│ Next.js Frontend   │
│ - Upload PDFs      │
│ - Quota UI (3 max) │
│ - Chat Interface   │
│ - SSE Client       │
└─────────┬──────────┘
          │ REST/SSE
          ▼
┌────────────────────┐
│ FastAPI Backend    │
│                    │
│ IP Resolution      │
│ Quota Enforcement  │
│ Upload Service     │
│ Chat Service       │
│ Memory Service     │
│ Retrieval Service  │
└─────────┬──────────┘
          │
 ┌────────┴────────┐
 │                 │
 ▼                 ▼
PostgreSQL      Pinecone
Metadata        Vector Store
(per client_ip) (namespace = client_ip)

          │
          ▼
     OpenAI GPT-4o
```

---

# 3. Recommended Tech Stack

## Frontend

### Next.js 16

Reason:

* Server Components
* App Router
* Streaming support
* SEO ready
* Production-grade routing

---

### TypeScript

Reason:

* Type safety
* Better maintainability
* Easier scaling

---

### Tailwind CSS

Reason:

* Fast development
* Small bundle size
* Consistent design system

---

### React Dropzone

Reason:

* Drag-and-drop uploads
* File validation
* Progress handling

---

### TanStack Query

Reason:

* API caching
* Retry support
* Optimistic updates

---

### Zustand

Reason:

* Lightweight state management
* Ideal for chat state

---

### shadcn/ui

Reason:

* Production-ready components
* Accessible
* Easy customization

---

# Backend

## FastAPI

Reason:

* High performance
* Async-first
* SSE support
* Excellent Python ecosystem
* Easy middleware for IP extraction

---

## LangChain

Reason:

* Retrieval orchestration
* Memory handling
* Prompt management
* Future agent support

---

## Pinecone

Reason:

* Managed vector database
* Fast similarity search
* Metadata filtering
* Namespace isolation per IP

---

## PostgreSQL

Reason:

Application metadata must not live only in Pinecone.

Store:

* Documents (scoped by `client_ip`)
* Chat sessions
* Messages
* Citations
* Chunk-to-vector mappings

Do **not** store user accounts or password hashes.

---

## SQLAlchemy + Alembic

Reason:

* ORM
* Migrations
* Production standard

---

## Celery + Redis

Recommended for production.

Used for:

* PDF processing
* Embedding generation
* Background indexing

Without this, large PDFs block requests.

---

# AI Layer

## OpenAI GPT-4o

Reason:

* Strong reasoning
* Fast streaming
* Excellent RAG performance

---

## Embedding Model

Recommended:

### text-embedding-3-large

Reason:

* High retrieval quality
* Good multilingual support

---

# 4. Tenancy & Quota Model

## Client IP Resolution

On every mutating and data-access request:

1. Read `X-Forwarded-For` (first hop) or `X-Real-IP` when `TRUST_PROXY_HEADERS=true`
2. Else use `request.client.host`
3. Normalize to a stable string (e.g. strip port, lowercase IPv6)

```python
# Dependency: get_client_ip() -> str
```

## Quota Rules

| Rule | Implementation |
| ---- | -------------- |
| Max PDFs per IP | `COUNT(documents WHERE client_ip = ? AND deleted_at IS NULL) < 3` before upload |
| Document ownership | All queries filter `client_ip = current_ip` |
| Session ownership | `chat_sessions.client_ip = current_ip` |
| Vector isolation | Pinecone `namespace = client_ip` |
| Delete frees slot | Soft or hard delete document + purge vectors for that doc |

## Security Posture (No Auth)

* **Not** a multi-user security boundary—IPs can be shared (NAT) or spoofed if headers are trusted incorrectly.
* Always validate `client_ip` on document/session/chat access; never accept `client_ip` from request body.
* Rate-limit upload and chat per IP.
* Configure proxy trust explicitly in production.

---

# 5. Data Flow

## Upload Flow

```text
Visitor Uploads PDF
       │
       ▼
Resolve client_ip
       │
       ▼
Check count(documents for ip) < 3
       │ (else 409 Quota Exceeded)
       ▼
Next.js → FastAPI
       │
       ▼
Store PDF (disk or object storage)
       │
       ▼
Extract Text → Chunk → Embed
       │
       ▼
Upsert to Pinecone (namespace = client_ip)
       │
       ▼
Save metadata in PostgreSQL (client_ip, ...)
```

---

## Question Flow

```text
Visitor Question
      │
      ▼
Resolve client_ip
      │
      ▼
Load session (verify session.client_ip == ip)
      │
      ▼
Conversation Memory
      │
      ▼
Retriever Query (namespace = client_ip, filter document_ids)
      │
      ▼
Pinecone Search → Top K Chunks
      │
      ▼
GPT-4o Prompt → SSE Stream → Frontend
```

---

# 6. Folder Structure

## Frontend

```text
frontend/
│
├── public/
│
├── src/
│   ├── app/
│   │   ├── page.tsx              # Landing
│   │   ├── workspace/            # Documents + chats (no auth routes)
│   │   ├── chat/
│   │   └── layout.tsx
│   │
│   ├── components/
│   │   ├── chat/
│   │   ├── upload/
│   │   │   ├── UploadZone.tsx
│   │   │   ├── UploadProgress.tsx
│   │   │   └── QuotaBanner.tsx   # "2 / 3 PDFs used"
│   │   └── ui/
│   │
│   ├── hooks/
│   ├── services/
│   ├── store/
│   └── types/
│
├── package.json
└── next.config.ts
```

No `login/`, `signup/`, or `settings/account` routes.

---

## Backend

```text
backend/
│
├── app/
│   │
│   ├── api/
│   │   ├── chat.py
│   │   ├── upload.py
│   │   ├── sessions.py
│   │   └── documents.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   └── client_ip.py          # IP extraction dependency
│   │
│   ├── models/
│   │   ├── document.py
│   │   ├── chunk.py
│   │   ├── session.py
│   │   └── message.py
│   │   # NO user.py
│   │
│   ├── schemas/
│   │
│   ├── services/
│   │   ├── quota.py              # enforce 3 PDF limit
│   │   ├── pdf_parser.py
│   │   ├── chunker.py
│   │   ├── embeddings.py
│   │   ├── retriever.py
│   │   ├── memory.py
│   │   ├── citation.py
│   │   └── chat_service.py
│   │
│   ├── workers/
│   │   └── indexing_tasks.py
│   │
│   └── main.py
│
├── uploads/                       # or S3/R2 in production
├── alembic/
└── requirements.txt
```

No `security.py` JWT helpers unless added later for optional API keys.

---

# 7. Database Schema

Use PostgreSQL.

There is **no `users` table**.

---

## documents

| Field         | Type      | Notes |
| ------------- | --------- | ----- |
| id            | UUID      | PK |
| client_ip     | VARCHAR   | Indexed; tenancy key |
| file_name     | TEXT      | Storage path key |
| original_name | TEXT      | Display name |
| file_size     | BIGINT    | |
| page_count    | INTEGER   | Nullable until processed |
| upload_status | TEXT      | pending / processing / ready / failed |
| created_at    | TIMESTAMP | |
| deleted_at    | TIMESTAMP | Nullable; soft delete frees quota |

Constraints:

* Application enforces `COUNT(*) WHERE client_ip = ? AND deleted_at IS NULL <= 3`
* Optional DB trigger or partial unique index patterns if desired later

---

## document_chunks

| Field              | Type      |
| ------------------ | --------- |
| id                 | UUID      |
| document_id        | UUID      |
| pinecone_vector_id | TEXT      |
| page_number        | INTEGER   |
| chunk_index        | INTEGER   |
| chunk_text         | TEXT      |
| created_at         | TIMESTAMP |

Purpose:

Maps Pinecone vectors back to PDFs for citations.

---

## chat_sessions

| Field      | Type      |
| ---------- | --------- |
| id         | UUID      |
| client_ip  | VARCHAR   | Indexed |
| title      | TEXT      |
| created_at | TIMESTAMP |

---

## session_documents

| Field       | Type |
| ----------- | ---- |
| session_id  | UUID |
| document_id | UUID |

Purpose:

A session can query one or more of the IP's PDFs (up to 3 total in library).

---

## messages

| Field       | Type      |
| ----------- | --------- |
| id          | UUID      |
| session_id  | UUID      |
| role        | TEXT      | user / assistant / system |
| content     | TEXT      |
| token_count | INTEGER   |
| created_at  | TIMESTAMP |

---

## citations

| Field           | Type  |
| --------------- | ----- |
| id              | UUID  |
| message_id      | UUID  |
| chunk_id        | UUID  |
| relevance_score | FLOAT |

---

## session_memory

| Field      | Type      |
| ---------- | --------- |
| session_id | UUID      |
| summary    | TEXT      |
| updated_at | TIMESTAMP |

---

# 8. Pinecone Structure

**Namespace per client IP** (not per user id).

```text
namespace: <normalized_client_ip>
```

Example:

```text
namespace: "203.0.113.42"
```

Metadata on each vector:

```json
{
  "document_id": "uuid",
  "document_name": "contract.pdf",
  "page": 12,
  "chunk_index": 34,
  "client_ip": "203.0.113.42"
}
```

On document delete:

* Delete all vectors where `document_id` matches in that namespace
* Or delete-by-filter if supported

---

# 9. Chunking Strategy

```text
Chunk Size: 1000 chars
Overlap: 200 chars
```

Use:

```python
RecursiveCharacterTextSplitter
```

---

# 10. Memory Architecture

Do NOT send full chat history on every request.

### Store

* Last N messages (e.g. 10)
* Rolling `session_memory.summary`

Reduces token cost while preserving follow-up context.

---

# 11. API Design

All endpoints infer `client_ip` server-side. Clients never send `client_ip` in the body.

## Upload

```http
POST /api/documents/upload
```

Precondition: fewer than 3 active documents for this IP.

Returns `201`:

```json
{
  "documentId": "uuid",
  "quota": { "used": 2, "max": 3 }
}
```

Returns `409` when quota exceeded:

```json
{
  "error": "pdf_quota_exceeded",
  "message": "Maximum 3 PDFs per visitor. Delete a document to upload another.",
  "quota": { "used": 3, "max": 3 }
}
```

---

## List Documents

```http
GET /api/documents
```

Returns only documents for resolved IP.

---

## Delete Document

```http
DELETE /api/documents/{document_id}
```

Verifies `document.client_ip == current_ip`, removes file, vectors, and chunks; frees quota slot.

---

## Create Session

```http
POST /api/sessions
```

Body (optional):

```json
{
  "title": "Contract review",
  "documentIds": ["uuid1", "uuid2"]
}
```

`documentIds` must all belong to current IP.

---

## Send Message / Stream

```http
POST /api/chat
```

```json
{
  "sessionId": "uuid",
  "question": "What is RAG?"
}
```

```http
GET /api/chat/stream?sessionId=...
```

SSE token stream.

---

## Quota Status

```http
GET /api/quota
```

```json
{
  "pdfs": { "used": 2, "max": 3 },
  "canUpload": true
}
```

---

# 12. Environment Variables

## Backend

```env
OPENAI_API_KEY=

PINECONE_API_KEY=
PINECONE_INDEX_NAME=

DATABASE_URL=

REDIS_URL=

UPLOAD_DIR=uploads

EMBEDDING_MODEL=text-embedding-3-large
CHAT_MODEL=gpt-4o

MAX_FILE_SIZE_MB=50
MAX_PDF_PAGES=500
MAX_PDFS_PER_IP=3

TRUST_PROXY_HEADERS=true

ENVIRONMENT=development
```

Removed from MVP:

* `JWT_SECRET`
* `JWT_ALGORITHM`
* `SECRET_KEY` (unless needed for session cookies later—not required without auth)

---

## Frontend

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_MAX_UPLOAD_MB=50
NEXT_PUBLIC_MAX_PDFS=3
```

---

# 13. Rate Limiting & Abuse

Without auth, rely on:

* **3 PDF cap** per IP (storage bound)
* Rate limits on `POST /api/documents/upload` and `POST /api/chat` per IP (e.g. slowapi + Redis)
* Max file size and page count
* Optional global daily spend cap on OpenAI (ops config)

---

# 14. Production Improvements

### Object Storage

Store PDFs in S3 / R2 / UploadThing instead of local disk.

### Reverse Proxy

Terminate TLS at nginx/Caddy/Cloudflare; set `TRUST_PROXY_HEADERS` and forward `X-Forwarded-For`.

### Observability

* Sentry
* PostHog or Plausible (anonymous events; include hashed IP only if privacy policy allows)

### Data Retention

Cron job to delete documents/sessions older than N days per inactive IP.

---

# 15. Resume / CV Impact

This project demonstrates:

* End-to-end RAG architecture design
* Vector search with **namespace isolation** without user accounts
* **Quota enforcement** at API and data layers
* Streaming AI systems with SSE
* Multi-document citation tracing (up to 3 PDFs)
* Conversation memory management
* Production-grade FastAPI services
* Pinecone integration
* LLM cost optimization strategies
* Pragmatic tenancy for demo/portfolio apps (IP-scoped)

For a portfolio project, this architecture is strong and simpler than full auth. For a production SaaS with billing, you would add optional accounts or API keys on top of this foundation—not replace the RAG core.
