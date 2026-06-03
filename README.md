# DocuChat — RAG-based PDF Q&A Assistant

Ask questions about any PDF using Retrieval-Augmented Generation.

## Stack
- **Frontend**: Next.js 16, Tailwind CSS, React Dropzone
- **Backend**: FastAPI, LangChain, Pinecone
- **LLM**: OpenAI GPT-4o (streaming via SSE)

## Unique Features
- Multi-PDF upload with per-document source citation
- Streaming responses with live typing indicator
- Chunk relevance score displayed alongside answers
- Conversation memory across multiple Q&A turns

## Setup
```bash
# Backend
cd backend
cp .env.example .env        # fill in your keys
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd ../frontend
cp .env.local.example .env.local
npm install && npm run dev
```

## Architecture
```
User → Next.js → FastAPI → LangChain Retriever → Pinecone
                                    ↓
                             OpenAI GPT-4o (SSE stream)
```

## CV Talking Points
- Built a production RAG pipeline with vector search and citation tracing
- Implemented streaming LLM output to a React frontend via SSE
- Designed a multi-tenant session memory system for Q&A conversations
