# LA Permit Workflow — Real Source Catalog

> **Purpose:** Replace synthetic workflow steps, references, and permit-type taxonomy with verified official sources. Live case/parcel API integration is explicitly out of scope.
>
> **Status flags:**
> - ✅ **Confirmed primary source** — official city document/page, directly usable
> - ⚠️ **Partially confirmed** — official source exists but fragmented, requires compilation, or partially superseded
> - ❌ **Gap** — no single authoritative public document found; best available substitute noted

---

## 1. Official process documentation (replaces the 135 hand-written workflow steps)

### 1A. LADBS — Building & Safety (plan review, permitting, inspections)

| Source | URL | Status |
|---|---|---|
| Plan review & permitting hub (all permit types, all plan-check tracks) | https://dbs.lacity.gov/services/plan-review-permitting | ✅ |
| Counter Plan Check | linked from hub (e.g. `/plan-check-permit/counter-plan-check`) | ✅ |
| Expanded Counter Plan Check | linked from hub | ✅ |
| Express Permits | https://dbs.lacity.gov/express-permits | ✅ |
| Regular Plan Check | https://dbs.lacity.gov/plan-check-permit/regular-plan-check | ✅ |
| Homeowners step-by-step guide (web) | https://dbs.lacity.gov/services/homeowner-step-by-step | ✅ |
| Homeowners Guide PDF | https://dbs.lacity.gov/sites/default/files/efs/pdf/publications/misc/homeowners-guide-to-permits-inspections.pdf | ✅ |
| ADU-specific process hub | https://dbs.lacity.gov/adu | ✅ |
| Forms & Publications library (searchable) | https://dbs.lacity.gov/forms-and-publications | ✅ but ⚠️ Requires per-process-type query |
| Standard Corrections List (what reviewers check) | https://dbs.lacity.gov/forms-publications/publications/standard-corrections-list | ✅ |
| Information Bulletins sub-tab (procedure memos) | https://dbs.lacity.gov/forms-and-publications → filter by "Information Bulletins" | ✅ but ⚠️ Searchable database, not a single doc |
| Building Permit & Clearance Handbook (inter-department clearances) | https://dbs.lacity.gov/sites/default/files/efs/pdf/publications/clearance-handbook.pdf | ✅ |
| LADBS Fee Schedules | https://dbs.lacity.gov/fee-schedules | ✅ |
| LADBS Inspection page | https://dbs.lacity.gov/services/inspections | ✅ |
| Permit Status Information page | https://dbs.lacity.gov/services/permit-status | ✅ |
| LADBS Building Permits open dataset | https://data.lacity.org (search "Building Permits") | ✅ Schema = ground truth for status codes & inspection types |

### 1B. City Planning — Entitlements & Land Use

| Source | URL | Status |
|---|---|---|
| Planning Approvals (3-tier: by‑right / ministerial / discretionary) | https://planning.lacity.gov/project-review/planning-approvals | ✅ |
| Land Use Determinations | https://planning.lacity.gov/project-review/land-use-determinations | ✅ |
| Case Filing & Condition Clearances | https://planning.lacity.gov/project-review/case-filings | ✅ |
| Planning Services hub (DSC services, BESt, Housing, etc.) | https://planning.lacity.gov/project-review/planning-services | ✅ |
| Application Forms (per-entitlement-type, Chapter 1 vs Chapter 1A) | https://planning.lacity.gov/project-review/application-forms | ✅ |
| Expedited Processing | https://planning.lacity.gov/project-review/expedited-processing | ✅ |
| Universal Review | https://planning.lacity.gov/project-review/universal-review | ✅ |
| Public Hearings | https://planning.lacity.gov/project-review/public-hearings | ✅ |
| Processes & Procedures | https://planning.lacity.gov/project-review/processes-procedures | ✅ |
| Urban Design Project Review | https://planning.lacity.gov/project-review/urban-design-project-review | ✅ |
| Design Review | https://planning.lacity.gov/project-review/design-review | ✅ |
| Zoning Review | https://planning.lacity.gov/project-review/zoning-review | ✅ |
| City Planning Fee Estimator | https://planning.lacity.gov/project-review/fee-estimator | ✅ |
| Online Application System (OAS) | https://planning.lacity.gov/online-application-system | ✅ |
| CEQA & Environmental Review | https://planning.lacity.gov/project-review/environmental-review | ✅ |
| Housing Services (Density Bonus, TOC, etc.) | https://planning.lacity.gov/project-review/planning-services (Housing section) | ✅ |
| Alcohol Sales (BESt — CUB/CUX) | https://planning.lacity.gov/project-review/planning-services (BESt section) | ✅ |
| Map Processing (Parcel Maps, Tract Maps) | https://planning.lacity.gov/project-review/planning-services (Map Processing) | ✅ |
| SB 9 / AB 2097 / ED1 / AB 2011 / SHRA / Adaptive Reuse | https://planning.lacity.gov/project-review/senate-bill-9 (and linked pages) | ✅ |
| Wireless Telecommunications | https://planning.lacity.gov/project-review/wireless-telecommunications | ✅ |
| City Planning Glossary | https://planning.lacity.gov/glossary | ✅ |

