For an AI coding workflow, the best approach is not one ticket per page, but one ticket per deployable capability. The tickets below are ordered in the sequence I would actually build them.

**Access model for V1:** No authentication. Each visitor is identified by **client IP**. Each IP may have at most **3 active PDFs** and all documents/sessions/vectors are scoped to that IP.

# DOCUCHAT - FEATURE TICKET LIST

## EPIC 1: Project Foundation

### TICKET-001: Backend FastAPI Project Setup

Priority: Must-Have

Description:

Create the FastAPI backend foundation with environment configuration, API routing structure, dependency injection, health check endpoint, and startup configuration.

Acceptance Criteria:

* FastAPI application starts successfully
* Environment variables load correctly
* Health endpoint returns 200 status
* API routes organized by module
* CORS configured for frontend
* Structured logging enabled

Dependencies:

None

Prompt For AI Coding Tool:

Build a production-ready FastAPI application with modular routing, environment configuration using pydantic-settings, health endpoint, CORS support, logging middleware, and project structure for future APIs.

---

### TICKET-002: PostgreSQL Database Integration

Priority: Must-Have

Description:

Configure PostgreSQL connection using SQLAlchemy and Alembic migrations.

Acceptance Criteria:

* Database connection established
* Alembic migration system works
* Base models created
* Connection pooling enabled
* Migration command executes successfully

Dependencies:

TICKET-001

Prompt:

Implement PostgreSQL integration using SQLAlchemy 2.0 and Alembic. Create database session management, migration setup, and dependency injection for database access.

---

### TICKET-003: Frontend Next.js Foundation

Priority: Must-Have

Description:

Initialize Next.js frontend with Tailwind CSS, TypeScript, API client, and application layout. No auth routes.

Acceptance Criteria:

* Application runs locally
* Tailwind configured
* Global layout created
* API client configured
* Error boundary implemented
* Landing and workspace routes exist (no login/signup pages)

Dependencies:

None

Prompt:

Create a Next.js 16 application using App Router, Tailwind CSS, TypeScript, Axios API client, shared layout, loading states, and error boundaries. Do not add authentication pages.

---

## EPIC 2: IP-Scoped Tenancy & Quotas

### TICKET-004: Client IP Resolution Middleware

Priority: Must-Have

Description:

Implement a FastAPI dependency that resolves the visitor's client IP on every request, with optional support for reverse-proxy headers.

Acceptance Criteria:

* `get_client_ip()` dependency returns normalized IP string
* Uses `X-Forwarded-For` / `X-Real-IP` when `TRUST_PROXY_HEADERS=true`
* Falls back to `request.client.host`
* IP never accepted from request body or query params
* Unit tests cover direct connection and proxied requests

Dependencies:

TICKET-001

Prompt:

Add FastAPI middleware/dependency for client IP extraction. Support configurable proxy trust, normalize IPv4/IPv6, and inject `client_ip` into route handlers. Document env vars.

---

### TICKET-005: PDF Quota Service (3 per IP)

Priority: Must-Have

Description:

Enforce a maximum of three active PDFs per client IP across upload and list APIs.

Acceptance Criteria:

* `GET /api/quota` returns `{ used, max: 3, canUpload }`
* Upload rejected with 409 when IP already has 3 active documents
* Active count excludes soft-deleted documents
* Deleting a document decrements used count
* Quota logic covered by unit tests

Dependencies:

TICKET-002
TICKET-004

Prompt:

Implement quota service counting documents by `client_ip`. Expose quota endpoint and integrate checks into upload flow. Return structured 409 errors with clear messages.

---

### TICKET-006: Rate Limiting (Per IP)

Priority: Should-Have

Description:

Protect upload and chat endpoints from abuse using per-IP rate limits.

Acceptance Criteria:

* Upload endpoint rate limited (configurable)
* Chat endpoint rate limited (configurable)
* Returns 429 with retry guidance
* Uses Redis or in-memory store for MVP

Dependencies:

TICKET-004

Prompt:

Add per-IP rate limiting to upload and chat routes using slowapi or custom middleware with Redis. Make limits configurable via environment variables.

---

## EPIC 3: Document Management & RAG

