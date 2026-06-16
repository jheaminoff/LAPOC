"""Seed synthetic data — 30 cases across verified LA parcels, real permit number formats."""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import engine, SessionLocal, Base
from models import Plot, Case, WorkflowStep, WorkflowPersona

Base.metadata.create_all(bind=engine)


# --------------------------------------------------------------------------- #
# Parcels — verified real APNs from GIS query (maps.lacity.org, June 2026)
# --------------------------------------------------------------------------- #

PLOTS = [
    # Silver Lake — SFR on Sunset Blvd
    dict(apn="5462-001-016", address="2815 Sunset Blvd, Los Angeles, CA 90026",
         neighborhood="Silver Lake", zoning="R1-1-HCR",
         lot_size_sqft=6800, current_use="Single Family Residential"),

    # Silver Lake — duplex-zoned residential
    dict(apn="5423-011-023", address="2414 Effie St, Los Angeles, CA 90026",
         neighborhood="Silver Lake", zoning="R2-1VL",
         lot_size_sqft=5400, current_use="Single Family Residential"),

    # Hollywood — commercial strip
    dict(apn="5547-026-018", address="1757 N Las Palmas Ave, Los Angeles, CA 90028",
         neighborhood="Hollywood", zoning="C1-1VL",
         lot_size_sqft=7200, current_use="Retail/Commercial"),

    # Venice — beachside residential
    dict(apn="4226-012-012", address="23 Windward Ave, Venice, CA 90291",
         neighborhood="Venice", zoning="R3-1-O",
         lot_size_sqft=4500, current_use="Single Family Residential"),

    # South LA — SFR
    dict(apn="5017-026-049", address="3800 S Vermont Ave, Los Angeles, CA 90007",
         neighborhood="South LA", zoning="R1-1",
         lot_size_sqft=6200, current_use="Single Family Residential"),

    # Leimert Park — SFR
    dict(apn="5006-008-016", address="4216 Degnan Blvd, Los Angeles, CA 90008",
         neighborhood="Leimert Park", zoning="R1-1",
         lot_size_sqft=7000, current_use="Single Family Residential"),

    # Downtown LA — high-density commercial (complex zoning overlay)
    dict(apn="5144-010-401", address="800 W 7th St, Los Angeles, CA 90017",
         neighborhood="Downtown LA", zoning="[HB5-SH1-5][CX4-FA][CPIO]",
         lot_size_sqft=22000, current_use="Commercial Office"),

    # West Adams — commercial with CPIO overlay
    dict(apn="5075-003-026", address="1239 S Westmoreland Ave, Los Angeles, CA 90006",
         neighborhood="West Adams", zoning="C2-2D-CPIO",
         lot_size_sqft=8400, current_use="Retail/Commercial"),

    # West Adams — specific plan area commercial
    dict(apn="5024-018-012", address="3450 W 43rd St, Los Angeles, CA 90008",
         neighborhood="West Adams", zoning="C1.5-1-SP",
         lot_size_sqft=5800, current_use="Commercial/Retail"),

    # Sunset Strip — hillside residential (coastal range)
    dict(apn="5555-026-025", address="9000 Sunset Blvd, West Hollywood, CA 90069",
         neighborhood="Sunset Strip", zoning="R1-1-HCR",
         lot_size_sqft=9200, current_use="Restaurant/Bar"),
]


# --------------------------------------------------------------------------- #
# Cases — 30 cases using real LADBS and City Planning number formats
#
# LADBS permit# format:  YY-TTT-OO-MMM-#####
#   YY  = 2-digit year
#   TTT = permit type code (ADD=Addition, BLD=New Building, ALT=Alter/Repair,
#         GRD=Grading, ELE=Electrical, PLM=Plumbing, MEC=HVAC,
#         SPK=Fire Sprinkler, POL=Pool/Spa, SGN=Sign, ELV=Elevator)
#   OO  = branch (10=Metro, 20=Van Nuys, 30=West LA, 40=San Pedro,
#         70=South LA, 90=e-Permit)
#   MMM = 000 master / 001+ supplemental
#   ##### = 5-digit sequential
#
# City Planning case# format:  PREFIX-YEAR-SEQ#-SUFFIX(es)
#   e.g. ZA-2024-001234-CUB
# --------------------------------------------------------------------------- #

