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
| Install deps (CI uses) | `frontend/` | `npm ci` |

**Verification order**: lint → typecheck → build. No test runner exists.

---

## Frontend conventions

- **CSS Modules only** — no Tailwind, no inline styles. Every component has a paired `*.module.css`.
- **`@/` alias** → `src/`. Use it for all non-relative imports.
- **`VITE_API_URL`**: empty string in development (Vite proxy handles it); set to `https://tre-app-lapoc.azurewebsites.net` in production.
- **tsconfig strict**: `strict`, `noUnusedLocals`, `noUnusedParameters` all on. Prefix unused vars with `_` (ESLint enforces via `varsIgnorePattern: '^_'` and `argsIgnorePattern: '^_'`).
- **Vite proxy** (dev only): `/plots`, `/cases`, `/chat`, `/health`, `/speech-token`, `/static` → `localhost:8000`.
- **Three.js / R3F** present — `.glb` assets via `assetsInclude` in `vite.config.ts`.
- **React-Leaflet** present (`MapCard`) — `leaflet` + `react-leaflet` in deps.
- **Azure Speech SDK** — `optimizeDeps.include` in `vite.config.ts`; do not remove.
- **`presentation.html`** is a second rollup entry point (`vite.config.ts`).

---

## Structured text protocol (sentinels)

The LLM returns card/map data as plain text with sentinel prefixes. **New tool output must use a sentinel prefix** or the frontend can't render it as a card.

| Sentinel | Frontend parser | Renders as |
|---|---|---|
| `PARCEL:` | `parseParcelText()` in `ParcelCard.tsx` | Property info + cases table |
| `CASE DETAIL:` | `parseCaseDetailText()` in `CaseDetailCard.tsx` | Status + fees + next-action |
| `WORKFLOW:` | `parseWorkflowText()` in `WorkflowTimeline.tsx` | Animated step timeline |
| `MAP:` | `parseMapText()` in `MapCard.tsx` | Leaflet map with marker |
| `ADU ELIGIBILITY CHECK:` | **No card component exists** — renders as raw text in bubble | Raw prose only |

Format: field labels indented 2 spaces; empty lines separate sections. `ChatWindow.tsx` strips known sentinel blocks from the prose bubble via `stripStructuredBlocks()` — only `PARCEL:`, `CASE DETAIL:`, `WORKFLOW:`, and `MAP:` are in `SENTINEL_RE`. `ADU ELIGIBILITY CHECK:` is **not** stripped, so it renders as text in the bubble alongside any fallback.

To add a new sentinel card: sentinel in tool output → `parseXxxText()` → React component → `*.module.css` → wire into `ChatWindow.tsx` `useCardData()` and `AssistantContent` → add to `SENTINEL_RE` and `stripStructuredBlocks()`.

---

## Agent tools

**Five tools** in `agent/tools.py`, registered as OpenAI function schemas in `agent.py`:

| Tool | Key args | Returns |
|---|---|---|
| `lookup_parcel(apn_or_address)` | APN `XXXX-XXX-XXX` or partial address | `PARCEL:` block |
| `get_case_detail(case_id)` | LADBS or City Planning case ID | `CASE DETAIL:` block |
| `get_workflow(process_type, persona)` | Process type + persona (`resident`/`developer`/`contractor`) | `WORKFLOW:` block |
| `lookup_address(address)` | Street address | Prose + `MAP:` block (Leaflet coords) |
| `check_adu_eligibility(apn_or_address)` | APN or partial address | `ADU ELIGIBILITY CHECK:` block |

`lookup_address` calls the LA City BOE GeoQuery API with a **hardcoded API key** (`tools.py:245`). The other four hit SQLite.

`run_agent` loop: max 6 iterations, `tool_choice: "auto"`, returns `(reply_text, tool_names_called, detected_persona)`. Add a tool by implementing in `tools.py` → adding schema to `TOOLS` list in `agent.py` → adding dispatch branch in `_dispatch_tool()`.

---

## System prompts

Jinja2 blocks in `agent/prompts/system_prompts.jinja` — edit there, not inline in Python. Blocks: `resident`, `developer`, `contractor`, `auto`, `suggest`. The `base` block is extended by the others. The `auto` persona appends `[PERSONA:resident|developer|contractor]` only on the first reply.

**Dynamic suggestions**: fires a second LLM call after the first user message only (`is_first_query` check in `chat.py`). Falls back to keyed defaults if JSON is malformed.

**TTS keynotes**: fires a third LLM call on every response, producing max 40 words spoken summary. Falls back to regex-stripped first two sentences.

---

## Backend gotchas

- **`load_dotenv()` before all imports** — `main.py` line 7. Any module-level code reading env vars must be in `main.py` or after startup; router-level code is fine.
- **Azure-only LLM** — `AsyncAzureOpenAI` in `agent.py`. Comments describe how to swap to standard OpenAI.
- **Azure OpenAI endpoint format** — no trailing slash, no `/openai/...` path suffix. See `.env.example`.
- **Azure Speech** — `/speech-token` proxied every 9 min. Requires `AZURE_SPEECH_ENDPOINT` + `AZURE_SPEECH_KEY` (not in `.env.example`). Speech fails silently.
- **DB location**: `lapoc.db` relative to CWD (`.gitignore`).
- **CI reseeds every deploy** — `python -m seed.seed_data && uvicorn …` in `azure-pipelines-backend.yml`. Production data is always synthetic.
- **`/cases/random` route** — must be declared before `/{case_id}` (already correct).
- **CORS origins** — hardcoded in `main.py`. Add new deploy URLs here.
- **Unused model fields** (not exposed by tools): `valuation`, `pc_job_number`, `plan_type`, `conditions_of_approval`.

---

## Frontend gotchas

- **30s fetch timeout** — `Chat.tsx` aborts `/chat` after 30 s. Deep agent chains (6 iterations × slow tool) can hit this.
- **Greeting audio cached in IndexedDB** — key `"greeting"` via `src/utils/audioCache.ts`. Stale audio survives reloads; clear IndexedDB manually when testing.
- **`Landing.module.css` has no paired component** — stale artifact from removed `Landing.tsx`. Don't recreate it unless intentional.
- **`WorkflowTimeline` collapse** — >7 steps shows only first 5, with "Show all N steps" toggle.