### TICKET-007: Document Storage Model

Priority: Must-Have

Description:

Create database models for documents scoped by `client_ip` (no user table).

Acceptance Criteria:

* `documents` table created with `client_ip` indexed
* Upload status tracked
* Soft delete via `deleted_at` frees quota slot
* Metadata stored (name, size, page count)
* Repository methods filter by `client_ip`
* No `user_id` column

Dependencies:

TICKET-002

Prompt:

Create document schema with client_ip tenancy, upload status, soft delete, metadata fields, and repository methods. Do not create a users table.

---

### TICKET-008: PDF Upload API

Priority: Must-Have

Description:

Allow anonymous visitors to upload PDF files, subject to the 3-PDF-per-IP quota.

Acceptance Criteria:

* PDF validation works
* Size limits enforced
* Quota checked before save (TICKET-005)
* File saved successfully
* Upload metadata recorded with `client_ip`
* Upload response returns document ID and quota status
* 409 returned when quota exceeded

Dependencies:

TICKET-007
TICKET-004
TICKET-005

Prompt:

Implement PDF upload endpoint with validation, storage, metadata persistence, client_ip scoping, and quota enforcement. No JWT or ownership by user id.

---

### TICKET-009: PDF Upload UI

Priority: Must-Have

Description:

Create drag-and-drop upload interface with quota awareness.

Acceptance Criteria:

* Drag and drop supported
* Upload progress shown
* Error handling visible (including quota exceeded)
* Multi-file upload respects remaining slots (e.g. 2 slots left → max 2 files)
* Quota banner shows "X / 3 PDFs used"
* Success state displayed

Dependencies:

TICKET-008

Prompt:

Build PDF upload component using React Dropzone. Show quota from GET /api/quota, disable upload at limit, and display friendly error on 409.

---

### TICKET-010: Document Delete API & UI

Priority: Must-Have

Description:

Allow visitors to delete a PDF to free a quota slot.

Acceptance Criteria:

* `DELETE /api/documents/{id}` verifies `client_ip` ownership
* File removed from storage
* Vectors removed from Pinecone for that document
* DB record soft-deleted
* UI delete action with confirmation
* Quota updates after delete

Dependencies:

TICKET-007
TICKET-012 (vector delete can be stubbed initially, completed after Pinecone ticket)

Prompt:

Implement document delete flow: ownership check by client_ip, storage cleanup, soft delete, and UI integration with quota refresh.

---

### TICKET-011: PDF Text Extraction Service

Priority: Must-Have

Description:

Extract text and metadata from uploaded PDFs.

Acceptance Criteria:

* PDF pages parsed
* Text extracted
* Page numbers preserved
* Errors handled
* Metadata returned

Dependencies:

TICKET-008

Prompt:

Implement PDF extraction service using PyMuPDF. Extract text, page numbers, metadata, and handle corrupted files gracefully.

---

### TICKET-012: Chunking Service

Priority: Must-Have

Description:

Split extracted PDF text into retrieval chunks.

Acceptance Criteria:

* Recursive chunking implemented
* Chunk overlap configured
* Metadata preserved
* Chunk indexes stored

Dependencies:

TICKET-011

Prompt:

Build a LangChain chunking service using RecursiveCharacterTextSplitter with configurable chunk size and overlap while preserving document metadata.

---

### TICKET-013: Pinecone Integration

Priority: Must-Have

Description:

Create vector database integration with **namespace per client IP**.

Acceptance Criteria:

* Pinecone connection established
* Namespace = normalized `client_ip`
* Upsert works
* Query scoped to namespace
* Metadata stored (document_id, page, chunk_index)
* Delete-by-document works in namespace

Dependencies:

TICKET-012

Prompt:

Implement Pinecone integration with namespace per client_ip, vector upsert, metadata filtering, similarity search, and document-level vector deletion.

---

### TICKET-014: Embedding Pipeline

Priority: Must-Have

Description:

Generate embeddings and index chunks under the IP namespace.

Acceptance Criteria:

* OpenAI embeddings generated
* Chunks indexed in correct Pinecone namespace
* Failures retried
* Status updates tracked on document record

Dependencies:

