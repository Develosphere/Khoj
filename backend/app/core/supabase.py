from supabase import Client, create_client

from app.core.config import get_settings


_settings = get_settings()

# Supabase client initialized exclusively from environment-backed settings.
supabase: Client = create_client(
    _settings.SUPABASE_URL,
    _settings.SUPABASE_ANON_KEY,
)
