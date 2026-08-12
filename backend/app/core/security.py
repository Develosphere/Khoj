from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.supabase import supabase

bearer_scheme = HTTPBearer(auto_error=False)


def _unauthorized(message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=message,
        headers={"WWW-Authenticate": "Bearer"},
    )


def _extract_user_payload(response: Any) -> Any:
    """Normalize Supabase auth.get_user responses across supabase-py versions."""
    user = getattr(response, "user", None)
    if user is not None:
        return user

    if isinstance(response, dict):
        return response.get("user") or response.get("data", {}).get("user")

    return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> Any:
    """Validate a Supabase JWT from Authorization: Bearer <token>.

    Returns the Supabase user payload when valid. Raises 401 for missing,
    malformed, expired, or otherwise invalid tokens.
    """
    if credentials is None:
        raise _unauthorized("Missing Authorization bearer token")

    if credentials.scheme.lower() != "bearer":
        raise _unauthorized("Malformed authorization header: expected Bearer token")

    token = credentials.credentials.strip() if credentials.credentials else ""
    if not token:
        raise _unauthorized("Missing JWT token")

    try:
        response = supabase.auth.get_user(token)
    except Exception as exc:
        message = str(exc).lower()
        if "expired" in message or "jwt expired" in message:
            raise _unauthorized("JWT token has expired") from exc
        raise _unauthorized("Invalid or malformed JWT token") from exc

    user = _extract_user_payload(response)
    if not user:
        raise _unauthorized("Invalid or expired JWT token")

    return user