TICKET-013

Prompt:

Build document indexing pipeline using OpenAI text-embedding-3-large and Pinecone with client_ip namespace and retry handling.

---

### TICKET-015: Document Library UI

Priority: Must-Have

Description:

Allow visitors to view and manage their IP's uploaded documents (max 3).

Acceptance Criteria:

* List documents for current IP only
* Show processing status
* Delete documents
* Show quota indicator
* Empty state when no documents

Dependencies:

TICKET-007
TICKET-009
TICKET-010

Prompt:

Build document library page listing up to 3 PDFs with status, delete action, and quota banner. No user account UI.

---

## EPIC 4: Chat & Retrieval

### TICKET-016: Chat Session Model

Priority: Must-Have

Description:

Create chat_sessions, messages, session_documents, session_memory, and citations tables—all scoped by `client_ip` on sessions (no user_id).

Acceptance Criteria:

* Tables migrated
* Sessions linked to `client_ip`
* session_documents supports multi-PDF within IP library
* Messages and citations related correctly

Dependencies:

TICKET-002

Prompt:

Create chat schema with client_ip on sessions, many-to-many session_documents, messages, citations, and session_memory. No users table.

---

### TICKET-017: Session Management API

Priority: Must-Have

Description:

Create, list, rename, and delete chat sessions for the current IP.

Acceptance Criteria:

* CRUD endpoints work
* Sessions filtered by `client_ip`
* documentIds in create body validated against IP's documents
* Cross-IP session access returns 404

Dependencies:

TICKET-016
TICKET-004

Prompt:

Implement session APIs with client_ip ownership checks and optional document selection from the IP's library (max 3 docs total).

---

### TICKET-018: Retriever Service

Priority: Must-Have

Description:

Retrieve top-k chunks from Pinecone using IP namespace and document filters.

Acceptance Criteria:

* Search only in namespace for current IP
* Metadata filtering by session document IDs
* Relevance scores returned
* No cross-IP data leakage in tests

Dependencies:

TICKET-013
TICKET-017

Prompt:

Build retriever that queries Pinecone with namespace=client_ip and filters by document_ids. Return scored chunks for RAG.

---

### TICKET-019: Conversation Memory Service

Priority: Must-Have

Description:

Store recent messages and maintain rolling summaries per session.

Acceptance Criteria:

* Last N messages loaded
* Summary updated after turns
* Session ownership verified via client_ip

Dependencies:

TICKET-016
TICKET-017

Prompt:

Implement conversation memory with recent message window and rolling session summary. Enforce session belongs to client_ip.

---

### TICKET-020: RAG Prompt Builder

Priority: Must-Have

Description:

Combine retrieved chunks, citations, memory, and user question into a structured GPT-4o prompt.

Acceptance Criteria:

* Context-only answering instructions
* Citation format defined
* Multi-document context supported (up to 3 PDFs)

Dependencies:

TICKET-018
TICKET-019

Prompt:

Build RAG prompt template with retrieved chunks, memory summary, and citation requirements for GPT-4o.

---

### TICKET-021: Streaming Chat API (SSE)

Priority: Must-Have

Description:

Stream GPT-4o responses token-by-token; verify session belongs to IP.

Acceptance Criteria:

* SSE stream works end-to-end
* Session/IP ownership enforced
* Citations persisted after completion
* Errors handled mid-stream

Dependencies:

TICKET-020
TICKET-004

Prompt:

Implement streaming chat endpoint with SSE, OpenAI streaming, client_ip session checks, and citation persistence.

---

### TICKET-022: Citation Tracking Service

Priority: Must-Have

Description:

Persist chunk references used for answer generation.

Acceptance Criteria:

* Citations linked to assistant messages
* Relevance scores stored
* Chunk → document/page mapping correct

Dependencies:

TICKET-016
TICKET-021

Prompt:

Save citation records after each assistant turn with chunk_id and relevance_score for UI display.

---

### TICKET-023: Chat UI

Priority: Must-Have

Description:

Build chat interface with messages, input box, scrolling, and session history.

Acceptance Criteria:

* Create/select sessions
* Message list renders user and assistant roles
* No login gate
* Works for returning IP with existing sessions

