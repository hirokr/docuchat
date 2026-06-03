from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
router = APIRouter()

class ChatRequest(BaseModel):
    question: str
    session_id: str

@router.post("/chat")
async def chat(req: ChatRequest):
    # TODO: retrieve top-k chunks → stream LLM response via SSE
    return {"answer": "placeholder", "sources": []}
