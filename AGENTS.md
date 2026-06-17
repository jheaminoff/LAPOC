# LAPOC — LA City Planning One-Stop-Shop

Stack: **Python FastAPI + SQLite** (backend) · **React 18 + TypeScript + Vite** (frontend)

---

## Commands

| What | Where | Command |
|---|---|---|
| Backend dev | `backend/` | `uvicorn main:app --reload` |
| Reseed DB (destructive) | `backend/` | `python seed/seed_data.py` |
| Frontend dev | `frontend/` | `npm run dev` |
| Type-check | `frontend/` | `npx tsc -b --noEmit` |
| Production build | `frontend/` | `npm run build` (runs `tsc -b && vite build`) |
| API docs | — | `open http://localhost:8000/docs` |

No lint config, no test framework, no formatter. tsconfig has `strict: true`, `noUnusedLocals`, `noUnusedParameters`.

Frontend conventions: **CSS Modules** (`*.module.css`), **`@/` path alias** maps to `src/`, **`VITE_API_URL`** env var (empty in `frontend/.env.development` → same-origin via Vite proxy; set to `https://tre-app-lapoc.azurewebsites.net` in production).

---

## Project layout

```
backend/
  main.py           load_dotenv() first, then create_all(), CORS, 4 routers
  database.py       SQLAlchemy engine + session (lapoc.db relative to CWD)
  models.py         Plot, Case, WorkflowStep, WorkflowPersona
  schemas.py        Pydantic v2
  routers/          plots, cases (also /random), chat, token
  agent/            agent.py (AsyncAzureOpenAI loop) + tools.py (3 tools)
  seed/seed_data.py Destructive reseed — 10 parcels, 30 cases, 135 steps
frontend/
  src/pages/Chat.tsx   30s fetch timeout, suggestion chips, speech hooks
  src/components/      ChatWindow, ParcelCard, CaseDetailCard, WorkflowTimeline, CaseStatusBadge, ChatMascot
  src/hooks/           useSpeechToken (refreshes every 9 min), useSpeechRecognizer, useSpeechSynthesizer, useVisemeScheduler
  src/styles/tokens.ts LA brand colors/fonts (Montserrat + Open Sans)
```

**Key wiring**: Vite proxies `/plots`, `/cases`, `/chat`, `/health`, `/speech-token` → `localhost:8000`.

---

## Structured text protocol

LLM communicates cards to the frontend via sentinel-prefixed plain text. **New tool output must follow this format** or the frontend parser returns null.

| Sentinel | Parser | Renders as |
|---|---|---|
| `PARCEL:` | `parseParcelText()` | Property info + cases table |
| `CASE DETAIL:` | `parseCaseDetailText()` | Status + fees + next-action |
| `WORKFLOW:` | `parseWorkflowText()` | Animated step timeline |

Format: field labels indented 2 spaces, empty lines separate sections. Failed parse → raw text visible (no crash).

---

## Agent

**Three tools** in `agent/tools.py` wired as OpenAI function schemas in `agent.py`:

| Tool | Args | Source of truth |
|---|---|---|
| `lookup_parcel(apn_or_address)` | APN `XXXX-XXX-XXX` or partial address | Parcel card |
| `get_case_detail(case_id)` | Case ID (LADBS or City Planning format) | Case detail card |
| `get_workflow(process_type, persona)` | One of 20 process types + `resident`/`developer`/`contractor` | Workflow timeline |

`run_agent` loop: `AsyncAzureOpenAI` (Azure-only), max 6 iterations, `tool_choice: "auto"`, returns `(reply_text, tool_names_called, detected_persona)`.

**To add a tool**: implement in `tools.py`, add schema to `TOOLS` in `agent.py`, add dispatch branch in `_dispatch_tool()`. For frontend cards: sentinel prefix + `parseXxxText()` + React component + CSS Module + wire into `ChatWindow.tsx` `useCardData()`.

**Persona**: Frontend sends `persona: "auto"` every message. LLM appends `[PERSONA:resident|developer|contractor]` on first reply only. `_extract_persona_tag()` strips it.

| Persona | Style |
|---|---|
| `resident` | Plain language, define jargon, next steps |
| `developer` | Technical LA planning terms (LOD, CEQA, ZIMAS, DSC), flag risks |
| `contractor` | LADBS terms (PC branch, TCO vs CofO, inspection codes) |

When calling `get_workflow`, infer persona from context. Falls back to `resident` if no persona-specific rows exist.

---

## Data model

- **DB**: `backend/lapoc.db` (relative to CWD). `.gitignore` has `*.db`. Seeding is destructive.
- **APN format**: `XXXX-XXX-XXX` (LA County). 10 seed parcels use real APNs.
- **Case IDs**: LADBS `YY-TTT-OO-MMM-#####` | City Planning `PREFIX-YEAR-SEQ-SUFFIX`
- **30 seed case IDs** documented in `case_numbers.md` at root.
- **Case model extras** not surfaced in tool output: `valuation`, `pc_job_number`, `plan_type`, `conditions_of_approval`.
- **20 workflow process types**: `ADU`, `ADU_standard`, `Bldg-New`, `Bldg-Alter/Repair`, `Bldg-Addition`, `CUB`, `ZC`, `ZV`, `ADJ`, `TOC`, `CDP`, `EIR`, `PM`, `SPPA`, `Grading`, `Electrical`, `Plumbing`, `HVAC`, `Fire Sprinkler`, `Swimming-Pool/Spa`

---

## Gotchas

- **Azure-only**: `AsyncAzureOpenAI` in `agent.py`. To swap to standard OpenAI, replace client init and `model=` — notes at bottom of file.
- **load_dotenv() runs before imports**: `main.py:6` calls `load_dotenv()` *before* importing routers/models. New top-level code in those modules won't see env vars.
- **Azure Speech**: `microsoft-cognitiveservices-speech-sdk` in frontend. `/speech-token` endpoint proxies Azure STS. Requires `AZURE_SPEECH_ENDPOINT` + `AZURE_SPEECH_KEY` in `backend/.env`.
- **30s fetch timeout**: `Chat.tsx:43` — long agent chains can abort.
- **CORS**: 3 origins — `localhost:5173`, `localhost:3000`, `https://mango-pond-098047a03.7.azurestaticapps.net`. Add more for other deployments.
- **Persona re-detection**: every message sends `persona: "auto"`, so persona tag may re-appear each turn.
- **No tests**: zero test files, no pytest/vitest/jest config.
- **Azure Pipelines CI**: `azure-pipelines-backend.yml` (deploys to Azure Web Apps, runs seed on startup: `python -m seed.seed_data && uvicorn main:app --host 0.0.0.0 --port ${PORT}`), `azure-pipelines-frontend.yml` (deploys to Azure Static Web Apps).
- **Env**: `backend/.env` holds Azure keys. Frontend env vars in `frontend/.env.development` (`VITE_API_URL=` empty) and `.env.production` (`VITE_API_URL=https://tre-app-lapoc.azurewebsites.net`).
