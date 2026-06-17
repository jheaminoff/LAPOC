"""Chat router — proxies requests to the agent."""

from agent.agent import (generate_speech_keynotes, generate_suggestions,
                         run_agent)
from database import get_db
from fastapi import APIRouter, Depends
from schemas import ChatRequest, ChatResponse
from sqlalchemy.orm import Session

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """Run the agent with the given persona and message history."""
    reply, tool_calls_made, detected_persona = await run_agent(
        persona=request.persona,
        messages=[m.model_dump() for m in request.messages],
        db=db,
    )

    suggestions: list[str] = []
    is_first_query = sum(1 for m in request.messages if m.role == "user") == 1
    if is_first_query:
        user_query = next((m.content for m in request.messages if m.role == "user"), "")
        suggestions = await generate_suggestions(
            user_query=user_query,
            reply=reply,
            persona=detected_persona or request.persona,
        )

    speech_text = await generate_speech_keynotes(reply)

    return ChatResponse(
        reply=reply,
        speech_text=speech_text,
        tool_calls_made=tool_calls_made,
        detected_persona=detected_persona,
        suggestions=suggestions,
    )