CASES = [

    # ---- Silver Lake 5462-001-016 ----

    # 1. ADU — resident, standard plan path (Abodu prefab, HCD-approved)
    dict(
        case_id="24-ADD-10-000-88441",
        apn="5462-001-016",
        department="LADBS",
        process_type="ADU",
        applicant_type="resident",
        applicant_name="Maria Gonzalez",
        submitted_date="2024-03-15",
        current_status="Issued",
        assigned_to="Plan Check Engr. J. Nakamura",
        description="Attached ADU, 480 sq ft — standard plan ADU3 (Abodu, HCD-approved prefab). Garage conversion.",
        fees_paid=2800.0,
        fees_outstanding=0.0,
        hearing_date=None,
        next_action="Permit issued. Post permit on site. Schedule foundation inspection (type 010) before any work.",
        portal_url="https://ladbs.org/services/check-status",
        valuation=95000.0,
        pc_job_number="B-24-10-88441",
        plan_type="standard_plan",
        conditions_of_approval=None,
    ),

    # 2. ADU — City Planning HPOZ ministerial review (same parcel, linked)
    dict(
        case_id="ZA-2024-006550-ADUH",
        apn="5462-001-016",
        department="City Planning",
        process_type="ADU",
        applicant_type="resident",
        applicant_name="Maria Gonzalez",
        submitted_date="2024-04-01",
        current_status="Under Review",
        assigned_to="HPOZ Preservation Planner: C. Park",
        description="ADUH — ADU within Silver Lake HPOZ. Garage conversion must comply with HPOZ design guidelines.",
        fees_paid=1800.0,
        fees_outstanding=0.0,
        hearing_date=None,
        next_action="HPOZ board review Q4 2024. Submit revised exterior materials board per Silver Lake HPOZ Design Guidelines.",
        portal_url="https://planning.lacity.gov/pdiscaseinfo",
        valuation=None,
        pc_job_number=None,
        plan_type="standard_plan",
        conditions_of_approval=None,
    ),

    # 3. Swimming pool — resident, finaled
    dict(
        case_id="24-POL-10-000-31045",
        apn="5462-001-016",
        department="LADBS",
        process_type="Swimming-Pool/Spa",
        applicant_type="resident",
        applicant_name="Maria Gonzalez",
        submitted_date="2024-01-10",
        current_status="CofO Issued",
        assigned_to=None,
        description="New in-ground pool and spa, 380 sq ft, residential backyard.",
        fees_paid=1200.0,
        fees_outstanding=0.0,
        hearing_date=None,
        next_action="CofO issued 2024-06-15. No further action required.",
        portal_url="https://ladbs.org/services/check-status",
        valuation=42000.0,
        pc_job_number=None,
        plan_type=None,
        conditions_of_approval=None,
    ),

    # ---- Silver Lake 5423-011-023 ----

    # 4. Electrical panel upgrade — contractor, finaled
    dict(
        case_id="24-ELE-10-000-67401",
        apn="5423-011-023",
        department="LADBS",
        process_type="Electrical",
        applicant_type="contractor",
        applicant_name="SoCal Electric Inc. (Lic. C-10 #812345)",
        submitted_date="2024-07-18",
        current_status="Permit Finaled",
        assigned_to=None,
        description="200A panel upgrade, new service entrance, EV charger rough-in.",
        fees_paid=420.0,
        fees_outstanding=0.0,
        hearing_date=None,
        next_action="Permit finaled 2024-09-10. No further action required.",
        portal_url="https://ladbs.org/services/check-status",
        valuation=12000.0,
        pc_job_number=None,
        plan_type=None,
        conditions_of_approval=None,
    ),

    # 5. Zone Variance — developer, appeal filed
    dict(
        case_id="ZA-2024-002187-ZV-1A",
        apn="5423-011-023",
        department="City Planning",
        process_type="ZV",
        applicant_type="developer",
        applicant_name="Silver Lake Development LLC",
        submitted_date="2024-02-01",
        current_status="Appeal Pending",
        assigned_to="APC East: Panel TBD",
        description="Variance — rear yard setback reduction from 15 ft to 7 ft for two-story addition. Neighbor appealed ZA approval.",
        fees_paid=3200.0,
        fees_outstanding=0.0,
        hearing_date="2025-02-18",
        next_action="Appeal hearing 2025-02-18 at East LA APC. Retain land use counsel. Prepare response to appellant's findings.",
        portal_url="https://planning.lacity.gov/pdiscaseinfo",
        valuation=None,
        pc_job_number=None,
        plan_type=None,
        conditions_of_approval=None,
    ),

    # 6. Building addition — developer, fees due (triggered by ZV)
    dict(
        case_id="25-ADD-10-000-11203",
        apn="5423-011-023",
        department="LADBS",
        process_type="Bldg-Addition",
        applicant_type="developer",
        applicant_name="Silver Lake Development LLC",
        submitted_date="2025-01-20",
        current_status="Fees Due",
        assigned_to=None,
        description="Two-story rear addition, 800 sq ft — pending ZV appeal resolution.",
        fees_paid=0.0,
        fees_outstanding=4800.0,
        hearing_date=None,
        next_action="Plan check fees ($4,800) due before submission. Do not pay until ZA-2024-002187-ZV-1A appeal is resolved — LOD required for LADBS clearance.",
        portal_url="https://ladbs.org/services/check-status",
        valuation=185000.0,
        pc_job_number=None,
        plan_type=None,
        conditions_of_approval=None,
    ),

    # ---- Hollywood 5547-026-018 ----

    # 7. CUB for rooftop bar — developer, hearing scheduled
    dict(
        case_id="ZA-2024-003812-CUB",
        apn="5547-026-018",
        department="City Planning",
        process_type="CUB",
        applicant_type="developer",
        applicant_name="Apex Urban Development LLC",
        submitted_date="2024-01-22",
        current_status="Pending Hearing",
        assigned_to="Case Planner: P. Martinez (GeoTeam West)",
        description="Conditional Use — alcohol service on rooftop bar/restaurant, Type 47 ABC license, capacity 120.",
        fees_paid=14500.0,
        fees_outstanding=0.0,
        hearing_date="2025-03-06",
        next_action="Public hearing at West LA APC 2025-03-06. Submit additional evidence 10 days prior. Confirm LAPD/Fire comments addressed.",
        portal_url="https://planning.lacity.gov/pdiscaseinfo",
        valuation=None,
        pc_job_number=None,
        plan_type=None,
        conditions_of_approval=None,
    ),

    # 8. ENV / MND linked to CUB — developer, CEQA circulating
    dict(
        case_id="ENV-2024-003812-MND",
        apn="5547-026-018",
        department="City Planning",
        process_type="EIR",
        applicant_type="developer",
        applicant_name="Apex Urban Development LLC",
        submitted_date="2024-06-10",
        current_status="CEQA Circulating",
        assigned_to="CEQA Analyst: R. Nguyen",
        description="Mitigated Negative Declaration for rooftop bar/restaurant project. Noise, traffic, and land use analysis.",
        fees_paid=9200.0,
        fees_outstanding=0.0,
        hearing_date=None,
        next_action="MND public comment period closes 2025-01-31. Respond to any comments received. CEQA clearance needed before APC hearing.",
        portal_url="https://planning.lacity.gov/pdiscaseinfo",
        valuation=None,
        pc_job_number=None,
        plan_type=None,
        conditions_of_approval=None,
    ),

    # 9. Tenant improvement — contractor, PC Assigned
    dict(
        case_id="25-ALT-10-000-22104",
        apn="5547-026-018",
        department="LADBS",
        process_type="Bldg-Alter/Repair",
        applicant_type="contractor",
        applicant_name="Pacific Build Group LLC (Lic. B #887722)",
        submitted_date="2025-01-08",
        current_status="PC Assigned",
        assigned_to="Plan Check Engr. D. Stein (Commercial Team)",
        description="Tenant improvement — new rooftop bar build-out, 1,800 sq ft, new kitchen, bar, ADA restrooms.",
        fees_paid=8500.0,
        fees_outstanding=0.0,
        hearing_date=None,
        next_action="Await plan check comments. First correction letter expected within 6 weeks. Track via MyLADBS.",
        portal_url="https://ladbs.org/services/check-status",
        valuation=320000.0,
        pc_job_number="B-25-10-22104",
        plan_type=None,
        conditions_of_approval=None,
    ),

    # 10. Plumbing — contractor, finaled
    dict(
        case_id="24-PLM-10-000-43009",
        apn="5547-026-018",
        department="LADBS",
        process_type="Plumbing",
        applicant_type="contractor",
        applicant_name="Pacific Plumbing Inc. (Lic. C-36 #445566)",
        submitted_date="2024-10-05",
        current_status="Permit Finaled",
        assigned_to=None,
        description="New grease interceptor and commercial kitchen rough plumbing.",
        fees_paid=680.0,
        fees_outstanding=0.0,
        hearing_date=None,
        next_action="Permit finaled 2024-12-02. No further action required.",
        portal_url="https://ladbs.org/services/check-status",
        valuation=18000.0,
        pc_job_number=None,
        plan_type=None,
        conditions_of_approval=None,
    ),

    # ---- Venice 4226-012-012 ----

    # 11. New construction — contractor, corrections needed
    dict(
        case_id="24-BLD-30-000-55210",
        apn="4226-012-012",
        department="LADBS",
        process_type="Bldg-New",
        applicant_type="contractor",
        applicant_name="Windward Build Co. (Lic. B #664433)",
        submitted_date="2024-04-20",
        current_status="Corrections Needed",
        assigned_to="Plan Check Engr. A. Reyes (Coastal Team)",
        description="New SFR, 2,400 sq ft, 2 stories, Type V-B, Venice Coastal Zone.",
        fees_paid=12800.0,
        fees_outstanding=0.0,
        hearing_date=None,
        next_action="Respond to plan check correction letter (issued 2024-09-15). Revise structural calcs per correction items 3, 7, and 12. Resubmit via ePlanLA.",
        portal_url="https://ladbs.org/services/check-status",
        valuation=680000.0,
        pc_job_number="B-24-30-55210",
        plan_type=None,
        conditions_of_approval=None,
    ),

    # 12. Coastal Development Permit — developer, LOD issued
    dict(
        case_id="DIR-2024-007831-CDP",
        apn="4226-012-012",
        department="City Planning",
        process_type="CDP",
        applicant_type="developer",
        applicant_name="Venice Coastal Properties LLC",
        submitted_date="2024-01-15",
        current_status="LOD Issued",
        assigned_to="Coastal Planner: J. Wu",
        description="Coastal Development Permit for new SFR in Venice Coastal Zone. Sea level rise analysis included.",
        fees_paid=7800.0,
        fees_outstanding=0.0,
        hearing_date=None,
        next_action="LOD issued 2024-08-22. Appeal period expired 2024-09-06. Clear conditions at DSC West LA. File LADBS permit.",
        portal_url="https://planning.lacity.gov/pdiscaseinfo",
        valuation=None,
        pc_job_number=None,
        plan_type=None,
        conditions_of_approval=json.dumps([
            "Applicant shall submit a final drainage plan to Bureau of Engineering prior to LADBS permit issuance.",
            "All exterior lighting shall be shielded away from the ocean per Section 12.04.09.",
            "No development shall occur below the 100-year flood elevation.",
        ]),
    ),

    # 13. Alter/Repair — resident, intent to revoke
    dict(
        case_id="23-ALT-30-000-11442",
        apn="4226-012-012",
        department="LADBS",
        process_type="Bldg-Alter/Repair",
        applicant_type="resident",
        applicant_name="Chen Wei",
        submitted_date="2023-05-12",
        current_status="Intent to Revoke",
        assigned_to="Inspector K. Brown",
        description="Rear deck expansion, 300 sq ft. Work performed outside approved plan scope.",
        fees_paid=650.0,
        fees_outstanding=0.0,
        hearing_date="2025-03-20",
        next_action="Notice of Intent to Revoke issued 2025-01-10. Work exceeded approved scope. Attend hearing 2025-03-20 or remove non-compliant work immediately and file revision.",
        portal_url="https://ladbs.org/services/check-status",
        valuation=22000.0,
        pc_job_number=None,
        plan_type=None,
        conditions_of_approval=None,
    ),

    # ---- South LA 5017-026-049 ----

    # 14. ADU — resident, standard plan path, ready to issue
    dict(
        case_id="25-ADD-70-000-08801",
        apn="5017-026-049",
        department="LADBS",
        process_type="ADU",
        applicant_type="resident",
        applicant_name="Darnell Washington",
        submitted_date="2025-02-10",
        current_status="Ready to Issue",
        assigned_to=None,
        description="New detached ADU, 400 sq ft, standard plan ADU9 (Fung + Blatt). Backyard.",
        fees_paid=1600.0,
        fees_outstanding=320.0,
        hearing_date=None,
        next_action="Pay issuance fees ($320) via MyLADBS. Permit will be emailed within 1 business day.",
        portal_url="https://ladbs.org/services/check-status",
        valuation=78000.0,
        pc_job_number="B-25-70-08801",
        plan_type="standard_plan",
        conditions_of_approval=None,
    ),

    # 15. ADU — resident, custom plan path, recheck (same parcel, second ADU attempt)
    dict(
        case_id="24-ADD-70-000-06612",
        apn="5017-026-049",
        department="LADBS",
        process_type="ADU",
        applicant_type="resident",
        applicant_name="Darnell Washington",
        submitted_date="2024-08-15",
        current_status="Recheck",
        assigned_to="Plan Check Engr. M. Torres",
        description="Custom ADU plan — detached 600 sq ft, 1 bed/1 bath. First submission had Title 24 and setback errors.",
        fees_paid=2200.0,
        fees_outstanding=0.0,
        hearing_date=None,
        next_action="Resubmit corrected plans via ePlanLA. Address correction items: (1) Title 24 energy calc missing, (2) north side setback must be 4 ft min, (3) utility easement conflict on site plan.",
        portal_url="https://ladbs.org/services/check-status",
        valuation=145000.0,
        pc_job_number="B-24-70-06612",
        plan_type="custom",
        conditions_of_approval=None,
    ),

    # ---- Leimert Park 5006-008-016 ----

    # 16. HVAC — contractor, finaled
    dict(
        case_id="24-MEC-10-000-72188",
        apn="5006-008-016",
        department="LADBS",
        process_type="HVAC",
        applicant_type="contractor",
        applicant_name="Pacific Air Systems (Lic. C-20 #567890)",
        submitted_date="2024-08-05",
        current_status="Permit Finaled",
        assigned_to=None,
        description="Replace central HVAC — new split system, 3-ton, SFR.",
        fees_paid=380.0,
        fees_outstanding=0.0,
        hearing_date=None,
        next_action="Permit finaled 2024-09-20. No further action required.",
        portal_url="https://ladbs.org/services/check-status",
        valuation=8500.0,
        pc_job_number=None,
        plan_type=None,
        conditions_of_approval=None,
    ),

    # 17. Parcel Map — developer, map recorded
    dict(
        case_id="AA-2025-001723-PM",
        apn="5006-008-016",
        department="City Planning",
        process_type="PM",
        applicant_type="developer",
        applicant_name="Leimert Park Homes LLC",
        submitted_date="2025-01-10",
        current_status="Map Recorded",
        assigned_to="Advisory Agency: B. Chen",
        description="Parcel Map — lot split into 2 parcels per SB 9. Both lots meet 1,200 sq ft min.",
        fees_paid=11200.0,
        fees_outstanding=0.0,
        hearing_date=None,
        next_action="Map recorded at LA County Recorder 2025-04-22. Obtain new APNs from County Assessor. File separate LADBS permits for each new parcel.",
        portal_url="https://planning.lacity.gov/pdiscaseinfo",
        valuation=None,
        pc_job_number=None,
        plan_type=None,
        conditions_of_approval=json.dumps([
            "Each resulting parcel shall maintain independent utility connections prior to recordation.",
            "Applicant shall dedicate 5-ft sidewalk easement along Degnan Blvd frontage.",
        ]),
    ),

    # ---- Downtown LA 5144-010-401 ----

    # 18. New multi-family tower — developer, submitted
    dict(
        case_id="24-BLD-10-000-77700",
        apn="5144-010-401",
        department="LADBS",
        process_type="Bldg-New",
        applicant_type="developer",
        applicant_name="Downtown Core Partners LLC",
        submitted_date="2024-06-20",
        current_status="Submitted",
        assigned_to=None,
        description="New 28-story mixed-use tower — 280 residential units + 40,000 sf commercial. Type I-A, high-rise.",
        fees_paid=62000.0,
        fees_outstanding=0.0,
        hearing_date=None,
        next_action="Application submitted. Awaiting PC assignment. High-rise complex plan check queue — expect assignment within 4-6 weeks.",
        portal_url="https://ladbs.org/services/check-status",
        valuation=85000000.0,
        pc_job_number="B-24-10-77700",
        plan_type=None,
        conditions_of_approval=None,
    ),

    # 19. EIR — developer, NOP comment period
    dict(
        case_id="ENV-2024-005502-EIR",
        apn="5144-010-401",
        department="City Planning",
        process_type="EIR",
        applicant_type="developer",
        applicant_name="Downtown Core Partners LLC",
        submitted_date="2024-05-01",
        current_status="Notice of Preparation",
        assigned_to="EIR Coordinator: L. Park (CEQA Team)",
        description="Program EIR for 28-story mixed-use tower. Traffic, air quality, noise, shadow/shade analysis.",
        fees_paid=52000.0,
        fees_outstanding=28000.0,
        hearing_date="2025-04-10",
        next_action="NOP scoping meeting 2025-04-10. Pay remaining EIR deposit ($28,000) before scoping. Responses to NOP comments due 30 days post-NOP.",
        portal_url="https://planning.lacity.gov/pdiscaseinfo",
        valuation=None,
        pc_job_number=None,
        plan_type=None,
        conditions_of_approval=None,
    ),

    # 20. TOC density bonus — developer, LOD issued
    dict(
        case_id="CPC-2024-011002-TOC",
        apn="5144-010-401",
        department="City Planning",
        process_type="TOC",
        applicant_type="developer",
        applicant_name="Downtown Core Partners LLC",
        submitted_date="2024-02-28",
        current_status="LOD Issued",
        assigned_to="Case Planner: R. Nguyen (EPS)",
        description="TOC Tier 4 incentives — 280-unit project, 14% affordable at 80% AMI (39 units). Adjacent to Metro Red/Purple Line.",
        fees_paid=9200.0,
        fees_outstanding=0.0,
        hearing_date=None,
        next_action="LOD issued 2024-11-20. Appeal period expired 2024-12-05. Clear conditions at DSC Metro. Conditions include recorded covenant for affordable units.",
        portal_url="https://planning.lacity.gov/pdiscaseinfo",
        valuation=None,
        pc_job_number=None,
        plan_type=None,
        conditions_of_approval=json.dumps([
            "Applicant shall record an Affordable Housing Agreement covenant with the City prior to LADBS permit issuance.",
            "39 units shall be restricted to households earning ≤80% AMI for a minimum of 55 years.",
            "Applicant shall provide Transportation Demand Management (TDM) plan to LADOT prior to CofO.",
        ]),
    ),

    # ---- West Adams 5075-003-026 ----

    # 21. CUB — developer, LOD issued with conditions
    dict(
        case_id="ZA-2024-009503-CUB",
        apn="5075-003-026",
        department="City Planning",
        process_type="CUB",
        applicant_type="developer",
        applicant_name="West Adams Restaurant Group",
        submitted_date="2024-03-05",
        current_status="LOD Issued",
        assigned_to="Zoning Administrator: H. Kim",
        description="CUB for beer and wine service (Type 41 ABC license) at new restaurant. CPIO overlay applies.",
        fees_paid=13800.0,
        fees_outstanding=0.0,
        hearing_date=None,
        next_action="LOD issued 2024-10-15. Appeal period expired 2024-10-30. Clear conditions at DSC South LA. Allow 2-3 weeks.",
        portal_url="https://planning.lacity.gov/pdiscaseinfo",
        valuation=None,
        pc_job_number=None,
        plan_type=None,
        conditions_of_approval=json.dumps([
            "Alcohol service limited to on-site consumption only. No off-site sales permitted.",
            "Hours of alcohol service: 11:00 AM to 11:00 PM Sunday–Thursday; 11:00 AM to midnight Friday–Saturday.",
            "Applicant shall provide a Security Plan to LAPD Senior Lead Officer prior to ABC license issuance.",
            "No exterior signage advertising alcohol shall be visible from the public right-of-way.",
        ]),
    ),

    # 22. Tenant improvement — contractor, PC Approved
    dict(
        case_id="24-ALT-10-000-81002",
        apn="5075-003-026",
        department="LADBS",
        process_type="Bldg-Alter/Repair",
        applicant_type="contractor",
        applicant_name="Westside Build Partners (Lic. B #334455)",
        submitted_date="2024-07-01",
        current_status="PC Approved",
        assigned_to="Plan Check Engr. B. Patel",
        description="Restaurant tenant improvement — new kitchen, service bar, ADA restrooms, 2,200 sq ft.",
        fees_paid=6800.0,
        fees_outstanding=0.0,
        hearing_date=None,
        next_action="Plans approved. Pay issuance fees ($890) at Metro DSC or online. Pick up approved plans. Post permit before any work begins.",
        portal_url="https://ladbs.org/services/check-status",
        valuation=240000.0,
        pc_job_number="B-24-10-81002",
        plan_type=None,
        conditions_of_approval=None,
    ),

    # 23. Fire sprinkler — contractor, ready to issue (supplemental to TI)
    dict(
        case_id="24-SPK-10-001-81002",
        apn="5075-003-026",
        department="LADBS",
        process_type="Fire Sprinkler",
        applicant_type="contractor",
        applicant_name="LA Fire Protection Co. (Lic. C-16 #234567)",
        submitted_date="2024-09-10",
        current_status="Ready to Issue",
        assigned_to=None,
        description="Fire sprinkler supplemental to TI permit 24-ALT-10-000-81002. New NFPA 13 system, full restaurant coverage.",
        fees_paid=0.0,
        fees_outstanding=520.0,
        hearing_date=None,
        next_action="Pay issuance fees ($520) to receive permit. Coordinate with GC — sprinkler rough must precede drywall.",
        portal_url="https://ladbs.org/services/check-status",
        valuation=38000.0,
        pc_job_number=None,
        plan_type=None,
        conditions_of_approval=None,
    ),

    # ---- West Adams 5024-018-012 ----

    # 24. ZA Adjustment — developer, conditions clearance
    dict(
        case_id="ZA-2024-012201-ADJ",
        apn="5024-018-012",
        department="City Planning",
        process_type="ADJ",
        applicant_type="developer",
        applicant_name="Adams Mixed Use LLC",
        submitted_date="2024-04-12",
        current_status="Conditions Clearance",
        assigned_to="Zoning Administrator: H. Kim",
        description="ZA Adjustment — reduced front yard setback (10 ft to 5 ft) and increased FAR for mixed-use infill. Specific Plan area.",
        fees_paid=5400.0,
        fees_outstanding=0.0,
        hearing_date=None,
        next_action="LOD issued 2024-12-01. Return to DSC South LA to clear conditions. Bring updated site plan and recorded street dedication deed.",
        portal_url="https://planning.lacity.gov/pdiscaseinfo",
        valuation=None,
        pc_job_number=None,
        plan_type=None,
        conditions_of_approval=json.dumps([
            "Applicant shall dedicate and improve a 5-ft wide sidewalk easement along 43rd St frontage prior to LADBS permit issuance.",
            "Ground floor commercial space shall maintain a minimum 18-ft floor-to-floor height.",
            "All bicycle parking shall comply with LAMC 12.21-A.16.",
        ]),
    ),

    # 25. Building addition — developer, PC Assigned (waiting for ADJ clearance)
    dict(
        case_id="25-ADD-10-000-14400",
        apn="5024-018-012",
        department="LADBS",
        process_type="Bldg-Addition",
        applicant_type="developer",
        applicant_name="Adams Mixed Use LLC",
        submitted_date="2025-01-15",
        current_status="PC Assigned",
        assigned_to="Plan Check Engr. J. Lee (Mixed-Use Team)",
        description="Mixed-use addition — 4-story, 8 residential units above ground floor commercial, 6,800 sq ft.",
        fees_paid=18200.0,
        fees_outstanding=0.0,
        hearing_date=None,
        next_action="PC assigned. Submit conditions clearance letter from City Planning (ZA-2024-012201-ADJ) to plan check engineer to unblock review.",
        portal_url="https://ladbs.org/services/check-status",
        valuation=1800000.0,
        pc_job_number="B-25-10-14400",
        plan_type=None,
        conditions_of_approval=None,
    ),

    # 26. Kitchen remodel — resident, finaled
    dict(
        case_id="24-ALT-10-000-55021",
        apn="5024-018-012",
        department="LADBS",
        process_type="Bldg-Alter/Repair",
        applicant_type="resident",
        applicant_name="Sofia Ramirez",
        submitted_date="2024-05-20",
        current_status="Permit Finaled",
        assigned_to=None,
        description="Kitchen remodel — non-structural, new cabinets, counters, fixtures. No layout change.",
        fees_paid=480.0,
        fees_outstanding=0.0,
        hearing_date=None,
        next_action="Permit finaled 2024-08-05. No further action required.",
        portal_url="https://ladbs.org/services/check-status",
        valuation=32000.0,
        pc_job_number=None,
        plan_type=None,
        conditions_of_approval=None,
    ),

    # ---- Sunset Strip 5555-026-025 ----

    # 27. Specific Plan Project Permit Adjustment — developer, PC expired
    dict(
        case_id="DIR-2023-015700-SPPA",
        apn="5555-026-025",
        department="City Planning",
        process_type="SPPA",
        applicant_type="developer",
        applicant_name="Sunset Strip Entertainment Group",
        submitted_date="2023-09-15",
        current_status="PC Expired",
        assigned_to=None,
        description="Specific Plan Permit Adjustment under Sunset Specific Plan — expanded outdoor dining area, 800 sq ft.",
        fees_paid=5200.0,
        fees_outstanding=0.0,
        hearing_date=None,
        next_action="Case expired 2025-03-15 with no action. Refile new SPPA application via OAS to restart. Fees apply again.",
        portal_url="https://planning.lacity.gov/pdiscaseinfo",
        valuation=None,
        pc_job_number=None,
        plan_type=None,
        conditions_of_approval=None,
    ),

    # 28. New construction — developer, PC on hold
    dict(
        case_id="24-BLD-10-000-90321",
        apn="5555-026-025",
        department="LADBS",
        process_type="Bldg-New",
        applicant_type="developer",
        applicant_name="Sunset Strip Entertainment Group",
        submitted_date="2024-01-10",
        current_status="PC on Hold",
        assigned_to="Plan Check Engr. C. Wong",
        description="New restaurant/entertainment venue — 4,200 sq ft, 2 stories, Type V-B, hillside lot.",
        fees_paid=28500.0,
        fees_outstanding=0.0,
        hearing_date=None,
        next_action="Hold placed by Geology/Soils unit — geotechnical report does not address liquefaction per CBC Section 1803.5.11. Provide updated soils report from licensed geotechnical engineer.",
        portal_url="https://ladbs.org/services/check-status",
        valuation=1200000.0,
        pc_job_number="B-24-10-90321",
        plan_type=None,
        conditions_of_approval=None,
    ),

    # 29. CUB appeal — developer, appeal pending
    dict(
        case_id="ZA-2023-019800-CUB-1A",
        apn="5555-026-025",
        department="City Planning",
        process_type="CUB",
        applicant_type="developer",
        applicant_name="Sunset Strip Entertainment Group",
        submitted_date="2023-11-01",
        current_status="Appeal Pending",
        assigned_to="APC West: Panel TBD",
        description="CUB for late-night alcohol service (Type 48, 2am closing) at entertainment venue — appealed by neighboring residents.",
        fees_paid=14800.0,
        fees_outstanding=0.0,
        hearing_date="2025-05-15",
        next_action="Appeal hearing 2025-05-15 at West LA APC. Retain land use counsel. Prepare response to neighbor objections re: noise and parking. Submit noise study.",
        portal_url="https://planning.lacity.gov/pdiscaseinfo",
        valuation=None,
        pc_job_number=None,
        plan_type=None,
        conditions_of_approval=None,
    ),

    # 30. Grading — contractor, issued
    dict(
        case_id="24-GRD-10-000-55880",
        apn="5555-026-025",
        department="LADBS",
        process_type="Grading",
        applicant_type="contractor",
        applicant_name="Hillside Grading & Excavation (Lic. C-12 #445566)",
        submitted_date="2024-03-01",
        current_status="Issued",
        assigned_to=None,
        description="Rough grading — 600 CY cut, 150 CY fill, 450 CY export. Hillside lot pad prep.",
        fees_paid=5400.0,
        fees_outstanding=0.0,
        hearing_date=None,
        next_action="Permit issued. Schedule rough grading inspection (type 400) via MyLADBS. Soils engineer must be on site for any cut exceeding 5 ft.",
        portal_url="https://ladbs.org/services/check-status",
        valuation=65000.0,
        pc_job_number=None,
        plan_type=None,
        conditions_of_approval=None,
    ),
]


