"""Agent tool functions — each wraps DB queries and returns plain-text summaries."""

import json
import re

import httpx
from models import Case, Plot, WorkflowPersona, WorkflowStep
from sqlalchemy.orm import Session

# --------------------------------------------------------------------------- #
# Tool 1: lookup_parcel
# --------------------------------------------------------------------------- #


def lookup_parcel(apn_or_address: str, db: Session) -> str:
    """
    Look up a parcel by APN (XXXX-XXX-XXX) or partial address.
    Returns a plain-text summary of the plot, ZIMAS overlays, incentives, and
    all associated cases.
    """
    plot = db.query(Plot).filter(Plot.apn == apn_or_address).first()

    if not plot:
        plots = (
            db.query(Plot)
            .filter(Plot.address.ilike(f"%{apn_or_address}%"))
            .limit(5)
            .all()
        )
        if not plots:
            return f"No parcel found matching '{apn_or_address}'."
        if len(plots) > 1:
            lines = [f"Multiple parcels matched '{apn_or_address}':"]
            for p in plots:
                lines.append(f"  \u2022 APN {p.apn} \u2014 {p.address}")
            lines.append("Please specify the APN to continue.")
            return "\n".join(lines)
        plot = plots[0]

    cases = db.query(Case).filter(Case.apn == plot.apn).all()

    lines = [
        f"PARCEL: {plot.address}",
        f"  APN: {plot.apn}",
        f"  Neighborhood: {plot.neighborhood}",
        f"  Zoning: {plot.zoning}",
        (
            f"  Lot size: {plot.lot_size_sqft:,} sq ft"
            if plot.lot_size_sqft
            else "  Lot size: unknown"
        ),
        f"  Current use: {plot.current_use}",
    ]

    # --- Zoning overlays (parsed from JSON string) ---
    if plot.zoning_overlays:
        try:
            overlays = json.loads(plot.zoning_overlays)
            if overlays:
                lines.append("")
                lines.append("  ZONING OVERLAYS:")
                for o in overlays:
                    lines.append(f"    \u2022 {o}")
        except (json.JSONDecodeError, TypeError):
            pass

    # --- Development incentives ---
    incentives = []
    if plot.toc_tier:
        incentives.append(f"TOC: {plot.toc_tier}")
    if plot.sb9_eligible and plot.sb9_eligible != "No":
        incentives.append(f"SB 9: {plot.sb9_eligible}")
    if plot.sb35_eligible and plot.sb35_eligible != "No":
        incentives.append(f"SB 35: {plot.sb35_eligible}")
    if plot.ab2097_eligible and plot.ab2097_eligible != "No":
        incentives.append("AB 2097: Within 1/2 mi of Major Transit Stop")
    if plot.adaptive_reuse:
        incentives.append(f"Adaptive Reuse: {plot.adaptive_reuse}")
    if incentives:
        lines.append("")
        lines.append("  DEVELOPMENT INCENTIVES:")
        for i in incentives:
            lines.append(f"    \u2022 {i}")

    # --- Hazards & constraints ---
    hazards = []
    if plot.flood_zone and plot.flood_zone != "Outside Flood Zone":
        hazards.append(f"Flood Zone: {plot.flood_zone}")
    if plot.fire_hazard_severity and plot.fire_hazard_severity != "No":
        hazards.append(f"Fire Hazard: {plot.fire_hazard_severity}")
    if plot.hillside_area == "Yes":
        hazards.append("Hillside Construction Regulation (HCR) area")
    if hazards:
        lines.append("")
        lines.append("  HAZARDS & CONSTRAINTS:")
        for h in hazards:
            lines.append(f"    \u2022 {h}")

    # --- Jurisdictional info ---
    juris_parts = []
    if plot.council_district:
        juris_parts.append(plot.council_district)
    if plot.community_plan_area:
        juris_parts.append(plot.community_plan_area)
    if plot.ladbs_district_office:
        juris_parts.append(f"LADBS: {plot.ladbs_district_office}")
    if juris_parts:
        lines.append("")
        lines.append("  JURISDICTION:")
        for j in juris_parts:
            lines.append(f"    \u2022 {j}")

    # --- Cases ---
    lines.append("")
    lines.append(f"CASES ({len(cases)} total):")

    if not cases:
        lines.append("  No active or historical cases found.")
    else:
        for c in cases:
            fee_note = ""
            if c.fees_outstanding and c.fees_outstanding > 0:
                fee_note = f" | \u26a0 ${c.fees_outstanding:,.0f} outstanding"
            lines.append(
                f"  [{c.department}] {c.case_id}  |  {c.process_type}  "
                f"|  Status: {c.current_status}{fee_note}"
            )

    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# Tool 2: get_case_detail