### 1C. BOE — Bureau of Engineering (public right-of-way improvements)

**Main entry:** https://permitmanual.engineering.lacity.gov/

The BOE Development Services Procedures Manual is a living document managed by the Permit Case Management (PCM) team. It covers 12 permit type categories, each with sub-pages for Public Information, FAQs, Permit Overview, Technical Procedures, Checklists & Sample Documents, Reference Materials, and Design Standards.

| Permit type | Hub URL | Status |
|---|---|---|
| Construction "A" Permits (minor street construction in ROW) | https://permitmanual.engineering.lacity.gov/construction-permits | ✅ |
| Excavation "E" Permits (excavation in ROW — major) | https://permitmanual.engineering.lacity.gov/excavation-e-permits | ✅ |
| Excavation "U" Permits (utility excavation) | https://permitmanual.engineering.lacity.gov/excavation-u-permits | ✅ |
| "B" Permits (private development improvements adjacent to ROW) | https://permitmanual.engineering.lacity.gov/b-permits | ✅ |
| → B Permit Purpose & Definition | https://permitmanual.engineering.lacity.gov/b-permits/permit-overview/1-b-permit-purpose-definition | ✅ |
| → B Permit General Conditions & Requirements | https://permitmanual.engineering.lacity.gov/b-permits/permit-overview/2-b-permit-general-conditions-and-requirements | ✅ |
| → B Permit Processing Procedures (4-phase: Estimate→Design→Construction→Post-Construction) | https://permitmanual.engineering.lacity.gov/b-permits/technical-procedures/b-permit-processing-procedures | ✅ |
| Above Ground Facilities (AGF) Permits | https://permitmanual.engineering.lacity.gov/above-ground-facilities-agf | ✅ |
| Revocable "R" Permits (temporary ROW use) | https://permitmanual.engineering.lacity.gov/revocable-r-permits | ✅ |
| Maintenance Hole "MH" Permits | https://permitmanual.engineering.lacity.gov/maintenance-hole-mh-permits | ✅ |
| Sewer "S" Permits (sewer connections) | https://permitmanual.engineering.lacity.gov/sewer-s-permits | ✅ |
| Storm Drain "SD" Permits | https://permitmanual.engineering.lacity.gov/storm-drain-sd-permits | ✅ |
| Watercourse "W" Permits | https://permitmanual.engineering.lacity.gov/watercourse-w-permits | ✅ |
| Building & Safety Clearances (LADBS coordination) | https://permitmanual.engineering.lacity.gov/building-safety-clearances | ✅ |
| Land Development (conditions clearance, parcel maps) | https://permitmanual.engineering.lacity.gov/land-development | ✅ |
| Bond Control | https://permitmanual.engineering.lacity.gov/bond-control | ✅ |
| List of Terms (glossary — 55+ definitions) | https://permitmanual.engineering.lacity.gov/list-terms | ✅ |

**Key structural detail:** B-Permit processing went 100% online via ProjectDox in 2019 with a 4-phase workflow:
1. **Project Estimate Phase** — application, bond estimate, deposit payment
2. **Design Phase** — plan check payment, design plan submissions per discipline
3. **Construction Phase** — inspection fees, contractor info, performance bond
4. **Post-Construction Phase** — as-builts, bond release, close-out

