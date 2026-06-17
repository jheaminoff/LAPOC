"""Agent orchestration — Azure OpenAI function-calling loop with persona system prompts."""

import json
import os
import re
from typing import Any

from agent.tools import get_case_detail, get_workflow, lookup_parcel
from jinja2 import Environment, FileSystemLoader
from openai import AsyncAzureOpenAI
from sqlalchemy.orm import Session

client = AsyncAzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", ""),
    api_key=os.getenv("AZURE_OPENAI_API_KEY", ""),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
)

# --------------------------------------------------------------------------- #
# Tool definitions (OpenAI function-calling schema)
# --------------------------------------------------------------------------- #

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "lookup_parcel",
            "description": (
                "Look up a parcel (property) by APN number (format XXXX-XXX-XXX) or "
                "partial street address. Returns the plot details and a list of all "
                "associated permit/planning cases."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "apn_or_address": {
                        "type": "string",
                        "description": "APN number like '5149-022-018' or partial address like '1234 Sunset Blvd'",
                    }
                },
                "required": ["apn_or_address"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_case_detail",
            "description": (
                "Get full details for a specific permit or planning case. "
                "Use this after lookup_parcel returns a case_id to get status, "
                "next action, fees, hearing date, and assigned staff."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "case_id": {
                        "type": "string",
                        "description": "Case ID such as '24-010-10-000-12345' (LADBS) or 'ZA-2024-001234-CUB' (City Planning)",
                    }
                },
                "required": ["case_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_workflow",
            "description": (
                "Return the step-by-step workflow for a given permit or planning "
                "process type. Use when someone asks 'how do I get a permit for X?' "
                "or 'what are the steps for Y?'"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "process_type": {
                        "type": "string",
                        "description": (
                            "Process type. Examples: 'Bldg-New', 'Bldg-Alter/Repair', "
                            "'ADU', 'CUB', 'ZC', 'TT', 'Grading', 'Electrical'"
                        ),
                    },
                    "persona": {
                        "type": "string",
                        "enum": ["resident", "developer", "contractor"],
                        "description": (
                            "The user's role — affects the plain-language guidance shown per step. "
                            "Infer from context: use 'resident' for homeowners asking about their property, "
                            "'developer' for project/entitlement questions, 'contractor' for LADBS/plan-check questions."
                        ),
                    },
                },
                "required": ["process_type", "persona"],
            },
        },
    },
]


# --------------------------------------------------------------------------- #
# Persona system prompts — loaded from Jinja2 template
# --------------------------------------------------------------------------- #

_tpl_dir = os.path.join(os.path.dirname(__file__), "prompts")
_env = Environment(loader=FileSystemLoader(_tpl_dir))
_template = _env.get_template("system_prompts.jinja")


def _render_block(name: str, **kwargs: Any) -> str:
    context = _template.new_context(kwargs)
    return "".join(_template.blocks[name](context))


SYSTEM_PROMPTS: dict[str, str] = {
    "resident": _render_block("resident"),
    "developer": _render_block("developer"),
    "contractor": _render_block("contractor"),
    "auto": _render_block("auto"),
}


# --------------------------------------------------------------------------- #
# Tool dispatcher
# --------------------------------------------------------------------------- #


def _dispatch_tool(name: str, args: dict[str, Any], db: Session) -> str:
    """Call the appropriate tool function and return its string output."""
    if name == "lookup_parcel":
        return lookup_parcel(args["apn_or_address"], db)
    if name == "get_case_detail":
        return get_case_detail(args["case_id"], db)
    if name == "get_workflow":
        return get_workflow(args["process_type"], args["persona"], db)
    return f"Unknown tool: {name}"


# --------------------------------------------------------------------------- #
# Persona tag extraction
# --------------------------------------------------------------------------- #

_PERSONA_TAG_RE = re.compile(
    r"\[PERSONA:(resident|developer|contractor)\]", re.IGNORECASE
)


def _extract_persona_tag(text: str) -> tuple[str, str | None]:
    """
    Strip the [PERSONA:xxx] tag from the reply text and return
    (clean_text, detected_persona_or_None).
    """
    match = _PERSONA_TAG_RE.search(text)
    if match:
        persona = match.group(1).lower()
        clean = _PERSONA_TAG_RE.sub("", text).rstrip()
        return clean, persona
    return text, None


# --------------------------------------------------------------------------- #
# Agent loop
# --------------------------------------------------------------------------- #


async def run_agent(
    persona: str,
    messages: list[dict],
    db: Session,
    max_iterations: int = 6,
) -> tuple[str, list[str], str | None]:
    """
    Run the OpenAI function-calling loop.

    Returns:
        (final_reply_text, list_of_tool_names_called, detected_persona_or_None)
    """
    system_prompt = SYSTEM_PROMPTS.get(persona, SYSTEM_PROMPTS["auto"])
    conversation = [{"role": "system", "content": system_prompt}] + messages
    tools_called: list[str] = []

    for _ in range(max_iterations):
        response = await client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o"),
            messages=conversation,
            tools=TOOLS,
            tool_choice="auto",
        )

        message = response.choices[0].message
        conversation.append(message.model_dump(exclude_unset=True))

        if not message.tool_calls:
            raw_reply = message.content or ""
            clean_reply, detected = _extract_persona_tag(raw_reply)
            return clean_reply, tools_called, detected

        # Execute each tool call and append results
        for tc in message.tool_calls:
            fn_name = tc.function.name
            fn_args = json.loads(tc.function.arguments)
            tools_called.append(fn_name)

            result = _dispatch_tool(fn_name, fn_args, db)

            conversation.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                }
            )


