from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.core.security import get_current_user
from app.core.supabase import supabase

router = APIRouter()


def _read_user_value(user: Any, key: str, default: Any = None) -> Any:
    """Read a field from Supabase user payloads across SDK versions."""
    if isinstance(user, dict):
        return user.get(key, default)
    return getattr(user, key, default)


@router.get("/me")
async def read_current_user(current_user: Any = Depends(get_current_user)) -> dict[str, Any]:
    """Return the authenticated Supabase user's public profile fields."""
    return {
        "id": _read_user_value(current_user, "id"),
        "email": _read_user_value(current_user, "email"),
        "metadata": _read_user_value(current_user, "user_metadata", {}) or {},
    }


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(credentials: AuthCredentials) -> dict[str, Any]:
    """Register a user with Supabase email/password auth."""
    try:
        response = supabase.auth.sign_up(
            {"email": credentials.email, "password": credentials.password}
        )
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    user = _read_nested_value(response, "user") or _read_nested_value(response, "data", "user")
    return {
        "id": _read_user_value(user, "id"),
        "email": _read_user_value(user, "email", credentials.email),
        "metadata": _read_user_value(user, "user_metadata", {}) or {},
    }


@router.post("/login")
async def login_user(credentials: AuthCredentials) -> dict[str, Any]:
    """Authenticate a user with Supabase email/password auth."""
    try:
        response = supabase.auth.sign_in_with_password(
            {"email": credentials.email, "password": credentials.password}
        )
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    session = _read_nested_value(response, "session") or _read_nested_value(response, "data", "session")
    user = _read_nested_value(response, "user") or _read_nested_value(response, "data", "user")
    return {
        "access_token": _read_user_value(session, "access_token"),
        "token_type": "bearer",
        "aal": _read_user_value(session, "aal", "aal1"),
        "user": {
            "id": _read_user_value(user, "id"),
            "email": _read_user_value(user, "email", credentials.email),
            "metadata": _read_user_value(user, "user_metadata", {}) or {},
        },
    }


@router.get("/mfa/protected")
async def read_mfa_protected(current_user: Any = Depends(get_current_user)) -> dict[str, Any]:
    """Example MFA-guarded endpoint requiring an AAL2-authenticated user."""
    aal = _read_user_value(current_user, "aal") or _read_nested_value(current_user, "app_metadata", "aal")
    if aal != "aal2":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="MFA verification required",
        )
    return {"status": "ok", "aal": aal}


class AuthCredentials(BaseModel):
    email: str = Field(..., min_length=3)
    password: str = Field(..., min_length=1)


class MfaChallengeRequest(BaseModel):
    factor_id: str = Field(..., min_length=1)


class MfaVerifyRequest(BaseModel):
    factor_id: str = Field(..., min_length=1)
    challenge_id: str = Field(..., min_length=1)
    code: str = Field(..., min_length=6, max_length=6)


class MfaUnenrollRequest(BaseModel):
    factor_id: str = Field(..., min_length=1)


def _read_nested_value(payload: Any, *keys: str, default: Any = None) -> Any:
    current = payload
    for key in keys:
        if current is None:
            return default
        current = _read_user_value(current, key, default)
    return current if current is not None else default


def _mfa_error(action: str, exc: Exception) -> HTTPException:
    message = str(exc) or f"Unable to {action} MFA factor"
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=message,
    )


@router.post("/mfa/enroll")
async def enroll_mfa_factor(_current_user: Any = Depends(get_current_user)) -> dict[str, Any]:
    """Enroll the authenticated user in Supabase TOTP MFA."""
    try:
        response = supabase.auth.mfa.enroll(factor_type="totp")
    except Exception as exc:
        raise _mfa_error("enroll", exc) from exc

    factor_id = _read_nested_value(response, "id") or _read_nested_value(response, "factor", "id")
    qr_code_url = (
        _read_nested_value(response, "totp", "qr_code")
        or _read_nested_value(response, "totp", "qr_code_url")
        or _read_nested_value(response, "qr_code")
        or _read_nested_value(response, "qr_code_url")
    )

    return {"factor_id": factor_id, "qr_code_url": qr_code_url}


@router.post("/mfa/challenge")
async def challenge_mfa_factor(
    request: MfaChallengeRequest,
    _current_user: Any = Depends(get_current_user),
) -> dict[str, Any]:
    """Create a Supabase MFA challenge for an enrolled factor."""
    try:
        response = supabase.auth.mfa.challenge(factor_id=request.factor_id)
    except Exception as exc:
        raise _mfa_error("challenge", exc) from exc

    return {
        "factor_id": request.factor_id,
        "challenge_id": _read_nested_value(response, "id") or _read_nested_value(response, "challenge", "id"),
        "expires_at": _read_nested_value(response, "expires_at")
        or _read_nested_value(response, "challenge", "expires_at"),
    }


@router.post("/mfa/verify")
async def verify_mfa_factor(
    request: MfaVerifyRequest,
    _current_user: Any = Depends(get_current_user),
) -> dict[str, Any]:
    """Verify a TOTP code and return session data upgraded to AAL2."""
    try:
        response = supabase.auth.mfa.verify(
            factor_id=request.factor_id,
            challenge_id=request.challenge_id,
            code=request.code,
        )
    except Exception as exc:
        raise _mfa_error("verify", exc) from exc

    return {
        "factor_id": request.factor_id,
        "challenge_id": request.challenge_id,
        "aal": _read_nested_value(response, "aal") or "aal2",
        "session": _read_nested_value(response, "session"),
        "access_token": _read_nested_value(response, "session", "access_token")
        or _read_nested_value(response, "access_token"),
    }


@router.post("/mfa/unenroll")
async def unenroll_mfa_factor(
    request: MfaUnenrollRequest,
    _current_user: Any = Depends(get_current_user),
) -> dict[str, Any]:
    """Remove an enrolled Supabase MFA factor."""
    try:
        response = supabase.auth.mfa.unenroll(factor_id=request.factor_id)
    except Exception as exc:
        raise _mfa_error("unenroll", exc) from exc

    return {
        "factor_id": request.factor_id,
        "status": "unenrolled",
        "response": response if isinstance(response, dict) else None,
    }
