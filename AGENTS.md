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
| Lint | `frontend/` | `npx eslint src/` |
| Production build | `frontend/` | `npm run build` (runs `tsc -b && vite build`) |
| API docs | — | `open http://localhost:8000/docs` |
| Install deps (CI uses) | `frontend/` | `npm ci` (not `npm install`) |

**Verification order**: lint → typecheck → build. No test runner exists.

---

## Frontend conventions

- **CSS Modules only** — no Tailwind, no inline styles. Every component has a paired `*.module.css`.
- **`@/` alias** → `src/`. Use it for all non-relative imports.
- **`VITE_API_URL`**: empty string in `frontend/.env.development` (Vite proxy handles it); set to `https://tre-app-lapoc.azurewebsites.net` in `.env.production`.
- **tsconfig strict**: `strict`, `noUnusedLocals`, `noUnusedParameters` are all on. Unused variables are errors, not warnings — ESLint also enforces this with `varsIgnorePattern: '^_'`.
- **Vite proxy** (dev only): `/plots`, `/cases`, `/chat`, `/health`, `/speech-token`, `/static` → `localhost:8000`.
- **Three.js / R3F** present (`@react-three/fiber`, `@react-three/drei`, `three`) — `.glb` assets included via `assetsInclude`.
- **Azure Speech SDK** (`microsoft-cognitiveservices-speech-sdk`) requires special Vite `optimizeDeps.include` — already configured in `vite.config.ts`; don't remove it.

---

## Project layout

```
backend/
  main.py              load_dotenv() FIRST (line 7), then create_all(), CORS, 4 routers
  database.py          SQLAlchemy engine + session (lapoc.db relative to CWD)
  models.py            Plot, Case, WorkflowStep, WorkflowPersona
  schemas.py           Pydantic v2
  routers/             plots.py, cases.py (includes /random), chat.py, token.py
  agent/
    agent.py           AsyncAzureOpenAI loop + persona system prompts + suggestion generation
    tools.py           lookup_parcel, get_case_detail, get_workflow
    prompts/           system_prompts.jinja  ← Jinja2 blocks per persona
  seed/seed_data.py    Destructive reseed — 10 parcels, 30 cases, 135 steps, 99 persona rows
  static/              Served at /static (video banner etc.)
frontend/
  src/pages/Chat.tsx          Main page: suggestions, scroll, speech, error banner
  src/components/
    ChatWindow.tsx            Bubble renderer, inline markdown, card wiring (useCardData hook)
    ParcelCard.tsx            Parcel card + parseParcelText()
    CaseDetailCard.tsx        Case card + parseCaseDetailText()
    WorkflowTimeline.tsx      Animated step timeline + parseWorkflowText()
    CaseStatusBadge.tsx       Inline status pill (suppressed when CaseDetailCard renders)
    ChatMascot.tsx            3D mascot driven by viseme + conversation state
    PersonSelector.tsx        Persona picker card (landing screen)
  src/hooks/                  useSpeechToken (auto-refreshes every 9 min), useSpeechRecognizer,
                              useSpeechSynthesizer, useVisemeScheduler
  src/styles/tokens.ts        LA brand colours (#1c2253 navy) + fonts (Montserrat + Open Sans)
  src/types/                  Shared TypeScript types
  src/utils/                  Utility helpers
```

---

## Structured text protocol

The LLM returns card data as plain text with sentinel prefixes. **Any new tool must follow this format** or the frontend parser returns null and only raw text is shown.

| Sentinel | Parser in component | Renders as |
|---|---|---|
| `PARCEL:` | `parseParcelText()` in `ParcelCard.tsx` | Property info + cases table |
| `CASE DETAIL:` | `parseCaseDetailText()` in `CaseDetailCard.tsx` | Status + fees + next-action |
| `WORKFLOW:` | `parseWorkflowText()` in `WorkflowTimeline.tsx` | Animated step timeline |

Format: field labels indented 2 spaces; empty lines separate sections. `ChatWindow.tsx` strips sentinel blocks from the prose bubble via `stripStructuredBlocks()` so they don't render twice.

**Full checklist to add a new card type**: sentinel prefix in tool output → `parseXxxText()` → React component → `*.module.css` → wire into `ChatWindow.tsx` `useCardData()` and `AssistantContent`.

---

## Agent

**Three tools** in `agent/tools.py`, registered as OpenAI function schemas in `agent.py`:

| Tool | Key arg | Notes |
|---|---|---|
| `lookup_parcel(apn_or_address)` | APN `XXXX-XXX-XXX` or partial address | Returns `PARCEL:` block |
| `get_case_detail(case_id)` | LADBS or City Planning case ID | Returns `CASE DETAIL:` block |
| `get_workflow(process_type, persona)` | One of 20 process types + persona | Returns `WORKFLOW:` block |

`run_agent` loop: max 6 iterations, `tool_choice: "auto"`, returns `(reply_text, tool_names_called, detected_persona)`.

**System prompts** are Jinja2 blocks in `agent/prompts/system_prompts.jinja` — one block per persona (`resident`, `developer`, `contractor`, `auto`) plus a `suggest` block for suggestion generation. Edit there, not inline in Python.

**To add a tool**: implement in `tools.py` → add schema to `TOOLS` list in `agent.py` → add dispatch branch in `_dispatch_tool()`.

