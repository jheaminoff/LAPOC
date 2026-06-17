"""Pydantic schemas for request/response validation."""

from typing import Optional

from pydantic import BaseModel


class PlotOut(BaseModel):
    apn: str
    address: str
    neighborhood: Optional[str] = None
    zoning: Optional[str] = None
    lot_size_sqft: Optional[int] = None
    current_use: Optional[str] = None

    # ZIMAS-enriched fields (returned when available)
    zoning_overlays: Optional[str] = None
    toc_tier: Optional[str] = None
    general_plan_land_use: Optional[str] = None
    sb9_eligible: Optional[str] = None
    sb35_eligible: Optional[str] = None
    ab2097_eligible: Optional[str] = None
    hpoz_hcm: Optional[str] = None
    flood_zone: Optional[str] = None
    fire_hazard_severity: Optional[str] = None
    hillside_area: Optional[str] = None
    adaptive_reuse: Optional[str] = None
    council_district: Optional[str] = None
    community_plan_area: Optional[str] = None
    ladbs_district_office: Optional[str] = None

    model_config = {"from_attributes": True}


class CaseOut(BaseModel):
    case_id: str
    apn: str
    department: str
    process_type: str
    applicant_type: Optional[str] = None
    applicant_name: Optional[str] = None
    submitted_date: Optional[str] = None
    current_status: Optional[str] = None
    assigned_to: Optional[str] = None
    description: Optional[str] = None
    fees_paid: Optional[float] = None
    fees_outstanding: Optional[float] = None
    hearing_date: Optional[str] = None
    next_action: Optional[str] = None
    portal_url: Optional[str] = None

    model_config = {"from_attributes": True}


class ParcelResult(BaseModel):
    plot: PlotOut
    cases: list[CaseOut]


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    persona: str = (
        "auto"  # "resident" | "developer" | "contractor" | "auto" (detected from conversation)
    )
    messages: list[ChatMessage]


class ChatResponse(BaseModel):
    reply: str
    speech_text: str = ""  # condensed 2-sentence max version of reply for TTS
    tool_calls_made: list[str] = []
    detected_persona: Optional[str] = (
        None  # returned when agent resolves persona from "auto"
    )
    suggestions: list[str] = []  # likely next questions after first query
