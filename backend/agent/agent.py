"""Agent orchestration — Azure OpenAI function-calling loop with persona system prompts."""

import json
import os
import re
from typing import Any

from agent.tools import get_case_detail, get_workflow, lookup_parcel
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
# Persona system prompts
# --------------------------------------------------------------------------- #

_BASE = (
    "You are LAPOC, the City of Los Angeles planning and permits assistant. "
    "You help users understand permit processes, entitlement status, zoning, "
    "and next steps for any LA property. "
)

SYSTEM_PROMPTS: dict[str, str] = {
    "resident": (
        _BASE + "You are speaking with a homeowner or resident. "
        "Explain everything in plain, friendly language — avoid jargon. "
        "When jargon is unavoidable, define it in parentheses. "
        "Focus on what the resident needs to DO next and approximately how long it will take. "
        "Be empathetic — permitting can be stressful."
    ),
    "developer": (
        _BASE + "You are speaking with a real estate developer or project team. "
        "Use standard LA planning terminology (LOD, CUB, CEQA, ZIMAS, DSC, GeoTeams, EPS, etc.). "
        "Be direct and technical. Flag entitlement risks, fee exposure, and timeline milestones. "
        "Reference specific LAMC sections, case prefixes, and decision-maker levels when relevant."
    ),
    "contractor": (
        _BASE + "You are speaking with a licensed contractor navigating LADBS. "
        "Use LADBS terminology: plan check (PC), branch office codes, permit number formats, "
        "inspection scheduling, TCO vs. CofO. "
        "Be concise and practical — contractors need quick answers on status, fees, and next inspections."
    ),
    "auto": (
        _BASE + "Detect the user's role from how they write and what they ask about:\n"
        "- RESIDENT: asks about their own home, ADU, remodel, pool, simple permits, says 'my house' or 'my property'\n"
        "- DEVELOPER: uses terms like entitlement, zoning, TOC, EIR, project, units, yield, feasibility, LOD\n"
        "- CONTRACTOR: mentions license numbers (C-10, B license), plan check status, inspections, job sites, pull a permit\n\n"
        "Adapt your language to match the detected role:\n"
        "- Resident: plain language, friendly, define jargon, focus on next steps\n"
        "- Developer: technical LA planning terminology, flag risks and timelines\n"
        "- Contractor: concise LADBS terminology, status and inspection focus\n\n"
        "After your first substantive response, include a single line at the very end of your reply in this exact format:\n"
        "[PERSONA:resident] or [PERSONA:developer] or [PERSONA:contractor]\n"
        "Only include this tag once (on your first response). Do not include it in follow-up messages."
    ),
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
# Suggestion generation
# --------------------------------------------------------------------------- #

_SUGGEST_PROMPT = (
    "You are LAPOC, the City of Los Angeles planning and permits assistant. "
    "Based on this conversation, suggest {num} short, specific follow-up questions "
    "the user is most likely to ask next. Each must be a complete question (10\u201315 words)."
)

_JSON_ARRAY_RE = re.compile(r"\[.*?\]", re.DOTALL)

_DEFAULT_SUGGESTIONS: dict[str, list[str]] = {
    "lookup": [
        "What's the status of the permits on this property?",
        "How do I apply for a new building permit?",
        "What zoning rules apply to this property?",
        "Are there any fees I need to pay?",
    ],
    "case": [
        "What happens next in this case?",
        "How long until the case is approved?",
        "Can I appeal this decision?",
        "What documents do I need to provide?",
    ],
    "workflow": [
        "How long does this process typically take?",
        "What documents do I need to prepare?",
        "How much do the permits cost?",
        "Can I check the status online?",
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
    prompt = (
        f"{_SUGGEST_PROMPT.format(num=num_suggestions)}{role_context}\n\n"
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
