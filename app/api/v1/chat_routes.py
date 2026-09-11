from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.rag_service import rag_service
from app.services.safety_filter import safety_filter

router = APIRouter()


class ChatRequest(BaseModel):
    question: str
    user_id: str


class ChatResponse(BaseModel):
    answer: str
    sources_used: list[str]
    chunks_retrieved: int
    safety_flagged: bool
    flag_type: str | None


@router.post("/chat/", response_model=ChatResponse)
def chat(request: ChatRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    if len(request.question) > 500:
        raise HTTPException(status_code=400, detail="Question too long")

    safety_result = safety_filter.check(request.question)

    if not safety_result.is_safe:
        return ChatResponse(
            answer=safety_result.urgent_message,
            sources_used=["safety_filter"],
            chunks_retrieved=0,
            safety_flagged=True,
            flag_type=safety_result.flag_matched,
        )

    result = rag_service.answer(request.question)

    return ChatResponse(
        answer=result["answer"],
        sources_used=result["sources_used"],
        chunks_retrieved=result["chunks_retrieved"],
        safety_flagged=False,
        flag_type=None,
    )
