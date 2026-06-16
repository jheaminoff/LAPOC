"""Agent orchestration — Azure OpenAI function-calling loop with persona system prompts."""

import json
import os
import re
from typing import Any

from openai import AsyncAzureOpenAI
from sqlalchemy.orm import Session

from agent.tools import lookup_parcel, get_case_detail, get_workflow

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
                        "description": "The user's role — affects the plain-language guidance shown per step.",
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
        _BASE +
        "You are speaking with a homeowner or resident. "
        "Explain everything in plain, friendly language — avoid jargon. "
        "When jargon is unavoidable, define it in parentheses. "
        "Focus on what the resident needs to DO next and approximately how long it will take. "
        "Be empathetic — permitting can be stressful."
    ),
    "developer": (
        _BASE +
        "You are speaking with a real estate developer or project team. "
        "Use standard LA planning terminology (LOD, CUB, CEQA, ZIMAS, DSC, GeoTeams, EPS, etc.). "
        "Be direct and technical. Flag entitlement risks, fee exposure, and timeline milestones. "
        "Reference specific LAMC sections, case prefixes, and decision-maker levels when relevant."
    ),
    "contractor": (
        _BASE +
        "You are speaking with a licensed contractor navigating LADBS. "
        "Use LADBS terminology: plan check (PC), branch office codes, permit number formats, "
        "inspection scheduling, TCO vs. CofO. "
        "Be concise and practical — contractors need quick answers on status, fees, and next inspections."
    ),
    "auto": (
        _BASE +
        "Detect the user's role from how they write and what they ask about:\n"
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

_PERSONA_TAG_RE = re.compile(r'\[PERSONA:(resident|developer|contractor)\]', re.IGNORECASE)


def _extract_persona_tag(text: str) -> tuple[str, str | None]:
    """
    Strip the [PERSONA:xxx] tag from the reply text and return
    (clean_text, detected_persona_or_None).
    """
    match = _PERSONA_TAG_RE.search(text)
    if match:
        persona = match.group(1).lower()
        clean = _PERSONA_TAG_RE.sub('', text).rstrip()
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

            conversation.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result,
            })


