from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.rag_service import rag_service

router = APIRouter()

class ChatRequest(BaseModel):
    question: str
    user_id: str

class ChatResponse(BaseModel):
    answer: str
    sources_used: list[str]
    chunks_retrieved: int

@router.post("/chat/", response_model=ChatResponse)
def chat(request: ChatRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    if len(request.question) > 500:
        raise HTTPException(status_code=400, detail="Question too long")
    
    result = rag_service.answer(request.question)
    return ChatResponse(**result)
