# Product Requirements Document (PRD)

# Product Name

DocuChat

# Version

V1 (MVP)

# Product Vision

Enable anyone to understand large PDF documents through natural conversation instead of manual reading.

Visitors open the app, upload up to three PDFs, and ask questions in plain English. Answers are grounded in those documents and backed by citations. There is no account system—access is anonymous and scoped by client IP address.

# Problem Statement

Professionals, students, researchers, and knowledge workers spend significant time searching through lengthy PDFs to find specific information.

Common pain points include:

* PDFs contain hundreds of pages.
* Finding relevant information is slow.
* Users often miss important details.
* Traditional search only finds keywords, not meaning.
* Users cannot easily ask follow-up questions.

Current AI tools often lack reliable citations, making answers difficult to trust.

# Target Users

## Primary Users

### Students

Need help understanding textbooks, lecture notes, and research papers.

### Researchers

Need rapid extraction of insights from academic papers and reports.

### Legal Professionals

Need answers from contracts, compliance documents, and case files.

### Business Analysts

Need insights from reports, financial documents, and market research.

## Secondary Users

### HR Teams

Review policy documents and employee handbooks.

### Consultants

Analyze client documentation efficiently.

### Startup Founders

Extract information from investor materials and business documents.

# Jobs To Be Done

When I open DocuChat, I want to start immediately without creating an account so I can try the product with minimal friction.

When I upload PDFs, I want to use up to three documents at once so I can compare or cross-reference them in one conversation.

When I receive an answer, I want to know exactly where the information came from so I can trust it.

When I ask multiple questions, I want the system to remember previous context within my session so I don't need to repeat myself.

# Core Value Proposition

"Chat with up to three PDFs and get instant answers with citations—no signup required."

Key benefits:

* No authentication friction
* Save reading time
* Understand documents faster
* Trust answers through citations
* Query multiple documents in one session (within the 3-PDF limit)

# Access Model

## No Authentication

DocuChat does not provide:

* User registration
* Login or logout
* Passwords or OAuth
* User profiles or account settings

## IP-Scoped Usage

Each visitor is identified by **client IP address** (as seen by the backend, respecting `X-Forwarded-For` when behind a proxy).

Per IP address, the system enforces:

| Limit | Value |
| ----- | ----- |
| Maximum active PDFs | **3** |
| Maximum PDFs per upload batch | Remaining slots up to 3 total |
| Session ownership | All documents and chat sessions belong to that IP |

### Behavior When Limits Apply

* If an IP already has 3 PDFs indexed, new uploads are rejected with a clear message.
* The user must delete an existing PDF before uploading another.
* Returning visitors from the same IP see their existing documents and chat history (for that IP).
* Different IPs are fully isolated—no shared documents or sessions.

### Privacy & Fair-Use Notes

* IP-based scoping is a simple tenancy model for a portfolio/demo app, not strong identity.
* Users behind NAT or corporate networks may share limits with others on the same public IP.
* Document and chat data for an IP can be purged after a configurable retention period (post-MVP).

# Success Criteria

A visitor lands on the app, uploads at least one PDF, and receives a useful citation-backed answer within 60 seconds—without signing up.

# MVP Scope

## Must Have Features

### Anonymous Access (IP-Scoped)

* No signup or login
* Backend resolves client IP on every request
* Documents and sessions scoped to IP

### PDF Upload (Max 3 per IP)

Users can:

* Upload PDFs without an account
* Upload multiple PDFs in one batch, up to the remaining quota (3 total per IP)
* See a clear error when the 3-PDF limit is reached
* View upload and processing status
* Delete a PDF to free a slot for a new upload

### PDF Processing

System can:

* Extract text
* Chunk content
* Generate embeddings
* Index into vector database (namespace per IP)

### Chat Interface

Users can:

* Ask questions
* Receive answers
* Continue conversations within a session

### RAG Retrieval

System retrieves relevant chunks from the IP's uploaded PDFs before answering.

### Source Citations

Every answer includes:

* Source document
* Page number
* Relevant text excerpt

### Streaming Responses

Answers appear token-by-token.

### Conversation History (Per IP)

Users from the same IP can revisit previous sessions on return visits.

### Multi-PDF Retrieval

Answers can reference up to all PDFs uploaded by that IP (maximum 3).

### Relevance Scores

Display confidence/relevance for retrieved chunks.

# Nice-To-Have Features

Not required for MVP.

### PDF Highlighting

Jump directly to cited page sections.

### Chat Export

Export conversations as PDF or Markdown.

### Shared Links

Share a read-only snapshot of a conversation (no auth).

### Document Tagging

Categorize uploaded PDFs within the 3-document library.

### Citation Verification Panel

Advanced evidence inspection.

### Voice Questions

Speak instead of typing.

### OCR Support

Read scanned PDFs.

### Mobile Application

Native mobile apps.

### Custom AI Personas

Research assistant, legal assistant, tutor, etc.

### Data Retention Policy

Auto-delete documents and sessions for inactive IPs after N days.

# User Flow

## First-Time Visitor

Landing Page

↓

Open App (no signup)

↓

Upload PDF (1–3 files, within quota)

↓

Document Processing

↓

Ready State

↓

Ask Question

↓

Receive Streamed Answer

↓

View Citations

↓

Ask Follow-Up Questions

↓

Conversation Saved (scoped to IP)

## Returning Visitor (Same IP)

Open App

↓

See Existing Documents & Recent Chats

↓

