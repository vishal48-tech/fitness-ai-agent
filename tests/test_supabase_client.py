"""
tests/test_supabase_client.py
Unit tests for src/auth/supabase_client.py
"""
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Clean cached modules so we can patch settings cleanly
for mod in ["src.auth.supabase_client", "config.settings"]:
    if mod in sys.modules:
        del sys.modules[mod]

import src.auth.supabase_client as sc

class TestSupabaseClient:
    @patch("src.auth.supabase_client.create_client")
    def test_get_supabase_singleton(self, mock_create_client):
        # Reset the singleton reference for testing
        sc._supabase_client = None
        
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client

        with patch("src.auth.supabase_client.SUPABASE_URL", "https://xyz.supabase.co"), \
             patch("src.auth.supabase_client.SUPABASE_PUBLISHABLE_KEY", "test-key"):
            
            c1 = sc.get_supabase()
            c2 = sc.get_supabase()
            
            assert c1 is mock_client
            assert c2 is mock_client
            mock_create_client.assert_called_once_with("https://xyz.supabase.co", "test-key")

    def test_get_supabase_missing_config_raises_error(self):
        sc._supabase_client = None
        
        with patch("src.auth.supabase_client.SUPABASE_URL", ""), \
             patch("src.auth.supabase_client.SUPABASE_PUBLISHABLE_KEY", ""):
            
            with pytest.raises(ValueError) as excinfo:
                sc.get_supabase()
            assert "SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY" in str(excinfo.value)
