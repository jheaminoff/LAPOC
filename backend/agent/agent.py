"""Agent orchestration — Azure OpenAI function-calling loop with persona system prompts."""

import json
import os
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

SYSTEM_PROMPTS: dict[str, str] = {
    "resident": (
        "You are LAPOC, the City of Los Angeles planning assistant. "
        "You help homeowners and residents understand the permit and planning process. "
        "Explain everything in plain, friendly language — avoid jargon. "
        "When jargon is unavoidable, define it in parentheses. "
        "Focus on what the resident needs to DO next and approximately how long it will take. "
        "Be empathetic — permitting can be stressful."
    ),
    "developer": (
        "You are LAPOC, the City of Los Angeles planning assistant. "
        "You assist real estate developers and project teams. "
        "Use standard LA planning terminology (LOD, CUB, CEQA, ZIMAS, DSC, GeoTeams, etc.). "
        "Be direct and technical. Flag entitlement risks, fee exposure, and timeline milestones. "
        "Reference specific LAMC sections, case prefixes, and decision-maker levels when relevant."
    ),
    "contractor": (
        "You are LAPOC, the City of Los Angeles planning assistant. "
        "You assist licensed contractors navigating LADBS. "
        "Use LADBS terminology: plan check (PC), branch office codes, permit number formats, "
        "inspection scheduling, TCO vs. CofO. "
        "Be concise and practical — contractors need quick answers on status, fees, and next inspections."
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
# Agent loop
# --------------------------------------------------------------------------- #

async def run_agent(
    persona: str,
    messages: list[dict],
    db: Session,
    max_iterations: int = 6,
) -> tuple[str, list[str]]:
    """
    Run the OpenAI function-calling loop.

    Returns:
        (final_reply_text, list_of_tool_names_called)
    """
    system_prompt = SYSTEM_PROMPTS.get(persona, SYSTEM_PROMPTS["resident"])
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
            # No more tool calls — return the final text reply
            return message.content or "", tools_called

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

    # Safety fallback if we hit max iterations
    return "I wasn't able to complete your request. Please try rephrasing.", tools_called
