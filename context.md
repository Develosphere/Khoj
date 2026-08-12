# Khoj Backend Authentication Context

## Phase 2 Supabase backend authentication — Completed

Implemented backend authentication support for FastAPI using Supabase Auth.

### Completed files

- `backend/app/core/config.py`
  - Added environment-backed settings with `pydantic-settings`.
  - Loads `SUPABASE_URL` and `SUPABASE_ANON_KEY` from environment variables and `.env`.
  - Uses cached `get_settings()` so configuration is centralized and reusable.

- `backend/app/core/supabase.py`
  - Added a Supabase client initialized via `create_client(...)`.
  - The client uses `get_settings().SUPABASE_URL` and `get_settings().SUPABASE_ANON_KEY`.
  - No static Supabase URL or key strings are embedded in code.

- `backend/app/core/security.py`
  - Added FastAPI `get_current_user` dependency.
  - Uses `HTTPBearer(auto_error=False)` to extract `Authorization: Bearer <token>` credentials.
  - Validates JWTs with `supabase.auth.get_user(token)`.
  - Returns the Supabase user payload for valid tokens.
  - Raises `401 Unauthorized` with `WWW-Authenticate: Bearer` for:
    - missing authorization header,
    - malformed/non-Bearer authorization header,
    - empty JWT token,
    - expired JWT token,
    - invalid or malformed JWT token.

- `backend/requirements.txt`
  - Added FastAPI, Uvicorn, pydantic-settings, and supabase dependencies needed by the backend authentication implementation.

### Environment variables required

The backend requires these values in the environment or `.env` file:

```env
SUPABASE_URL=your-supabase-project-url
SUPABASE_ANON_KEY=your-supabase-anon-key
```

### Usage example

FastAPI routes can protect endpoints by depending on `get_current_user`:

```python
from fastapi import APIRouter, Depends
from app.core.security import get_current_user

router = APIRouter()

@router.get("/me")
async def read_me(current_user = Depends(get_current_user)):
    return current_user
```

---

## Phase 3 authenticated user endpoint — Completed

Implemented the authenticated user profile endpoint and API router wiring.

### Completed files

- `backend/app/api/v1/endpoints/auth.py`
  - Added an `APIRouter` for authentication-related endpoints.
  - Added `GET /me`, protected by the Phase 2 `get_current_user` dependency.
  - Returns the authenticated Supabase user's `id`, `email`, and `metadata`.
  - Handles Supabase user payloads represented either as SDK objects or dictionaries.

- `backend/app/api/v1/router.py`
  - Added the versioned root API router.
  - Includes authentication routes under the `/auth` prefix.

- `backend/app/main.py`
  - Created the FastAPI application entrypoint.
  - Mounted the v1 API router under `/api/v1`.
  - Added a lightweight `/health` endpoint for service checks.

- Package initializers
  - Added `__init__.py` files for the new `backend/app/api`, `backend/app/api/v1`, and `backend/app/api/v1/endpoints` packages.

- `.env.example`
  - Documented required Supabase environment variables.

### Available endpoint

```http
GET /api/v1/auth/me
Authorization: Bearer <supabase-access-token>
```

Successful responses return:

```json
{
  "id": "user-id",
  "email": "user@example.com",
  "metadata": {}
}
```

---

## Phase 4 CORS and auth endpoint verification — Completed

Implemented environment-backed CORS configuration and authentication endpoint verification.

### Completed files

- `backend/app/core/config.py`
  - Added `CORS_ALLOWED_ORIGINS`, `CORS_ALLOWED_METHODS`, and `CORS_ALLOWED_HEADERS` settings.
  - Values are loaded from environment variables or `.env`, keeping CORS configuration out of hardcoded application logic.

- `backend/app/main.py`
  - Added FastAPI `CORSMiddleware`.
  - Uses `get_settings()` for allowed origins, methods, and headers.
  - Keeps the v1 API router mounted at `/api/v1`.

- `backend/tests/test_auth.py`
  - Added verification that `GET /api/v1/auth/me` without an authorization header returns `401`.
  - Added mocked Supabase auth validation for a valid bearer token and verifies the endpoint returns user `id`, `email`, and `metadata`.

