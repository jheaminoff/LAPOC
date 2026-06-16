"""Chat router — proxies requests to the agent."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from schemas import ChatRequest, ChatResponse
from agent.agent import run_agent

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """Run the agent with the given persona and message history."""
    reply, tool_calls_made = await run_agent(
        persona=request.persona,
        messages=[m.model_dump() for m in request.messages],
        db=db,
    )
    return ChatResponse(reply=reply, tool_calls_made=tool_calls_made)
