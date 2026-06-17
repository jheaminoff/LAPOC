"""Chat router — proxies requests to the agent."""

import re

from agent.agent import generate_suggestions, run_agent
from database import get_db
from fastapi import APIRouter, Depends
from schemas import ChatRequest, ChatResponse
from sqlalchemy.orm import Session

router = APIRouter(prefix="/chat", tags=["chat"])

# Sentinel prefixes that mark structured card blocks — not spoken
_CARD_SENTINELS = ("PARCEL:", "CASE DETAIL:", "WORKFLOW:")


def extract_speech_text(reply: str) -> str:
    """Return a 2-sentence max plain-text summary of reply for TTS.

    Strips card sentinel blocks, markdown formatting, and list bullets,
    then returns the first two sentences of what remains.
    """
    lines = reply.splitlines()
    clean: list[str] = []
    skip = False

    for line in lines:
        stripped = line.strip()
        # Start skipping when we hit a sentinel block
        if any(stripped.startswith(s) for s in _CARD_SENTINELS):
            skip = True
            continue
        # Resume on a blank line after a sentinel block
        if skip:
            if stripped == "":
                skip = False
            continue
        clean.append(stripped)

    text = " ".join(clean)

    # Strip markdown: headers, bold/italic, inline code, links, bullets
    text = re.sub(r"#{1,6}\s+", "", text)
    text = re.sub(r"\*{1,3}(.+?)\*{1,3}", r"\1", text)
    text = re.sub(r"`[^`]+`", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"^\s*[-*•]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"\s{2,}", " ", text).strip()

    # Split on sentence-ending punctuation and keep first two sentences
    sentences = re.split(r"(?<=[.!?])\s+", text)
    speech = " ".join(sentences[:2]).strip()

    return speech


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
        user_query = next(
            (m.content for m in request.messages if m.role == "user"), ""
        )
        suggestions = await generate_suggestions(
            user_query=user_query,
            reply=reply,
            persona=detected_persona or request.persona,
        )

    return ChatResponse(
        reply=reply,
        speech_text=extract_speech_text(reply),
        tool_calls_made=tool_calls_made,
        detected_persona=detected_persona,
        suggestions=suggestions,
    )