# --------------------------------------------------------------------------- #


def get_case_detail(case_id: str, db: Session) -> str:
    """
    Return full details for a single case: status, next action, fees, hearing date,
    assigned staff, portal link.
    """
    case = db.query(Case).filter(Case.case_id == case_id).first()
    if not case:
        return f"Case '{case_id}' not found. Please verify the case number."

    lines = [
        f"CASE DETAIL: {case.case_id}",
        f"  Department:    {case.department}",
        f"  Type:          {case.process_type}",
        f"  Description:   {case.description}",
        f"  Applicant:     {case.applicant_name} ({case.applicant_type})",
        f"  Submitted:     {case.submitted_date}",
        f"  Status:        {case.current_status}",
        f"  Assigned to:   {case.assigned_to or 'Not yet assigned'}",
        (
            f"  Fees paid:     ${case.fees_paid:,.0f}"
            if case.fees_paid
            else "  Fees paid:     $0"
        ),
        (
            f"  Fees owed:     ${case.fees_outstanding:,.0f}"
            if case.fees_outstanding
            else "  Fees owed:     $0"
        ),
    ]

    if case.hearing_date:
        lines.append(f"  Hearing date:  {case.hearing_date}")

    lines.append(f"  Next action:   {case.next_action or 'None on record'}")

    if case.portal_url:
        lines.append(f"  Portal link:   {case.portal_url}")

    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# Tool 3: get_workflow
# --------------------------------------------------------------------------- #


def get_workflow(process_type: str, persona: str, db: Session) -> str:
    """
    Return the ordered workflow steps for a process type, with persona-specific
    plain-language guidance injected per step.
    Persona falls back to 'resident' if no specific guidance rows exist.
    """
    steps = (
        db.query(WorkflowStep)
        .filter(WorkflowStep.process_type == process_type)
        .order_by(WorkflowStep.step_order)
        .all()
    )

    if not steps:
        return (
            f"No workflow steps found for process type '{process_type}'. "
            "Try a type like: Bldg-New, Bldg-Alter/Repair, ADU, CUB, ZC, TT."
        )

    # Build a lookup of persona guidance keyed by step_name
    # Fall back to 'resident' if no rows exist for the requested persona
    persona_rows = (
        db.query(WorkflowPersona)
        .filter(
            WorkflowPersona.process_type == process_type,
            WorkflowPersona.persona == persona,
        )
        .all()
    )
    if not persona_rows and persona != "resident":
        persona_rows = (
            db.query(WorkflowPersona)
            .filter(
                WorkflowPersona.process_type == process_type,
                WorkflowPersona.persona == "resident",
            )
            .all()
        )
    guidance_map = {row.step_name: row.guidance for row in persona_rows}

    lines = [f"WORKFLOW: {process_type}  (view: {persona})", ""]

    for step in steps:
        party_tag = f"[{step.responsible_party}]" if step.responsible_party else ""
        days_tag = f"  ~{step.typical_days} days" if step.typical_days else ""
        lines.append(
            f"  Step {step.step_order}. {step.step_name} {party_tag}{days_tag}"
        )
        if step.description:
            lines.append(f"    {step.description}")
        guidance = guidance_map.get(step.step_name)
        if guidance:
            lines.append(f"    \U0001f4a1 {guidance}")
        lines.append("")

    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# Tool 4: lookup_address  (LA City BOE GeoQuery API)
# --------------------------------------------------------------------------- #

_BOE_API_URL = "https://api.lacity.org/boe_geoquery/addressvalidationservice"
_BOE_API_KEY = "B5thBZ3BXlR1waoUvderfnrMETLwk2SE"


