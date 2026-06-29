"""
tests/test_settings.py
Unit tests for config/settings.py

Run with:
    pytest tests/test_settings.py -v
"""
import os
import sys
import importlib
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# ---------------------------------------------------------------------------
# Ensure project root is on sys.path so 'config' package is importable
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# ---------------------------------------------------------------------------
# Helper: reload settings with a fully controlled environment.
# Patches both os.environ AND load_dotenv so the .env file cannot
# interfere with the values we want to test.
# ---------------------------------------------------------------------------
def _reload_settings(env_override: dict):
    """Reload config.settings with fully controlled environment.

    Patches os.environ AND the dotenv.load_dotenv function at the
    package level so the .env file is never read during the reload.
    """
    import config.settings as settings_module

    # Patch at the dotenv package level to intercept wherever it's imported from
    with patch("dotenv.main.load_dotenv", return_value=None), \
         patch("dotenv.load_dotenv", return_value=None), \
         patch.dict(os.environ, env_override, clear=True):
        importlib.reload(settings_module)
        return settings_module


# ---------------------------------------------------------------------------
# Tests: Supabase constants
# ---------------------------------------------------------------------------
class TestSupabaseSettings:
    def test_supabase_url_reads_from_env(self):
        s = _reload_settings({"SUPABASE_URL": "https://abc.supabase.co"})
        assert s.SUPABASE_URL == "https://abc.supabase.co"

    def test_supabase_url_defaults_to_empty_string(self):
        # load_dotenv is patched at package level so .env file is skipped
        s = _reload_settings({})
        assert s.SUPABASE_URL == ""

    def test_supabase_publishable_key_reads_from_env(self):
        s = _reload_settings({"SUPABASE_PUBLISHABLE_KEY": "eyJpublishablekey"})
        assert s.SUPABASE_PUBLISHABLE_KEY == "eyJpublishablekey"

    def test_supabase_publishable_key_is_string(self):
        # Verify the attribute exists and is always a string (env may be set)
        import config.settings as s
        assert isinstance(s.SUPABASE_PUBLISHABLE_KEY, str)

    def test_supabase_secret_key_reads_from_env(self):
        s = _reload_settings({"SUPABASE_SECRET_KEY": "secret-role-key"})
        assert s.SUPABASE_SECRET_KEY == "secret-role-key"

    def test_supabase_secret_key_is_string(self):
        # Verify the attribute exists and is always a string (env may be set)
        import config.settings as s
        assert isinstance(s.SUPABASE_SECRET_KEY, str)

    def test_auth_redirect_url_default(self):
        s = _reload_settings({})
        assert s.SUPABASE_AUTH_REDIRECT_URL == "http://localhost:8501"

    def test_auth_redirect_url_override(self):
        s = _reload_settings(
            {"SUPABASE_AUTH_REDIRECT_URL": "https://myapp.streamlit.app"}
        )
        assert s.SUPABASE_AUTH_REDIRECT_URL == "https://myapp.streamlit.app"

    def test_session_key_constants(self):
        import config.settings as s
        assert s.SUPABASE_SESSION_KEY == "supabase_session"
        assert s.SUPABASE_USER_KEY == "supabase_user"


# ---------------------------------------------------------------------------
# Tests: Groq constants
# ---------------------------------------------------------------------------
class TestGroqSettings:
    def test_groq_model_is_string(self):
        import config.settings as s
        assert isinstance(s.GROQ_MODEL, str)
        assert len(s.GROQ_MODEL) > 0

    def test_groq_models_dict_has_entries(self):
        import config.settings as s
        assert isinstance(s.GROQ_MODELS, dict)
        assert len(s.GROQ_MODELS) >= 3

    def test_groq_models_values_are_strings(self):
        import config.settings as s
        for name, model_id in s.GROQ_MODELS.items():
            assert isinstance(name, str), f"Key '{name}' is not a string"
            assert isinstance(model_id, str), f"Value '{model_id}' is not a string"
            assert len(model_id) > 0, f"Model ID for '{name}' is empty"

    def test_default_model_is_in_groq_models(self):
        import config.settings as s
        assert s.GROQ_MODEL in s.GROQ_MODELS.values(), (
            f"GROQ_MODEL '{s.GROQ_MODEL}' not found in GROQ_MODELS values"
        )

    def test_groq_api_key_reads_from_env(self):
        s = _reload_settings({"GROQ_API_KEY": "gsk_test_key"})
        assert s.GROQ_API_KEY == "gsk_test_key"


# ---------------------------------------------------------------------------
# Tests: ChromaDB Cloud constants
# ---------------------------------------------------------------------------
class TestChromaSettings:
    def test_chroma_api_key_reads_from_env(self):
        s = _reload_settings({"CHROMA_API_KEY": "ck-test-key"})
        assert s.CHROMA_API_KEY == "ck-test-key"

    def test_chroma_api_key_defaults_empty(self):
        s = _reload_settings({})
        assert s.CHROMA_API_KEY == ""

    def test_chroma_tenant_reads_from_env(self):
        s = _reload_settings({"CHROMA_TENANT": "my-tenant"})
        assert s.CHROMA_TENANT == "my-tenant"

    def test_chroma_database_reads_from_env(self):
        s = _reload_settings({"CHROMA_DATABASE": "fitness-db"})
        assert s.CHROMA_DATABASE == "fitness-db"

    def test_chroma_attrs_are_strings(self):
        import config.settings as s
        assert isinstance(s.CHROMA_API_KEY, str)
        assert isinstance(s.CHROMA_TENANT, str)
        assert isinstance(s.CHROMA_DATABASE, str)


# ---------------------------------------------------------------------------
# Tests: Agent / LLM constants
# ---------------------------------------------------------------------------
class TestAgentSettings:
    def test_max_conversation_turns_positive(self):
        import config.settings as s
        assert s.MAX_CONVERSATION_TURNS > 0

    def test_similarity_threshold_in_range(self):
        import config.settings as s
        assert 0.0 <= s.SIMILARITY_THRESHOLD <= 1.0

    def test_max_tokens_positive(self):
        import config.settings as s
        assert s.MAX_TOKENS > 0

    def test_temperature_in_valid_range(self):
        import config.settings as s
        assert 0.0 <= s.TEMPERATURE <= 2.0


# ---------------------------------------------------------------------------
# Tests: Streamlit metadata
# ---------------------------------------------------------------------------
class TestStreamlitSettings:
    def test_page_title_is_set(self):
        import config.settings as s
        assert s.PAGE_TITLE == "AI Fitness Coach"

    def test_page_icon_is_emoji(self):
        import config.settings as s
        assert len(s.PAGE_ICON) > 0

    def test_app_version_exists(self):
        import config.settings as s
        assert hasattr(s, "APP_VERSION")
        assert s.APP_VERSION.startswith("2.")


# ---------------------------------------------------------------------------
# Tests: BASE_DIR
# ---------------------------------------------------------------------------
class TestBaseDirSettings:
    def test_base_dir_is_path(self):
        import config.settings as s
        assert isinstance(s.BASE_DIR, Path)

    def test_base_dir_exists(self):
        import config.settings as s
        assert s.BASE_DIR.exists()
