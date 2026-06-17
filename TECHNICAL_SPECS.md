# LAPOC Technical Specifications

> **Project:** LA City Planning One-Stop-Shop
> **Stack:** Python FastAPI + SQLite · React 18 + TypeScript + Vite · Azure OpenAI · Azure Speech
> **Status:** Proof-of-concept v0.1.0

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Data Model](#2-data-model)
3. [Backend Architecture](#3-backend-architecture)
4. [Agent System](#4-agent-system)
5. [Frontend Architecture](#5-frontend-architecture)
6. [External Integrations](#6-external-integrations)
7. [Structured Text Protocol](#7-structured-text-protocol)
8. [CI/CD Pipeline](#8-cicd-pipeline)
9. [Configuration Reference](#9-configuration-reference)

---

## 1. System Overview

### 1.1 Purpose

LAPOC is an agentic chatbot that provides LA City planning and permit information to three user personas: homeowners/residents, real estate developers, and licensed contractors. It answers questions about parcel details, permit case status, process workflows, and ADU eligibility using a combination of a synthetic SQLite database and live external APIs.

### 1.2 High-Level Architecture

```
┌──────────────┐     HTTP/JSON      ┌──────────────────┐     Azure OpenAI API
│  React SPA   │ ──────────────────→ │  FastAPI Server  │ ──────────────────→
│  (Vite build)│ ←────────────────── │  (Uvicorn)       │ ←──────────────────
│  port 5173   │   proxy /chat       │  port 8000       │   gpt-4o tool-calling
└──────────────┘                     └──────────────────┘
       │                                    │
       │ Azure Speech SDK                    │ SQLAlchemy ORM
       │ (STT + TTS)                         ▼
       │                              ┌──────────────┐
       └───────────────────────────── │   SQLite DB   │
                                     │  (lapoc.db)   │
                                     └──────────────┘
                                              │
                                     ┌───────┴────────┐
                                     │  External APIs  │
                                     │  BOE GeoQuery   │
                                     │  ZIMAS ArcGIS   │
                                     └────────────────┘
```

### 1.3 Request Flow

1. User sends message via `POST /chat`
2. `run_agent()` in `agent.py` prepends the appropriate persona system prompt (Jinja2-rendered)
3. Agent loop iterates up to 6 times:
   a. Call Azure OpenAI `chat.completions.create()` with `tools` (function schemas) and `tool_choice: "auto"`
   b. If the response contains `tool_calls`, dispatch each to the corresponding tool function in `tools.py`
   c. Append tool results as `role: "tool"` messages to the conversation
   d. If no tool calls, extract the final text reply
4. On first user query, a second LLM call generates 4 contextual suggestions
5. A third LLM call generates a condensed 1-2 sentence spoken version (speech keynotes)
6. Response returned as JSON with `reply`, `speech_text`, `tool_calls_made`, `detected_persona`, `suggestions`

---

## 2. Data Model

### 2.1 Entity Relationship

```
Plot (parcels)     1────N    Case
   │                          │
   │                          │ process_type
   └──────────────────────────┘
                               │
                    WorkflowStep (process_type)
                               │
                    WorkflowPersona (process_type + step_name + persona)
```

### 2.2 Tables

#### `plots` — Parcel/property records

| Column | Type | Description |
|---|---|---|
| `apn` | TEXT PK | Assessor Parcel Number (`XXXX-XXX-XXX`) |
| `address` | TEXT NOT NULL | Street address |
| `neighborhood` | TEXT | Neighborhood name |
| `zoning` | TEXT | Zoning code (e.g. `R1-1-HCR`) |
| `lot_size_sqft` | INTEGER | Lot size in square feet |
| `current_use` | TEXT | Current use description |
| `zoning_overlays` | TEXT | JSON array of overlay labels |
| `toc_tier` | TEXT | Transit Oriented Communities tier (`Tier 1`–`Tier 4`) |
| `general_plan_land_use` | TEXT | General Plan land use category |
| `sb9_eligible` | TEXT | `Yes`/`No`/`Review Eligibility` |
| `sb35_eligible` | TEXT | Senate Bill 35 eligibility |
| `ab2097_eligible` | TEXT | `Yes`/`No` |
| `hpoz_hcm` | TEXT | Historic Preservation Overlay Zone status |
| `flood_zone` | TEXT | FEMA flood zone designation |
| `fire_hazard_severity` | TEXT | Fire hazard severity |
| `hillside_area` | TEXT | `Yes`/`No` |
| `adaptive_reuse` | TEXT | Adaptive reuse program eligibility |
| `council_district` | TEXT | LA City Council district |
| `community_plan_area` | TEXT | Community plan area name |
| `ladbs_district_office` | TEXT | LADBS district office (Metro, West LA, South LA) |

#### `cases` — Permit and planning cases

| Column | Type | Description |
|---|---|---|
| `case_id` | TEXT PK | LADBS or City Planning case ID |
| `apn` | TEXT FK → plots.apn | Associated parcel |
| `department` | TEXT NOT NULL | `LADBS` or `City Planning` |
| `process_type` | TEXT NOT NULL | e.g. `ADU`, `CUB`, `Bldg-New`, `Grading` |
| `applicant_type` | TEXT | `resident`/`developer`/`contractor` |
| `applicant_name` | TEXT | Applicant or company name |
| `submitted_date` | TEXT | ISO date of submission |
| `current_status` | TEXT | Current case status |
| `assigned_to` | TEXT | Staff assignee |
| `description` | TEXT | Case description |
| `fees_paid` | FLOAT | Fees paid to date |
| `fees_outstanding` | FLOAT | Outstanding fees |
| `hearing_date` | TEXT | Scheduled hearing date |
| `next_action` | TEXT | Next required action |
| `portal_url` | TEXT | LADBS or City Planning portal URL |
| `valuation` | FLOAT | Project dollar valuation |
| `pc_job_number` | TEXT | Plan check job number (e.g. `B-24-10-88441`) |
| `plan_type` | TEXT | ADU: `standard_plan` or `custom` |
| `conditions_of_approval` | TEXT | JSON array of condition strings |

#### `workflow_steps` — Process workflow steps

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER PK auto | Auto-increment ID |
| `process_type` | TEXT NOT NULL | Process type identifier |
| `step_order` | INTEGER NOT NULL | 1-based step ordering |
| `step_name` | TEXT NOT NULL | Step name |
| `description` | TEXT | Step description |
| `responsible_party` | TEXT | `Applicant`/`LADBS`/`City Planning`/`LADOT` |
| `typical_days` | TEXT | Duration string (e.g. `5-14` or `30-90`) |

#### `workflow_personas` — Persona-specific step guidance

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER PK auto | Auto-increment ID |
| `process_type` | TEXT NOT NULL | Process type identifier |
| `step_name` | TEXT NOT NULL | Step name (matches workflow_steps) |
| `persona` | TEXT NOT NULL | `resident`/`developer`/`contractor` |
| `guidance` | TEXT | Plain-language guidance text |

### 2.3 Status Values

Common case statuses across the data model:

| Status | Meaning |
|---|---|
| `Submitted` | Application received, not yet assigned |
| `PC Assigned` | Plan check engineer assigned |
| `Completeness Review` | City Planning verifying documents |
| `Corrections Needed` | Plan check correction letter issued |
| `Recheck` | Resubmitted plans under re-review |
| `PC on Hold` | Blocked by external review (geology, LAFD, etc.) |
| `PC Approved` | Plans approved, fees due |
| `Ready to Issue` | Issuance fees paid, permit ready |
| `Issued` | Permit active |
| `Fees Due` | Outstanding balance |
| `Permit Finaled` | All inspections passed |
| `CofO Issued` | Certificate of Occupancy issued |
| `LOD Issued` | Letter of Determination issued (entitlement) |
| `Conditions Clearance` | LOD conditions being cleared |
| `Pending Hearing` | Public hearing scheduled |
| `Appeal Pending` | Decision under appeal |
| `Intent to Revoke` | Violation notice |
| `PC Expired` | Plan check lapsed with no action |
| `Map Recorded` | Parcel map recorded at County Recorder |

---

## 3. Backend Architecture

### 3.1 File Layout

```
backend/
├── main.py                     FastAPI entry point
├── database.py                 SQLAlchemy engine + session factory
├── models.py                   ORM model definitions
├── schemas.py                  Pydantic v2 schemas
├── requirements.txt            Python dependencies
├── routers/
│   ├── plots.py                Parcel endpoints
│   ├── cases.py                Case endpoints
│   ├── chat.py                 Chat endpoint (agent entry)
│   └── token.py                Azure Speech STS token proxy
├── agent/
│   ├── __init__.py
│   ├── agent.py                OpenAI function-calling loop
│   ├── tools.py                Agent tool implementations
│   └── prompts/
│       └── system_prompts.jinja  Jinja2 persona prompts
├── seed/
│   ├── seed_data.py             Synthetic data seeder
│   └── seed_cases.md            Case ID reference
└── static/
    ├── lacity-banner.mp4        Footer background video
    └── baah.mp3                 Mascot sound effect
```

### 3.2 Dependencies (`requirements.txt`)

| Package | Version | Purpose |
|---|---|---|
| `fastapi` | 0.115.0 | API framework |
| `uvicorn[standard]` | 0.30.6 | ASGI server |
| `sqlalchemy` | 2.0.35 | ORM |
| `pydantic` | 2.9.2 | Request/response validation |
| `openai` | 1.57.0 | Azure OpenAI SDK |
| `python-dotenv` | 1.0.1 | Environment variable loading |
| `httpx` | 0.27.0 | HTTP client for external APIs |
| `Jinja2` | 3.1.5 | System prompt template engine |

### 3.3 API Endpoints

| Method | Path | Description | Response Model |
|---|---|---|---|
| `GET` | `/health` | Health check | `{"status": "ok"}` |
| `POST` | `/chat` | Main agent endpoint | `ChatResponse` |
| `GET` | `/plots/{apn}` | Parcel by APN | `ParcelResult` |
| `GET` | `/plots/search/address` | Parcel by address | `list[ParcelResult]` |
| `GET` | `/cases/random` | Random case ID | `{"case_id": string}` |
| `GET` | `/cases/{case_id}` | Case detail | `CaseOut` |
| `GET` | `/speech-token` | Azure Speech STS | `{"token": string, "region": string}` |
| `GET` | `/static/*` | Static files | File |

### 3.4 Key Implementation Details

**`main.py`:**
- `load_dotenv()` at line 3, called before any other imports to ensure env vars are available
- `Base.metadata.create_all(bind=engine)` creates tables on startup
- CORS configured for `localhost:5173`, `localhost:3000`, and the Azure Static Web Apps domain
- Routers included: plots, cases, chat, token
- Static files mounted at `/static`

**`database.py`:**
- Single SQLite file `lapoc.db` relative to CWD
- `check_same_thread=False` because FastAPI uses multiple threads
- `get_db()` dependency yields a session per request, closed in `finally`

**`chat.py`:**
- Detects first user query via `is_first_query` flag (exactly 1 user message)
- Calls `generate_suggestions()` on first query only
- Calls `generate_speech_keynotes()` on every response for TTS
- Returns `ChatResponse` with suggestions and speech text

---

## 4. Agent System

### 4.1 Agent Loop (`run_agent`)

```
┌─────────────────────────────────────┐
│  Start with system_prompt + messages │
└────────────┬────────────────────────┘
             ▼
┌─────────────────────────────────────┐
│  Call OpenAI chat.completions.create │
│  with tools (function schemas)       │
└────────────┬────────────────────────┘
             ▼
      ┌──────┴──────┐
      │ tool_calls  │
      │   present?  │
      └──────┬──────┘
         NO  │  YES
         ▼   ▼
┌────────────────┐  ┌──────────────────────────────┐
│ Extract reply  │  │ For each tool_call:            │
│ Check persona  │  │  json.loads(arguments)         │
│ tag [PERSONA:] │  │  _dispatch_tool(name, args,db) │
│ Return         │  │  Append tool result to conv    │
└────────────────┘  └──────────────┬───────────────┘
                                   │ loop (max 6)
                                   ▼
                          ┌────────────────────┐
                          │ Continue iteration  │
                          └────────────────────┘
```

### 4.2 Persona Detection

When persona is `"auto"`, the LLM is instructed to append a `[PERSONA:resident|developer|contractor]` tag to its first reply. The `_extract_persona_tag()` function in `agent.py` parses this tag, strips it from the response text, and returns the detected persona. The tag is only included on the first response.

### 4.3 Tool Definitions (OpenAI Function Schemas)

All five tool schemas are defined in `TOOLS` list in `agent.py` (lines 29-150). Each includes:
- `name` — snake_case function name
- `description` — detailed description for LLM reasoning
- `parameters` — JSON Schema with required fields and descriptions

### 4.4 Tool Dispatch (`_dispatch_tool`)

Simple if/elif chain routing tool name to the corresponding function in `tools.py`. All tools return plain text strings. Tool functions are synchronous — the agent loop runs them sequentially.

### 4.5 Tool Implementations

| Tool | DB Queries | External API | Key Logic |
|---|---|---|---|
| `lookup_parcel` | Plots + Cases by APN or address LIKE | — | `_find_plot()` handles exact APN match, partial address, and disambiguation for multiple matches |
| `get_case_detail` | Single Case by case_id | — | Returns structured fields with null-safe formatting |
| `get_workflow` | WorkflowSteps + WorkflowPersona by process_type | — | Bundles steps with persona-specific guidance; falls back to `resident` if no persona rows exist |
| `lookup_address` | — | BOE GeoQuery API | Calls `api.lacity.org` with hardcoded API key; parses jurisdictional layers; appends `MAP:` block |
| `check_adu_eligibility` | Plot lookup, then `_plot_to_adu_fields` | ZIMAS ArcGIS API (fallback) | Evaluates 6 criteria (zoning, HPOZ, flood, fire, hillside, coastal); returns eligibility verdict |

### 4.6 Speech Keynotes (`generate_speech_keynotes`)

A separate LLM call that condenses the agent's reply into a natural spoken paragraph (1-2 sentences, max 40 words). Falls back to regex processing: strip sentinel blocks, remove markdown formatting, return first two sentences.

### 4.7 Suggestion Generation (`generate_suggestions`)

On first user query only, a second LLM call generates 4-5 context-aware follow-up questions. Uses a Jinja2 `suggest` block as the prompt. Falls back to keyed default suggestions based on keyword matching (`"case"` → case defaults, `"workflow"` → workflow defaults, else → lookup defaults).

---

## 5. Frontend Architecture

### 5.1 File Layout

```
frontend/src/
├── App.tsx                           Router: single route `/`
├── main.tsx                          ReactDOM entry, BrowserRouter
├── vite-env.d.ts
├── pages/
│   └── Chat.tsx                      Main chat page (state management, API, suggestions)
├── components/
│   ├── ChatWindow.tsx                Message list, text input, mic, card rendering
│   ├── ChatWindow.module.css
│   ├── ChatMascot.tsx                3D ram mascot (Three.js + GLB)
│   ├── ChatMascot.module.css
│   ├── ParcelCard.tsx                PARCEL block → visual property card
│   ├── ParcelCard.module.css
│   ├── CaseDetailCard.tsx            CASE DETAIL block → case status card
│   ├── CaseDetailCard.module.css
│   ├── WorkflowTimeline.tsx          WORKFLOW block → step timeline
│   ├── WorkflowTimeline.module.css
│   ├── MapCard.tsx                   MAP block → Leaflet map
│   ├── MapCard.module.css
│   ├── CaseStatusBadge.tsx           Inline status pills
│   └── CaseStatusBadge.module.css
├── hooks/
│   ├── useSpeechRecognizer.ts        Azure Speech-to-Text
│   ├── useSpeechSynthesizer.ts       Azure Text-to-Speech + caching
│   ├── useSpeechToken.ts             Token refresh (9 min interval)
│   └── useVisemeScheduler.ts         Viseme timing queue
├── utils/
│   └── audioCache.ts                 IndexedDB audio cache
├── types/
│   └── speech.ts                     Type definitions
├── styles/
│   └── global.css                    LA City global reset
└── assets/
    └── ram.glb                       3D mascot model
```

### 5.2 Component Tree

```
<App>
  └── <BrowserRouter>
       └── <Chat>  (pages/Chat.tsx)
            ├── Header (lacity.gov-style)
            ├── Error banner (conditional)
            ├── <ChatMascot>        (3D ram, viseme-driven)
            ├── Suggestions chips   (pre-defined list, 5 random)
            └── <ChatWindow>        (message area + input)
                 ├── Message bubbles (user + assistant)
                 │    ├── <AssistantContent>
                 │    │    ├── Markdown text
                 │    │    ├── <ParcelCard>         (conditional)
                 │    │    ├── <CaseDetailCard>     (conditional)
                 │    │    ├── <WorkflowTimeline>   (conditional)
                 │    │    ├── <MapCard>            (conditional)
                 │    │    ├── <CaseStatusBadge>    (conditional)
                 │    │    └── Replay button        (conditional)
                 │    └── <UserContent>
                 │         └── Markdown text
                 ├── Dynamic suggestion chips (LLM-generated)
                 ├── Typing indicator (loading)
                 └── Voice input area (mic + text input)
```

### 5.3 State Flow

```
Chat.tsx (pages)
─────────────────────────────────────────────────────────
  messages: Message[]            ← conversation history
  loading: boolean               ← API call in progress
  detectedPersona: string|null   ← auto-detected role
  serverError: string|null       ← error banner text
  suggestions: string[]          ← LLM-generated follow-ups
  visibleSuggestions: Suggestion[] ← random pre-defined suggestions
  conversationState:             ← idle|listening|thinking|synthesizing|speaking
  
  Speech hooks:
    useSpeechToken()             → token, region
    useSpeechRecognizer()        → isListening, startListening, mute, unmute
    useSpeechSynthesizer()       → speak, isSynthesizing, isSpeaking, stop
    useVisemeScheduler()         → scheduleViseme, currentVisemeId, clearQueue
```

### 5.4 Message Flow

1. User types text (or speaks via voice recognition)
2. `sendMessage()` or `handleVoiceResult()` is called
3. Appends user message to `messages` state
4. Calls `sendToApi()` which:
   - Sets `loading=true`, dispatches `'thinking'` state
   - POSTs to `/chat` with `{persona: "auto", messages}`
   - 30-second timeout via `AbortController`
   - On success: appends assistant response, updates persona/suggestions
   - On failure: sets `serverError` for error banner
5. `ChatWindow` re-renders with new messages
6. Scrolls to bottom if user is at bottom

### 5.5 Card Parsing

Each card component exports a `parseXxxText()` function that takes raw LLM reply text and returns structured data or `null`. The `useCardData` memo hook in `ChatWindow.tsx` runs all parsers simultaneously on each assistant message. Cards render below the prose text bubble.

### 5.6 CSS Modules

Every component uses CSS Modules (`*.module.css`). The `global.css` file provides the LA City brand reset: `Montserrat` (headings), `Open Sans` (body), LA navy `#1c2253`, link blue `#000db5`.

### 5.7 Speech Features

**Speech token refresh:** `/speech-token` fetched on mount and every 9 minutes via `useSpeechToken.ts`.

**Speech-to-text (STT):** Azure Speech SDK continuous recognition via `useSpeechRecognizer.ts`. 10-second connection timeout with auto-retry. Mute state supported.

**Text-to-speech (TTS):** Azure Speech SDK via `useSpeechSynthesizer.ts`. Uses `DragonHDLatestNeural` voice (Aria). MP3 output for universal browser support. Three-layer caching: in-memory Map → IndexedDB (via `audioCache.ts`) → synthesis fallback. Viseme events drive the mascot's jaw animation.

**Viseme scheduler:** `useVisemeScheduler.ts` maintains a queue of `(visemeId, offsetMs)` events, sorted by offset. Uses `requestAnimationFrame` to update the current viseme ID, which the mascot's jaw bone rotates to match.

### 5.8 Mascot (`ChatMascot.tsx`)

- Loads `ram.glb` (CC0 3D model) via Three.js `useGLTF`
- Traverses scene to find jaw/bone for viseme-driven lip-sync
- On GLB load failure: `ProceduralMascot` fallback (sphere-based geometric ram)
- GlbErrorBoundary catches 3D load errors gracefully
- `useFrame` animation varies by conversation state:
  - `idle`: slow Y rotation
  - `listening`: Y rotation + gentle vertical bob
  - `thinking`: slower rotation + deeper bob
  - `speaking`: rapid vertical bob + jaw rotation via viseme ID
- Click plays `/baah.mp3`

---

## 6. External Integrations

### 6.1 LA City BOE GeoQuery API

**Endpoint:** `https://api.lacity.org/boe_geoquery/addressvalidationservice`
**Authentication:** API key (`B5thBZ3BXlR1waoUvderfnrMETLwk2SE`) passed as query parameter
**Used by:** `lookup_address()` tool

**Parameters:**
- `address` — Street address string
- `status` — Always `"new"`
- `layerset` — Always `"neighborhoodinfo"`
- `apikey` — Hardcoded key

**Returns:**
- Standardized address + ZIP + APN
- Coordinates (lat/lng) for map
- Jurisdictional layers: council district, area planning commission, police division, neighborhood council, community plan area, fire station, LAUSD cluster, county supervisor, state senate, state assembly, US congress
- LADBS permit and code enforcement URLs

**Error handling:** Returns prose error message on timeout or non-exact-match. Status check: `data.status === "exactMatch"`.

### 6.2 ZIMAS ArcGIS API

**Endpoint 1:** `https://zimas.lacity.org/arcgis/rest/services/zm4/landbase/MapServer/dynamicLayer/query`
**Endpoint 2:** `https://zimas.lacity.org/zm4WS/GetProjectData`
**Authentication:** None (public API)
**Used by:** `check_adu_eligibility()` as fallback when parcel not in SQLite

**Flow:**
1. Parse address into house number, direction, street (with abbreviation normalization)
2. Query ArcGIS dynamic layer `zim4s.search_addressparts` to get PIN
3. Fetch ProjectData JSON using PIN
4. Extract ADU-relevant fields: zoning, HPOZ, flood zone, fire hazard, hillside, coastal zone
5. Format into ADU ELIGIBILITY CHECK block

**Key detail:** The `_parse_address_parts()` function normalizes street suffixes (DRIVE→DR, STREET→ST, etc.) to match ArcGIS data format.

### 6.3 Azure OpenAI

**SDK:** `openai` Python package `>=1.57.0`
**Client:** `AsyncAzureOpenAI` (not standard OpenAI)
**Model:** `gpt-4o` (default, configurable via `AZURE_OPENAI_DEPLOYMENT`)
**API Version:** `2024-12-01-preview`
**Authentication:** API key

**Three LLM calls per request:**
1. Main agent loop (up to 6 iterations with tool calls)
2. Suggestion generation (first query only)
3. Speech keynotes (every response)

### 6.4 Azure Speech Services

**SDK:** `microsoft-cognitiveservices-speech-sdk` (frontend, v1.50.0)
**Authentication:** STS token via `/speech-token` endpoint (proxied to Azure)
**Endpoint:** `AZURE_SPEECH_ENDPOINT` → STS at `{endpoint}/sts/v1.0/issueToken`
**Voice:** `en-US-Aria:DragonHDLatestNeural`

**Frontend services:**
- **STT:** Continuous recognition, 10s connection timeout, auto-retry, mute support
- **TTS:** SSML-based synthesis, MP3 output, viseme events, 3-level audio caching

---

## 7. Structured Text Protocol

### 7.1 Protocol Overview

Agent tools return plain text with sentinel-prefixed blocks. The LLM passes these blocks through verbatim (per system prompt instruction). The frontend strips sentinel blocks from the prose bubble and renders them as visual cards.

### 7.2 Block Formats

**PARCEL block:**
```
PARCEL: 2815 Sunset Blvd, Los Angeles, CA 90026
  APN: 5462-001-016
  Neighborhood: Silver Lake
  Zoning: R1-1-HCR
  Lot size: 6,800 sq ft
  Current use: Single Family Residential

  DEVELOPMENT INCENTIVES:
    • TOC: Tier 3
    • SB 9: Yes

  HAZARDS & CONSTRAINTS:
    • Hillside Construction Regulation (HCR) area

  CASES (3 total):
    [LADBS] 24-ADD-10-000-88441  |  ADU  |  Status: Issued
    [City Planning] ZA-2024-006550-ADUH  |  ADU  |  Status: Under Review
```

**CASE DETAIL block:**
```
CASE DETAIL: 24-ADD-10-000-88441
  Department:    LADBS
  Type:          ADU
  Description:   Attached ADU, 480 sq ft — standard plan ADU3...
  Applicant:     Maria Gonzalez (resident)
  Submitted:     2024-03-15
  Status:        Issued
  Assigned to:   Plan Check Engr. J. Nakamura
  Fees paid:     $2,800
  Fees owed:     $0
  Next action:   Permit issued. Post permit on site...
  Portal link:   https://ladbs.org/services/check-status
```

**WORKFLOW block:**
```
WORKFLOW: ADU  (view: resident)

  Step 1. Check ADU Eligibility [Applicant]  ~1-3 days
    Verify lot meets ADU requirements...
    💡 Go to zimas.lacity.org and enter your address...

  Step 2. Prepare Plans [Applicant]  ~5-14 days
    ...
```

**MAP block:**
```
MAP:
  latitude: 34.0490609096
  longitude: -118.325872923
```

**ADU ELIGIBILITY CHECK block:**
```
ADU ELIGIBILITY CHECK for 2815 Sunset Blvd
  APN: 5462-001-016
  Zoning: R1-1-HCR

  ZONING: ✅ Residential zone — ADU permitted by right
  HILLSIDE (HCR): ⚠ Hillside Construction Regulation area...
  OVERALL: ✅ ELIGIBLE — With conditions
    → Your parcel is eligible, but the constraints above...
```

### 7.3 Frontend Parsing

Each card component exports a parser function:

| Function | File | Regex/Search Pattern |
|---|---|---|
| `parseParcelText()` | `ParcelCard.tsx` | Starts with `PARCEL:`, extracts fields by label, parses case rows with `\[([^\]]+)\]\s+(\S+)...Status: (.*)` |
| `parseCaseDetailText()` | `CaseDetailCard.tsx` | Starts with `CASE DETAIL:`, extracts by label, parses fees with `\$?([\d,]+)` |
| `parseWorkflowText()` | `WorkflowTimeline.tsx` | Matches `WORKFLOW:\s*(.*?)\(view:\s*(.*?)\)`, step lines with `Step (\d+)\.\s+(.*?)\s+\[(.*?)\]?\s*~(\d+)\s*days?` |
| `parseMapText()` | `MapCard.tsx` | Starts with `MAP:`, extracts `latitude:` and `longitude:` |

### 7.4 Stripping Logic

`stripStructuredBlocks()` in `ChatWindow.tsx`:
- Removes lines starting with sentinel + all indented lines that follow
- Re-enters normal text mode on encountering a non-empty, non-indented line
- `SENTINEL_RE = /^(PARCEL:|CASE DETAIL:|WORKFLOW:|MAP:)/`
- `ADU ELIGIBILITY CHECK:` is NOT stripped — renders as raw text in the bubble

---

## 8. CI/CD Pipeline

### 8.1 Backend Pipeline (`azure-pipelines-backend.yml`)

**Trigger:** `main` branch, `backend/*` path changes
**Agent:** `ubuntu-latest`

```
1. UsePythonVersion@0 → Python 3.12
2. pip install -r backend/requirements.txt
3. ArchiveFiles@2 → zip backend/
4. PublishBuildArtifacts@1
5. AzureWebApp@1 → deploy to tre-app-lapoc
   Startup command: python -m seed.seed_data && uvicorn main:app --host 0.0.0.0 --port ${PORT}
```

### 8.2 Frontend Pipeline (`azure-pipelines-frontend.yml`)

**Trigger:** `main` branch (any path)
**Agent:** `ubuntu-latest`

```
1. NodeTool@0 → Node.js 20.x
2. npm ci && npm run build
3. npm install -g @azure/static-web-apps-cli
4. swa deploy ./frontend/dist --deployment-token $SWA_TOKEN --env production
```

### 8.3 Azure Resources

| Resource | Type | Name |
|---|---|---|
| Backend | App Service | `tre-app-lapoc` |
| Frontend | Static Web Apps | (linked to repo) |
| LLM | Azure OpenAI | gpt-4o deployment |
| Speech | Cognitive Services | Azure Speech |

---

## 9. Configuration Reference

### 9.1 Environment Variables

```
AZURE_OPENAI_ENDPOINT      # https://<resource>.openai.azure.com
AZURE_OPENAI_API_KEY       # 32-char hex key
AZURE_OPENAI_API_VERSION   # 2024-12-01-preview
AZURE_OPENAI_DEPLOYMENT    # gpt-4o
AZURE_SPEECH_ENDPOINT      # https://<region>.cognitiveservices.azure.com
AZURE_SPEECH_KEY           # 32-char hex key
VITE_API_URL               # "" (dev) or "https://tre-app-lapoc.azurewebsites.net" (prod)
```

### 9.2 Vite Proxy Config

```
/plots        → http://localhost:8000
/cases        → http://localhost:8000
/chat         → http://localhost:8000
/health       → http://localhost:8000
/speech-token → http://localhost:8000
/static       → http://localhost:8000
```

### 9.3 CORS Origins

```
http://localhost:5173
http://localhost:3000
https://mango-pond-098047a03.7.azurestaticapps.net
```

---

## Appendix A: Seed Data Reference

See `backend/seed/seed_cases.md` for the full list of case IDs, APNs, and statuses.

**Process types with defined workflows:** `ADU`, `ADU_standard`, `Bldg-New`, `Bldg-Alter/Repair`, `Bldg-Addition`, `CUB`, `ZC`, `ZV`, `ADJ`, `TOC`, `EIR`, `CDP`, `Grading`, `Electrical`, `Plumbing`, `HVAC`, `Fire Sprinkler`, `Swimming-Pool/Spa`, `PM`, `SPPA`

**Process types with persona guidance:** All of the above, with guidance rows for `resident`, `developer`, and/or `contractor` personas.

## Appendix B: Case ID Formats

**LADBS:** `YY-TTT-OO-MMM-#####`
- `YY` = 2-digit year
- `TTT` = permit type (ADD, BLD, ALT, GRD, ELE, PLM, MEC, SPK, POL)
- `OO` = branch (10=Metro, 30=West LA, 70=South LA)
- `MMM` = 000 master, 001+ supplemental
- `#####` = 5-digit sequential

**City Planning:** `PREFIX-YEAR-SEQ#-SUFFIX(es)`
- e.g. `ZA-2024-003812-CUB`, `DIR-2024-007831-CDP`, `CPC-2024-011002-TOC`, `ENV-2024-005502-EIR`

## Appendix C: Quick Reference

```bash
# Full bootstrap
bash init

# Backend only
cd backend
python -m venv ../.venv && source ../.venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then edit
python seed/seed_data.py
uvicorn main:app --reload

# Frontend only
cd frontend
npm install
npm run dev

# Verify
open http://localhost:5173
open http://localhost:8000/docs
```