# --------------------------------------------------------------------------- #
# Speech keynotes generation
# --------------------------------------------------------------------------- #


async def generate_speech_keynotes(reply: str) -> str:
    """Return a 1-2 sentence spoken keynotes paragraph for TTS.

    Calls the LLM with a focused prompt to distil the reply into natural,
    conversational spoken language — no markdown, no lists, no card data.
    Falls back to a simple regex strip of the first two sentences if the
    LLM call fails.
    """
    if not reply.strip():
        return ""

    prompt = (
        "You are a voice assistant. "
        "Read the following assistant reply and write a single short spoken paragraph "
        "(1-2 sentences, max 40 words) that captures the key point for text-to-speech. "
        "Write in natural spoken English — no bullet points, no lists, no markdown, "
        "no property data, no step numbers. Just the essential takeaway a listener needs.\n\n"
        f"Reply:\n{reply}\n\n"
        "Spoken keynote:"
    )

    try:
        response = await client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o"),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=80,
            temperature=0.3,
        )
        keynote = (response.choices[0].message.content or "").strip()
        if keynote:
            return keynote
    except Exception:
        pass

    # Fallback: strip card blocks and markdown, return first two sentences
    import re as _re

    _CARD_SENTINELS = ("PARCEL:", "CASE DETAIL:", "WORKFLOW:")
    lines = reply.splitlines()
    clean: list[str] = []
    skip = False
    for line in lines:
        s = line.strip()
        if any(s.startswith(sentinel) for sentinel in _CARD_SENTINELS):
            skip = True
            continue
        if skip:
            if s == "":
                skip = False
            continue
        clean.append(s)
    text = " ".join(clean)
    text = _re.sub(r"#{1,6}\s+", "", text)
    text = _re.sub(r"\*{1,3}(.+?)\*{1,3}", r"\1", text)
    text = _re.sub(r"`[^`]+`", "", text)
    text = _re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = _re.sub(r"^\s*[-*•]\s+", "", text, flags=_re.MULTILINE)
    text = _re.sub(r"\s{2,}", " ", text).strip()
    sentences = _re.split(r"(?<=[.!?])\s+", text)
    return " ".join(sentences[:2]).strip()


# --------------------------------------------------------------------------- #
# Suggestion generation
# --------------------------------------------------------------------------- #

_JSON_ARRAY_RE = re.compile(r"\[.*?\]", re.DOTALL)

_DEFAULT_SUGGESTIONS: dict[str, list[str]] = {
    "lookup": [
        "What's the status of the permits on this property?",
        "How do I apply for a new building permit?",
        "What zoning rules apply to this property?",
        "Are there any fees I need to pay?",
        "Can you check a different address or APN for me?",
    ],
    "case": [
        "What happens next in this case?",
        "How long until the case is approved?",
        "Can I appeal this decision?",
        "What documents do I need to provide?",
        "Are there any fees or conditions on this case?",
    ],
    "workflow": [
        "How long does this process typically take?",
        "What documents do I need to prepare?",
        "How much do the permits cost?",
        "Can I check the status online?",
        "Are there overlapping approvals I should know about?",
    ],
}


async def generate_suggestions(
    user_query: str,
    reply: str,
    persona: str | None = None,
    num_suggestions: int = 4,
) -> list[str]:
    """Generate likely next questions based on the first user query and the assistant reply."""
    if not user_query:
        return []

    role_context = (
        f" The user's role is: {persona}." if persona and persona != "auto" else ""
    )
    suggest_prompt = _render_block("suggest", num=num_suggestions)
    prompt = (
        f"{suggest_prompt}{role_context}\n\n"
        f"User: {user_query}\n"
        f"Assistant: {reply}\n\n"
        f"Return ONLY a JSON array of strings, no other text."
    )

    try:
        response = await client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o"),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.7,
        )
        content = (response.choices[0].message.content or "").strip()

        # Try parsing as-is
        try:
            parsed = json.loads(content)
            if isinstance(parsed, list):
                return [str(s).strip() for s in parsed if str(s).strip()][
                    :num_suggestions
                ]
        except json.JSONDecodeError:
            pass

        # Try extracting first JSON array from response via regex
        match = _JSON_ARRAY_RE.search(content)
        if match:
            try:
                parsed = json.loads(match.group(0))
                if isinstance(parsed, list):
                    return [str(s).strip() for s in parsed if str(s).strip()][
                        :num_suggestions
                    ]
            except json.JSONDecodeError:
                pass
    except Exception:
        pass

    # Fallback: return contextual defaults based on tool keywords
    q = user_query.lower()
    if "case" in q or "status" in q or "permit" in q:
        return _DEFAULT_SUGGESTIONS["case"]
    if "workflow" in q or "step" in q or "process" in q or "how do i" in q:
        return _DEFAULT_SUGGESTIONS["workflow"]
    return _DEFAULT_SUGGESTIONS["lookup"]
