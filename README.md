<img width="2752" height="1536" alt="Crime_scene_banner_design_2K_202608130721" src="https://github.com/user-attachments/assets/ba3242e7-0c29-4c83-99bf-42ff6aabf450" />


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

* **Python 3.9+** (for backend)
* **Node.js 18+** and npm (for frontend)
* **Supabase project** ([create one here](https://supabase.com))
* **Gemini API key** ([get one here](https://aistudio.google.com/app/apikey))

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment (recommended):**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your credentials:
   ```env
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_ANON_KEY=your-supabase-anon-key
   BACKEND_CORS_ORIGINS=http://localhost:3000
   GEMINI_API_KEY=your-gemini-api-key
   OPENROUTER_API_KEY=your-openrouter-key  # Optional fallback
   ```

5. **Start the backend server:**
   ```bash
   uvicorn app.main:app --reload
   ```
   
   Backend will be available at `http://localhost:8000`
   
   API documentation: `http://localhost:8000/docs`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure environment:**
   
   Create `.env.local` with your Supabase credentials:
   ```env
   NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

4. **Start development server:**
   ```bash
   npm run dev
   ```
   
   Frontend will be available at `http://localhost:3000`

### Docker Compose (Alternative)

Run the entire stack with Docker:

```bash
docker-compose up --build
```

### Verify Setup

1. **Backend health check:**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Test Investigation API:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/investigations/run \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -d '{"case_name": "test investigation"}'
   ```

### Running Tests

Backend includes validation scripts:

```bash
cd backend
python validate_imports.py
```

For unit tests (requires pytest):
```bash
pytest tests/
```

---

## 📡 Investigation Engine API

The backend provides a complete investigation pipeline with the following authenticated endpoints:

### Full Investigation Pipeline

```http
POST /api/v1/investigations/run
Authorization: Bearer {token}
Content-Type: application/json

{
  "case_name": "JFK Assassination Investigation"
}
```

**Response:** Complete investigation object with sources, evidence, timeline, theories, and summary.

### Individual Stages

- **Source Collection:** `GET /api/v1/investigations/sources?case_name=...`
- **Timeline Generation:** `POST /api/v1/investigations/timeline/generate`
- **Theory Generation:** `POST /api/v1/investigations/theories/generate`
- **Summary Generation:** `POST /api/v1/investigations/summary/generate`

See `/docs/API_SPEC.md` for detailed endpoint documentation.

---

## 🔐 Environment Variables

```env
# Backend (.env)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
BACKEND_CORS_ORIGINS=http://localhost:3000
GEMINI_API_KEY=your-gemini-api-key
OPENROUTER_API_KEY=your-openrouter-key  # Optional

# Frontend (.env.local)
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Security:** Never commit secrets or API keys to the repository. Use `.env` files (which are gitignored).

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

---

## 🧪 AI Models & Tools Used

### Primary AI Model
- **Gemini 2.0 Flash Lite** — Google's lightweight generative AI model for evidence extraction, timeline generation, theory development, and investigation summarization

### Fallback Provider
- **OpenRouter** — Multi-model API gateway (implementation complete, currently unused)

### Development Tools
- **GitHub Copilot** — AI pair programming assistant
- **Kiro IDE** — AI-powered development environment

### Libraries & Frameworks
All open-source dependencies are listed in:
- `backend/requirements.txt` (Python)
- `frontend/package.json` (Node.js)

### Licenses
- FastAPI: MIT License
- Next.js: MIT License
- Pydantic: MIT License
- Three.js: MIT License
- shadcn/ui: MIT License

See individual library documentation for complete license information.

---

## 🏗️ Implementation Status

### ✅ Completed Modules

**Phase 1 - Authentication**
- Supabase Auth integration
- JWT token validation
- 2FA support

**Phase 3 - Investigation Engine (100% Complete)**
- Source collection with DuckDuckGo provider
- Evidence extraction with Gemini AI
- Timeline generation with AI + fallback regex
- Theory generation (≥3 competing theories)
- Investigation summarization
- Unified orchestration pipeline
- All API endpoints tested and validated

### 🚧 In Progress

**Phase 2 - Case Management**
- Database schema design
- CRUD operations

**Phase 4-8 - Frontend & Visualization**
- Investigation dashboard UI
- Evidence board visualization
- 3D reconstruction engine
- Interactive simulation viewer

---
