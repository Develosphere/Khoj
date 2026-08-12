from typing import Any

from fastapi import APIRouter, Depends

from app.core.security import get_current_user

router = APIRouter(tags=["auth"])


def _get_user_value(user: Any, key: str, default: Any = None) -> Any:
    """Read a value from either a Supabase User object or dict payload."""
    if isinstance(user, dict):
        return user.get(key, default)
    return getattr(user, key, default)


@router.get("/me")
async def read_current_user(current_user: Any = Depends(get_current_user)):
    """Return the authenticated Supabase user's public profile payload."""
    metadata = _get_user_value(current_user, "user_metadata")
    if metadata is None:
        metadata = _get_user_value(current_user, "raw_user_meta_data", {})

    return {
        "id": _get_user_value(current_user, "id"),
        "email": _get_user_value(current_user, "email"),
        "metadata": metadata or {},
    }
