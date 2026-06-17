# LAPOC — LA City Planning One-Stop-Shop

A proof-of-concept agentic chatbot that lets Los Angeles residents, developers, and contractors look up permit status, planning case details, and process workflows — grounded in real LA City planning processes and data structures.

The assistant auto-detects whether you're a homeowner, developer, or contractor and adapts its language accordingly.

---

## Features

- **Parcel lookup** — search by APN (`XXXX-XXX-XXX`) or address; returns property details and all associated cases
- **Case detail** — full status, fees paid/owed, next action, hearing date, portal link for any LADBS permit or City Planning case
- **Workflow guide** — step-by-step process cards for 20 permit/entitlement types (ADU, CUB, Zone Change, Grading, TOC, CDP, and more)
- **Persona auto-detection** — detects homeowner / developer / contractor from natural language; tailors terminology and guidance
- **Inline structured cards** — parcel, case detail, and workflow data render as visual cards in the chat, not raw text
- **LA brand** — Montserrat + Open Sans, LA navy (`#1c2253`), official seal

---

## Architecture

```
lapoc/
├── backend/                 Python FastAPI + SQLite
│   ├── main.py              App entry, CORS, router registration
│   ├── database.py          SQLAlchemy engine + session factory
│   ├── models.py            ORM: Plot, Case, WorkflowStep, WorkflowPersona
│   ├── schemas.py           Pydantic v2 request/response schemas
│   ├── routers/
│   │   ├── plots.py         GET /plots/{apn}, GET /plots/search/address
│   │   ├── cases.py         GET /cases/{case_id}
│   │   └── chat.py          POST /chat  ← main agent endpoint
│   ├── agent/
│   │   ├── agent.py         Azure OpenAI tool-calling loop + persona detection
│   │   └── tools.py         lookup_parcel, get_case_detail, get_workflow
│   └── seed/
│       └── seed_data.py     10 real-APN parcels, 30 synthetic cases, 135 workflow steps
│
└── frontend/                React 18 + TypeScript + Vite
    └── src/
        ├── pages/
        │   └── Chat.tsx     Main chat page (error banner, suggestions, scroll logic)
        ├── components/
        │   ├── ChatWindow.tsx        Bubble renderer, markdown, inline card wiring
        │   ├── ParcelCard.tsx        Property + cases table card
        │   ├── CaseDetailCard.tsx    Status + fees + next action card
        │   ├── WorkflowTimeline.tsx  Animated step-by-step process card
        │   └── CaseStatusBadge.tsx  Inline status pill detection
        └── styles/
            └── tokens.ts    LA brand colour/font tokens
```

**Sequence:** `POST /chat` → agent loop → tool calls hit SQLite → structured text returned to LLM → LLM composes reply → frontend parses reply → inline cards rendered.

---

## Prerequisites

- Python 3.11+
- Node.js 18+
- An Azure OpenAI deployment of `gpt-4o` (or any model with function calling)

---

## Setup

### 1. Clone and prepare

```bash
git clone <repo>
cd LAPOC
```

### 2. Backend

```bash
cd backend

# Create and activate a virtual environment (recommended)
python -m venv ../.venv
source ../.venv/bin/activate   # Windows: ..\.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env — fill in your Azure OpenAI credentials (see Environment Variables below)

# Seed the database (creates lapoc.db in the project root)
python seed/seed_data.py

# Start the API server
uvicorn main:app --reload
# → http://localhost:8000
# → API docs: http://localhost:8000/docs
```

### 3. Frontend

```bash
cd frontend

npm install
npm run dev
# → http://localhost:5173
```