The glossary confirms important distinctions: **Ministerial Decision** (established procedures, no judgment call) vs. **Discretionary Decision** (requires exercise of judgment) — mirroring the Planning 3-tier framework.

### 1D. Legal Code

| Source | URL | Status |
|---|---|---|
| LAMC — current (Chapter 1 Original + Chapter 1A New Code) | https://codelibrary.amlegal.com/codes/los_angeles/latest/lamc | ✅ Live, up to ~3 month lag |
| Chapter 1A (New Zoning Code) article-by-article PDFs | https://zoning.lacity.gov/ (swap article number in URL) | ✅ |
| "Brownbook" (LAMC compilation for public works) | referenced by BOE manual, no single URL | ⚠️ |

### 1E. Zoning & Parcel Data

| Source | URL | Status |
|---|---|---|
| ZIMAS — official parcel zoning lookup | https://zimas.lacity.org/ | ✅ Live system |
| NavigateLA — parcel map + address search | https://navigatela.lacity.org/ | ✅ |
| zoning.lacity.gov — Chapter 1A interactive viewer | https://zoning.lacity.gov/ | ✅ |
| LADBS Clearance Handbook (inter-department clearance requirements) | https://dbs.lacity.gov/sites/default/files/efs/pdf/publications/clearance-handbook.pdf | ✅ |

---

## 2. Process taxonomy (replaces the 20 hand-picked process types)

⚠️ **No single official document lists "the complete taxonomy."** LA uses two separate classification systems:

### 2A. LADBS Permit Types

Sourced from https://dbs.lacity.gov/services/plan-review-permitting:

| Permit Type | Notes |
|---|---|
| Building — New | New construction |
| Building — Addition | Additions to existing structures |
| Building — Alteration/Repair | Alterations and repairs |
| Building — Demo | Demolition permits |
| Electrical | Electrical systems |
| Plumbing | Plumbing systems |
| Mechanical/HVAC | HVAC systems |
| Grading | Earthwork / grading permits |
| Fire Sprinkler | Fire suppression systems |
| Elevator / Pressure Vessel | Vertical transport / pressure systems |
| Disabled Access | ADA-related retrofits |
| ADU — Standard Plan | Approved pre-designed plans (~2-3 week path) |
| ADU — Custom Plan | Full plan check (~4-8 week path) |
| Swimming Pool / Spa | Pool construction |
| Sign | Signage permits |
| Temporary | Temporary structures/events |

### 2B. City Planning Entitlement Types

Sourced from https://planning.lacity.gov/project-review/application-forms (one form per entitlement type):

| Type | Abbreviation | Description |
|---|---|---|
| Zone Change | ZC | Map amendment (LAMC 12.32, 12.33) |
| Zone Variance | ZV | Area/setback variance (ZAA also used) |
| Zoning Administrator Adjustment | ZAA | Adjustment within existing code |
| Conditional Use Permit | CUB | Beverage/alcohol/entertainment (BESt unit) |
| Conditional Use — Other | CUX | Non-alcohol CUP |
| Transit Oriented Communities | TOC | Density bonus program |
| Density Bonus | — | State density bonus law compliance |
| Coastal Development Permit | CDP | Coastal zone compliance |
| Site Plan Review | SPR | Large project design review |
| General Plan Amendment | GPA | Amend General Plan designation |
| Preferential Parking | — | Parking permit zone establishment |
| Vesting Tentative Tract | VTT | Subdivision map — tract |
| Tentative Tract | TT | Subdivision map — tract |
| Parcel Map | PM | Subdivision map — 4 parcels or fewer |
| Vesting Tentative Parcel Map | VPM | Parcel map with vesting rights |
| Appeals | — | Appeal of planning determination |
| Specific Plan Project Permit Adjustment | SPPA | Adjustments within specific plans |
| Home-Sharing | — | Short-term rental registration |
| SB 9 Urban Lot Split | — | Two-unit housing development |
| Housing Replacement | — | Affordable housing replacement |
| Adaptive Reuse | — | Conversion of non-residential to residential |