# --------------------------------------------------------------------------- #
# Workflow steps
# --------------------------------------------------------------------------- #

WORKFLOW_STEPS = [

    # ADU — standard plan path (faster)
    dict(process_type="ADU_standard", step_order=1, step_name="Choose a Standard Plan",
         description="Browse LADBS-approved standard ADU plans at permitpath.la or ladbs.org. "
                     "Prefab options (Abodu ADU3-5, Connect Homes ADU14-15) include factory delivery.",
         responsible_party="Applicant", typical_days="1-3"),
    dict(process_type="ADU_standard", step_order=2, step_name="Check Eligibility & HPOZ",
         description="Verify lot meets ADU requirements via ZIMAS. If HPOZ overlay present, "
                     "file ADUH with City Planning before LADBS submission.",
         responsible_party="Applicant", typical_days="1-2"),
    dict(process_type="ADU_standard", step_order=3, step_name="Submit to LADBS",
         description="Submit online via MyLADBS with selected standard plan number. "
                     "Pay plan check fees. Standard plan path skips custom plan review.",
         responsible_party="Applicant", typical_days="1"),
    dict(process_type="ADU_standard", step_order=4, step_name="Plan Check (Expedited)",
         description="LADBS reviews site-specific items only (setbacks, utilities, soils if hillside). "
                     "Standard plans approved in 10-15 business days vs 20-30 for custom.",
         responsible_party="LADBS", typical_days="10-15"),
    dict(process_type="ADU_standard", step_order=5, step_name="Pay Issuance Fees & Receive Permit",
         description="Once PC Approved, pay issuance fees. Post permit on job site.",
         responsible_party="Applicant", typical_days="1"),
    dict(process_type="ADU_standard", step_order=6, step_name="Construction",
         description="Build or install per approved standard plan. No field modifications allowed.",
         responsible_party="Applicant", typical_days="30-90"),
    dict(process_type="ADU_standard", step_order=7, step_name="Inspections & Final",
         description="Schedule inspections: foundation, framing, rough MEP, insulation, final. LADBS finals permit.",
         responsible_party="LADBS", typical_days="5-30"),

    # ADU — custom plan path
    dict(process_type="ADU", step_order=1, step_name="Check ADU Eligibility",
         description="Verify lot meets ADU requirements: zoning, fire zone, HPOZ, lot size. Use ZIMAS.",
         responsible_party="Applicant", typical_days="1-3"),
    dict(process_type="ADU", step_order=2, step_name="Prepare Plans",
         description="Architect or draftsperson draws site plan, floor plan, elevations. "
                     "Must show setbacks, height, utility connections, Title 24 energy.",
         responsible_party="Applicant", typical_days="5-14"),
    dict(process_type="ADU", step_order=3, step_name="Submit to LADBS",
         description="File online via MyLADBS or in-person at district office. Pay plan check fees.",
         responsible_party="Applicant", typical_days="1"),
    dict(process_type="ADU", step_order=4, step_name="Plan Check Review",
         description="LADBS reviews plans. May issue correction letter for Title 24, setbacks, soils.",
         responsible_party="LADBS", typical_days="20-30"),
    dict(process_type="ADU", step_order=5, step_name="Respond to Corrections",
         description="Revise plans per correction letter and resubmit via ePlanLA.",
         responsible_party="Applicant", typical_days="7-14"),
    dict(process_type="ADU", step_order=6, step_name="Pay Issuance Fees & Receive Permit",
         description="Once PC Approved, pay issuance fees. Permit issued — post on job site.",
         responsible_party="Applicant", typical_days="1-2"),
    dict(process_type="ADU", step_order=7, step_name="Construction",
         description="Build per approved plans. Do not deviate without prior LADBS approval.",
         responsible_party="Applicant", typical_days="60-180"),
    dict(process_type="ADU", step_order=8, step_name="Inspections",
         description="Schedule and pass: foundation (010), framing (020), rough plumbing (030), "
                     "rough electrical (040), insulation (055), final (999).",
         responsible_party="LADBS", typical_days="5-30"),
    dict(process_type="ADU", step_order=9, step_name="Final Sign-Off",
         description="All inspections pass. LADBS finals the permit.",
         responsible_party="LADBS", typical_days="2-5"),

    # Bldg-New
    dict(process_type="Bldg-New", step_order=1, step_name="Confirm Zoning & Entitlements",
         description="Verify project is by-right or determine which City Planning entitlements are needed first. "
                     "Run ZIMAS for zone, overlays, Q/D conditions.",
         responsible_party="Applicant", typical_days="1-5"),
    dict(process_type="Bldg-New", step_order=2, step_name="Prepare Construction Documents",
         description="Architect prepares full plan set: architectural, structural, MEP, Title 24 energy, civil/grading.",
         responsible_party="Applicant", typical_days="30-90"),
    dict(process_type="Bldg-New", step_order=3, step_name="Submit to LADBS",
         description="Submit via ePlanLA. Pay plan check fees based on project valuation.",
         responsible_party="Applicant", typical_days="1"),
    dict(process_type="Bldg-New", step_order=4, step_name="Plan Check Review",
         description="LADBS engineers review architectural, structural, fire, MEP, accessibility. "
                     "First round: 6-10 weeks residential, 8-16 weeks commercial/multi-family.",
         responsible_party="LADBS", typical_days="30-80"),
    dict(process_type="Bldg-New", step_order=5, step_name="Respond to Corrections",
         description="Address plan check comments and resubmit. Multiple rounds possible.",
         responsible_party="Applicant", typical_days="14-30"),
    dict(process_type="Bldg-New", step_order=6, step_name="PC Approved — Issue Permit",
         description="Plans approved. Pay issuance fees. Post permit on site before any work begins.",
         responsible_party="Applicant", typical_days="1-3"),
    dict(process_type="Bldg-New", step_order=7, step_name="Construction & Inspections",
         description="Construct per plans. LADBS inspector visits for foundation, framing, rough MEP, structural, insulation, drywall, final.",
         responsible_party="Applicant", typical_days="90-365"),
    dict(process_type="Bldg-New", step_order=8, step_name="Certificate of Occupancy",
         description="After final inspection passes, LADBS issues CofO or TCO. Required before occupancy.",
         responsible_party="LADBS", typical_days="5-14"),

    # Bldg-Alter/Repair
    dict(process_type="Bldg-Alter/Repair", step_order=1, step_name="Determine Permit Type",
         description="Check if project requires full plan check or express/OTC. Non-structural remodels "
                     "may qualify for online permit with no plan check.",
         responsible_party="Applicant", typical_days="1"),
    dict(process_type="Bldg-Alter/Repair", step_order=2, step_name="Prepare Plans or Scope",
         description="Draw plans showing existing and proposed conditions. Non-structural may not need stamped plans.",
         responsible_party="Applicant", typical_days="2-14"),
    dict(process_type="Bldg-Alter/Repair", step_order=3, step_name="Submit & Pay Fees",
         description="Submit online or at district office. Pay plan check fees.",
         responsible_party="Applicant", typical_days="1"),
    dict(process_type="Bldg-Alter/Repair", step_order=4, step_name="Plan Check Review",
         description="LADBS reviews plans. Simple projects approved same day (OTC). Complex: 3-6 weeks.",
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

    # CUB
    dict(process_type="CUB", step_order=1, step_name="Pre-Application Meeting",
         description="Meet with City Planning staff at DSC to understand requirements and potential issues.",
         responsible_party="Applicant", typical_days="1"),
    dict(process_type="CUB", step_order=2, step_name="File CUB Application",
         description="Submit via OAS portal. Pay filing fees (~$13,000–$15,000). "
                     "Include site plan, floor plan, operating parameters, ABC license info.",
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
         description="Hearing before Zoning Administrator (ZA) or Area Planning Commission (APC). "
                     "Present project, respond to public objections.",
         responsible_party="Applicant", typical_days="1"),
    dict(process_type="CUB", step_order=7, step_name="Letter of Determination (LOD)",
         description="ZA or APC issues LOD with approval/denial and all conditions of approval.",
         responsible_party="City Planning", typical_days="10-21"),
    dict(process_type="CUB", step_order=8, step_name="Appeal Period",
         description="15-day window for neighbors or applicant to appeal. If appealed, case goes to APC or CPC.",
         responsible_party="City Planning", typical_days="15"),
    dict(process_type="CUB", step_order=9, step_name="Clear Conditions at DSC",
         description="Return to DSC to demonstrate compliance with each LOD condition. Allow 2-4 weeks.",
         responsible_party="Applicant", typical_days="5-30"),
    dict(process_type="CUB", step_order=10, step_name="File LADBS Building Permit",
         description="With LOD and conditions cleared, file LADBS TI or new construction permit.",
         responsible_party="Applicant", typical_days="1"),

    # ZC — 9 steps
    dict(process_type="ZC", step_order=1, step_name="Preliminary Zoning Assessment",
         description="File PZA with City Planning to identify non-conforming aspects. Fee ~$862 (LAMC 19.09).",
         responsible_party="Applicant", typical_days="5-10"),
    dict(process_type="ZC", step_order=2, step_name="Pre-Application Conference",
         description="Meet with GeoTeam or EPS planner to discuss scope and entitlement strategy.",
         responsible_party="Applicant", typical_days="1"),
    dict(process_type="ZC", step_order=3, step_name="File Zone Change Application",
         description="Submit via OAS. Pay fees ($12,000–$17,000+). Include legal description, CEQA forms, site plans.",
         responsible_party="Applicant", typical_days="1"),
    dict(process_type="ZC", step_order=4, step_name="Application Completeness",
         description="City Planning verifies all required materials submitted.",
         responsible_party="City Planning", typical_days="14-30"),
    dict(process_type="ZC", step_order=5, step_name="CEQA Review",
         description="Environmental analysis — Initial Study determines if CE, MND, or EIR required. "
                     "MND adds 2-4 months; EIR adds 18-36 months.",
         responsible_party="City Planning", typical_days="60-180"),
    dict(process_type="ZC", step_order=6, step_name="Technical Staff Review",
         description="Planner prepares staff report with findings, conditions, and recommendation.",
         responsible_party="City Planning", typical_days="60-90"),
    dict(process_type="ZC", step_order=7, step_name="Public Hearing — APC or CPC",
         description="Area Planning Commission or City Planning Commission holds public hearing.",
         responsible_party="City Planning", typical_days="1"),
    dict(process_type="ZC", step_order=8, step_name="Council File / City Council",
         description="Zone changes require City Council action. CPC recommendation forwarded to Council.",
         responsible_party="City Planning", typical_days="30-90"),
    dict(process_type="ZC", step_order=9, step_name="Ordinance Effective",
         description="Zone Change Ordinance effective 30 days after City Council approval. Zone updated in ZIMAS.",
         responsible_party="City Planning", typical_days="30"),

    # Bldg-Addition — 8 steps (mirrors Bldg-New but scoped for additions)
    dict(process_type="Bldg-Addition", step_order=1, step_name="Confirm Zoning & Setbacks",
         description="Verify setbacks, height limits, lot coverage, and FAR for the proposed addition via ZIMAS. "
                     "Determine if any City Planning entitlement (variance, adjustment) is required first.",
         responsible_party="Applicant", typical_days="1-3"),
    dict(process_type="Bldg-Addition", step_order=2, step_name="Prepare Construction Documents",
         description="Architect prepares plans: site plan, floor plan, elevations showing existing and new. "
                     "Structural calcs required for second-story or load-bearing additions.",
         responsible_party="Applicant", typical_days="14-45"),
    dict(process_type="Bldg-Addition", step_order=3, step_name="Submit to LADBS",
         description="Submit via MyLADBS online or at district office. Pay plan check fees based on valuation.",
         responsible_party="Applicant", typical_days="1"),
    dict(process_type="Bldg-Addition", step_order=4, step_name="Plan Check Review",
         description="LADBS reviews plans. Typical first round: 4-8 weeks residential, 8-12 weeks multi-family.",
         responsible_party="LADBS", typical_days="20-60"),
    dict(process_type="Bldg-Addition", step_order=5, step_name="Respond to Corrections",
         description="Address plan check correction letter items. Revise and resubmit via ePlanLA.",
         responsible_party="Applicant", typical_days="7-21"),
    dict(process_type="Bldg-Addition", step_order=6, step_name="Pay Issuance Fees & Receive Permit",
         description="Once PC Approved, pay issuance fees. Post permit on site before work begins.",
         responsible_party="Applicant", typical_days="1-2"),
    dict(process_type="Bldg-Addition", step_order=7, step_name="Construction & Inspections",
         description="Build per approved plans. Key inspections: foundation, framing, rough MEP, insulation, drywall, final.",
         responsible_party="Applicant", typical_days="30-180"),
    dict(process_type="Bldg-Addition", step_order=8, step_name="Final Inspection & Permit Finaled",
         description="All inspections complete. LADBS inspector finals the permit.",
         responsible_party="LADBS", typical_days="1-5"),

    # Electrical — 5 steps
    dict(process_type="Electrical", step_order=1, step_name="Determine Scope & Permit Type",
         description="Confirm permit is required. Panel upgrades, new circuits, EV chargers, service changes: always permit. "
                     "Minor repairs in existing wiring: check with LADBS.",
         responsible_party="Applicant", typical_days="1"),
    dict(process_type="Electrical", step_order=2, step_name="Submit & Pay Fees",
         description="Residential: pull e-permit online at ladbs.org. Commercial: submit to LADBS Electrical division. "
                     "Fees: $100–$400 residential, higher for commercial.",
         responsible_party="Applicant", typical_days="1"),
    dict(process_type="Electrical", step_order=3, step_name="Permit Issued",
         description="Permit issued same-day for e-permits. Post permit on job site.",
         responsible_party="Applicant", typical_days="1"),
    dict(process_type="Electrical", step_order=4, step_name="Inspections & Final",
         description="Rough wiring inspection (320) before walls close. Final electrical (399) when work complete.",
         responsible_party="LADBS", typical_days="1-7"),
    dict(process_type="Electrical", step_order=5, step_name="Permit Finaled",
         description="Final inspection passed. Permit finaled. LADWP re-sets meter for service upgrades.",
         responsible_party="LADBS", typical_days="1"),

    # Plumbing — 5 steps
    dict(process_type="Plumbing", step_order=1, step_name="Determine Scope & Permit Type",
         description="Water heaters, re-pipes, fixture additions, and new drain lines all require permits. "
                     "Like-for-like fixture replacements: e-permit. New piping or commercial: plan check.",
         responsible_party="Applicant", typical_days="1"),
    dict(process_type="Plumbing", step_order=2, step_name="Submit & Pay Fees",
         description="Residential e-permit online. Commercial: submit to LADBS Plumbing division with isometric diagrams. "
                     "Fees: $80–$350 residential.",
         responsible_party="Applicant", typical_days="1"),
    dict(process_type="Plumbing", step_order=3, step_name="Permit Issued",
         description="E-permit issued immediately. Plan check permits issued after approval.",
         responsible_party="Applicant", typical_days="1"),
    dict(process_type="Plumbing", step_order=4, step_name="Inspections & Final",
         description="Rough plumbing (030) before walls close. Pressure test required on new water lines. Final (099) when complete.",
         responsible_party="LADBS", typical_days="1-7"),
    dict(process_type="Plumbing", step_order=5, step_name="Permit Finaled",
         description="Final inspection passed. Permit finaled.",
         responsible_party="LADBS", typical_days="1"),

    # HVAC — 5 steps
    dict(process_type="HVAC", step_order=1, step_name="Determine Scope & Permit Type",
         description="Like-for-like HVAC replacement: e-permit, no plan check. "
                     "New ductwork, new system, or commercial: plan check required with Title 24 compliance.",
         responsible_party="Applicant", typical_days="1"),
    dict(process_type="HVAC", step_order=2, step_name="Submit & Pay Fees",
         description="Residential replacement: online e-permit, $100–$300. "
                     "Commercial: submit to LADBS Mechanical division with load calcs and duct diagram.",
         responsible_party="Applicant", typical_days="1"),
    dict(process_type="HVAC", step_order=3, step_name="Permit Issued",
         description="E-permit issued immediately. Plan check permits issued after approval.",
         responsible_party="Applicant", typical_days="1"),
    dict(process_type="HVAC", step_order=4, step_name="Inspections & Final",
         description="Rough duct inspection (240) before ceilings close. Equipment set (241). Final HVAC (299) when complete.",
         responsible_party="LADBS", typical_days="1-7"),
    dict(process_type="HVAC", step_order=5, step_name="Permit Finaled",
         description="Final inspection passed. Permit finaled.",
         responsible_party="LADBS", typical_days="1"),

    # Fire Sprinkler — 6 steps
    dict(process_type="Fire Sprinkler", step_order=1, step_name="Prepare Sprinkler Plans",
         description="Licensed C-16 contractor prepares plans with hydraulic calcs, head layout, and water supply data. "
                     "NFPA 13, 13R, or 13D depending on occupancy.",
         responsible_party="Applicant", typical_days="5-14"),
    dict(process_type="Fire Sprinkler", step_order=2, step_name="Submit & Pay Fees",
         description="Submit to LADBS Fire Sprinkler division. LAFD also reviews concurrently. "
                     "Fees based on number of heads and project type.",
         responsible_party="Applicant", typical_days="1"),
    dict(process_type="Fire Sprinkler", step_order=3, step_name="Plan Check Review",
         description="LADBS and LAFD review in parallel. Typical: 3-6 weeks. "
                     "LAFD may comment on FDC location, water supply, and riser room access.",
         responsible_party="LADBS", typical_days="15-30"),
    dict(process_type="Fire Sprinkler", step_order=4, step_name="Permit Issued",
         description="Pay issuance fees. Post permit. Coordinate rough-in timing with general contractor.",
         responsible_party="Applicant", typical_days="1"),
    dict(process_type="Fire Sprinkler", step_order=5, step_name="Rough Inspection",
         description="Rough sprinkler inspection before ceilings close. "
                     "Hydrostatic pressure test (200 psi, 2 hrs) performed at this stage.",
         responsible_party="LADBS", typical_days="1-3"),
    dict(process_type="Fire Sprinkler", step_order=6, step_name="Final & LAFD Witness Test",
         description="Final LADBS inspection. LAFD witness test required for commercial systems. "
                     "System must pass flow test before CofO can issue.",
         responsible_party="LADBS", typical_days="1-5"),

    # Grading — 6 steps
    dict(process_type="Grading", step_order=1, step_name="Prepare Grading Plans",
         description="Licensed civil engineer prepares grading plans with cut/fill quantities, drainage, and erosion control. "
                     "Geotechnical report required for hillside lots (slope >2:1 or cut >5 ft).",
         responsible_party="Applicant", typical_days="14-30"),
    dict(process_type="Grading", step_order=2, step_name="Submit to LADBS",
         description="Submit to LADBS Grading division with soils report, SWPPP (if >1 acre), and haul route plan.",
         responsible_party="Applicant", typical_days="1"),
    dict(process_type="Grading", step_order=3, step_name="Plan Check Review",
         description="LADBS Grading and Geology sections review. Typical: 4-8 weeks. "
                     "Geology hold common on hillside lots pending soils review.",
         responsible_party="LADBS", typical_days="20-40"),
    dict(process_type="Grading", step_order=4, step_name="Permit Issued",
         description="Pay issuance fees. Post permit. Coordinate haul route and export timing.",
         responsible_party="Applicant", typical_days="1"),
    dict(process_type="Grading", step_order=5, step_name="Inspections & Final",
         description="Rough grading inspection (400). Drainage inspection (401). Soils engineer on site for cuts >5 ft. "
                     "Final grading certification (499) required before building permit.",
         responsible_party="LADBS", typical_days="5-30"),
    dict(process_type="Grading", step_order=6, step_name="Grading Certificate Issued",
         description="Grading engineer certifies finished grades match approved plan. "
                     "LADBS issues Grading Certificate — required before LADBS will issue building permit.",
         responsible_party="LADBS", typical_days="2-7"),

    # Swimming-Pool/Spa — 6 steps
    dict(process_type="Swimming-Pool/Spa", step_order=1, step_name="Verify Setbacks & Zoning",
         description="Confirm pool setbacks (typically 5 ft from property lines), equipment location, "
                     "and any hillside/fire zone requirements via ZIMAS.",
         responsible_party="Applicant", typical_days="1-2"),
    dict(process_type="Swimming-Pool/Spa", step_order=2, step_name="Prepare Plans",
         description="Pool contractor or designer draws site plan showing pool dimensions, setbacks, "
                     "equipment pad, drainage, and utility connections.",
         responsible_party="Applicant", typical_days="3-7"),
    dict(process_type="Swimming-Pool/Spa", step_order=3, step_name="Submit Plans to LADBS",
         description="Submit online or at district office. Include structural/shell design for gunite pools. "
                     "Fees: $800–$1,500 typical.",
         responsible_party="Applicant", typical_days="1"),
    dict(process_type="Swimming-Pool/Spa", step_order=4, step_name="Plan Check Review",
         description="LADBS reviews for setbacks, drainage, electrical, and barrier/fencing compliance (LAMC 91.7106). "
                     "Typical: 2-4 weeks.",
         responsible_party="LADBS", typical_days="10-20"),
    dict(process_type="Swimming-Pool/Spa", step_order=5, step_name="Permit Issued & Construction",
         description="Pay issuance fees. Pool contractor builds shell, plumbing, electrical. "
                     "Safety barrier/fence must be installed before water is added.",
         responsible_party="Applicant", typical_days="30-90"),
    dict(process_type="Swimming-Pool/Spa", step_order=6, step_name="Inspections & Final",
         description="Pre-gunite/pre-plaster inspection, rough plumbing/electrical, barrier inspection, final. "
                     "Pool cannot be filled until final inspection passes.",
         responsible_party="LADBS", typical_days="5-20"),

    # EIR / ENV — 5 steps
    dict(process_type="EIR", step_order=1, step_name="File Environmental Assessment Form",
         description="EAF filed with the discretionary application. City Planning uses it to determine CEQA pathway: "
                     "CE (exempt), ND, MND, SCEA, or EIR.",
         responsible_party="Applicant", typical_days="1"),
    dict(process_type="EIR", step_order=2, step_name="CEQA Determination",
         description="City Planning issues CEQA determination. If EIR required, Notice of Preparation (NOP) issued. "
                     "NOP opens 30-day public scoping period.",
         responsible_party="City Planning", typical_days="30-60"),
    dict(process_type="EIR", step_order=3, step_name="Draft EIR Circulation",
         description="Draft EIR circulated for 45-day public comment period. "
                     "Covers traffic, air quality, noise, cultural resources, biology, land use.",
         responsible_party="City Planning", typical_days="45-60"),
    dict(process_type="EIR", step_order=4, step_name="Final EIR & Response to Comments",
         description="City Planning prepares Final EIR responding to all public comments. "
                     "Applicant may be required to fund additional technical studies.",
         responsible_party="City Planning", typical_days="60-180"),
    dict(process_type="EIR", step_order=5, step_name="EIR Certification & Findings",
         description="Decision-maker certifies EIR and adopts CEQA Findings. "
                     "Mitigation Monitoring and Reporting Program (MMRP) adopted. "
                     "Discretionary hearing proceeds after certification.",
         responsible_party="City Planning", typical_days="1-30"),

    # TOC — 5 steps
    dict(process_type="TOC", step_order=1, step_name="Confirm TOC Eligibility",
         description="Project must be within 1/2 mile of a major transit stop per TOC Tier map. "
                     "Tier (1-4) determines density bonus and incentive level.",
         responsible_party="Applicant", typical_days="1-2"),
    dict(process_type="TOC", step_order=2, step_name="File TOC Application",
         description="TOC case filed via OAS as DIR- prefix. EPS handles all TOC cases. "
                     "Fee ~$4,000–$9,000 depending on project size.",
         responsible_party="Applicant", typical_days="1"),
    dict(process_type="TOC", step_order=3, step_name="Ministerial Review",
         description="City Planning reviews project for TOC compliance (affordable unit count, "
                     "design standards, incentives requested). Ministerial: 60-90 days.",
         responsible_party="City Planning", typical_days="60-90"),
    dict(process_type="TOC", step_order=4, step_name="LOD Issued — Record Affordable Housing Agreement",
         description="LOD issued. Applicant must record Affordable Housing Agreement covenant with LA County Recorder "
                     "and obtain HCIDLA sign-off before LADBS permit.",
         responsible_party="Applicant", typical_days="14-30"),
    dict(process_type="TOC", step_order=5, step_name="Clear Conditions & File LADBS Permit",
         description="Clear LOD conditions at DSC. Submit LADBS building permit application with TOC LOD and clearance letter.",
         responsible_party="Applicant", typical_days="1-5"),

    # ZV — 8 steps
    dict(process_type="ZV", step_order=1, step_name="Pre-Application Meeting",
         description="Meet with City Planning at DSC to assess whether variance findings can be met. "
                     "Staff will confirm if a simpler path (adjustment) is available.",
         responsible_party="Applicant", typical_days="1"),
    dict(process_type="ZV", step_order=2, step_name="File Variance Application",
         description="File ZV via OAS. Fee ~$7,000–$9,000. "
                     "Must demonstrate 4 LAMC 12.27 findings: exceptional circumstances, hardship, "
                     "not self-created, consistent with general welfare.",
         responsible_party="Applicant", typical_days="1"),
    dict(process_type="ZV", step_order=3, step_name="Completeness Review",
         description="City Planning verifies application is complete.",
         responsible_party="City Planning", typical_days="14-30"),
    dict(process_type="ZV", step_order=4, step_name="Technical Review",
         description="Planner reviews findings, prepares staff report.",
         responsible_party="City Planning", typical_days="45-90"),
    dict(process_type="ZV", step_order=5, step_name="Public Notice",
         description="500-ft mailing, site posting, newspaper notice.",
         responsible_party="City Planning", typical_days="21"),
    dict(process_type="ZV", step_order=6, step_name="Public Hearing",
         description="Hearing before Zoning Administrator. Applicant presents findings; public may object.",
         responsible_party="Applicant", typical_days="1"),
    dict(process_type="ZV", step_order=7, step_name="LOD Issued",
         description="ZA issues Letter of Determination — approval, denial, or approval with conditions.",
         responsible_party="City Planning", typical_days="10-21"),
    dict(process_type="ZV", step_order=8, step_name="Appeal Period & LADBS Filing",
         description="15-day appeal window. After appeal period expires, clear conditions at DSC and file LADBS permit.",
         responsible_party="City Planning", typical_days="15"),

    # ADJ — 7 steps
    dict(process_type="ADJ", step_order=1, step_name="Confirm Adjustment Eligibility",
         description="ZAA allows up to 20% deviation from development standards. "
                     "More than 20%: variance required. File PZA first to identify all deviations.",
         responsible_party="Applicant", typical_days="1-3"),
    dict(process_type="ADJ", step_order=2, step_name="File Adjustment Application",
         description="ADJ/ZAA filed via OAS. Fee ~$3,000–$5,500. ZA can approve without full hearing "
                     "if no written objections received during notice period.",
         responsible_party="Applicant", typical_days="1"),
    dict(process_type="ADJ", step_order=3, step_name="Completeness Review",
         description="City Planning verifies application is complete.",
         responsible_party="City Planning", typical_days="14-30"),
    dict(process_type="ADJ", step_order=4, step_name="Technical Review & Notice",
         description="Planner reviews compliance. 500-ft mailing notice. Written comments period.",
         responsible_party="City Planning", typical_days="30-60"),
    dict(process_type="ADJ", step_order=5, step_name="ZA Decision",
         description="If no objections: ZA approves by mail order. If objections: public hearing scheduled.",
         responsible_party="City Planning", typical_days="10-30"),
    dict(process_type="ADJ", step_order=6, step_name="LOD Issued",
         description="ZA issues LOD with approval/denial and conditions.",
         responsible_party="City Planning", typical_days="5-14"),
    dict(process_type="ADJ", step_order=7, step_name="Clear Conditions at DSC",
         description="Clear LOD conditions at DSC. File LADBS permit with conditions clearance letter.",
         responsible_party="Applicant", typical_days="5-14"),

    # PM (Parcel Map) — 7 steps
    dict(process_type="PM", step_order=1, step_name="Pre-Application / Lot Tie Reversal Check",
         description="Confirm parcel is not subject to Covenant and Agreement (C&A) lot tie. "
                     "Check with Bureau of Engineering (BOE). SB 9 lot splits have a separate ministerial pathway.",
         responsible_party="Applicant", typical_days="1-3"),
    dict(process_type="PM", step_order=2, step_name="File Parcel Map Application",
         description="Parcel maps (4 or fewer lots) filed with Advisory Agency (AA). "
                     "Fee ~$10,000–$14,000. Include tentative map, legal description, and title report.",
         responsible_party="Applicant", typical_days="1"),
    dict(process_type="PM", step_order=3, step_name="Technical Review",
         description="Advisory Agency reviews map for zoning compliance, access, utilities, and dedications.",
         responsible_party="City Planning", typical_days="60-120"),
    dict(process_type="PM", step_order=4, step_name="Conditions of Approval",
         description="Advisory Agency issues conditions: street dedications, utility easements, drainage improvements.",
         responsible_party="City Planning", typical_days="14-30"),
    dict(process_type="PM", step_order=5, step_name="Clear Conditions",
         description="Clear conditions at DSC. Obtain BOE sign-off on street/utility dedications.",
         responsible_party="Applicant", typical_days="14-60"),
    dict(process_type="PM", step_order=6, step_name="Final Map Preparation",
         description="Licensed surveyor prepares final parcel map for recordation.",
         responsible_party="Applicant", typical_days="14-30"),
    dict(process_type="PM", step_order=7, step_name="Map Recordation & New APNs",
         description="Final map recorded at LA County Recorder. "
                     "New APNs assigned by County Assessor. File LADBS permits using new APNs.",
         responsible_party="Applicant", typical_days="5-14"),

    # SPPA — 5 steps
    dict(process_type="SPPA", step_order=1, step_name="Confirm Specific Plan Requirements",
         description="Each Specific Plan has unique development standards and permit types. "
                     "Download the applicable plan from planning.lacity.gov and review permit requirements.",
         responsible_party="Applicant", typical_days="1-3"),
    dict(process_type="SPPA", step_order=2, step_name="File SPPA Application",
         description="SPPAs filed via OAS as DIR- prefix. Fee ~$3,000–$7,000. "
                     "Include project plans, findings statement, and Specific Plan compliance checklist.",
         responsible_party="Applicant", typical_days="1"),
    dict(process_type="SPPA", step_order=3, step_name="Technical Review",
         description="City Planning reviews project against Specific Plan standards.",
         responsible_party="City Planning", typical_days="30-90"),
    dict(process_type="SPPA", step_order=4, step_name="Decision & LOD",
         description="Director or ZA issues determination. Conditions may apply.",
         responsible_party="City Planning", typical_days="10-21"),
    dict(process_type="SPPA", step_order=5, step_name="Clear Conditions & File LADBS Permit",
         description="Clear any conditions at DSC. File LADBS permit within approval validity period. "
                     "File time extension (EXT) before expiry if needed.",
         responsible_party="Applicant", typical_days="1-14"),

    # CDP — 7 steps
    dict(process_type="CDP", step_order=1, step_name="Confirm Coastal Zone Boundary",
         description="Verify parcel is within City of LA Coastal Zone via ZIMAS (look for 'Coastal Zone' overlay). "
                     "City LCP governs — separate from County Coastal Commission jurisdiction.",
         responsible_party="Applicant", typical_days="1"),
    dict(process_type="CDP", step_order=2, step_name="Pre-Application Meeting",
         description="Meet with Coastal Planning section at West LA DSC. "
                     "Discuss sea level rise, drainage, visual impact, and public access requirements.",
         responsible_party="Applicant", typical_days="1"),
    dict(process_type="CDP", step_order=3, step_name="File CDP Application",
         description="CDPs filed via OAS as DIR- prefix. Fee ~$5,000–$9,000. "
                     "Include sea level rise analysis, drainage plan, and visual impact study. CEQA runs concurrently.",
         responsible_party="Applicant", typical_days="1"),
    dict(process_type="CDP", step_order=4, step_name="Completeness & Technical Review",
         description="City Planning verifies completeness. Coastal planner reviews for LCP consistency. "
                     "Typical: 3-6 months.",
         responsible_party="City Planning", typical_days="60-120"),
    dict(process_type="CDP", step_order=5, step_name="Public Notice",
         description="500-ft mailing notice and site posting. Coastal projects also noticed in local paper.",
         responsible_party="City Planning", typical_days="21"),
    dict(process_type="CDP", step_order=6, step_name="LOD Issued",
         description="Director issues LOD. Conditions typically include drainage BOE sign-off, lighting, public access.",
         responsible_party="City Planning", typical_days="10-21"),
    dict(process_type="CDP", step_order=7, step_name="Clear Conditions & File LADBS Permit",
         description="BOE drainage sign-off, any other conditions. File LADBS permit with CDP LOD and clearance. "
                     "Appeal period: 10 days post-LOD.",
         responsible_party="Applicant", typical_days="14-30"),
]


# --------------------------------------------------------------------------- #
# Persona guidance
# --------------------------------------------------------------------------- #

WORKFLOW_PERSONAS = [

    # ADU standard plan — resident
    dict(process_type="ADU_standard", step_name="Choose a Standard Plan", persona="resident",
         guidance="Browse approved plans at permitpath.la — filter by bedrooms and size. "
                  "Prefab options (Abodu, Connect Homes) include delivery and install. "
                  "YOU-ADU is the free City of LA plan if budget is tight."),
    dict(process_type="ADU_standard", step_name="Check Eligibility & HPOZ", persona="resident",
         guidance="Go to zimas.lacity.org and enter your address. If you see 'HPOZ' in the overlay list, "
                  "you must file with City Planning first (ADUH case) before LADBS. Call (213) 974-1234."),
    dict(process_type="ADU_standard", step_name="Submit to LADBS", persona="resident",
         guidance="Go to ladbs.org → Submit a Permit Application → ADU. Enter your standard plan number. "
                  "Much faster than going in person — you'll get a case number immediately."),
    dict(process_type="ADU_standard", step_name="Pay Issuance Fees & Receive Permit", persona="resident",
         guidance="Issuance fees for a standard plan ADU are usually $150–$400. Pay online via MyLADBS "
                  "and your permit PDF will be emailed within 1 business day."),

    # ADU custom — resident
    dict(process_type="ADU", step_name="Check ADU Eligibility", persona="resident",
         guidance="Go to zimas.lacity.org and enter your address. Look for 'Zoning' and any 'Overlay' zones. "
                  "If you see HPOZ, there's extra review — call City Planning first."),
    dict(process_type="ADU", step_name="Prepare Plans", persona="resident",
         guidance="You don't need a licensed architect for a simple garage conversion, but a draftsperson "
                  "($500–$1,500) saves you from correction letters. Standard plans (permitpath.la) are faster."),
    dict(process_type="ADU", step_name="Submit to LADBS", persona="resident",
         guidance="You can start online at ladbs.org. Choose 'Submit a Permit Application' → 'ADU'. "
                  "Much faster than going in person."),
    dict(process_type="ADU", step_name="Plan Check Review", persona="resident",
         guidance="LADBS usually reviews ADUs in 20-30 days for custom plans. "
                  "You'll get an email with any corrections needed. Check your MyLADBS inbox."),
    dict(process_type="ADU", step_name="Pay Issuance Fees & Receive Permit", persona="resident",
         guidance="Issuance fees are separate from plan check fees. Usually $200–$600 for a custom ADU. "
                  "Pay online to avoid a trip downtown."),
    dict(process_type="ADU", step_name="Inspections", persona="resident",
         guidance="Schedule inspections via MyLADBS or call your district office. You'll need: "
                  "foundation, framing, rough electrical/plumbing, insulation, and final. "
                  "Your contractor should coordinate these."),

    # ADU — contractor
    dict(process_type="ADU", step_name="Submit to LADBS", persona="contractor",
         guidance="Use ePlanLA (eplanla.lacity.org) for electronic plan submission. "
                  "Ensure Title 24 energy calcs and CALGreen checklist are included."),
    dict(process_type="ADU", step_name="Plan Check Review", persona="contractor",
         guidance="Custom ADU plan check at Metro branch averages 20-25 days first round. "
                  "Track status via MyLADBS or call (213) 482-0000."),
    dict(process_type="ADU", step_name="Inspections", persona="contractor",
         guidance="Required inspections: 010 (foundation), 020 (framing), 030 (rough plumbing), "
                  "040 (rough electrical), 055 (insulation), 999 (final). Use MyLADBS inspection portal."),

    # Bldg-New — developer
    dict(process_type="Bldg-New", step_name="Confirm Zoning & Entitlements", persona="developer",
         guidance="Run ZIMAS to confirm base zone, applicable overlays (TOC, HPOZ, CDO, RIO, CPIO), "
                  "Q/D conditions, and community plan land use. Flag discretionary entitlements before starting CDs."),
    dict(process_type="Bldg-New", step_name="Submit to LADBS", persona="developer",
         guidance="Multi-family goes to Multi-Family Plan Check team (Metro branch). "
                  "Include fire dept prelim approval for Type V-A+. Submit via ePlanLA. "
                  "High-rise (55 ft+) requires separate LAFD plan check."),
    dict(process_type="Bldg-New", step_name="Plan Check Review", persona="developer",
         guidance="First round: 8-12 weeks multi-family, 12-20 weeks high-rise. "
                  "Track correction queue via MyLADBS. Consider plan check expediter for complex projects."),
    dict(process_type="Bldg-New", step_name="Certificate of Occupancy", persona="developer",
         guidance="File CofO application before final inspection. LADBS issues TCO for minor outstanding items. "
                  "CofO is required for final loan draw in most construction finance agreements."),

    # CUB — developer
    dict(process_type="CUB", step_name="Pre-Application Meeting", persona="developer",
         guidance="Book DSC appointment at planning.lacity.gov/contact. Bring site plan and proposed ABC license type. "
                  "Ask about Specific Plan overlays (Sunset, Hollywood, etc.) that add requirements."),
    dict(process_type="CUB", step_name="File CUB Application", persona="developer",
         guidance="File via OAS at planning.lacity.gov/oas. Case prefix ZA- (faster, 3-5 mo) or APC- (5-8 mo) "
                  "depending on project scale and zone."),
    dict(process_type="CUB", step_name="Public Hearing", persona="developer",
         guidance="Prepare formal presentation: site plan, operating parameters, community outreach evidence, "
                  "LAPD/Fire comment responses. Land use attorney strengthens the record."),
    dict(process_type="CUB", step_name="Clear Conditions at DSC", persona="developer",
         guidance="Get LOD copy from case planner. Work through each condition systematically. "
                  "Some require separate agency sign-offs (LAPD, Health Dept, LADOT). Allow 2-4 weeks."),

    # ZC — developer
    dict(process_type="ZC", step_name="Preliminary Zoning Assessment", persona="developer",
         guidance="PZA fee ~$862 (LAMC 19.09). Identifies non-compliance before you invest in full CDs. "
                  "Critical for locking down the issues list early."),
    dict(process_type="ZC", step_name="CEQA Review", persona="developer",
         guidance="MND: 20-30 day public comment + 10-day response. "
                  "EIR: NOP (30 days) + Scoping + Draft EIR (45-day comment) + Final EIR + Findings. "
                  "Budget 18-36 months for EIR track."),
    dict(process_type="ZC", step_name="Council File / City Council", persona="developer",
         guidance="Files move through PLUM Committee before full Council vote. "
                  "Engage Council office staff early. Allow 3-6 months post-CPC action."),

    # Bldg-Alter/Repair — resident
    dict(process_type="Bldg-Alter/Repair", step_name="Determine Permit Type", persona="resident",
         guidance="Simple non-structural work (painting, flooring, cabinet swap) needs no permit. "
                  "Anything touching walls, electrical, plumbing, or structure needs one. "
                  "When in doubt, call LADBS at (213) 482-0000."),
    dict(process_type="Bldg-Alter/Repair", step_name="Prepare Plans or Scope", persona="resident",
         guidance="For a kitchen or bath remodel with no layout changes, a simple sketch works. "
                  "For anything structural, hire a licensed architect or structural engineer."),
    dict(process_type="Bldg-Alter/Repair", step_name="Submit & Pay Fees", persona="resident",
         guidance="Many simple remodels can be permitted online at ladbs.org — no trip to the office needed. "
                  "Fees for a typical kitchen remodel run $200–$600."),
    dict(process_type="Bldg-Alter/Repair", step_name="Construction & Inspections", persona="resident",
         guidance="You or your contractor must call for inspections at key stages — "
                  "don't cover walls before rough electrical/plumbing is signed off. "
                  "Schedule online at ladbs.org or call (213) 482-0000."),
    dict(process_type="Bldg-Alter/Repair", step_name="Final Inspection", persona="resident",
         guidance="Once all work is done, call for a final inspection. "
                  "When passed, the permit is 'finaled' and you're done."),

    # Bldg-Alter/Repair — contractor
    dict(process_type="Bldg-Alter/Repair", step_name="Determine Permit Type", persona="contractor",
         guidance="Check if project qualifies for OTC (over-the-counter) review — "
                  "non-structural TIs under $50K valuation often qualify. "
                  "Structural or MEP-heavy work goes to full plan check."),
    dict(process_type="Bldg-Alter/Repair", step_name="Submit & Pay Fees", persona="contractor",
         guidance="Submit via ePlanLA for electronic plan check. "
                  "Include all required docs: Title 24 if HVAC/lighting affected, "
                  "accessibility compliance for commercial TIs (CBC Chapter 11B)."),
    dict(process_type="Bldg-Alter/Repair", step_name="Construction & Inspections", persona="contractor",
         guidance="Required inspection types vary by scope. Common: 015 (framing), 030 (rough plumbing), "
                  "040 (rough electrical), 055 (insulation), 999 (final). "
                  "Commercial TIs also need 095 (accessibility) and fire dept sign-off."),

    # Bldg-Alter/Repair — developer
    dict(process_type="Bldg-Alter/Repair", step_name="Determine Permit Type", persona="developer",
         guidance="For large-scale TIs (>5,000 sf, multi-floor, change of occupancy), "
                  "plan check is mandatory. Confirm with LADBS if change of occupancy triggers "
                  "full accessibility and fire code upgrade requirements."),
    dict(process_type="Bldg-Alter/Repair", step_name="Submit & Pay Fees", persona="developer",
         guidance="Multi-tenant or large commercial TIs: submit via ePlanLA to Metro Commercial plan check team. "
                  "Fees are valuation-based — declare accurate valuation to avoid re-calc delays."),
    dict(process_type="Bldg-Alter/Repair", step_name="Final Inspection", persona="developer",
         guidance="For commercial, final inspection triggers CofO review if occupancy class changed. "
                  "Coordinate CofO application in advance to avoid occupancy delay."),

    # Bldg-Addition — all personas
    dict(process_type="Bldg-Addition", step_name="Confirm Zoning & Setbacks", persona="resident",
         guidance="Before hiring anyone, check ZIMAS for your setbacks, height limits, and lot coverage max. "
                  "A rear addition commonly triggers rear-yard setback issues — confirm yours first."),
    dict(process_type="Bldg-Addition", step_name="Prepare Construction Documents", persona="resident",
         guidance="You need a licensed architect for anything structural or over 120 sq ft. "
                  "Get at least 2 quotes — residential addition design runs $3,000–$8,000."),
    dict(process_type="Bldg-Addition", step_name="Submit to LADBS", persona="resident",
         guidance="Submit via MyLADBS online or in person at your nearest district office. "
                  "Plan check fees are based on valuation — a $100K addition runs roughly $1,500–$3,000."),
    dict(process_type="Bldg-Addition", step_name="Plan Check Review", persona="resident",
         guidance="First round typically 4-8 weeks for a residential addition. "
                  "Check your MyLADBS inbox for the correction letter."),
    dict(process_type="Bldg-Addition", step_name="Confirm Zoning & Setbacks", persona="developer",
         guidance="Run full ZIMAS check: base zone setbacks, height district, FAR limits, Q/D conditions, "
                  "and any specific plan constraints. Flag variance or adjustment needs before starting CDs."),
    dict(process_type="Bldg-Addition", step_name="Submit to LADBS", persona="developer",
         guidance="Multi-family additions go to Multi-Family plan check team at Metro. "
                  "Submit via ePlanLA with full set: architectural, structural, MEP, Title 24."),
    dict(process_type="Bldg-Addition", step_name="Confirm Zoning & Setbacks", persona="contractor",
         guidance="Verify the architect's plans reflect actual site conditions before pulling permit. "
                  "Check for any open violations on the parcel via LADBS VCO search first."),
    dict(process_type="Bldg-Addition", step_name="Construction & Inspections", persona="contractor",
         guidance="Key inspections: 010 (foundation), 015 (framing), 030/040 (rough MEP), "
                  "055 (insulation), 999 (final). For second-story additions, shear wall nailing "
                  "inspection (016) is required before any sheathing."),

    # Electrical — resident + contractor
    dict(process_type="Electrical", step_name="Determine Scope & Permit Type", persona="resident",
         guidance="Minor work like adding an outlet or light fixture in existing wiring may be exempt. "
                  "Panel upgrades, new circuits, EV chargers, and service changes all need a permit. "
                  "Check ladbs.org or call (213) 482-0000."),
    dict(process_type="Electrical", step_name="Submit & Pay Fees", persona="resident",
         guidance="Most residential electrical permits can be pulled online at ladbs.org in minutes. "
                  "Fees for a panel upgrade or EV charger typically run $150–$400."),
    dict(process_type="Electrical", step_name="Inspections & Final", persona="resident",
         guidance="Rough wiring inspection (type 320) must happen before walls are closed. "
                  "Final electrical (type 399) is the last step. Your licensed electrician "
                  "should schedule both."),
    dict(process_type="Electrical", step_name="Determine Scope & Permit Type", persona="contractor",
         guidance="C-10 license required. Simple residential: e-permit online. "
                  "Commercial, multi-family, or service entrance work: submit to LADBS Electrical division. "
                  "For 400A+ services, LADAP (LA Department of Water & Power) coordination required."),
    dict(process_type="Electrical", step_name="Submit & Pay Fees", persona="contractor",
         guidance="Use MyLADBS for residential pulls. Commercial goes to Metro Electrical plan check. "
                  "Include load calc and single-line diagram for service upgrades."),
    dict(process_type="Electrical", step_name="Inspections & Final", persona="contractor",
         guidance="Inspection types: 320 (rough wiring), 340 (service entrance), 399 (final). "
                  "LADWP meter pull and re-set required for service upgrades — coordinate timing."),

    # Plumbing — resident + contractor
    dict(process_type="Plumbing", step_name="Determine Scope & Permit Type", persona="resident",
         guidance="Replacing a water heater, toilet, or faucet in-kind usually needs a permit. "
                  "Rerouting pipes or adding new fixtures always does. "
                  "Pull online at ladbs.org — it takes 5 minutes."),
    dict(process_type="Plumbing", step_name="Submit & Pay Fees", persona="resident",
         guidance="Most residential plumbing permits are $100–$350 online. "
                  "Water heater replacements are same-day e-permits."),
    dict(process_type="Plumbing", step_name="Inspections & Final", persona="resident",
         guidance="Rough plumbing (type 030) before walls close. Final plumbing (type 099) when done. "
                  "Your plumber should schedule — don't let them skip it."),
    dict(process_type="Plumbing", step_name="Determine Scope & Permit Type", persona="contractor",
         guidance="C-36 license required. Residential re-pipes and water heaters: online e-permit. "
                  "Commercial kitchen, medical gas, backflow, or sewer: full plan check required."),
    dict(process_type="Plumbing", step_name="Submit & Pay Fees", persona="contractor",
         guidance="Commercial plumbing plan check: submit to LADBS Plumbing division at Metro. "
                  "Include isometric diagrams for re-pipe or commercial kitchen work."),
    dict(process_type="Plumbing", step_name="Inspections & Final", persona="contractor",
         guidance="Inspection types: 030 (rough plumbing), 031 (sewer/DWV), 099 (final). "
                  "Pressure test required on new water lines before rough inspection sign-off."),

    # HVAC — resident + contractor
    dict(process_type="HVAC", step_name="Determine Scope & Permit Type", persona="resident",
         guidance="Replacing an existing HVAC unit same-for-same: online permit, no plan check. "
                  "Adding new ductwork or a new system to a room that didn't have one: plan check. "
                  "Pull permit online at ladbs.org before work starts."),
    dict(process_type="HVAC", step_name="Submit & Pay Fees", persona="resident",
         guidance="Like-for-like HVAC replacement permits are $100–$300 online. "
                  "Same-day approval is typical for residential replacements."),
    dict(process_type="HVAC", step_name="Inspections & Final", persona="resident",
         guidance="Rough HVAC duct inspection (type 240) before ceilings/walls close. "
                  "Final HVAC (type 299) when fully installed. Your HVAC contractor handles scheduling."),
    dict(process_type="HVAC", step_name="Determine Scope & Permit Type", persona="contractor",
         guidance="C-20 license required. Residential replacements: e-permit. "
                  "New duct systems, commercial HVAC, Title 24 compliance work: plan check required. "
                  "Include load calc and duct diagram for plan check submissions."),
    dict(process_type="HVAC", step_name="Submit & Pay Fees", persona="contractor",
         guidance="Commercial HVAC plan check: submit to Mechanical division at Metro. "
                  "Title 24 MECH forms required for any work affecting energy performance."),
    dict(process_type="HVAC", step_name="Inspections & Final", persona="contractor",
         guidance="Inspection types: 240 (rough duct), 241 (equipment set), 299 (final). "
                  "TAB (test-and-balance) report required for commercial systems over 5 tons."),

    # Fire Sprinkler — contractor + developer
    dict(process_type="Fire Sprinkler", step_name="Submit & Pay Fees", persona="contractor",
         guidance="C-16 license required. Submit sprinkler plans to LADBS Fire Sprinkler division at Metro. "
                  "LAFD also reviews plans — coordinate dual submission. "
                  "Include hydraulic calcs and NFPA 13/13R/13D designation."),
    dict(process_type="Fire Sprinkler", step_name="Plan Check Review", persona="contractor",
         guidance="LADBS and LAFD review in parallel. Typical first round: 3-5 weeks. "
                  "LAFD comments often cover water supply, FDC location, and head spacing."),
    dict(process_type="Fire Sprinkler", step_name="Inspections & Final", persona="contractor",
         guidance="Rough sprinkler inspection before ceilings close. "
                  "Hydrostatic pressure test (200 psi, 2 hours) required at rough inspection. "
                  "Final: LAFD witness test required for commercial systems."),
    dict(process_type="Fire Sprinkler", step_name="Submit & Pay Fees", persona="developer",
         guidance="For new construction, fire sprinkler permit is a supplemental to the main building permit. "
                  "Submit early — LAFD review can add 3-6 weeks to the critical path. "
                  "Coordinate with structural engineer if concealed heads require ceiling framing changes."),

    # Grading — contractor + developer
    dict(process_type="Grading", step_name="Prepare Grading Plans", persona="contractor",
         guidance="C-12 license required. Grading plans must be prepared by a licensed civil engineer. "
                  "For hillside lots (slope >2:1 or cut >5 ft), geotechnical report is mandatory."),
    dict(process_type="Grading", step_name="Submit to LADBS", persona="contractor",
         guidance="Submit to LADBS Grading division. Include soils report, erosion control plan, "
                  "SWPPP if over 1 acre disturbed, and haul route approval if exporting material."),
    dict(process_type="Grading", step_name="Inspections & Final", persona="contractor",
         guidance="Key inspections: 400 (rough grading), 401 (drainage), 499 (final grading cert). "
                  "Soils engineer must be on site for any cut exceeding 5 ft. "
                  "Final grading cert required before LADBS will issue building permit."),
    dict(process_type="Grading", step_name="Prepare Grading Plans", persona="developer",
         guidance="For large earthwork, pre-coordinate with Bureau of Engineering (BOE) for haul routes "
                  "and with LADBS geology unit for hillside review. "
                  "Factor grading permit timeline into project schedule — can be 6-12 weeks."),

    # Swimming-Pool/Spa — resident
    dict(process_type="Swimming-Pool/Spa", step_name="Verify Setbacks & Zoning", persona="resident",
         guidance="Pools must meet minimum setbacks: typically 5 ft from property lines in residential zones. "
                  "Check ZIMAS and your property survey. "
                  "If you're in a hillside zone, soils report may be required."),
    dict(process_type="Swimming-Pool/Spa", step_name="Submit Plans to LADBS", persona="resident",
         guidance="You'll need a site plan showing pool dimensions, setbacks, and drain/equipment location. "
                  "Submit online or at your nearest district office. "
                  "Plan check fees for a typical pool run $800–$1,500."),
    dict(process_type="Swimming-Pool/Spa", step_name="Inspections & Final", persona="resident",
         guidance="Required inspections: pre-gunite/pre-plaster (pool shell), "
                  "rough plumbing/electrical (before backfill), and final. "
                  "Your pool contractor should schedule all inspections."),

    # EIR / ENV — developer
    dict(process_type="EIR", step_name="File Environmental Assessment Form", persona="developer",
         guidance="EAF filed with the discretionary application. City Planning uses it to determine "
                  "the appropriate CEQA pathway: CE, ND, MND, or EIR. "
                  "Submit CEQA Initial Study checklist with the application."),
    dict(process_type="EIR", step_name="CEQA Determination", persona="developer",
         guidance="If EIR required, you'll receive a Notice of Preparation (NOP). "
                  "NOP opens a 30-day public scoping period. "
                  "Hire an environmental consultant early — EIR prep runs $150K–$500K+."),
    dict(process_type="EIR", step_name="Draft EIR Circulation", persona="developer",
         guidance="Draft EIR circulated for 45-day public comment. "
                  "Respond to all comments in the Final EIR. "
                  "City Planning certifies the EIR before the discretionary hearing."),
    dict(process_type="EIR", step_name="EIR Certification & Findings", persona="developer",
         guidance="Decision-maker (ZA, APC, CPC, or Council) certifies EIR and adopts CEQA Findings. "
                  "If significant unavoidable impacts exist, Statement of Overriding Considerations required. "
                  "Mitigation Monitoring and Reporting Program (MMRP) attached to project approval."),

    # TOC — developer
    dict(process_type="TOC", step_name="Confirm TOC Eligibility", persona="developer",
         guidance="Project must be within 1/2 mile of a major transit stop. "
                  "Use the TOC Affordable Housing Incentive Program map at planning.lacity.gov. "
                  "Tier determines incentive level — Tier 4 is closest to transit and most generous."),
    dict(process_type="TOC", step_name="File TOC Application", persona="developer",
         guidance="TOC cases filed via OAS as DIR- prefix. "
                  "EPS (Expedited Processing Section) handles TOC cases. "
                  "Ministerial TOC determinations: 60-90 days. Larger projects may require discretionary review."),
    dict(process_type="TOC", step_name="Record Affordable Housing Agreement", persona="developer",
         guidance="Affordable Housing Agreement covenant must be recorded with LA County Recorder "
                  "before LADBS will issue a building permit. "
                  "Coordinate with Housing + Community Investment Dept (HCIDLA) for covenant language."),
    dict(process_type="TOC", step_name="Clear Conditions & File LADBS Permit", persona="developer",
         guidance="After LOD, return to DSC to clear any TOC conditions. "
                  "Bring recorded covenant, HCIDLA sign-off, and updated site plan. "
                  "LADBS requires TOC LOD and clearance letter before permit issuance."),

    # ZV — developer + resident
    dict(process_type="ZV", step_name="Pre-Application Meeting", persona="developer",
         guidance="Book DSC appointment. Bring a site plan showing the specific deviation requested "
                  "and your justification (hardship, exceptional circumstances). "
                  "ZA will tell you if the variance is grantable before you pay filing fees."),
    dict(process_type="ZV", step_name="File Variance Application", persona="developer",
         guidance="File ZV via OAS. Fee ~$7,000–$9,000. "
                  "Must demonstrate all four variance findings (LAMC 12.27): "
                  "exceptional circumstances, hardship, not self-created, consistent with general welfare."),
    dict(process_type="ZV", step_name="Public Hearing", persona="developer",
         guidance="ZA hears variances. Prepare a findings brief — the record must support all four findings. "
                  "Neighbor objections can sink a variance if the hardship isn't documented."),
    dict(process_type="ZV", step_name="Pre-Application Meeting", persona="resident",
         guidance="Call City Planning at (213) 974-1234 or walk in to a DSC to ask whether a variance "
                  "is needed for your project — staff can often point to a simpler path (adjustment, "
                  "administrative exception) that costs less and takes less time."),
    dict(process_type="ZV", step_name="File Variance Application", persona="resident",
         guidance="Variance fees ($7,000–$9,000) plus a public hearing mean this is a 4-6 month process. "
                  "A land use attorney or planning consultant is strongly recommended."),

    # ADJ — developer
    dict(process_type="ADJ", step_name="Confirm Adjustment Eligibility", persona="developer",
         guidance="Adjustments (ZAA) allow up to 20% deviation from development standards (setbacks, height, FAR). "
                  "More than 20% needs a full variance. "
                  "File PZA first to confirm which deviations apply."),
    dict(process_type="ADJ", step_name="File Adjustment Application", persona="developer",
         guidance="ADJ/ZAA filed via OAS. Fee ~$3,000–$5,500. "
                  "Faster than a variance — ZA can approve without a full public hearing "
                  "if no objections received during notice period."),
    dict(process_type="ADJ", step_name="Clear Conditions at DSC", persona="developer",
         guidance="ADJ LOD conditions typically involve recordation, utility dedications, or design requirements. "
                  "Clear at DSC before filing LADBS permit. Allow 1-2 weeks for straightforward conditions."),

    # PM (Parcel Map) — developer
    dict(process_type="PM", step_name="Pre-Application / Lot Tie Reversal Check", persona="developer",
         guidance="Confirm parcel is not subject to a lot tie agreement (Covenant and Agreement C&A) "
                  "that would prevent subdivision. Check with Bureau of Engineering (BOE) first."),
    dict(process_type="PM", step_name="File Parcel Map Application", persona="developer",
         guidance="Parcel maps (4 lots or fewer) filed with Advisory Agency (AA). "
                  "For SB 9 lot splits: urban lot split pathway applies, ministerial approval. "
                  "Standard PM: $10,000–$14,000 in fees, 6-12 month timeline."),
    dict(process_type="PM", step_name="Conditions of Approval & Map Recordation", persona="developer",
         guidance="Advisory Agency issues conditions (street dedications, utility easements, drainage). "
                  "Map must be recorded at LA County Recorder. "
                  "New APNs assigned by County Assessor after recordation — obtain before filing LADBS permits."),

    # SPPA — developer
    dict(process_type="SPPA", step_name="Confirm Specific Plan Requirements", persona="developer",
         guidance="SPPAs are project-specific — each Specific Plan (Sunset, Hollywood, Venice, etc.) "
                  "has its own standards and permit types. "
                  "Download the applicable Specific Plan document from planning.lacity.gov before filing."),
    dict(process_type="SPPA", step_name="File SPPA Application", persona="developer",
         guidance="SPPAs filed via OAS as DIR- prefix. Fee varies by plan (~$3,000–$7,000). "
                  "Attach project plans, a findings statement, and the applicable Specific Plan checklist."),
    dict(process_type="SPPA", step_name="Decision & Conditions", persona="developer",
         guidance="Director or ZA issues determination. If approved with conditions, clear at DSC. "
                  "Note: SPPA approvals expire — file LADBS permit within the validity period "
                  "or file a time extension (EXT) before expiry."),

    # CDP — developer + resident
    dict(process_type="CDP", step_name="Confirm Coastal Zone Boundary", persona="developer",
         guidance="Use ZIMAS to confirm the parcel is in the Coastal Zone. "
                  "City of LA Local Coastal Program (LCP) governs — separate from County CCC jurisdiction. "
                  "Projects in the Coastal Zone require CDP before LADBS permit."),
    dict(process_type="CDP", step_name="File CDP Application", persona="developer",
         guidance="CDPs filed via OAS as DIR- prefix. Fee ~$5,000–$9,000. "
                  "Include sea level rise analysis, drainage plan, and visual impact study. "
                  "CEQA analysis runs concurrently."),
    dict(process_type="CDP", step_name="Conditions & LADBS Filing", persona="developer",
         guidance="CDP conditions often involve drainage, lighting, and public access. "
                  "Bureau of Engineering (BOE) sign-off on drainage conditions required before LADBS permit. "
                  "Appeal period: 10 days after LOD for appeals to the City Council."),
    dict(process_type="CDP", step_name="Confirm Coastal Zone Boundary", persona="resident",
         guidance="If your Venice, Pacific Palisades, or San Pedro property is in the Coastal Zone, "
                  "you need a CDP for most construction work. "
                  "Check ZIMAS — look for 'Coastal Zone' in the overlay list."),
    dict(process_type="CDP", step_name="File CDP Application", persona="resident",
         guidance="Fees and complexity mean most residents hire a planning consultant. "
                  "Timeline is typically 4-8 months. "
                  "Contact the Coastal Planning section at West LA DSC for guidance."),
]


# --------------------------------------------------------------------------- #
# Seed function
# --------------------------------------------------------------------------- #

def seed():
    db = SessionLocal()
    try:
        # Wipe existing data (order matters for FK constraints)
        db.query(WorkflowPersona).delete()
        db.query(WorkflowStep).delete()
        db.query(Case).delete()
        db.query(Plot).delete()
        db.commit()

        for p in PLOTS:
            db.add(Plot(**p))
        db.commit()

        for c in CASES:
            db.add(Case(**c))
        db.commit()

        for s in WORKFLOW_STEPS:
            db.add(WorkflowStep(**s))
        db.commit()

        for g in WORKFLOW_PERSONAS:
            db.add(WorkflowPersona(**g))
        db.commit()

        print(
            f"✓ Seeded {len(PLOTS)} plots, {len(CASES)} cases, "
            f"{len(WORKFLOW_STEPS)} workflow steps, {len(WORKFLOW_PERSONAS)} persona rows."
        )
    finally:
        db.close()


if __name__ == "__main__":
    seed()
