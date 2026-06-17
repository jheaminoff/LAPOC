"""Agent tool functions — each wraps DB queries and returns plain-text summaries."""

from models import Case, Plot, WorkflowPersona, WorkflowStep
from sqlalchemy.orm import Session

# --------------------------------------------------------------------------- #
# Tool 1: lookup_parcel
# --------------------------------------------------------------------------- #


def lookup_parcel(apn_or_address: str, db: Session) -> str:
    """
    Look up a parcel by APN (XXXX-XXX-XXX) or partial address.
    Returns a plain-text summary of the plot and all its open cases.
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
                lines.append(f"  • APN {p.apn} — {p.address}")
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
        "",
        f"CASES ({len(cases)} total):",
    ]

    if not cases:
        lines.append("  No active or historical cases found.")
    else:
        for c in cases:
            fee_note = ""
            if c.fees_outstanding and c.fees_outstanding > 0:
                fee_note = f" | ⚠ ${c.fees_outstanding:,.0f} outstanding"
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
            lines.append(f"    💡 {guidance}")
        lines.append("")

    return "\n".join(lines)