**Important:** The form split between Chapter 1 (Original Zoning Code) and Chapter 1A (New Zoning Code) matters — since early 2025, the Downtown Community Plan Area uses Chapter 1A forms.

**Recommendation from catalog audit:** Model as two separate taxonomies (LADBS × Planning) rather than forcing into one flat list of 20, since a given project commonly needs one of each.

---

## 3. Permit number format (replaces `YY-TTT-OO-MMM-#####`)

⚠️ The structure is substantively correct but sourced from industry knowledge, not an LADBS-published document.

**Confirmed structure:** `YY-TTT-OO-MMM-#####`

| Segment | Meaning | Values |
|---|---|---|
| `YY` | 2-digit year | e.g. `24`, `25` |
| `TTT` | 3-digit application type | e.g. Bldg-New, Bldg-Addition, Electrical |
| `OO` | Branch office code | `10`-Metro, `20`-Van Nuys, `30`-West LA, `40`-San Pedro, `70`-South LA, `90`-Internet e-Permit, `91`-Facsimile |
| `MMM` | Master/Supplemental | `000` = master permit, `001`+ = supplemental |
| `#####` | Sequence number | Sequential per year/office/type |

**Best path to authoritative confirmation:** Pull a sample of real permit numbers from https://data.lacity.org (LADBS Building Permits dataset) and reverse-validate against `permit_type`, `apc` (branch office), and `status` fields.

**Planning case number format:** `PREFIX-YEAR-SEQ#-SUFFIX(es)` (e.g., `ZA-2024-003812-CUB`). These are documented per case type on the Planning application forms page.

---

## 4. Inspection codes (e.g. "010," "020," "030")

❌ **Gap.** No single published LADBS document enumerates inspection codes.

