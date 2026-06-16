"""Seed synthetic data — ~30 cases across LA neighborhoods, personas, and statuses."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import engine, SessionLocal, Base
from models import Plot, Case, WorkflowStep, WorkflowPersona

Base.metadata.create_all(bind=engine)


# --------------------------------------------------------------------------- #
# Parcels
# --------------------------------------------------------------------------- #

PLOTS = [
    # Silver Lake
    dict(apn="5149-022-018", address="2412 Hyperion Ave, Los Angeles, CA 90027",
         neighborhood="Silver Lake", zoning="RD1.5-1", lot_size_sqft=6200, current_use="Single Family Residential"),
    dict(apn="5149-031-004", address="3801 Sunset Blvd, Los Angeles, CA 90026",
         neighborhood="Silver Lake", zoning="C2-1VL", lot_size_sqft=7800, current_use="Retail/Commercial"),

    # Hollywood
    dict(apn="5551-020-007", address="1234 N Highland Ave, Los Angeles, CA 90038",
         neighborhood="Hollywood", zoning="C4-2D", lot_size_sqft=11000, current_use="Mixed-Use"),
    dict(apn="5551-007-015", address="6400 Selma Ave, Los Angeles, CA 90028",
         neighborhood="Hollywood", zoning="R4-2", lot_size_sqft=9500, current_use="Multi-Family Residential"),

    # West Adams
    dict(apn="5054-011-022", address="3620 W Adams Blvd, Los Angeles, CA 90018",
         neighborhood="West Adams", zoning="RD2-1", lot_size_sqft=5800, current_use="Single Family Residential"),
    dict(apn="5054-020-031", address="4100 S Western Ave, Los Angeles, CA 90062",
         neighborhood="West Adams", zoning="C2-1", lot_size_sqft=8400, current_use="Commercial/Retail"),

    # Downtown LA
    dict(apn="5149-001-900", address="600 S Spring St, Los Angeles, CA 90014",
         neighborhood="Downtown LA", zoning="C5-4D-CDO", lot_size_sqft=18500, current_use="Commercial Office"),
    dict(apn="5149-002-811", address="440 S Flower St, Los Angeles, CA 90071",
         neighborhood="Downtown LA", zoning="C5-4D", lot_size_sqft=22000, current_use="Commercial Office"),

    # Venice
    dict(apn="4228-005-019", address="741 Brooks Ave, Venice, CA 90291",
         neighborhood="Venice", zoning="RD1.5-1", lot_size_sqft=4200, current_use="Single Family Residential"),
    dict(apn="4228-011-044", address="1902 Lincoln Blvd, Venice, CA 90291",
         neighborhood="Venice", zoning="C2-1VL", lot_size_sqft=6600, current_use="Retail/Commercial"),

    # Sunset Strip / West Hollywood border
    dict(apn="4342-003-027", address="8800 Sunset Blvd, West Hollywood, CA 90069",
         neighborhood="Sunset Strip", zoning="C2-1L", lot_size_sqft=9200, current_use="Restaurant/Bar"),
]


# --------------------------------------------------------------------------- #
# Cases
# --------------------------------------------------------------------------- #

CASES = [
    # ---- RESIDENT cases ----
    # ADU on Silver Lake single-family
    dict(case_id="24-012-10-000-88441", apn="5149-022-018", department="LADBS",
         process_type="ADU", applicant_type="resident",
         applicant_name="Maria Gonzalez", submitted_date="2024-03-15",
         current_status="PC Approved",
         assigned_to="Plan Check Engr. J. Nakamura",
         description="Attached ADU, 600 sq ft, converting detached garage",
         fees_paid=2800.0, fees_outstanding=0.0, hearing_date=None,
         next_action="Pay issuance fees ($430) at Metro office or online via MyLADBS to receive permit.",
         portal_url="https://ladbs.org/services/check-status"),

    # Kitchen/bath remodel — simple alter/repair
    dict(case_id="24-010-10-000-55210", apn="5054-011-022", department="LADBS",
         process_type="Bldg-Alter/Repair", applicant_type="resident",
         applicant_name="James Okafor", submitted_date="2024-06-01",
         current_status="Issued",
         assigned_to=None,
         description="Kitchen and bathroom remodel, non-structural",
         fees_paid=950.0, fees_outstanding=0.0, hearing_date=None,
         next_action="Schedule rough framing inspection via MyLADBS (inspection type 015).",
         portal_url="https://ladbs.org/services/check-status"),

    # Small swimming pool
    dict(case_id="24-007-20-000-31045", apn="4228-005-019", department="LADBS",
         process_type="Swimming-Pool/Spa", applicant_type="resident",
         applicant_name="Chen Wei", submitted_date="2024-08-10",
         current_status="Corrections Needed",
         assigned_to="Plan Check Engr. A. Reyes",
         description="New in-ground pool and spa, 400 sq ft",
         fees_paid=1200.0, fees_outstanding=0.0, hearing_date=None,
         next_action="Respond to plan check correction letter. Resubmit revised grading/drainage plan showing 5-ft setback compliance.",
         portal_url="https://ladbs.org/services/check-status"),

    # Roof replacement — express permit
    dict(case_id="24-014-10-000-09921", apn="5054-011-022", department="LADBS",
         process_type="Bldg-Alter/Repair", applicant_type="resident",
         applicant_name="James Okafor", submitted_date="2024-09-02",
         current_status="Permit Finaled",
         assigned_to=None,
         description="Re-roof: remove and replace existing comp shingle, same-for-same",
         fees_paid=180.0, fees_outstanding=0.0, hearing_date=None,
         next_action="Permit finaled. No further action required.",
         portal_url="https://ladbs.org/services/check-status"),

    # ---- DEVELOPER cases ----
    # New 12-unit apartment — Hollywood
    dict(case_id="23-001-10-000-44100", apn="5551-007-015", department="LADBS",
         process_type="Bldg-New", applicant_type="developer",
         applicant_name="Apex Urban Development LLC", submitted_date="2023-10-15",
         current_status="PC Assigned",
         assigned_to="Plan Check Engr. D. Stein (Multi-Family Team)",
         description="New 12-unit apartment building, Type V-A, 3 stories, 14,000 sq ft",
         fees_paid=38000.0, fees_outstanding=0.0, hearing_date=None,
         next_action="Await plan check comments. Estimated first correction letter in 6-8 weeks (Complex plan check queue).",
         portal_url="https://ladbs.org/services/check-status"),

    # CUB for rooftop bar — Hollywood
    dict(case_id="ZA-2024-003812-CUB", apn="5551-020-007", department="City Planning",
         process_type="CUB", applicant_type="developer",
         applicant_name="Apex Urban Development LLC", submitted_date="2024-01-22",
         current_status="Pending Hearing",
         assigned_to="Case Planner: P. Martinez (GeoTeam West)",
         description="Conditional Use — alcohol service on rooftop bar/restaurant, Type 47 license, capacity 120",
         fees_paid=14500.0, fees_outstanding=0.0, hearing_date="2024-11-14",
         next_action="Attend public hearing at West LA APC on 2024-11-14. Submit any additional evidence 10 days prior.",
         portal_url="https://planning.lacity.gov/pdiscaseinfo"),

    # Zone Change — West Adams commercial to mixed-use
    dict(case_id="CPC-2023-008741-ZC", apn="5054-020-031", department="City Planning",
         process_type="ZC", applicant_type="developer",
         applicant_name="Westside Realty Partners Inc.", submitted_date="2023-07-05",
         current_status="Technical Review",
         assigned_to="Senior Planner: T. Yamamoto (GeoTeam South)",
         description="Zone Change from C2-1 to C2-1-CDO to enable mixed-use development with residential above",
         fees_paid=16200.0, fees_outstanding=0.0, hearing_date=None,
         next_action="CEQA Initial Study in progress. Anticipate MND publication Q1 2025. 30-day public comment period follows.",
         portal_url="https://planning.lacity.gov/pdiscaseinfo"),

    # TOC density bonus — Hollywood
    dict(case_id="DIR-2024-011002-TOC", apn="5551-007-015", department="City Planning",
         process_type="TOC", applicant_type="developer",
         applicant_name="Apex Urban Development LLC", submitted_date="2024-02-28",
         current_status="Completeness Review",
         assigned_to="Case Planner: R. Nguyen (EPS)",
         description="Transit Oriented Communities Tier 3 incentives — 18-unit project, 3 affordable units at 80% AMI",
         fees_paid=7200.0, fees_outstanding=0.0, hearing_date=None,
         next_action="Completeness letter expected within 30 days. Provide updated site plan showing required open space compliance.",
         portal_url="https://planning.lacity.gov/pdiscaseinfo"),

    # EIR scoping — DTLA office tower
    dict(case_id="ENV-2024-005502-EIR", apn="5149-001-900", department="City Planning",
         process_type="EIR", applicant_type="developer",
         applicant_name="Downtown Core Partners LLC", submitted_date="2024-05-01",
         current_status="Notice of Preparation",
         assigned_to="EIR Coordinator: L. Park (CEQA Team)",
         description="Program EIR for 28-story mixed-use tower, 280 residential + 40,000 sf commercial",
         fees_paid=52000.0, fees_outstanding=28000.0, hearing_date="2024-12-03",
         next_action="NOP comment period closes 2024-12-03. Pay remaining EIR deposit ($28,000) before scoping meeting.",
         portal_url="https://planning.lacity.gov/pdiscaseinfo"),

    # Tract map — Hollywood multi-unit condo conversion
    dict(case_id="AA-2024-007231-TT", apn="5551-007-015", department="City Planning",
         process_type="TT", applicant_type="developer",
         applicant_name="Apex Urban Development LLC", submitted_date="2024-03-10",
         current_status="Pending Conditions Clearance",
         assigned_to="Advisory Agency: B. Chen",
         description="Tentative Tract Map for 12-unit residential condominium conversion",
         fees_paid=11800.0, fees_outstanding=0.0, hearing_date=None,
         next_action="LOD issued 2024-09-18. Return to DSC Metro to clear Conditions 4, 7, and 12 before map recordation.",
         portal_url="https://planning.lacity.gov/pdiscaseinfo"),

    # ED1 affordable housing — Venice
    dict(case_id="DIR-2024-014220-ED1", apn="4228-011-044", department="City Planning",
         process_type="ED1", applicant_type="developer",
         applicant_name="Community Housing LA Inc.", submitted_date="2024-06-15",
         current_status="Under Review",
         assigned_to="Case Planner: M. Torres (EPS)",
         description="ED1 streamlining — 24-unit 100% affordable housing project, Venice",
         fees_paid=4100.0, fees_outstanding=0.0, hearing_date=None,
         next_action="ED1 determination expected within 60 days per Executive Directive 1 timelines.",
         portal_url="https://planning.lacity.gov/pdiscaseinfo"),

    # DB (Density Bonus) — Silver Lake
    dict(case_id="ZA-2024-009012-DB", apn="5149-031-004", department="City Planning",
         process_type="DB", applicant_type="developer",
         applicant_name="Silver Lake Development LLC", submitted_date="2024-04-20",
         current_status="LOD Issued",
         assigned_to="Zoning Administrator: H. Kim",
         description="Density Bonus — 15 units base + 5 bonus units, 2 Very Low Income units required",
         fees_paid=8900.0, fees_outstanding=0.0, hearing_date=None,
         next_action="LOD issued 2024-10-05. Appeal period expired 2024-10-20. Clear conditions at DSC then file LADBS permit.",
         portal_url="https://planning.lacity.gov/pdiscaseinfo"),

    # Variance — Venice
    dict(case_id="ZA-2024-002187-ZV", apn="4228-005-019", department="City Planning",
         process_type="ZV", applicant_type="developer",
         applicant_name="Chen Wei", submitted_date="2024-02-01",
         current_status="Application Withdrawn",
         assigned_to=None,
         description="Variance request — rear yard setback reduction from 15 ft to 8 ft for two-story addition",
         fees_paid=3200.0, fees_outstanding=0.0, hearing_date=None,
         next_action="Application withdrawn by applicant 2024-08-14. No further action.",
         portal_url="https://planning.lacity.gov/pdiscaseinfo"),

    # ---- CONTRACTOR cases ----
    # Electrical panel upgrade — West Adams
    dict(case_id="24-016-10-000-67401", apn="5054-011-022", department="LADBS",
         process_type="Electrical", applicant_type="contractor",
         applicant_name="SoCal Electric Inc. (Lic. C-10 #812345)", submitted_date="2024-07-18",
         current_status="Issued",
         assigned_to=None,
         description="200A panel upgrade, new service entrance, EV charger rough-in",
         fees_paid=420.0, fees_outstanding=0.0, hearing_date=None,
         next_action="Schedule rough wiring inspection (inspection type 320) via MyLADBS or call Metro (213) 482-0000.",
         portal_url="https://ladbs.org/services/check-status"),

    # HVAC replacement — Hollywood apartment
    dict(case_id="24-009-10-000-72188", apn="5551-007-015", department="LADBS",
         process_type="HVAC", applicant_type="contractor",
         applicant_name="Pacific Air Systems (Lic. C-20 #567890)", submitted_date="2024-08-05",
         current_status="Permit Finaled",
         assigned_to=None,
         description="Replace 6 HVAC units, split system, multi-family building",
         fees_paid=680.0, fees_outstanding=0.0, hearing_date=None,
         next_action="Permit finaled 2024-09-20. No further action required.",
         portal_url="https://ladbs.org/services/check-status"),

    # Fire sprinkler — DTLA office TI
    dict(case_id="24-008-10-000-81002", apn="5149-001-900", department="LADBS",
         process_type="Fire Sprinkler", applicant_type="contractor",
         applicant_name="LA Fire Protection Co. (Lic. C-16 #234567)", submitted_date="2024-09-01",
         current_status="PC Approved",
         assigned_to="Plan Check Engr. B. Patel",
         description="Tenant improvement — new fire sprinkler system, floors 14-16, NFPA 13",
         fees_paid=3100.0, fees_outstanding=0.0, hearing_date=None,
         next_action="Pay issuance fees and pick up approved plans. Schedule rough sprinkler inspection after rough-in.",
         portal_url="https://ladbs.org/services/check-status"),

    # Grading permit — Hollywood new build
    dict(case_id="23-003-10-000-55880", apn="5551-007-015", department="LADBS",
         process_type="Grading", applicant_type="contractor",
         applicant_name="Hillside Grading & Excavation (Lic. C-12 #445566)", submitted_date="2023-11-01",
         current_status="Issued",
         assigned_to=None,
         description="Rough grading — 800 CY cut, 200 CY fill, import 600 CY for new apartment building pad",
         fees_paid=5400.0, fees_outstanding=0.0, hearing_date=None,
         next_action="Schedule rough grading inspection. Obtain soils engineer sign-off before final grading inspection.",
         portal_url="https://ladbs.org/services/check-status"),

    # Plumbing reroute — Silver Lake SFR
    dict(case_id="24-015-10-000-43009", apn="5149-022-018", department="LADBS",
         process_type="Plumbing", applicant_type="contractor",
         applicant_name="SilverLake Plumbing Inc. (Lic. C-36 #778899)", submitted_date="2024-05-30",
         current_status="Ready to Issue",
         assigned_to=None,
         description="Repipe entire SFR — copper to PEX, 1,800 sq ft home",
         fees_paid=0.0, fees_outstanding=285.0, hearing_date=None,
         next_action="Pay issuance fees ($285) via MyLADBS to receive permit before starting work.",
         portal_url="https://ladbs.org/services/check-status"),

    # New construction — Sunset Strip restaurant build-out
    dict(case_id="24-001-10-000-90321", apn="4342-003-027", department="LADBS",
         process_type="Bldg-New", applicant_type="contractor",
         applicant_name="Sunset Build Group LLC (Lic. B #998877)", submitted_date="2024-01-10",
         current_status="CofO in Progress",
         assigned_to="Inspector J. Alvarez",
         description="New restaurant/bar build-out — 4,200 sq ft, 2 stories, Type V-B occupancy A-2",
         fees_paid=28500.0, fees_outstanding=0.0, hearing_date=None,
         next_action="CofO application filed 2024-10-01. Final inspection scheduled 2024-11-08. Ensure punch list items (accessibility, fire exit signage) resolved.",
         portal_url="https://ladbs.org/services/check-status"),

    # Intent to Revoke — non-compliant sign permit
    dict(case_id="23-020-10-000-11442", apn="5054-020-031", department="LADBS",
         process_type="Sign", applicant_type="contractor",
         applicant_name="LA Sign Works (Lic. C-45 #312098)", submitted_date="2023-05-12",
         current_status="Intent to Revoke",
         assigned_to="Inspector K. Brown",
         description="Wall sign — 8ft x 4ft illuminated channel letters, commercial building",
         fees_paid=650.0, fees_outstanding=0.0, hearing_date="2024-11-20",
         next_action="LADBS issued Notice of Intent to Revoke on 2024-10-10. Sign installed exceeds approved dimensions. Attend hearing 2024-11-20 or remove/modify sign immediately.",
         portal_url="https://ladbs.org/services/check-status"),

    # Elevator modernization — DTLA
    dict(case_id="24-004-10-000-22987", apn="5149-002-811", department="LADBS",
         process_type="Elevator", applicant_type="contractor",
         applicant_name="West Coast Elevator Inc. (Lic. C-11 #654321)", submitted_date="2024-04-15",
         current_status="PC on Hold",
         assigned_to="Elevator Plan Check Engr. M. Lee",
         description="Elevator modernization — 2 traction elevators, cab refurbish, new controls, ADA updates",
         fees_paid=4200.0, fees_outstanding=0.0, hearing_date=None,
         next_action="Plan check placed on hold pending structural calculation review. Contact engr. M. Lee at (213) 482-0000 Ext. 4402 for requirements.",
         portal_url="https://ladbs.org/services/check-status"),

    # New commercial building — DTLA
    dict(case_id="24-001-10-000-77700", apn="5149-002-811", department="LADBS",
         process_type="Bldg-New", applicant_type="developer",
         applicant_name="Downtown Core Partners LLC", submitted_date="2024-06-20",
         current_status="Fees Due",
         assigned_to=None,
         description="New 6-story office/retail building, 55,000 sq ft, Type I-A",
         fees_paid=0.0, fees_outstanding=62000.0, hearing_date=None,
         next_action="Plan check fees of $62,000 due before submission. Pay at Metro DSC or online.",
         portal_url="https://ladbs.org/services/check-status"),

    # HPOZ review — Silver Lake
    dict(case_id="ZA-2024-006550-ADUH", apn="5149-022-018", department="City Planning",
         process_type="ADU", applicant_type="resident",
         applicant_name="Maria Gonzalez", submitted_date="2024-04-01",
         current_status="Under Review",
         assigned_to="HPOZ Preservation Planner: C. Park",
         description="ADUH — ADU in Historic Preservation Overlay Zone (Silver Lake HPOZ), garage conversion, must meet HPOZ design guidelines",
         fees_paid=1800.0, fees_outstanding=0.0, hearing_date=None,
         next_action="HPOZ board review scheduled Q4 2024. Submit revised exterior materials board per Silver Lake HPOZ Design Guidelines.",
         portal_url="https://planning.lacity.gov/pdiscaseinfo"),

    # CUB appeal — Sunset Strip
    dict(case_id="ZA-2023-015700-CUB-1A", apn="4342-003-027", department="City Planning",
         process_type="CUB", applicant_type="developer",
         applicant_name="Sunset Strip Entertainment Group", submitted_date="2023-09-15",
         current_status="Appeal Pending",
         assigned_to="APC West LA: Panel TBD",
         description="CUB for late-night alcohol service (Type 47, 2am closing) — appealed by neighboring property owners",
         fees_paid=14800.0, fees_outstanding=0.0, hearing_date="2024-12-11",
         next_action="Appeal hearing scheduled 2024-12-11 at West LA APC. Retain land use counsel. Prepare response to neighbor objections.",
         portal_url="https://planning.lacity.gov/pdiscaseinfo"),

    # SIP (SB35) — Hollywood
    dict(case_id="DIR-2024-008001-SIP", apn="5551-020-007", department="City Planning",
         process_type="SIP", applicant_type="developer",
         applicant_name="Hollywood Housing Partners", submitted_date="2024-07-30",
         current_status="Completeness Review",
         assigned_to="Case Planner: A. Singh (EPS)",
         description="SB 35 Streamlined Infill — 30-unit multi-family, 6 affordable at 50% AMI, Hollywood",
         fees_paid=6500.0, fees_outstanding=0.0, hearing_date=None,
         next_action="Completeness determination due within 60 days per SB 35 timelines. Provide updated noise study.",
         portal_url="https://planning.lacity.gov/pdiscaseinfo"),

    # GPA — West Adams
    dict(case_id="CPC-2022-005500-GPA", apn="5054-020-031", department="City Planning",
         process_type="GPA", applicant_type="developer",
         applicant_name="Westside Realty Partners Inc.", submitted_date="2022-11-20",
         current_status="Hearing Scheduled",
         assigned_to="Senior Planner: T. Yamamoto (GeoTeam South)",
         description="General Plan Amendment — land use designation from Low Industrial to Medium Residential",
         fees_paid=21000.0, fees_outstanding=0.0, hearing_date="2025-01-15",
         next_action="CPC public hearing 2025-01-15. Publish public notice within 500-ft radius and in local newspaper per LAMC 12.32.",
         portal_url="https://planning.lacity.gov/pdiscaseinfo"),
]


# --------------------------------------------------------------------------- #
# Workflow steps — key process types
# --------------------------------------------------------------------------- #

WORKFLOW_STEPS = [
    # ADU (LADBS administrative)
    dict(process_type="ADU", step_order=1, step_name="Check ADU Eligibility",
         description="Verify lot meets ADU requirements: zoning, fire zone, HPOZ, lot size. Use ZIMAS.",
         responsible_party="Applicant", typical_days="1-3"),
    dict(process_type="ADU", step_order=2, step_name="Prepare Plans",
         description="Draw site plan, floor plan, elevations showing ADU. Must show setbacks, height, utility connections.",
         responsible_party="Applicant", typical_days="5-14"),
    dict(process_type="ADU", step_order=3, step_name="Submit to LADBS",
         description="File online via MyLADBS or in-person at district office. Pay plan check fees.",
         responsible_party="Applicant", typical_days="1"),
    dict(process_type="ADU", step_order=4, step_name="Plan Check Review",
         description="LADBS reviews plans against zoning code and building code. May issue correction letter.",
         responsible_party="LADBS", typical_days="20-30"),
    dict(process_type="ADU", step_order=5, step_name="Respond to Corrections",
         description="If correction letter issued, revise plans and resubmit.",
         responsible_party="Applicant", typical_days="7-14"),
    dict(process_type="ADU", step_order=6, step_name="Pay Issuance Fees & Receive Permit",
         description="Once PC Approved, pay issuance fees. Permit issued — post on job site.",
         responsible_party="Applicant", typical_days="1-2"),
    dict(process_type="ADU", step_order=7, step_name="Construction",
         description="Build per approved plans. Do not deviate without prior LADBS approval.",
         responsible_party="Applicant", typical_days="60-180"),
    dict(process_type="ADU", step_order=8, step_name="Inspections",
         description="Schedule and pass all required inspections: foundation, framing, rough MEP, insulation, final.",
         responsible_party="LADBS", typical_days="5-30"),
    dict(process_type="ADU", step_order=9, step_name="Final Sign-Off",
         description="All inspections pass. LADBS finals the permit.",
         responsible_party="LADBS", typical_days="2-5"),

    # Bldg-New (residential)
    dict(process_type="Bldg-New", step_order=1, step_name="Confirm Zoning & Entitlements",
         description="Verify project is by-right or determine which City Planning entitlements are needed first.",
         responsible_party="Applicant", typical_days="1-5"),
    dict(process_type="Bldg-New", step_order=2, step_name="Prepare Construction Documents",
         description="Architect prepares full plan set: architectural, structural, MEP, Title 24 energy, civil/grading.",
         responsible_party="Applicant", typical_days="30-90"),
    dict(process_type="Bldg-New", step_order=3, step_name="Pre-Application Meeting (Optional)",
         description="Optional DSC meeting to clarify requirements before submitting.",
         responsible_party="Applicant", typical_days="1"),
    dict(process_type="Bldg-New", step_order=4, step_name="Submit to LADBS",
         description="Submit full plan set to LADBS. Pay plan check fees at submission.",
         responsible_party="Applicant", typical_days="1"),
    dict(process_type="Bldg-New", step_order=5, step_name="Plan Check Review",
         description="LADBS engineers review architectural, structural, fire, MEP, accessibility. First round typically 6-10 weeks.",
         responsible_party="LADBS", typical_days="30-70"),
    dict(process_type="Bldg-New", step_order=6, step_name="Respond to Corrections",
         description="Address plan check comments and resubmit. Multiple rounds possible.",
         responsible_party="Applicant", typical_days="14-30"),
    dict(process_type="Bldg-New", step_order=7, step_name="PC Approved — Issue Permit",
         description="Plans approved. Pay issuance fees. Post permit on site before any work begins.",
         responsible_party="Applicant", typical_days="1-3"),
    dict(process_type="Bldg-New", step_order=8, step_name="Construction & Inspections",
         description="Construct per plans. LADBS inspector visits for foundation, framing, rough MEP, structural, insulation, drywall, final.",
         responsible_party="Applicant", typical_days="90-365"),
    dict(process_type="Bldg-New", step_order=9, step_name="Certificate of Occupancy",
         description="After final inspection passes, LADBS issues CofO or TCO. Required before occupancy.",
         responsible_party="LADBS", typical_days="5-14"),

    # Bldg-Alter/Repair
    dict(process_type="Bldg-Alter/Repair", step_order=1, step_name="Determine Permit Type",
         description="Check if project requires full plan check or can be permitted as express/over-the-counter.",
         responsible_party="Applicant", typical_days="1"),
    dict(process_type="Bldg-Alter/Repair", step_order=2, step_name="Prepare Plans or Scope",
         description="Draw plans showing existing and proposed conditions. Non-structural may not need stamped plans.",
         responsible_party="Applicant", typical_days="2-14"),
    dict(process_type="Bldg-Alter/Repair", step_order=3, step_name="Submit & Pay Fees",
         description="Submit online or at district office. Pay plan check fees.",
         responsible_party="Applicant", typical_days="1"),
    dict(process_type="Bldg-Alter/Repair", step_order=4, step_name="Plan Check Review",
         description="LADBS reviews plans. Simple projects may be approved same day (OTC). Complex takes 3-6 weeks.",
         responsible_party="LADBS", typical_days="1-30"),
    dict(process_type="Bldg-Alter/Repair", step_order=5, step_name="Permit Issued",
         description="Pay issuance fees. Keep permit and approved plans on site during construction.",
         responsible_party="Applicant", typical_days="1"),
    dict(process_type="Bldg-Alter/Repair", step_order=6, step_name="Construction & Inspections",
         description="Perform work per approved plans. Call for inspections at required stages.",
         responsible_party="Applicant", typical_days="7-90"),
    dict(process_type="Bldg-Alter/Repair", step_order=7, step_name="Final Inspection",
         description="LADBS inspector finals permit after all work and inspections complete.",
         responsible_party="LADBS", typical_days="1-3"),

    # CUB — Conditional Use Beverage/Alcohol
    dict(process_type="CUB", step_order=1, step_name="Pre-Application Meeting",
         description="Meet with City Planning staff at DSC to understand requirements and potential issues.",
         responsible_party="Applicant", typical_days="1"),
    dict(process_type="CUB", step_order=2, step_name="File CUB Application",
         description="Submit application via OAS portal. Pay filing fees (~$13,000-$15,000). Include site plan, floor plan, ABC license info.",
         responsible_party="Applicant", typical_days="1"),
    dict(process_type="CUB", step_order=3, step_name="Completeness Review",
         description="City Planning checks application is complete. Requests any missing materials.",
         responsible_party="City Planning", typical_days="14-30"),
    dict(process_type="CUB", step_order=4, step_name="Technical Review & Draft Conditions",
         description="Planner reviews for zoning compliance, community plan, LAMC 12.24. Drafts conditions of approval.",
         responsible_party="City Planning", typical_days="60-90"),
    dict(process_type="CUB", step_order=5, step_name="Public Notice",
         description="500-ft mailing to neighboring properties. Post notice on site. LA Times or local paper publication.",
         responsible_party="City Planning", typical_days="21"),
    dict(process_type="CUB", step_order=6, step_name="Public Hearing",
         description="Hearing before Zoning Administrator (ZA) or Area Planning Commission (APC). Present project, respond to objections.",
         responsible_party="Applicant", typical_days="1"),
    dict(process_type="CUB", step_order=7, step_name="Letter of Determination (LOD)",
         description="ZA or APC issues LOD with approval/denial and all conditions of approval.",
         responsible_party="City Planning", typical_days="10-21"),
    dict(process_type="CUB", step_order=8, step_name="Appeal Period",
         description="15-day window for neighbors or applicant to appeal. If appealed, case goes to next decision-maker level.",
         responsible_party="City Planning", typical_days="15"),
    dict(process_type="CUB", step_order=9, step_name="Clear Conditions at DSC",
         description="Return to DSC to demonstrate compliance with each condition in LOD before LADBS will issue building permit.",
         responsible_party="Applicant", typical_days="5-30"),
    dict(process_type="CUB", step_order=10, step_name="File LADBS Building Permit",
         description="With LOD and conditions cleared, file for LADBS tenant improvement or new construction permit.",
         responsible_party="Applicant", typical_days="1"),

    # ZC — Zone Change
    dict(process_type="ZC", step_order=1, step_name="Preliminary Zoning Assessment",
         description="File PZA with City Planning to identify non-conforming aspects of the proposed zone change.",
         responsible_party="Applicant", typical_days="5-10"),
    dict(process_type="ZC", step_order=2, step_name="Pre-Application Conference",
         description="Meet with GeoTeam or EPS planner to discuss project scope and entitlement strategy.",
         responsible_party="Applicant", typical_days="1"),
    dict(process_type="ZC", step_order=3, step_name="File Zone Change Application",
         description="Submit application via OAS. Pay fees ($12,000-$17,000+). Include legal description, CEQA forms, site plans.",
         responsible_party="Applicant", typical_days="1"),
    dict(process_type="ZC", step_order=4, step_name="Application Completeness",
         description="City Planning verifies all required materials submitted.",
         responsible_party="City Planning", typical_days="14-30"),
    dict(process_type="ZC", step_order=5, step_name="CEQA Review",
         description="Environmental analysis — Initial Study to determine if CE, MND, or EIR required. MND/EIR adds months.",
         responsible_party="City Planning", typical_days="60-180"),
    dict(process_type="ZC", step_order=6, step_name="Technical Staff Review",
         description="Planner prepares staff report with findings, conditions, and recommendation.",
         responsible_party="City Planning", typical_days="60-90"),
    dict(process_type="ZC", step_order=7, step_name="Public Hearing — APC or CPC",
         description="Area Planning Commission or City Planning Commission holds public hearing on zone change.",
         responsible_party="City Planning", typical_days="1"),
    dict(process_type="ZC", step_order=8, step_name="Council File / City Council",
         description="Zone changes require City Council action. CPC recommendation forwarded to Council.",
         responsible_party="City Planning", typical_days="30-90"),
    dict(process_type="ZC", step_order=9, step_name="Ordinance Effective",
         description="Zone Change Ordinance effective 30 days after City Council approval. Zone updated in ZIMAS.",
         responsible_party="City Planning", typical_days="30"),
]


# --------------------------------------------------------------------------- #
# Persona guidance
# --------------------------------------------------------------------------- #

WORKFLOW_PERSONAS = [
    # ADU — resident
    dict(process_type="ADU", step_name="Check ADU Eligibility", persona="resident",
         guidance="Go to zimas.lacity.org and enter your address. Look for 'Zoning' and any 'Overlay' zones. If you see HPOZ, there's extra review — call City Planning first."),
    dict(process_type="ADU", step_name="Prepare Plans", persona="resident",
         guidance="You don't need a licensed architect for a simple garage conversion, but a draftsperson ($500-$1,500) can save you from correction letters."),
    dict(process_type="ADU", step_name="Submit to LADBS", persona="resident",
         guidance="You can start online at ladbs.org. Choose 'Submit a Permit Application' → 'ADU'. Much faster than going in person."),
    dict(process_type="ADU", step_name="Plan Check Review", persona="resident",
         guidance="LADBS usually reviews ADUs in 20-30 days. You'll get an email with any corrections needed. Check your MyLADBS inbox."),
    dict(process_type="ADU", step_name="Pay Issuance Fees & Receive Permit", persona="resident",
         guidance="Issuance fees are separate from plan check fees. Usually $200-$600 for an ADU. Pay online to avoid a trip downtown."),
    dict(process_type="ADU", step_name="Inspections", persona="resident",
         guidance="Schedule inspections via MyLADBS or by calling your district office. You'll need: foundation, framing, rough electrical/plumbing, insulation, and final. Your contractor should coordinate these."),

    # ADU — contractor
    dict(process_type="ADU", step_name="Submit to LADBS", persona="contractor",
         guidance="Use ePlanLA (eplanla.lacity.org) for electronic plan submission. Ensure Title 24 energy calcs and CALGreen checklist are included in the package."),
    dict(process_type="ADU", step_name="Plan Check Review", persona="contractor",
         guidance="ADU plan check at Metro branch averages 20-25 days first round. Track status via MyLADBS or call (213) 482-0000."),
    dict(process_type="ADU", step_name="Inspections", persona="contractor",
         guidance="Required inspections: 010 (foundation), 020 (framing), 030 (rough plumbing), 040 (rough electrical), 055 (insulation), 999 (final). Use MyLADBS inspection scheduling portal."),

    # Bldg-New — developer
    dict(process_type="Bldg-New", step_name="Confirm Zoning & Entitlements", persona="developer",
         guidance="Run ZIMAS to confirm base zone, applicable overlays (TOC, HPOZ, CDO, RIO), Q/D conditions, and community plan land use. Flag any discretionary entitlements before starting CDs."),
    dict(process_type="Bldg-New", step_name="Submit to LADBS", persona="developer",
         guidance="Multi-family projects go to the Multi-Family Plan Check team (Metro branch). Include fire dept prelim approval for Type V-A+. Submit via ePlanLA."),
    dict(process_type="Bldg-New", step_name="Plan Check Review", persona="developer",
         guidance="First round typically 8-12 weeks for multi-family. Track correction queue via MyLADBS. Consider hiring a plan check expediter for complex projects."),
    dict(process_type="Bldg-New", step_name="Certificate of Occupancy", persona="developer",
         guidance="File CofO application before final inspection. LADBS issues TCO if minor outstanding items remain — allows occupancy while resolving. CofO required for final loan draw in most construction finance agreements."),

    # CUB — developer
    dict(process_type="CUB", step_name="Pre-Application Meeting", persona="developer",
         guidance="Book a DSC appointment at planning.lacity.gov/contact. Bring site plan and proposed ABC license type. Ask about any Specific Plan overlays (Sunset Specific Plan, etc.) that add requirements."),
    dict(process_type="CUB", step_name="File CUB Application", persona="developer",
         guidance="File via OAS at planning.lacity.gov/oas. Case prefix will be ZA- or APC- depending on project scale. ZA cases are faster (3-5 months) vs APC (5-8 months)."),
    dict(process_type="CUB", step_name="Public Hearing", persona="developer",
         guidance="Prepare a formal presentation: site plan, operating parameters, community outreach evidence, responses to LAPD/Fire dept comments. Having a land use attorney present strengthens the record."),
    dict(process_type="CUB", step_name="Clear Conditions at DSC", persona="developer",
         guidance="Obtain a copy of the LOD from the case planner. Go through each condition systematically. Some require separate permits or agency sign-offs (LAPD, Health Dept). Allow 2-4 weeks."),

    # ZC — developer
    dict(process_type="ZC", step_name="Preliminary Zoning Assessment", persona="developer",
         guidance="PZA fee ~$862 (LAMC 19.09). Identifies any non-compliance that the ZC must address. Critical for locking down the issues list before investing in full CDs."),
    dict(process_type="ZC", step_name="CEQA Review", persona="developer",
         guidance="If MND: 20-30 day public comment period + 10-day response period. If EIR: NOP (30 days) + Scoping + Draft EIR (45-day comment) + Final EIR + Findings. Budget 18-36 months for EIR track."),
    dict(process_type="ZC", step_name="Council File / City Council", persona="developer",
         guidance="Council files move through Planning & Land Use Management (PLUM) Committee before full Council vote. Engage Council office staff early. Allow 3-6 months post-CPC action."),
]


# --------------------------------------------------------------------------- #
# Seed function
# --------------------------------------------------------------------------- #

def seed():
    db = SessionLocal()
    try:
        # Wipe existing data
        db.query(WorkflowPersona).delete()
        db.query(WorkflowStep).delete()
        db.query(Case).delete()
        db.query(Plot).delete()
        db.commit()

        # Insert plots
        for p in PLOTS:
            db.add(Plot(**p))
        db.commit()

        # Insert cases
        for c in CASES:
            db.add(Case(**c))
        db.commit()

        # Insert workflow steps
        for s in WORKFLOW_STEPS:
            db.add(WorkflowStep(**s))
        db.commit()

        # Insert persona guidance
        for g in WORKFLOW_PERSONAS:
            db.add(WorkflowPersona(**g))
        db.commit()

        print(f"✓ Seeded {len(PLOTS)} plots, {len(CASES)} cases, "
              f"{len(WORKFLOW_STEPS)} workflow steps, {len(WORKFLOW_PERSONAS)} persona rows.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