Continue Conversation or Upload (if fewer than 3 PDFs)

↓

Review Previous Answers

## At PDF Limit

Open App

↓

3 PDFs Already Uploaded

↓

Upload Blocked with Message

↓

Delete One PDF (optional)

↓

Upload New PDF

# Screens

## Landing Page

Purpose:

Explain the product and drive visitors into the app.

Contains:

* Product explanation
* "No signup" messaging
* Demo examples
* CTA to start chatting

## Workspace / Dashboard

Contains:

* Uploaded documents (0–3)
* Remaining upload slots indicator (e.g. "2 of 3 PDFs used")
* Recent chats
* Create new session

## Upload Screen

Contains:

* Drag-and-drop uploader
* Upload progress
* Quota messaging when at limit

## Chat Screen

Contains:

* Message history
* Input box
* Streaming responses
* Citation panel
* Active documents for this session (subset of IP's PDFs)

## Document Library

Contains:

* Uploaded PDFs (max 3)
* Processing status
* Delete actions (frees a slot)

# User Stories

## Start Without Account

As a visitor, I want to use DocuChat immediately without registering so I can evaluate it quickly.

## Upload Documents

As a visitor, I want to upload up to three PDFs for my IP so I can ask questions about them.

## Respect PDF Quota

As a visitor, I want a clear message when I've reached three PDFs so I know I must delete one to upload another.

## Ask Questions

As a visitor, I want natural language answers so I don't need to search manually.

## Verify Sources

As a visitor, I want citations so I can verify AI-generated responses.

## Continue Conversations

As a visitor, I want memory across questions so I can explore a topic naturally.

## Return Later

As a returning visitor from the same network, I want to see my previous documents and chats without logging in.

# Functional Requirements

## Client Identity

* Resolve client IP on each API request
* Support `X-Forwarded-For` / `X-Real-IP` when configured for reverse proxies
* Store `client_ip` (normalized string) on documents, sessions, and related records
* Reject or rate-limit requests with missing/untrusted IP in production (configurable)

## Upload System

Maximum file size configurable.

Maximum PDFs per IP: **3** (hard limit for MVP).

Supported format:

* PDF

Validation:

* File size
* File type
* Per-IP document count before accept

## Retrieval System

Must:

* Retrieve top relevant chunks
* Filter by selected documents (within IP's library)
* Scope all vector search to the IP's Pinecone namespace
* Return relevance scores

## Answer Generation

Must:

* Use retrieved context only
* Stream output
* Include citations

## Session Memory

Must:

* Remember previous conversation turns within a session
* Support follow-up questions
* Associate sessions with `client_ip`, not `user_id`

# Analytics & Metrics

## North Star Metric

Weekly Answered Questions

Definition:

Total number of successful questions answered (per IP session).

## Supporting Metrics

### Activation Rate

Visitors who:

Upload PDF + Ask First Question

### Time To First Answer

Target:

Under 60 seconds

### Retention (Same IP Return)

Visitors who return from the same IP within 7 days

### Average Questions Per Session

Target:

5+

### Citation Engagement Rate

Percentage of visitors clicking citations.

### Upload Success Rate

Target:

95%+

### Quota Hit Rate

Percentage of upload attempts rejected due to 3-PDF limit (product signal for UX copy).

# Monetization Strategy

MVP is a **portfolio / demo** product with no paid tiers.

Future options (post-MVP, if productized):

* Optional API keys for higher limits
* Hosted enterprise with SSO (separate product line)
* Sponsored or self-hosted deployments with configurable quotas

V1 does not implement billing or plans.

# Risks

## Hallucinations

Mitigation:

Force citation-backed responses.

## Long Processing Times

Mitigation:

Background indexing.

## Large PDF Costs

Mitigation:

Chunk optimization and caching.

## User Trust

Mitigation:

Show evidence alongside answers.

## IP Spoofing / Shared NAT

Mitigation:

Accept as demo limitation; document in README. For production, consider optional API keys or browser fingerprinting (out of MVP scope).

## Abuse (Upload / Chat Spam)

Mitigation:

Per-IP rate limits on upload and chat endpoints; max 3 PDFs caps storage abuse.

# Non-Goals (Version 1)

We are intentionally NOT building:

* User authentication (register, login, JWT, OAuth)
* User accounts or profiles
* Team workspaces or shared libraries across users
* Per-user billing or subscription tiers
* OCR for scanned documents
* Mobile apps
* Document editing
* Google Drive integration
* Dropbox integration
* Slack integration
* Voice chat
* AI agents
* Multi-modal image understanding
* Fine-tuned models
* Public document search
* Enterprise SSO
* Custom LLM selection

# Product Roadmap

## V1

* Anonymous IP-scoped access
* Up to 3 PDFs per IP
* RAG retrieval
* Citations
* Streaming chat
* Memory
* Document delete to free quota

## V1.5

* OCR
* Chat export
* Better citation viewer
* Configurable data retention per IP

## V2

* Optional API keys for power users
* Admin dashboard for abuse monitoring

## V3

* Enterprise knowledge base
* Connectors
* Multi-modal document intelligence

# Product Positioning

For people who work with PDFs regularly,

DocuChat is an AI-powered document assistant that lets anyone ask questions and receive citation-backed answers instantly—no account required.

Unlike generic chatbots, DocuChat grounds every response in your uploaded documents (up to three per visit) and shows exactly where the information came from.

Unlike signup-heavy tools, DocuChat optimizes for zero friction: open the app, upload, and chat.