- `backend/requirements.txt`
  - Added `pytest` and `httpx` for FastAPI test execution.

- `.env.example`
  - Documented CORS environment variables:
    - `CORS_ALLOWED_ORIGINS`
    - `CORS_ALLOWED_METHODS`
    - `CORS_ALLOWED_HEADERS`

### Verification commands

```bash
pip install -r backend/requirements.txt
pytest backend/tests
uvicorn app.main:app --app-dir backend --reload
```

The server startup command uses the existing backend app module and will load Supabase and CORS settings from the environment or `.env`.

---

## Phase 4 MFA enrollment and verification endpoints — Completed

Implemented authenticated Supabase TOTP MFA endpoints under the existing `/api/v1/auth` router.

### Completed files

- `backend/app/api/v1/endpoints/auth.py`
  - Added `POST /mfa/enroll`, protected by `get_current_user`.
  - Calls `supabase.auth.mfa.enroll(factor_type="totp")` and returns `factor_id` plus `qr_code_url`.
  - Added `POST /mfa/challenge` to call `supabase.auth.mfa.challenge(factor_id=...)` and return challenge details.
  - Added `POST /mfa/verify` to call `supabase.auth.mfa.verify(factor_id=..., challenge_id=..., code=...)` and return AAL/session data.
  - Added `POST /mfa/unenroll` to call `supabase.auth.mfa.unenroll(factor_id=...)`.
  - Added request models for challenge, verify, and unenroll payload validation.
  - MFA endpoints reuse the environment-configured Supabase client from `backend/app/core/supabase.py`.

- `backend/tests/test_auth.py`
  - Extended the existing auth tests with mocked Supabase MFA coverage for enroll, challenge, verify, and unenroll flows.

### Available MFA endpoints

```http
POST /api/v1/auth/mfa/enroll
Authorization: Bearer <supabase-access-token>

POST /api/v1/auth/mfa/challenge
Authorization: Bearer <supabase-access-token>
Content-Type: application/json

{"factor_id":"factor-id"}

POST /api/v1/auth/mfa/verify
Authorization: Bearer <supabase-access-token>
Content-Type: application/json

{"factor_id":"factor-id","challenge_id":"challenge-id","code":"123456"}

POST /api/v1/auth/mfa/unenroll
Authorization: Bearer <supabase-access-token>
Content-Type: application/json

{"factor_id":"factor-id"}
```

---

## Phase 5 CORS and comprehensive auth test suite — Completed

Implemented the Phase 5 authentication hardening and test coverage.

### Completed files

- `backend/app/core/config.py`
  - Added `BACKEND_CORS_ORIGINS`, `BACKEND_CORS_METHODS`, and `BACKEND_CORS_HEADERS` environment-backed settings.
  - Defaults now allow `GET`, `POST`, `OPTIONS`, `PUT`, and `DELETE`, with `Authorization` and `Content-Type` headers.
  - Kept compatibility properties used by `backend/app/main.py`.

- `backend/app/main.py`
  - Continues to apply `CORSMiddleware` using settings loaded from `.env` rather than hardcoded route configuration.

- `backend/app/api/v1/endpoints/auth.py`
  - Added `POST /auth/register` using `supabase.auth.sign_up`.
  - Added `POST /auth/login` using `supabase.auth.sign_in_with_password`.
  - Added `GET /auth/mfa/protected` as an MFA/AAL2-guarded verification endpoint.

- `backend/tests/test_auth.py`
  - Expanded mocked Supabase coverage for registration success/error, login success/error, JWT `/me` valid/invalid/missing token behavior, MFA enroll/challenge/verify/unenroll, and MFA guard `aal1` 403 vs `aal2` 200 behavior.

- `backend/requirements.txt`
  - Added `pytest-asyncio` alongside existing `pytest` and `httpx` test dependencies.

- `.env.example` and `README.md`
  - Updated CORS examples to use `BACKEND_CORS_*` variables.

### Verification commands

```bash
pip install -r backend/requirements.txt
pytest backend/tests
uvicorn app.main:app --app-dir backend --reload
```