def lookup_address(address: str) -> str:
    """
    Look up an address via the LA City BOE GeoQuery API.
    Returns standardized address, APN, council district, planning area,
    police/fire/school jurisdictions, and LADBS links.
    """
    params = {
        "address": address,
        "status": "new",
        "layerset": "neighborhoodinfo",
        "apikey": _BOE_API_KEY,
    }

    try:
        response = httpx.get(_BOE_API_URL, params=params, timeout=15.0)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        return f"Address lookup failed: {e}"

    if data.get("status") != "exactMatch":
        return (
            f"Address '{address}' could not be matched. "
            "Try a more complete address (e.g., '1220 S Crenshaw Blvd, Los Angeles')."
        )

    loc = data.get("location", {})
    coords = data.get("coords", {})
    layers = data.get("layers", {})

    lines = []

    # -- Standardized address + APN --
    lines.append(f"  Address:        {loc.get('address', 'N/A')}")
    lines.append(f"  APN:            {_fmt_apn(loc)}")
    lines.append(f"  ZIP:            {loc.get('zipcode', 'N/A')}")
    lat = coords.get("latitude")
    lng = coords.get("longitude")
    if lat and lng:
        lines.append(f"  Coordinates:    {lat}, {lng}")
    lines.append("")

    # -- Jurisdictional info --
    cd = layers.get("council districts", {})
    if cd:
        lines.append(
            f"  Council District:  {cd.get('cd_no', 'N/A')}"
            f"  \u2014 {cd.get('cdmember', 'N/A')}"
        )

    apc = layers.get("area planning commission", {})
    if apc:
        lines.append(f"  Area Planning:     {apc.get('apc', 'N/A')}")

    police = layers.get("police division", {})
    if police:
        lines.append(
            f"  Police Division:   {police.get('aprec', 'N/A')}"
            f"  ({police.get('bureau', 'N/A')})"
        )

    nc = layers.get("neighborhood council", {})
    if nc:
        lines.append(f"  Neighborhood Cncl: {nc.get('name', 'N/A')}")

    planning = layers.get("community planning area", {})
    if planning:
        lines.append(f"  Planning Area:     {planning.get('name', 'N/A')}")

    fire = layers.get("fire jurisdiction", {})
    if fire:
        lines.append(f"  Fire Station:      Station {fire.get('firstin_di', 'N/A')}")

    lausd = layers.get("lausd cluster", {})
    if lausd:
        lines.append(f"  LAUSD Cluster:     {lausd.get('clustername', 'N/A')}")

    county = layers.get("county supervisor", {})
    if county:
        lines.append(
            f"  County Supervisor: District {county.get('dist_', 'N/A')}"
            f"  \u2014 {county.get('who', 'N/A')}"
        )

    state_sen = layers.get("state senate", {})
    if state_sen:
        lines.append(
            f"  State Senate:      District {state_sen.get('dist_', 'N/A')}"
            f"  \u2014 {state_sen.get('name', 'N/A')}"
        )

    state_asm = layers.get("state assembly", {})
    if state_asm:
        lines.append(
            f"  State Assembly:    District {state_asm.get('dist_', 'N/A')}"
            f"  \u2014 {state_asm.get('name', 'N/A')}"
        )

    congress = layers.get("us congress", {})
    if congress:
        lines.append(
            f"  US Congress:       District {congress.get('dist_', 'N/A')}"
            f"  \u2014 {congress.get('name', 'N/A')}"
        )

    lines.append("")

    # -- LADBS links --
    ladbs = layers.get("ladbs", {})
    if ladbs:
        lines.append("  LADBS Links:")
        if ladbs.get("permit_url"):
            lines.append(f"    Permits:  {ladbs['permit_url']}")
        if ladbs.get("code_enforcement_url"):
            lines.append(f"    Code Enf: {ladbs['code_enforcement_url']}")
        lines.append("")

    lines.append("")

    # -- Map coordinates (rendered as map card on frontend) --
    if lat and lng:
        lines.append("MAP:")
        lines.append(f"  latitude: {lat}")
        lines.append(f"  longitude: {lng}")

    lines.append(
        "Tip: use the APN above to look up parcel details and associated cases."
    )

    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# ZIMAS API — live parcel data fallback
# --------------------------------------------------------------------------- #