Open [http://localhost:5173](http://localhost:5173). The frontend proxies `/chat`, `/plots`, `/cases`, and `/health` to `localhost:8000`.

---

## Environment Variables

Create `backend/.env` (copy from `.env.example`):

```env
AZURE_OPENAI_ENDPOINT=https://<your-resource>.openai.azure.com/
AZURE_OPENAI_API_KEY=<your-api-key>
AZURE_OPENAI_API_VERSION=2024-12-01-preview
AZURE_OPENAI_DEPLOYMENT=gpt-4o
```

| Variable | Description |
|---|---|
| `AZURE_OPENAI_ENDPOINT` | Your Azure OpenAI resource endpoint URL |
| `AZURE_OPENAI_API_KEY` | API key from Azure Portal |
| `AZURE_OPENAI_API_VERSION` | API version — `2024-12-01-preview` recommended |
| `AZURE_OPENAI_DEPLOYMENT` | Deployment name for your gpt-4o (or equivalent) model |

> **Note:** The backend uses `AsyncAzureOpenAI` from the `openai` Python SDK. Standard OpenAI (non-Azure) is not configured by default — swap the client in `agent/agent.py` if needed.

---

## API Reference

### `POST /chat`

Main agent endpoint. Accepts a conversation history and returns the agent's reply.

**Request:**
```json
{
  "persona": "auto",
  "messages": [
    { "role": "user", "content": "What's the status of 2815 Sunset Blvd?" }
  ]
}
```

| Field | Type | Description |
|---|---|---|
| `persona` | `string` | `"auto"` (detect from chat), `"resident"`, `"developer"`, or `"contractor"` |
| `messages` | `array` | Full conversation history in `[{role, content}]` format |

**Response:**
```json
{
  "reply": "PARCEL: 2815 Sunset Blvd\n  APN: 5462-001-016\n  ...",
  "tool_calls_made": ["lookup_parcel"],
  "detected_persona": "resident"
}
```

| Field | Description |
|---|---|
| `reply` | Agent's text reply (may contain structured `PARCEL:`, `CASE DETAIL:`, or `WORKFLOW:` blocks) |
| `tool_calls_made` | List of tool names the agent invoked |
| `detected_persona` | Detected role (`resident`/`developer`/`contractor`) or `null` if not yet determined |

### `GET /plots/{apn}`

Look up a parcel by exact APN.

### `GET /plots/search/address?q={query}`

Search parcels by partial address string.

### `GET /cases/{case_id}`

Retrieve full detail for a single case by ID.

### `GET /health`

Returns `{"status": "ok"}`. Use to verify the backend is running.

---

## Seed Data

The database ships with synthetic data modelled on real LA processes:

- **10 parcels** — verified real APNs from LA County GIS (maps.lacity.org), covering Silver Lake, Hollywood, Venice, DTLA, West Adams, South LA, Leimert Park, Sunset Strip
- **30 cases** — realistic permit and planning case numbers in proper LADBS (`YY-TTT-OO-MMM-#####`) and City Planning (`PREFIX-YEAR-SEQ#-SUFFIX`) formats
- **135 workflow steps** — 20 process types including ADU (standard + custom), CUB, Zone Change, TOC, CDP, EIR, Grading, Electrical, Plumbing, HVAC, and more
- **99 persona guidance rows** — plain-language (resident), technical (developer), and LADBS-focused (contractor) guidance per step

To reseed (drops and recreates all data):

```bash
cd backend
python seed/seed_data.py
```

---

## Data Note

This POC uses **synthetic case data** — permit numbers, applicant names, fees, and statuses are fabricated for demonstration purposes. The parcel APNs and zoning data are real. For production use, the data layer would be replaced with a live connection to LADBS PermitLA or a City Planning API.

---

## Development

```bash
# Type-check frontend
cd frontend && npx tsc -b --noEmit

# Production build
cd frontend && npm run build

# Backend with auto-reload
cd backend && uvicorn main:app --reload

# API docs (Swagger UI)
open http://localhost:8000/docs
```

---

## Known Limitations

- **Synthetic data only** — no live LADBS or City Planning data connection
- **Azure OpenAI required** — not configured for standard OpenAI or other providers out of the box
- **No authentication** — the API is open; not suitable for production deployment as-is
- **English only** — no Spanish / multilingual support (significant gap for LA residents)
- **No persistence** — conversation history is not saved between sessions
