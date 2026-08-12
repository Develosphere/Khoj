import base64
import json
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.supabase import get_user_from_token

security = HTTPBearer(auto_error=False)


def _require_bearer_token(creds: HTTPAuthorizationCredentials | None) -> str:
    if creds is None or creds.scheme.lower() != "bearer" or not creds.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header. Use 'Authorization: Bearer <token>'.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return creds.credentials


def _decode_jwt_payload(token: str) -> dict[str, Any]:
    """Decode JWT payload claims without re-verifying the signature.

    Supabase verification is handled by `get_current_user`; this helper only
    reads already-present claims such as `aal` for authorization decisions.
    """
    try:
        payload_segment = token.split(".")[1]
        padded_payload = payload_segment + "=" * (-len(payload_segment) % 4)
        decoded = base64.urlsafe_b64decode(padded_payload.encode("utf-8"))
        payload = json.loads(decoded.decode("utf-8"))
    except (IndexError, ValueError, json.JSONDecodeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid JWT payload.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    if not isinstance(payload, dict):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid JWT payload.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def _classify_auth_failure(message: str) -> str:
    lower = message.lower()
    if "expired" in lower or "jwt expired" in lower:
        return "Token has expired. Please sign in again."
    if "malformed" in lower or "invalid" in lower or "decode" in lower:
        return "Malformed or invalid token. Please provide a valid Supabase access token."
    return f"Token validation failed: {message}"


async def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(security),
):
    """Retrieve the current user by validating a Supabase access token."""
    token = _require_bearer_token(creds)
    try:
        user = get_user_from_token(token)
    except RuntimeError as exc:
        raise _unauthorized(_classify_auth_failure(str(exc))) from exc

    return user


async def require_mfa(
    creds: HTTPAuthorizationCredentials = Depends(security),
):
    """Require a verified Supabase JWT with an `aal2` MFA assurance level.

    Supabase JWTs include an `aal` claim. Authenticated users with only
    single-factor assurance (`aal1`) are rejected with 403 so the frontend can
    route them through the 2FA challenge before accessing protected resources.
    """
    token = _require_bearer_token(creds)
    try:
        user = get_user_from_token(token)
    except RuntimeError as exc:
        raise _unauthorized(_classify_auth_failure(str(exc))) from exc

    claims = _decode_jwt_payload(token)
    if claims.get("aal") != "aal2":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Multi-factor authentication required. Complete 2FA before accessing this resource.",
        )

    return user