_ZIMAS_HEADERS = {
    "User-Agent": "LAPOC-Backend/1.0",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://zimas.lacity.org/",
}

_ZIMAS_PARCEL_LAYER = {
    "source": {
        "type": "dataLayer",
        "fields": [
            {"alias": "PIN", "name": "PIN", "type": "esriFieldTypeString", "nullable": True},
            {"alias": "ADDRESS", "name": "ADDRESS", "type": "esriFieldTypeString", "nullable": True},
            {"alias": "HSE_NBR", "name": "HSE_NBR", "type": "esriFieldTypeString", "nullable": True},
            {"alias": "HSE_DIR_CD", "name": "HSE_DIR_CD", "type": "esriFieldTypeString", "nullable": True},
            {"alias": "PART_STR_NM", "name": "PART_STR_NM", "type": "esriFieldTypeString", "nullable": True},
        ],
        "dataSource": {
            "type": "table",
            "workspaceId": "zimas4",
            "dataSourceName": "zim4s.search_addressparts",
        },
    }
}

_RESIDENTIAL_ZONE_PREFIXES = ("R1", "R2", "R3", "R4", "R5", "RD", "RW", "RU", "RA", "RE", "RS")


def check_adu_eligibility(apn_or_address: str, db: Session) -> str:
    """
    Check if a parcel is eligible for an Accessory Dwelling Unit (ADU) by
    evaluating zoning, overlays, hazards, and historic status.
    Returns a structured ADU ELIGIBILITY CHECK: block.
    """
    try:
        plot = db.query(Plot).filter(Plot.apn == apn_or_address).first()

        if not plot:
            plots = (
                db.query(Plot)
                .filter(Plot.address.ilike(f"%{apn_or_address}%"))
                .limit(5)
                .all()
            )
            if plots:
                if len(plots) > 1:
                    lines = [f"Multiple parcels matched '{apn_or_address}':"]
                    for p in plots:
                        lines.append(f"  \u2022 APN {p.apn} \u2014 {p.address}")
                    lines.append("Please specify the APN to continue.")
                    return "\n".join(lines)
                plot = plots[0]

        if plot:
            return _format_adu_eligibility(_plot_to_adu_fields(plot))
    except Exception:
        pass

    zimas_data = _zimas_lookup(apn_or_address)
    if zimas_data is None:
        return f"No parcel found matching '{apn_or_address}'."
    return _format_adu_eligibility(zimas_data)


# --------------------------------------------------------------------------- #
# ADU helpers — shared between DB and ZIMAS paths
# --------------------------------------------------------------------------- #


def _plot_to_adu_fields(plot: Plot) -> dict:
    """Extract a flat dict of ADU-relevant fields from a DB Plot."""
    overlays = []
    if plot.zoning_overlays:
        try:
            overlays = json.loads(plot.zoning_overlays) or []
        except (json.JSONDecodeError, TypeError):
            pass
    return {
        "address": plot.address,
        "apn": plot.apn,
        "zoning": plot.zoning or "",
        "hpoz": plot.hpoz_hcm or "",
        "flood_zone": plot.flood_zone or "",
        "fire_hazard": plot.fire_hazard_severity or "",
        "hillside_area": plot.hillside_area or "",
        "zoning_overlays": overlays,
    }