**Persona**: frontend always sends `persona: "auto"`. LLM appends `[PERSONA:resident|developer|contractor]` on first reply only; `_extract_persona_tag()` strips it before returning. Tag may re-appear on subsequent turns.

**Dynamic follow-up suggestions**: `generate_suggestions()` in `agent.py` fires a second LLM call after the first user message only (`is_first_query` check in `chat.py`). Falls back to keyed defaults if the LLM returns malformed JSON.

**TTS keynotes**: `generate_speech_keynotes()` in `agent.py` fires a third LLM call on every response, producing a 1-2 sentence spoken summary (max 40 words, no markdown). Result is `speech_text` in `ChatResponse`. Falls back to regex-stripped first two sentences if the LLM call fails.

| Persona | Style |
|---|---|
| `resident` | Plain language, define jargon, next steps |
| `developer` | Technical LA planning terms (LOD, CEQA, ZIMAS, DSC), flag risks |
| `contractor` | LADBS terms (PC branch, TCO vs CofO, inspection codes) |

---

## Data model

- **DB location**: `lapoc.db` relative to CWD — place it in `backend/` when running from there. `.gitignore` excludes `*.db`. A second `lapoc.db` may exist at repo root if seeded from root.
- **APN format**: `XXXX-XXX-XXX` (LA County). 10 seed parcels use real APNs.
- **Case ID formats**: LADBS `YY-TTT-OO-MMM-#####` · City Planning `PREFIX-YEAR-SEQ-SUFFIX`
- **30 seed case IDs** listed in `case_numbers.md` at root — useful for testing tool calls.
- **Case fields not exposed by tools**: `valuation`, `pc_job_number`, `plan_type`, `conditions_of_approval`.
- **20 workflow process types**: `ADU`, `ADU_standard`, `Bldg-New`, `Bldg-Alter/Repair`, `Bldg-Addition`, `CUB`, `ZC`, `ZV`, `ADJ`, `TOC`, `CDP`, `EIR`, `PM`, `SPPA`, `Grading`, `Electrical`, `Plumbing`, `HVAC`, `Fire Sprinkler`, `Swimming-Pool/Spa`

---

## Gotchas

- **`load_dotenv()` before all imports** — `main.py` line 7 calls it before importing routers/models. Any module-level code that reads env vars must be in `main.py` or called after startup; it will not see vars if it runs at import time in a router.
- **Azure-only LLM client** — `AsyncAzureOpenAI` in `agent.py`. To switch to standard OpenAI, replace client init and `model=` argument; comments in the file describe how.
- **Azure OpenAI endpoint format** — `AZURE_OPENAI_ENDPOINT` must have **no trailing slash** and no `/openai/...` path suffix (bare base URL only). See `.env.example`.
- **Azure Speech** — frontend `useSpeechToken` calls `/speech-token` every 9 min. Requires `AZURE_SPEECH_ENDPOINT` + `AZURE_SPEECH_KEY` in `backend/.env`. These are **not** in `.env.example`. Speech fails silently if missing; chat still works.
- **30s fetch timeout** — `Chat.tsx` aborts `/chat` requests after 30 s. Deep agent chains (6 iterations × slow tool) can hit this.
- **CORS origins** — hardcoded in `main.py`: `localhost:5173`, `localhost:3000`, `https://mango-pond-098047a03.7.azurestaticapps.net`. Add new deploy URLs here.
- **CI reseeds on every deploy** — `azure-pipelines-backend.yml` startup command is `python -m seed.seed_data && uvicorn …`. Production data is always synthetic seed data.
- **CI uses Python 3.12 / Node 20** — local dev needs Python 3.11+ and Node 18+; CI is pinned to 3.12 and 20.x.
- **`/static` proxy** — Vite proxies `/static` to the backend in dev. The backend mounts `StaticFiles(directory="static")`. The video banner (`lacity-banner.mp4`) is served this way.
- **No tests** — zero test files, no pytest/vitest/jest config. Only verification is typecheck + lint + build.
- **`/cases/random` route order** — must be declared before `/{case_id}` in `cases.py` (already correct); reordering breaks it because FastAPI would parse the literal string "random" as a case ID.
- **`.glb` assets** — `assetsInclude: ['**/*.glb']` in `vite.config.ts` is required for the mascot model import; removing it breaks the R3F scene.
- **`WorkflowTimeline` collapse** — timelines with more than 7 steps collapse to show only the first 5 steps, with a "Show all N steps" toggle. Keep this threshold in mind when adding steps.
- **Unused variable convention** — prefix intentionally unused variables or parameters with `_` (e.g., `_s`, `_ref`) to satisfy `noUnusedLocals` / `noUnusedParameters` and the ESLint `varsIgnorePattern: '^_'` rule.
- **Greeting audio is cached in IndexedDB** — key `"greeting"` via `src/utils/audioCache.ts`. Stale audio survives page reloads. Clear IndexedDB manually when testing greeting changes.
- **`Landing.module.css` has no paired component** — the file exists but `Landing.tsx` was removed. `App.tsx` routes directly to `<Chat>` and redirects all other paths to `/`. The CSS file is a stale artifact; don't create a `Landing.tsx` unless intentionally restoring that page.
