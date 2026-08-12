# KHOJ — AI Investigation & 3D Reconstruction Platform

> **From fragmented information to structured evidence, competing theories, and visual reconstruction.**

KHOJ is an AI-powered investigation platform designed to help users understand complex real-world events by transforming fragmented public information into a structured and visual investigation.

Instead of manually reading dozens of articles, comparing conflicting reports, and reconstructing timelines, KHOJ brings the entire investigation workflow into one interactive experience.

---

## ✦ What KHOJ Does

KHOJ transforms scattered information into:

* **Structured Evidence** — extracts key claims and their sources
* **Investigation Summaries** — condenses complex cases into understandable context
* **Event Timelines** — organizes important events chronologically
* **Competing Theories** — explores plausible explanations based on available evidence
* **Evidence Visualization** — presents claims, sources, and confidence clearly
* **3D Reconstructions** — converts investigation theories into interactive visual simulations

The goal is not simply to summarize information.

KHOJ helps users **explore how the available evidence connects**.

---

## ◈ The Problem

Important information about major events is often scattered across:

* news reports
* public statements
* independent sources
* articles
* online discussions
* conflicting narratives

Understanding what happened can require hours of manually comparing sources, identifying contradictions, and building timelines.

KHOJ compresses that process into a unified investigation workspace.

---

## ◉ How It Works

```text
Public Information
        ↓
   Source Analysis
        ↓
 Evidence Extraction
        ↓
 Timeline Generation
        ↓
 Theory Analysis
        ↓
 Investigation Workspace
        ↓
 3D Reconstruction
        ↓
 Interactive Simulation
```

AI is used to transform unstructured information into structured investigation data, while the application's visualization and reconstruction systems turn that data into an experience users can explore.

---

## ◇ 3D Reconstruction

One of KHOJ's core capabilities is transforming an investigation theory into a visual reconstruction.

The reconstruction pipeline converts structured evidence, timeline events, and a selected theory into a machine-readable 3D scene containing:

* environments
* actors
* vehicles
* movement
* event sequences
* camera direction

The resulting simulation is rendered directly in the browser using **React Three Fiber** and **Three.js**.

This allows users to move beyond reading:

```text
8:15 PM — Person leaves building
8:18 PM — Vehicle approaches
8:21 PM — Interaction occurs
```

and instead **see a visual representation of how a theory may have unfolded**.

Reconstructed sequences may contain inferred details and should be understood as visualizations of available evidence and theories—not definitive representations of truth.

---

## ✦ Technology

### Frontend

* **Next.js**
* **TypeScript**
* **Tailwind CSS**
* **shadcn/ui**
* **Framer Motion**
* **React Three Fiber**
* **Three.js**

### Backend

* **FastAPI**
* **Python**
* **Pydantic**

### Database & Authentication

* **Supabase**
* PostgreSQL
* Supabase Auth
* Supabase Storage

### AI

* **Gemini Flash Lite** — primary AI model
* **OpenRouter** — fallback provider

---

## ◈ Architecture

```text
                    ┌──────────────────┐
                    │      Next.js     │
                    │   Web Interface  │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │     FastAPI      │
                    │ Investigation API│
                    └────────┬─────────┘
                             │
             ┌───────────────┼───────────────┐
             │               │               │
             ▼               ▼               ▼
        Gemini AI        Supabase       Reconstruction
                                          Engine
             │                               │
             ▼                               ▼
       Investigation                  Scene Instructions
           Data                              │
                                             ▼
                                   React Three Fiber
                                             │
                                             ▼
                                      3D Simulation
```

---

## ◎ Typical Experience

A user can:

1. Create an account and sign in
2. Select an investigation
3. Let KHOJ analyze available source information
4. Explore extracted evidence
5. Review the generated timeline
6. Compare possible theories
7. Generate a reconstruction
8. Watch the resulting 3D simulation

---

## ⚡ Getting Started

### Prerequisites

You will need:

* Node.js and npm
* Python
* a Supabase project
* a Gemini API key

### Clone

```bash
git clone <repository-url>
cd khoj
```

### Frontend

```bash
cd frontend
npm install
npm run build
```

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

- Copy `.env.example` to `.env` and fill in secrets.
- Requires running Supabase project (see Supabase docs).

### Docker Compose

```bash
docker-compose up --build
```

### Health Check

FastAPI backend exposes `/health` for readiness probes.

---
See `/docs/context.md` for stack, compliance, and milestone ledger.

## Source Collection Engine (Module 3.1)

- Modular async Python service for collecting web sources given a case name.
- Type-safe models and response schemas: `title`, `url`, `source_name`, `published_at`, `content`.
- Deduplication and filtering of results.
- Extensible provider-based design (e.g., DuckDuckGo News).
- FastAPI endpoint: `/api/v1/investigations/sources?case_name=...` returns structured source objects for investigation modules.

---

## 🔐 Environment Variables

Create the required environment files for the frontend and backend.

Example:

```env
GEMINI_API_KEY=
SUPABASE_URL=
SUPABASE_ANON_KEY=
BACKEND_CORS_ORIGINS=http://localhost:3000
```

Additional variables may be required depending on deployment and fallback-provider configuration.

Never commit secrets or API keys to the repository.

---

## 📁 Repository

```text
khoj/
├── frontend/       # Next.js application
├── backend/        # FastAPI application
├── data/           # Case/source data when required
├── docs/           # Technical specifications and documentation
├── .env.example
└── README.md
```

Detailed architecture, schemas, APIs, and development specifications belong in the [`docs/`](./docs/) directory rather than this README.

---

## ⚠️ Responsible Use

KHOJ does **not** claim to determine absolute truth.

AI-generated evidence relationships, theories, confidence values, and visual reconstructions may contain uncertainty or inference.

The platform is designed to help users:

* organize available information
* understand relationships between sources
* compare perspectives
* explore possible explanations

It should not be treated as an authoritative legal, forensic, or investigative conclusion.

---

## 🚀 Project Goal

KHOJ demonstrates a single connected AI workflow:

```text
Information
    ↓
Evidence
    ↓
Timeline
    ↓
Theories
    ↓
Reconstruction
    ↓
3D Simulation
```

**Turning investigation from something you only read into something you can explore.**


## Evidence Extraction Engine (Module 3.2)

- Implements modular, async service for extracting structured evidence from collected sources using Gemini Flash Lite.
- Type-safe Evidence model/schema with fields: claim, source, confidence, evidence_type, reasoning.
- Gemini model isolated behind `GeminiClient` for provider independence.
- Defensive handling of malformed AI output; all results validated with Pydantic.
- Test: `pytest backend/tests/test_evidence_engine.py`

## Timeline Engine (Module 3.3)

- Implements timeline generation as a modular Python service using extracted evidence objects as input.
- Type-safe TimelineEvent model/schema with fields: time, event, confidence, supporting_evidence.
- Merges duplicate events (same time and normalized event text), preserves supporting evidence references, and orders events chronologically.
- Output matches required contract for frontend consumption and is strictly validated by Pydantic.
- FastAPI POST endpoint: `/api/v1/investigations/timeline/generate` returns timeline events from evidence objects.