def _format_adu_eligibility(fields: dict) -> str:
    """Generate the ADU ELIGIBILITY CHECK: block from a fields dict."""
    zoning = fields["zoning"]
    lines = [
        f"ADU ELIGIBILITY CHECK for {fields['address']}",
        f"  APN: {fields['apn']}",
        f"  Zoning: {zoning}",
        "",
    ]

    zoning_ok = any(zoning.startswith(p) for p in _RESIDENTIAL_ZONE_PREFIXES)
    if zoning_ok:
        lines.append("  ZONING: \u2705 Residential zone \u2014 ADU permitted by right")
    else:
        lines.append("  ZONING: \u274c Non-residential zone \u2014 ADU not permitted")

    hpoz = fields["hpoz"]
    if hpoz and hpoz.strip().lower() not in ("", "no", "none"):
        lines.append(
            f"  HPOZ: \u26a0 {hpoz} \u2014 ADU allowed, requires HPOZ ministerial review (ADUH case type)"
        )

    flood = fields["flood_zone"]
    if flood and "outside" not in flood.lower() and "none" not in flood.lower():
        lines.append(
            f"  FLOOD ZONE: \u26a0 {flood} \u2014 ADU allowed, requires flood-proofing per FEMA standards"
        )

    fire = fields["fire_hazard"]
    if fire and fire.strip().lower() == "very high":
        lines.append(
            "  FIRE HAZARD: \u26a0 Very High Fire Hazard Severity Zone \u2014 "
            "ADU allowed, requires fire-hardened construction (ignition-resistant materials, ember-resistant vents)"
        )

    hillside = fields["hillside_area"]
    if hillside and hillside.strip().lower() == "yes":
        lines.append(
            "  HILLSIDE (HCR): \u26a0 Hillside Construction Regulation area \u2014 "
            "ADU allowed, expects HCR-compliant site plan (soils report, grading plan)"
        )

    overlays = fields.get("zoning_overlays", [])
    if isinstance(overlays, list):
        coastal = [o for o in overlays if "coastal" in o.lower()]
        if coastal:
            lines.append(
                "  COASTAL ZONE: \u26a0 Coastal Zone overlay \u2014 "
                "ADU may require a Coastal Development Permit"
            )

    lines.append("")
    constraints = [s for s in lines if "\u26a0" in s or "\u274c" in s]
    if not zoning_ok:
        lines.append("  OVERALL: \u274c NOT ELIGIBLE")
        lines.append(
            "    \u2192 This parcel is not zoned for residential use. ADUs are "
            "only permitted on parcels that allow residential development."
        )
    elif not constraints:
        lines.append("  OVERALL: \u2705 ELIGIBLE \u2014 No constraints")
        lines.append(
            "    \u2192 Your parcel qualifies for a by-right ADU. "
            "Proceed with Step 1: Prepare plans and submit to LADBS. "
            "Use get_workflow('ADU') for the full step-by-step process."
        )
    else:
        lines.append("  OVERALL: \u2705 ELIGIBLE \u2014 With conditions")
        lines.append(
            "    \u2192 Your parcel is eligible, but the constraints above "
            "require additional review or design measures. "
            "Use get_workflow('ADU') for the full step-by-step process."
        )

    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# ZIMAS API — live parcel data lookup
# --------------------------------------------------------------------------- #

_ZIMAS_ARCGIS_URL = (
    "https://zimas.lacity.org/arcgis/rest/services/zm4/landbase/MapServer/dynamicLayer/query"
)
_ZIMAS_PROJECT_DATA_URL = "https://zimas.lacity.org/zm4WS/GetProjectData"


def _parse_address_parts(address: str) -> dict | None:
    """Split an address into house number, direction, and normalized street name."""
    address = address.strip()
    m = re.match(r"(\d+(?:/\d+)?)\s+(.*)", address)
    if not m:
        return None
    house = m.group(1)
    rest = m.group(2).strip()
    dir_m = re.match(r"(N|S|E|W|North|South|East|West)\s+(.*)", rest, re.IGNORECASE)
    if dir_m:
        direction = dir_m.group(1).upper()[0]
        street = dir_m.group(2)
    else:
        direction = None
        street = rest
    street = street.upper().strip()
    street = re.sub(r"\bDRIVE\b", "DR", street)
    street = re.sub(r"\bSTREET\b", "ST", street)
    street = re.sub(r"\bAVENUE\b", "AVE", street)
    street = re.sub(r"\bBOULEVARD\b", "BLVD", street)
    street = re.sub(r"\bLANE\b", "LN", street)
    street = re.sub(r"\bCOURT\b", "CT", street)
    street = re.sub(r"\bPLACE\b", "PL", street)
    street = re.sub(r"\bROAD\b", "RD", street)
    street = re.sub(r"\bHIGHWAY\b", "HWY", street)
    street = re.sub(r"\bCIRCLE\b", "CIR", street)
    street = re.sub(r"\bWAY\b", "WY", street)
    return {"house": house, "direction": direction, "street": street}


