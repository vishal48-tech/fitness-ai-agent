# src/auth/supabase_client.py
"""
Singleton client for Supabase.
"""
from supabase import create_client, Client
from config.settings import SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY

_supabase_client: Client = None

def get_supabase() -> Client:
    """Get the singleton Supabase client instance."""
    global _supabase_client
    if _supabase_client is None:
        if not SUPABASE_URL or not SUPABASE_PUBLISHABLE_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY must be configured in environment.")
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY)
    return _supabase_client