**Best available sources:**
- https://data.lacity.org — LADBS Inspections-By-Permit-Status dataset — the column dictionary documents inspection-type codes as they exist in PCIS
- https://dbs.lacity.gov/forms-and-publications?cats=26 — Inspection Forms sub-tab — individual bulletins reference specific codes in context
- Third-party compiled lists (e.g., https://www.laconstructioncompliance.com/ladbs-glossary/) — useful but not authoritative

**Recommendation:** Derive from the open-data schema rather than from a procedure manual.

---

## 5. Case/permit status lifecycle and valid transitions

❌ **Gap.** No official LADBS document enumerates the full PCIS status set with valid transitions.

**Best available sources:**
- https://data.lacity.org — permit datasets expose actual status values used in production
- LADBS Permit Status page (https://dbs.lacity.gov/services/permit-status) — high-level explanation
- Third-party status glossaries (e.g., https://www.laconstructioncompliance.com/ladbs-glossary/) — list status *names* but aren't primary sources

**Recommendation:** Either (a) reverse-engineer transition rules from bulk historical permit data on data.lacity.org, or (b) pursue a records request / direct conversation with LADBS IT about PCIS workflow rules.

---

## 6. Zoning data (replaces strings like `R1-1-HCR`)

✅ **Confirmed live tools:**

| Source | URL | Notes |
|---|---|---|
| ZIMAS — official parcel zoning lookup | https://zimas.lacity.org/ | The actual system; shows which code applies (Ch 1 vs Ch 1A) |
| NavigateLA — parcel map + address search | https://navigatela.lacity.org/ | |
| zoning.lacity.gov — Chapter 1A (New Zoning Code) viewer | https://zoning.lacity.gov/ | Interactive, article-by-article PDFs available |
| LAMC Chapter 1A PDFs | https://zoning.lacity.gov/ (article_XX.pdf pattern) | |

**Important nuance:** LA is mid-transition between the **Original Zoning Code** (Chapter 1 — letter-number zones like `R1-1-HCR`) and the **New Zoning Code** (Chapter 1A — recodified by form/use/density), rolling out community-plan-area by community-plan-area starting with Downtown in early 2025. ZIMAS indicates which code applies to a given parcel.

---

## 7. LAMC citations (replaces strings like "LAMC 12.24")

✅ **Live, authoritative, and directly linkable:**

| Source | URL | Notes |
|---|---|---|
| LAMC — current (both chapters) | https://codelibrary.amlegal.com/codes/los_angeles/latest/lamc | ~3 month lag after legislation |
| LAMC §12.24 | https://codelibrary.amlegal.com/codes/los_angeles/latest/lamc/0-0-0-107363 | Correct section for CUP in Ch 1 |
| LAMC §13B.2.1–13B.2.3 | https://codelibrary.amlegal.com/codes/los_angeles/latest/lamc | Corresponding Ch 1A sections |

**Important:** Verify whether the parcel's community plan area uses Chapter 1 or Chapter 1A before citing a section. Link directly to the amlegal section rather than just naming it.

---

## 8. Conditions of approval (currently generic placeholder text)

✅ **Real templates exist, organized per entitlement type:**

| Source | URL | Notes |
|---|---|---|
| Application forms per entitlement type | https://planning.lacity.gov/project-review/application-forms | Each form package includes required findings language (e.g., CP-7810 for CUP) |
| BESt unit (alcohol/entertainment CUB/CUX) | https://planning.lacity.gov/project-review/planning-services (BESt section) | Entitlement-specific condition sets |
| Housing Services (Density Bonus/TOC) | https://planning.lacity.gov/project-review/planning-services (Housing section) | |
| Public Letters of Determination | `planning.lacity.gov/odocument/...` (searchable by case number) | Actual case-specific conditions |
| Commission/Hearing packets | `planning.lacity.gov/plndoc/Staff_Reports/...` | |

**Recommendation:** Source from the application-form "findings" language (per entitlement type) rather than writing generic placeholders.

---

## 9. Applicant names

❌ **Out of scope for direct sourcing** (privacy), but noting for completeness:
- Real applicant/owner names appear in public LADBS and Planning datasets on https://data.lacity.org
- Permit and entitlement applications are public records in California
- Pulling from those datasets needs its own privacy/anonymization review

---

## 10. LADOT — Driveway, Access & Circulation

LADOT reviews driveway designs, access management, and on-site circulation for projects requiring new driveways on arterial/collector streets, 25+ parking spaces, or drive-through operations.

| Source | URL | Status |
|---|---|---|
| Driveway, Access, Circulation Design Guidelines (Section 321, March 2024) — 25 pages | `permit_documentations/driveway-design-guide-march-2024.pdf` | ✅ |
| LADOT website | https://ladot.lacity.gov/ | ✅ |
| LADOT B-Permits Section (street improvements, signals) | Contact via BOE permit manual | ⚠️ Part of BOE process |
| LADOT Parking Meters Division | (213) 473-8270 | ✅ |
| Mobility Plan 2035 (policy foundation for driveway reviews) | https://planning.lacity.gov/plans-policies/mobility-plan-2035 | ✅ |
| Complete Streets Design Guide (driveway placement §6.9) | https://ladot.lacity.gov/complete-streets | ✅ |

**Document structure (Driveway Design Guide Section 321, March 2024, 25 pp.):**

| Section | Pages |
|---|---|
| I. Purpose | 1 |
| II. Policy Framework & Conditions of Land Use Entitlement | 1–2 |
| III. Code Requirements (LAMC sections enforced) | 2 |
| IV. Definitions | 3 |
| V. Driveway Location and Operation Planning | 3–10 |
|  A. Number of Driveways | 3–4 |
|  B. Channelization | 4 |
|  C. Intersection Adjacency (150 ft arterial, 75 ft collector/local) | 5 |
|  D. Bus Stop Zone Avoidance | 5 |
|  E. Turning Restrictions | 5–6 |
|  F. "T" Intersections (BOE Standard Plan S-440-45 Cases 3/4) | 7 |
|  G. One-Way Driveways | 8 |
|  H. Near Mid-Block Crosswalks | 8 |
|  I. Right Turn Only Lane (RTOL) | 9 |
|  J. Spacing (20 ft min between driveways, 50 ft preferred for two-way) | 9–10 |
| VI. Driveway Design | 11–18 |
|  A. Basic Principles | 11 |
|  B. Width of Driveways (recommended width table) | 11–13 |
|  C. Street-Type Driveways | 13 |
|  D. Turning Movement Path Evaluation for Large Vehicles/Trucks | 13 |
|  E. Queuing Capacity (table on p. 14) | 14–15 |
|  F. Drive-Through Service | 15 |
|  G. Driveway Access on High Injury Network (HIN) | 15 |
|  H. Parking Meter Removal | 15 |
|  I. Merging Drive Isles | 16 |
|  J. Narrow Internal Drive Aisle along Arterial Street | 17 |
|  K. Existing Driveways for Demolished Structures | 17 |
|  L. Pick-Up and Drop-Off Zones | 18 |
|  M. Abandoned Driveway | 18 |
|  N. Maneuvering Space | 18 |
|  O. Circular Driveways | 18 |
|  P. Community Plan Implementation Overlay (CPIO) | 18 |
| VII. Internal Circulation | 18–19 |
| VIII. Loading Docks | 19 |
| Appendix A — LAMC §12.21 excerpts (A-4(g), A-5(e), A-5(i), A-5(j), C-6(a)) | 20–21 |
| Appendix B — LAMC §62.105 excerpts (62.105.1–62.105.5) | 22–24 |
| Appendix C — Sample Site Plan | 25 |

**Key LAMC sections enforced by LADOT for driveway/access:**

| Section | Subject | Guide page |
|---|---|---|
| LAMC 12.21 A-4(g) | Location of Parking Area (within 750 ft) | p. 2 (III), full text in Appendix A p. 20 |
| LAMC 12.21 A-5(e) | Driveway Location (per LADOT-approved plan for 25+ spaces or P/PB zones) | p. 2 (III), full text in Appendix A p. 20 |
| LAMC 12.21 A-5(i) | Parking Stall Location (no backing onto street/sidewalk) | p. 2 (III), full text in Appendix A pp. 20–21 |
| LAMC 12.21 A-5(j) | Internal Circulation (no street use for lot-to-lot access) | p. 2 (III), full text in Appendix A p. 20 |
| LAMC 12.21 C-6(a) | Loading Space requirements | p. 2 (III), full text in Appendix A pp. 20–21 |
| LAMC 62.105.1 | Locations of Driveway Approaches | p. 2 (III), full text in Appendix B p. 22 |
| LAMC 62.105.2 | Width of Driveway Approach Apron (10 ft min RS, 12 ft min C/M, 30 ft max) | p. 2 (III), full text in Appendix B pp. 22–23 |
| LAMC 62.105.3 | Length of Curb Space (20 ft min between driveways, half-frontage for ≤40 ft lots) | p. 2 (III), full text in Appendix B pp. 23–24 |
| LAMC 62.105.5 | Deviations — Board of Public Works approval required | p. 2 (III), full text in Appendix B p. 24 |

**Driveway width standards** — Section VI.B, pp. 11–13:

| Development type | Non-arterial 2-lane | Non-arterial 1-lane | Arterial 2-lane | Arterial 1-lane |
|---|---|---|---|---|
| Commercial / Multi-family (25+ spaces) | 20–24 ft | 10–12 ft | 24–30 ft | 12–14 ft |
| Commercial / Multi-family (5–25 spaces) | 19–22 ft | 10–12 ft | 19–28 ft | 12–14 ft |
| Commercial / Multi-family (<5 spaces) | 18–20 ft | 10–12 ft | 19–24 ft | 12–14 ft |
| Single-family residential (1–2 car garage) | 18–20 ft | 9–12 ft | 19–24 ft | 12–14 ft |
| Single-family residential (3+ car garage) | 18–20 ft | 9–12 ft | 19–24 ft | 12–14 ft |

**Minimum queuing capacity** — Section VI.E, p. 14:

| Total parking spaces | Minimum queuing capacity |
|---|---|
| Up to 100 | 20 ft |
| 101 to 300 | 40 ft |
| More than 300 | 60 ft |

(p. 14 also notes: for 300+ spaces, additional queuing analysis based on "traffic intensity" methodology required.)

**Key BOE standard plan referenced:** S-440-45 — driveway case designs at T-intersections — Section V.F, p. 7.

---

## 11. Open Data Portal (cross-cutting)

All LA City public datasets relevant to permits, planning, and inspections:

| Dataset | URL | Use |
|---|---|---|
| LADBS Building Permits | https://data.lacity.org (search "Building Permits") | Permit numbers, statuses, valuations, applicant types, branch offices |
| LADBS Inspections-By-Permit-Status | https://data.lacity.org (search "Inspections-By-Permit-Status") | Inspection codes, results, schedule |
| Planning Case Files | https://data.lacity.org (search "Planning") | Entitlement case data |
| LADBS Code Enforcement | https://data.lacity.org (search "Code Enforcement") | Violation cases |

---

## 12. BOE Manual — Internal Page Structure Reference

The BOE manual at https://permitmanual.engineering.lacity.gov/ follows this section pattern per permit type:

```
{permit-type}/
├── (home page — Public Information, FAQs, etc.)
├── {permit-type}/permit-overview/
│   ├── 1-{slug}-purpose-definition
│   ├── 2-{slug}-general-conditions-and-requirements
│   └── ...
├── {permit-type}/technical-procedures/
│   ├── {slug}-processing-procedures
│   └── ...
├── {permit-type}/checklists-and-sample-documents/
├── {permit-type}/reference-foundational-materials/
├── {permit-type}/design-standards/
└── {permit-type}/other-city-dept-or-outside-agency-references/
```

**Confirmed URL patterns:**

| URL Pattern | Example |
|---|---|
| `/{slug}` | `/b-permits`, `/construction-permits`, `/excavation-e-permits` |
| `/{slug}/permit-overview/{n}-{topic}` | `/b-permits/permit-overview/1-b-permit-purpose-definition` |
| `/{slug}/technical-procedures/{topic}` | `/b-permits/technical-procedures/b-permit-processing-procedures` |
| `/list-terms` | glossary (single page) |

**Slug patterns discovered:**

| Permits | Slug path |
|---|---|
| Construction "A" | `/construction-permits` |
| Excavation "E" | `/excavation-e-permits` |
| Excavation "U" | `/excavation-u-permits` |
| "B" Permits | `/b-permits` |
| Above Ground Facilities (AGF) | `/above-ground-facilities-agf` |
| Revocable "R" | `/revocable-r-permits` |
| Maintenance Hole "MH" | `/maintenance-hole-mh-permits` |
| Sewer "S" | `/sewer-s-permits` |
| Storm Drain "SD" | `/storm-drain-sd-permits` |
| Watercourse "W" | `/watercourse-w-permits` |
| Building & Safety Clearances | `/building-safety-clearances` |
| Land Development | `/land-development` |
| Bond Control | `/bond-control` |
| Other BOE Permits/Processes | (URL not found — searchable via filter) |

---

## Summary: what's solid vs. what still needs a decision

| Category | Status | Key sources |
|---|---|---|
| **LADBS process & permitting** | ✅ Solid | dbs.lacity.gov hub + sub-pages + Clearance Handbook |
| **Planning entitlements & approvals** | ✅ Solid | planning.lacity.gov/project-review/* pages |
| **BOE ROW improvements** | ✅ Solid | permitmanual.engineering.lacity.gov (12 permit type hubs) |
| **LAMC citations** | ✅ Solid | codelibrary.amlegal.com/codes/los_angeles |
| **Zoning data** | ✅ Solid | ZIMAS + zoning.lacity.gov + NavigateLA |
| **Conditions of approval** | ✅ Solid | Per-entitlement-type forms on planning.lacity.gov |
| **Permit number format** | ⚠️ Needs data validation | Reverse-validate against data.lacity.org schema |
| **Inspection codes** | ❌ Gap | data.lacity.org schema is best proxy |
| **Status lifecycle transitions** | ❌ Gap | data.lacity.org schema + bulk analysis needed |
| **Applicant names** | ❌ Privacy-scoped | Public record but needs anonymization review |

**Needs compilation work:** Turning the Information Bulletins library and the Chapter 1 vs Chapter 1A form split into 135 discrete workflow steps — the catalog confirms this is real manual work, not something a single document solves.

**Genuine gaps:** Inspection codes and status transitions are realistically PCIS-internal. The data.lacity.org schema is the best public substitute.