def _zimas_get_pin(address: str) -> str | None:
    """Search ZIMAS parcel address layer to find the PIN for a given address."""
    parts = _parse_address_parts(address)
    if parts is None:
        return None

    where_parts = [f"(HSE_NBR in ({parts['house']}))"]
    if parts["direction"]:
        where_parts.append(f"(HSE_DIR_CD like '{parts['direction']}')")
    where_parts.append(f"(PART_STR_NM like '{parts['street']}%')")
    where = " AND ".join(where_parts)

    params = {
        "f": "json",
        "outFields": "PIN,ADDRESS",
        "returnDistinctValues": "true",
        "returnGeometry": "false",
        "spatialRel": "esriSpatialRelIntersects",
        "where": where,
        "layer": json.dumps(_ZIMAS_PARCEL_LAYER),
    }
    try:
        resp = httpx.get(_ZIMAS_ARCGIS_URL, params=params, headers=_ZIMAS_HEADERS, timeout=15.0)
        resp.raise_for_status()
        data = resp.json()
        features = data.get("features", [])
        if not features:
            return None
        exact = [f for f in features if f["attributes"].get("ADDRESS", "").upper().startswith(parts["house"])]
        if exact:
            return exact[0]["attributes"]["PIN"]
        return features[0]["attributes"]["PIN"]
    except Exception:
        return None


def _zimas_get_project_data(pin: str) -> list | None:
    """Fetch the full ZIMAS project-data JSON for a given PIN."""
    params = {"PIN": pin, "APN": "", "project": ""}
    try:
        resp = httpx.get(
            _ZIMAS_PROJECT_DATA_URL,
            params=params,
            headers=_ZIMAS_HEADERS,
            timeout=15.0,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None


def _zimas_extract_adu_fields(zimas_data: list) -> dict | None:
    """Pull ADU-relevant fields out of the ZIMAS GetProjectData response."""
    if not zimas_data or not isinstance(zimas_data, list):
        return None

    def _find(section_key: str, desc: str) -> str:
        for section in zimas_data:
            if section.get("Key") == section_key:
                for item in section.get("Value", []):
                    if item.get("Description") == desc:
                        return item.get("Value", "")
        return ""

    def _find_all(section_key: str, desc: str) -> list[str]:
        results = []
        for section in zimas_data:
            if section.get("Key") == section_key:
                for item in section.get("Value", []):
                    if item.get("Description") == desc:
                        v = item.get("Value", "")
                        if v:
                            results.append(v)
        return results

    zoning = _find("Planning and Zoning Information", "Zoning")
    hpoz = _find("Planning and Zoning Information", "Historic Preservation Review")
    flood = _find("Additional Information", "Flood Zone")
    fire = _find("Additional Information", "Very High Fire Hazard Severity Zone")
    coastal = _find("Additional Information", "Coastal Zone")
    hillside = _find("Planning and Zoning Information", "Hillside Area (Zoning Code)")
    address = _find("Address/Legal Information", "Site Address")
    apn = _find("Address/Legal Information", "Assessor Parcel No. (APN)")

    # Build zoning overlays list from ZI items
    zi_items = _find_all("Planning and Zoning Information", "Zoning Information (ZI)")
    overlays = list(zi_items)
    if coastal and coastal.lower() != "none":
        overlays.append(f"Coastal Zone: {coastal}")

    return {
        "address": address or "Unknown",
        "apn": apn or "Unknown",
        "zoning": zoning,
        "hpoz": hpoz,
        "flood_zone": flood,
        "fire_hazard": fire,
        "hillside_area": hillside,
        "zoning_overlays": overlays,
    }


def _zimas_lookup(address: str) -> dict | None:
    """Look up a parcel via the ZIMAS API by address, returns ADU fields dict."""
    pin = _zimas_get_pin(address)
    if not pin:
        return None
    raw = _zimas_get_project_data(pin)
    if not raw:
        return None
    return _zimas_extract_adu_fields(raw)


def _fmt_apn(loc: dict) -> str:
    """Extract and format the APN from location data (10-digit \u2192 XXXX-XXX-XXX)."""
    apn_values = loc.get("apn_values", {})
    apn = apn_values.get("apn")
    if apn:
        s = str(apn)
        if len(s) == 10:
            return f"{s[:4]}-{s[4:7]}-{s[7:]}"
        return s
    return "N/A"
