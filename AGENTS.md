# LAPOC — LA City Planning One-Stop-Shop

Stack: **Python FastAPI + SQLite** (backend) · **React 18 + TypeScript + Vite** (frontend) · **Azure OpenAI** (LLM)

---

## One-shot bootstrap

```bash
bash init               # venv + deps + .env copy + DB seed
source .venv/bin/activate
# edit backend/.env with Azure OpenAI credentials
# then: backend dev = uvicorn main:app --reload (port 8000)
# then: frontend dev = npm run dev (port 5173)
```

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
| API docs (Swagger) | — | `open http://localhost:8000/docs` |
| Install deps (CI uses) | `frontend/` | `npm ci` |

**Verification order**: lint → typecheck → build. No test runner exists.

---

## Frontend conventions

- **CSS Modules only** — no Tailwind, no inline styles. Each component gets a paired `*.module.css`.
- **`@/` alias** → `src/`. Use for all non-relative imports.
- **`VITE_API_URL`**: empty in dev (Vite proxy); `https://tre-app-lapoc.azurewebsites.net` in prod.
- **tsconfig strict**: `strict`, `noUnusedLocals`, `noUnusedParameters` on. Prefix unused params with `_`.
- **Vite proxy** (dev): `/plots`, `/cases`, `/chat`, `/health`, `/speech-token`, `/static` → `localhost:8000`.
- **Azure Speech SDK** — must stay in `optimizeDeps.include` in `vite.config.ts`.
- **`presentation.html`** — second rollup entry.

---

## Structured text protocol (sentinels)

The LLM returns card/map data as plain text with sentinel prefixes. **New tool output must use a sentinel prefix** or the frontend can't render it as a card.

| Sentinel | Frontend parser | Renders as |
|---|---|---|
| `PARCEL:` | `parseParcelText()` in `ParcelCard.tsx` | Property info + cases table |
| `CASE DETAIL:` | `parseCaseDetailText()` in `CaseDetailCard.tsx` | Status + fees + next-action |
| `WORKFLOW:` | `parseWorkflowText()` in `WorkflowTimeline.tsx` | Animated step timeline |
| `MAP:` | `parseMapText()` in `MapCard.tsx` | Leaflet map with marker |
| `ADU ELIGIBILITY CHECK:` | No card — renders as raw text in bubble | Raw prose only |

Format: field labels indented 2 spaces; empty lines separate sections. `stripStructuredBlocks()` in `ChatWindow.tsx` strips known sentinel blocks from the prose bubble — only `PARCEL:`, `CASE DETAIL:`, `WORKFLOW:`, `MAP:` are in `SENTINEL_RE` (line 62). `ADU ELIGIBILITY CHECK:` is **not** stripped.

To add a new sentinel card: sentinel in tool output → `parseXxxText()` → React component → `*.module.css` → wire into `ChatWindow.tsx` `useCardData()` and `AssistantContent` → add to `SENTINEL_RE` and `stripStructuredBlocks()`.

---

## Agent tools

**Five tools** in `agent/tools.py`, registered as OpenAI function schemas in `agent.py`:

| Tool | Key args | Returns |
|---|---|---|
| `lookup_parcel(apn_or_address)` | APN or partial address | `PARCEL:` block (SQLite) |
| `get_case_detail(case_id)` | LADBS / City Planning case ID | `CASE DETAIL:` block (SQLite) |
| `get_workflow(process_type, persona)` | Process + `resident`/`developer`/`contractor` | `WORKFLOW:` block (SQLite) |
| `lookup_address(address)` | Street address | Prose + `MAP:` block (BOE GeoQuery API) |
| `check_adu_eligibility(apn_or_address)` | APN or address | `ADU ELIGIBILITY CHECK:` block (SQLite → ZIMAS API) |

**`_find_plot()` behavior** (used by lookup_parcel and check_adu_eligibility):
1. Exact APN match first (`Plot.apn == value`)
2. Falls back to `address ILIKE %value%` (limit 5)
3. Multiple matches → returns disambiguation text listing all matches
4. Zero matches → returns None (ZIMAS fallback for ADU check)

**External APIs**:
- `lookup_address` calls LA City BOE GeoQuery (`api.lacity.org`) — **hardcoded key** at `tools.py:262`.
- `check_adu_eligibility` falls back to **ZIMAS API** (zimas.lacity.org) when parcel not in SQLite. Flow: ArcGIS `search_addressparts` query → PIN → `zm4WS/GetProjectData`. Street suffix normalization: DRIVE→DR, STREET→ST, AVENUE→AVE, etc. No API key needed.

**Agent loop**: `run_agent` in `agent.py` — max 6 iterations, `tool_choice: "auto"`. Returns `(reply_text, tool_names_called, detected_persona)`. Add a tool by: implement in `tools.py` → add schema to `TOOLS` list → add dispatch branch in `_dispatch_tool()`.

---

## System prompts

Jinja2 blocks in `agent/prompts/system_prompts.jinja` — edit there, not inline in Python. Blocks: `resident`, `developer`, `contractor`, `auto`, `suggest`. `base` is extended by the others. `auto` persona appends `[PERSONA:resident|developer|contractor]` on first reply only.

**Dynamic suggestions**: second LLM call after first user message (`is_first_query` in `chat.py`). Falls back to keyed defaults if JSON malformed.

**TTS keynotes**: third LLM call on every response, max 40 words. Falls back to regex-stripped first two sentences.

---

## Backend gotchas

- **`load_dotenv()` before all imports** — `main.py:3`. Any module-level code reading env vars must be in `main.py` or after startup; router-level is fine.
- **Azure-only LLM** — `AsyncAzureOpenAI` in `agent.py`. Comments describe how to swap to standard OpenAI.
- **Azure OpenAI endpoint**: no trailing slash, no `/openai/...` suffix.
- **Azure Speech**: `/speech-token` proxied every 9 min. Requires `AZURE_SPEECH_ENDPOINT` + `AZURE_SPEECH_KEY` (listed in `.env.example`). Fails silently if unset.
- **DB location**: `lapoc.db` relative to CWD (`.gitignore`). CI reseeds every deploy via `azure-pipelines-backend.yml`.
- **`/cases/random`** must be declared before `/{case_id}` (already correct).
- **CORS origins** hardcoded in `main.py` — add new deploy URLs here.
- **Unused model fields** (not exposed by tools): `valuation`, `pc_job_number`, `plan_type`, `conditions_of_approval`.

---

## Frontend gotchas

- **30s fetch timeout** — `Chat.tsx` aborts `/chat` after 30 s. Deep agent chains (6 iterations × slow tool) can hit this.
- **Greeting audio cached in IndexedDB** — key `"greeting"` via `src/utils/audioCache.ts`. Stale audio survives reloads; clear IndexedDB manually when testing.
- **`WorkflowTimeline` collapse** — >7 steps shows first 5 with "Show all N steps" toggle.
- **Mascot fallback**: `ram.glb` (Three.js GLB) → procedural geometric ram → `GlbErrorBoundary`. Jaw bone auto-detected by name (jaw/beak/mouth/chin/mandible).
- **Audio cache layers**: in-memory Map → IndexedDB (`audioCache.ts`) → Azure TTS synthesis (MP3). Cache key = speech text string.

---

## Reference docs

- `TECHNICAL_SPECS.md` — full data model, API ref, card parsers, CI/CD, config reference
- `README.md` — features, setup, dev guide
- `backend/seed/seed_cases.md` — test case IDs and APNs
