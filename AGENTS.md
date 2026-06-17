# LAPOC — LA City Planning One-Stop-Shop

Stack: **Python FastAPI + SQLite** (backend) · **React 18 + TypeScript + Vite** (frontend)

---

## Project structure

```
backend/
  main.py             FastAPI app entry, CORS, router registration, table creation on startup
  database.py         SQLAlchemy engine + session factory — lapoc.db relative to CWD
  models.py           ORM: Plot, Case, WorkflowStep, WorkflowPersona
  schemas.py          Pydantic v2 schemas
  routers/
    plots.py          GET /plots/{apn}, GET /plots/search/address?q=
    cases.py          GET /cases/{case_id}
    chat.py           POST /chat — proxies to agent loop
    token.py          GET /speech-token — Azure Speech STS proxy
  agent/
    agent.py          Azure OpenAI tool-calling loop + persona detection
    tools.py          3 tools: lookup_parcel, get_case_detail, get_workflow
  seed/seed_data.py   Drops & recreates all data — 10 parcels, 30 cases, 135 workflow steps
frontend/
  src/pages/Chat.tsx       Main chat page (speech hooks, 30s fetch timeout, persona badge)
  src/components/
    ChatWindow.tsx          Bubble renderer, inline card wiring (Parcel / CaseDetail / Workflow)
    ParcelCard.tsx          Parser + card for PARCEL: blocks
    CaseDetailCard.tsx      Parser + card for CASE DETAIL: blocks
    WorkflowTimeline.tsx    Parser + animated step card for WORKFLOW: blocks
    CaseStatusBadge.tsx     Inline status pill from free text
  src/hooks/               useSpeechToken, useSpeechRecognizer, useSpeechSynthesizer, useVisemeScheduler
  src/styles/tokens.ts     LA brand colors/fonts (Montserrat + Open Sans)
```

**Key wiring**: Vite dev server proxies `/plots`, `/cases`, `/chat`, `/health`, `/speech-token` → `localhost:8000`

---

## Quick start

```bash
# Backend
cd backend
python -m venv ../.venv && source ../.venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill AZURE_OPENAI_* vars — backend/.env only
python seed/seed_data.py
uvicorn main:app --reload

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

---

## Commands

| What | Command |
|---|---|
| Run backend dev | `cd backend && uvicorn main:app --reload` |
| Reseed DB (drops all data) | `cd backend && python seed/seed_data.py` |
| Run frontend dev | `cd frontend && npm run dev` |
| Type-check frontend | `cd frontend && npx tsc -b --noEmit` |
| Frontend production build | `cd frontend && npm run build` |
| API docs | `open http://localhost:8000/docs` |

No lint config, no test framework, no formatter config exists. The `tsconfig.json` has `strict: true`, `noUnusedLocals`, `noUnusedParameters`.

---

## Structured text protocol

The LLM communicates structured data to the frontend via sentinel-prefixed plain text. **Any new tool output must follow this exact format** or the frontend parser silently returns null.

| Sentinel | Frontend parser | Rendered as |
|---|---|---|
| `PARCEL:` | `parseParcelText()` | Property info + cases table card |
| `CASE DETAIL:` | `parseCaseDetailText()` | Status banner + fees + next-action card |
| `WORKFLOW:` | `parseWorkflowText()` | Animated step timeline card |

Format rules:
- Field labels are indented 2 spaces, followed by the value
- Empty lines separate sections
- If parsing fails, raw text is still visible in the chat bubble (no crash)

---

## Agent behavior

**Three tools** defined in `agent/tools.py`, wired into `agent/agent.py` as OpenAI function-calling schemas:

| Tool | What it does | Called when |
|---|---|---|
| `lookup_parcel(apn_or_address)` | Searches by APN (`XXXX-XXX-XXX`) or partial address. Returns parcel + case list. | "Look up 2815 Sunset Blvd" |
| `get_case_detail(case_id)` | Full detail for one permit/planning case | "Check case ZA-2024-003812-CUB" |
| `get_workflow(process_type, persona)` | Ordered steps w/ persona-specific guidance for 20 process types | "How do I get an ADU permit?" |

