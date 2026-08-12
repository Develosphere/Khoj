from typing import Any

from app.core.config import settings

try:
    from supabase import create_client
except Exception:  # pragma: no cover - imported at runtime
    create_client = None  # type: ignore


# Initialize Supabase client using environment-backed settings
if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
    raise RuntimeError(
        "Supabase configuration missing. Ensure SUPABASE_URL and SUPABASE_ANON_KEY are set in backend/.env"
    )

if create_client is None:
    raise RuntimeError("supabase library is not available. Add 'supabase' to your requirements and install dependencies")

supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)


def get_user_from_token(token: str) -> Any:
    """Validate a Supabase JWT and return the user payload.

    This helper tries the common supabase-py call signatures and returns
    the user object when available. It raises RuntimeError with a
    descriptive message on failure.
    """
    if not token:
        raise RuntimeError("Missing token")

    # Different supabase-py versions expose get_user in different places.
    # Try several common call patterns and normalize the result.
    attempts = []

    # 1) supabase.auth.get_user(token)
    try:
        res = supabase_client.auth.get_user(token)
        attempts.append(res)
    except Exception as exc:  # capture and continue trying other methods
        attempts.append({"error": str(exc)})
        res = None

    # 2) supabase.auth.api.get_user(token)
    if not res:
        try:
            res = supabase_client.auth.api.get_user(token)
            attempts.append(res)
        except Exception as exc:
            attempts.append({"error": str(exc)})
            res = None

    # 3) If still no result, raise with collected attempt messages
    if not res:
        msgs = "; ".join([str(a) for a in attempts if a])
        raise RuntimeError(f"Failed to validate token with Supabase: {msgs}")

    # Normalize response shape
    # Common shapes: {'data': {'user': {...}}, 'error': None} or {'user': {...}} or {'data': {...}}
    user = None
    if isinstance(res, dict):
        # Check for direct user
        if res.get("user"):
            user = res.get("user")
        # Check nested data.user
        elif isinstance(res.get("data"), dict) and res["data"].get("user"):
            user = res["data"]["user"]
        # Some versions return data as the user payload directly
        elif isinstance(res.get("data"), dict):
            user = res.get("data")
        # If an error field exists, surface it
        if res.get("error"):
            raise RuntimeError(f"Supabase auth error: {res.get('error')}")
    else:
        # Unknown response type, try to use it directly
        user = res

    if not user:
        raise RuntimeError("Token validation succeeded but no user information was returned")

    return user
