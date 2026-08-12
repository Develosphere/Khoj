# KHOJ Project Context

## Project

**Name:** KHOJ — AI Investigation & 3D Reconstruction Platform

**Description:**
KHOJ is an AI-powered web platform that transforms fragmented case information into structured evidence, timelines, competing theories, and interactive 3D reconstructions.

**Purpose:**
Help users understand complex real-world events by organizing available information, comparing possible explanations, and visually reconstructing selected theories without claiming absolute truth.

## Approved Stack

Frontend:
- Next.js App Router
- TypeScript
- Tailwind CSS
- shadcn/ui
- Framer Motion
- React Three Fiber
- Three.js

Backend:
- FastAPI
- Python
- Pydantic

Database / Authentication:
- Supabase PostgreSQL
- Supabase Auth
- Supabase Storage
- Authentication must support sign-up, sign-in, sessions, and 2FA

AI:
- Gemini Flash Lite Latest as primary application model
- OpenRouter only as fallback where required

## Project Modules

1. Authentication
2. Case Management
3. Evidence Engine
4. Timeline Engine
5. Theory Engine
6. Evidence Board
7. Reconstruction Engine
8. Simulation Viewer

Do not add module implementation details here. Each module receives its own independent development prompt.

## Hackathon Compliance

The project must follow these rules:

- Core functionality must make real live AI model calls.
- Production user/project data must use a persistent real database.
- Do not use in-memory arrays, localStorage-only persistence, or hardcoded JSON as production storage.
- Authentication must include sign-up, sign-in, and 2FA.
- The interface must be professional and contain no placeholder content in the final demo.
- Ideas may pre-exist, but hackathon project code must be written during the event.
- Repository must have been created after official build kickoff.
- First commit must be timestamped after kickoff.
- Commit throughout development rather than creating one final dump.
- Public repository is required.
- README must contain setup instructions.
- Final documentation must disclose AI tools/models used.
- Final documentation must disclose reused components/libraries and relevant licenses.
- At least two DevMarketplace code gigs must be published during the event.
- Gigs must contain code genuinely written for this project during the hackathon.
- Each gig requires a title, description, and usable setup instructions.
- Do not republish third-party/open-source code as a gig.
- Credit all appropriate team contributors on gigs.
- Pre-event prototype/research code must not be copied into the hackathon implementation unless explicitly permitted and declared.

## AI Agent Rules

1. Read this file before beginning a fresh development task.
2. Treat the current module prompt as the authoritative specification for that module.
3. Inspect only files explicitly named by the task or genuinely required by direct dependencies.
4. Do not scan the entire repository unless explicitly requested.
5. Never invent existing files, routes, APIs, database columns, environment variables, schemas, or completed functionality. Inspect the repository when uncertain.
6. Do not modify unrelated modules.
7. Avoid unsolicited refactoring.
8. Reuse existing project utilities/types/components when appropriate instead of creating duplicates.
9. Use only the approved stack unless explicitly authorized.
10. Keep responses concise and implementation-focused.
11. Do not repeat the entire project context back to the user.
12. Run relevant tests, type checks, or build checks after implementation and fix errors caused by your changes.
13. Do not use fake/hardcoded production data where persistent database data is required.
14. Do not replace required live AI behavior with mocked AI responses in the final application.
15. Optimize for the smallest correct implementation satisfying the current task.

## Current Build State

**Last Updated:** 2024-06-08 PKT

- Project foundation scaffolded with all required stack, directories, and minimal CORS/health endpoint.
- No business logic implemented yet (per hackathon rules).

## Compliance / Milestone Ledger

Maintain concise timestamped milestone entries using:

`YYYY-MM-DD HH:MM PKT — milestone`

2024-06-08 18:00 PKT — project foundation scaffold complete

Only record meaningful milestones such as:
- repository creation
- first commit
- module completion
- live AI integration
- database integration
- 2FA verification
- published DevMarketplace gigs
- deployment
- major integration completion

Do not record every minor file edit.

Never fabricate timestamps or completed milestones.

## Next Task

Implement Authentication (sign-up, sign-in, Supabase sessions, 2FA) module foundation.

---

Keep this file compact.

Do not add:
- detailed module specifications
- database schemas
- API documentation
- full file trees
- long implementation histories
- verbose agent summaries

Those belong in dedicated documentation or Git history.
## Backend Authentication Module Setup

- Created `backend` directory structure.
- Added `requirements.txt` with FastAPI, Supabase, python-dotenv, pydantic, and pydantic-settings.
- Added `.env` and `.env.example` files with Supabase credential placeholders.
- Implemented configuration manager using pydantic-settings in `backend/app/core/config.py` to load credentials dynamically and perform strict validation; missing keys produce descriptive errors on startup.
- Created a basic FastAPI app with a health check endpoint in `backend/app/main.py`.

All credentials are loaded dynamically from the `.env` file with validation and no hardcoded secrets.

# Backend Authentication Module Setup - Phase 1

- Created `backend` directory with necessary structure.
- Added `backend/requirements.txt` with core dependencies: fastapi, uvicorn[standard], supabase, python-dotenv, pydantic, pydantic-settings.
- Added `backend/.env` and `backend/.env.example` with placeholders for SUPABASE_URL and SUPABASE_ANON_KEY.
- Implemented configuration manager in `backend/app/core/config.py` using pydantic-settings to load environment variables from `.env` file with validation.
- Added a basic FastAPI app in `backend/app/main.py` with a health check endpoint `/health`.

# Backend Authentication Module Setup - Phase 2

- Implemented `backend/app/core/supabase.py` to initialize the Supabase client from environment-backed settings. The module raises a clear error if credentials are missing or the supabase library is unavailable.
- Implemented `backend/app/core/security.py` providing a FastAPI dependency `get_current_user` that:
  - Extracts Bearer tokens via HTTPBearer
  - Validates tokens using the Supabase client
  - Returns user payload on success
  - Raises 401 Unauthorized with descriptive messages on missing/invalid/expired tokens

# Backend Authentication Module Setup

- Created `backend` directory and added `requirements.txt` with FastAPI and Supabase dependencies.
- Added `backend/.env` and `backend/.env.example` files with placeholders for Supabase URL and anon key.
- Implemented configuration manager in `backend/app/core/config.py` using `pydantic-settings` to load environment variables with validation.
- Created basic FastAPI app entry point in `backend/app/main.py` with a health check endpoint returning app status and loaded Supabase URL.

# Backend Authentication Module Setup - Phase 3

- Added `backend/app/api/v1/endpoints/auth.py` with authenticated `GET /me` endpoint.
- Added `backend/app/api/v1/router.py` and included auth routes under `/auth`.
- Mounted the v1 API router in `backend/app/main.py` under `/api/v1`.
- `/api/v1/auth/me` now returns the authenticated user's ID, email, and metadata via the Supabase-backed `get_current_user` dependency.

# Backend Authentication Module Setup - Phase 4

- Added environment-backed `BACKEND_CORS_ORIGINS` configuration using `pydantic-settings`.
- Configured FastAPI `CORSMiddleware` in `backend/app/main.py` with origins loaded from `backend/.env`.
- Added `backend/tests/test_auth.py` covering missing authorization headers and mocked valid Supabase token access to `/api/v1/auth/me`.