The agent loop (`run_agent`):
- Uses **Azure OpenAI** (`AsyncAzureOpenAI`), **not** standard OpenAI by default
- Max 6 iterations (enough for lookup→case detail→workflow chains)
- `tool_choice: "auto"` — model decides whether to call
- Returns `(reply_text, tool_names_called, detected_persona)`

**Persona system**: The frontend always sends `persona: "auto"`. The LLM detects role from language and appends `[PERSONA:resident|developer|contractor]` on its first reply only. The `_extract_persona_tag()` function strips and returns it.

| Persona | Tone |
|---|---|
| `resident` | Plain language, define jargon, focus on next steps |
| `developer` | Technical, LOD/CEQA/ZIMAS/DSC terminology, flag risks |
| `contractor` | Concise LADBS terms (PC branch, TCO vs CofO, inspection codes) |

When calling `get_workflow`, infer the persona from conversation context. Falls back to "resident" guidance if no persona-specific rows exist.

---

## Requirements to add a new tool

1. Implement the function in `agent/tools.py`
2. Add its OpenAI function-calling schema to `TOOLS` in `agent/agent.py`
3. Add a dispatch branch in `_dispatch_tool()`
4. If the output should render as a frontend card, prefix with a sentinel (e.g. `STATUS SEARCH:`) and write a `parseXxxText()` function + React component + CSS module, then wire it into `ChatWindow.tsx` `useCardData()`

---

## Data model

- **DB location**: `backend/lapoc.db` (relative to CWD — created by `database.py`). The `.gitignore` has `*.db` — it is intentionally not committed.
- **Parcel APN format**: `XXXX-XXX-XXX` (LA County). All 10 seed parcels use verified real APNs.
- **Case ID formats**: LADBS `YY-TTT-OO-MMM-#####` (e.g. `24-ADD-10-000-88441`) | City Planning `PREFIX-YEAR-SEQ-SUFFIX` (e.g. `ZA-2024-003812-CUB`)
- **Case statuses**: `Issued`, `PC Approved`, `Corrections Needed`, `Recheck`, `Fees Due`, `Submitted`, `Permit Finaled`, `Appeal Pending`, `Intent to Revoke`, `PC Expired`, etc. — see `ParcelCard.tsx` `STATUS_COLOURS` for complete map.
- **20 workflow process types**: `ADU`, `ADU_standard`, `Bldg-New`, `Bldg-Alter/Repair`, `Bldg-Addition`, `CUB`, `ZC`, `ZV`, `ADJ`, `TOC`, `CDP`, `EIR`, `PM`, `SPPA`, `Grading`, `Electrical`, `Plumbing`, `HVAC`, `Fire Sprinkler`, `Swimming-Pool/Spa`

---

## Quirks & gotchas

- **Azure-only**: The backend uses `AsyncAzureOpenAI` from the `openai` SDK. To swap to standard OpenAI, replace the client init in `agent/agent.py` and update `model=` — documented at the bottom of the file.
- **Azure Speech**: The frontend uses `microsoft-cognitiveservices-speech-sdk`. The token endpoint (`/speech-token`) proxies Azure Speech STS. Requires `AZURE_SPEECH_ENDPOINT` and `AZURE_SPEECH_KEY` in `backend/.env`.
- **30-second timeout**: Frontend `POST /chat` aborts after 30 seconds. The agent loop has max 6 iterations, so very long chains could timeout.
- **CORS origins**: `main.py` allows only `localhost:5173` and `localhost:3000`. Add more if deploying elsewhere.
- **Persona re-detection**: The frontend sends `persona: "auto"` on every message rather than locking in the detected persona, so persona re-detection happens each turn.
- **No tests**: Zero test files exist anywhere in the repo. Backend has no pytest config. Frontend has no vitest/jest setup.
- **DB seeding is destructive**: `seed/seed_data.py` calls `Base.metadata.create_all()` then inserts — but the tool output text in `agent/tools.py` is the source of truth for the frontend card parsers, not the ORM schema docs.
- **Env files**: `backend/.env` only, no frontend env. Vite dev server handles proxying.
- **Case numbers reference**: `case_numbers.md` at root documents all 30 seed case IDs with their types — handy for testing queries.