Dependencies:

TICKET-017
TICKET-021

Prompt:

Build chat page with session sidebar, message thread, and input. Integrate session APIs without authentication.

---

### TICKET-024: Streaming Response UI

Priority: Must-Have

Description:

Display live token streaming and typing indicators.

Acceptance Criteria:

* SSE client consumes stream
* Tokens append in real time
* Loading and error states handled

Dependencies:

TICKET-021
TICKET-023

Prompt:

Implement useSSE hook and streaming message bubble with typing indicator.

---

### TICKET-025: Citation Panel UI

Priority: Must-Have

Description:

Show source document, page number, excerpt, and relevance score.

Acceptance Criteria:

* Citations listed per assistant message
* Click expands excerpt
* Document name and page visible

Dependencies:

TICKET-022
TICKET-023

Prompt:

Build citation panel/cards linked to assistant messages with page and excerpt display.

---

### TICKET-026: Multi-PDF Retrieval Support

Priority: Must-Have

Description:

Allow a session to query multiple of the IP's uploaded PDFs (up to 3 in library).

Acceptance Criteria:

* Session can attach 1–3 document IDs
* Retriever searches across selected docs
* Answers cite multiple sources when relevant

Dependencies:

TICKET-018
TICKET-017

Prompt:

Enable multi-document selection when creating a session and filter retrieval across all selected PDFs for that IP.

---

## EPIC 5: Production Readiness

### TICKET-027: Background Indexing Worker

Priority: Should-Have

Move extraction, chunking, and embedding into Celery workers.

Dependencies:

TICKET-014

---

### TICKET-028: Error Handling Framework

Priority: Must-Have

Centralized backend and frontend error handling (including 409 quota and 429 rate limit).

Dependencies:

TICKET-001
TICKET-003

---

### TICKET-029: Analytics Events (Anonymous)

Priority: Should-Have

Track uploads, first question, citations opened, quota exceeded—no user id, optional hashed IP.

Dependencies:

TICKET-008
TICKET-021

---

### TICKET-030: Monitoring & Logging

Priority: Should-Have

Integrate logging, request tracing, and error monitoring.

Dependencies:

TICKET-001

---

### TICKET-031: Data Retention Job

Priority: Nice-To-Have

Auto-delete old documents/sessions per IP after configurable inactivity.

Dependencies:

TICKET-007
TICKET-016

---

## EPIC 6: Post-MVP

### TICKET-032: PDF Highlight Viewer

Priority: Nice-To-Have

Jump directly to cited pages and highlighted sections.

---

### TICKET-033: Chat Export

Priority: Nice-To-Have

Export conversations as PDF and Markdown.

---

### TICKET-034: Shared Conversation Links

Priority: Nice-To-Have

Read-only public snapshot of a session (no auth).

---

### TICKET-035: OCR Support

Priority: Nice-To-Have

Extract text from scanned PDFs.

---

### TICKET-036: Optional API Keys

Priority: Nice-To-Have

Higher limits for programmatic access without full user accounts.

---

### TICKET-037: Voice Questions

Priority: Nice-To-Have

Speech-to-text input.

---

### TICKET-038: Google Drive Integration

Priority: Nice-To-Have

Import PDFs from Drive (still subject to 3-PDF quota per IP).

---

### TICKET-039: Dropbox Integration

Priority: Nice-To-Have

Import PDFs from Dropbox.

---

### TICKET-040: AI Research Assistant Mode

Priority: Nice-To-Have

Cross-document synthesis across up to 3 PDFs.

---

## Removed from V1 (was in earlier drafts)

The following are **explicitly out of scope** for this ticket list:

* User registration, login, logout
* JWT / OAuth / password hashing
* `users` table and user-scoped ownership
* Team workspaces and role permissions
* Monetization tiers tied to user accounts

---

## Recommended MVP Build Set

For a hackathon or portfolio project, build **TICKET-001 through TICKET-026**.

That is the smallest set that delivers:

**Open app (no signup) → Upload up to 3 PDFs per IP → Ask questions → Get citation-backed answers.**

Tickets 027–031 are production polish. Tickets 032–040 are expansion.
