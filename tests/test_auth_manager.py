"""
tests/test_auth_manager.py
Unit tests for src/auth/auth_manager.py
"""
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import manager after setting up sys.path
from src.auth.auth_manager import AuthManager

class TestAuthManager:
    @patch("src.auth.auth_manager.get_supabase")
    def test_sign_up(self, mock_get_supabase):
        mock_client = MagicMock()
        mock_get_supabase.return_value = mock_client
        mock_client.auth.sign_up.return_value = {"user": "test_user"}

        resp = AuthManager.sign_up("test@example.com", "password123", "Test User")
        
        assert resp == {"user": "test_user"}
        mock_client.auth.sign_up.assert_called_once_with({
            "email": "test@example.com",
            "password": "password123",
            "options": {"data": {"display_name": "Test User"}}
        })

    @patch("src.auth.auth_manager.get_supabase")
    def test_sign_in(self, mock_get_supabase):
        mock_client = MagicMock()
        mock_get_supabase.return_value = mock_client
        mock_client.auth.sign_in_with_password.return_value = {"session": "test_session"}

        resp = AuthManager.sign_in("test@example.com", "password123")
        
        assert resp == {"session": "test_session"}
        mock_client.auth.sign_in_with_password.assert_called_once_with({
            "email": "test@example.com",
            "password": "password123"
        })

    @patch("src.auth.auth_manager.get_supabase")
    def test_sign_out(self, mock_get_supabase):
        mock_client = MagicMock()
        mock_get_supabase.return_value = mock_client

        AuthManager.sign_out("jwt_token")
        mock_client.auth.sign_out.assert_called_once_with("jwt_token")

    @patch("src.auth.auth_manager.get_supabase")
    def test_get_google_auth_url(self, mock_get_supabase):
        mock_client = MagicMock()
        mock_get_supabase.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.url = "https://google.auth.url"
        mock_client.auth.sign_in_with_oauth.return_value = mock_response

        resp = AuthManager.get_google_auth_url()
        
        assert resp == "https://google.auth.url"
        mock_client.auth.sign_in_with_oauth.assert_called_once_with({
            "provider": "google",
            "options": {"redirect_to": "http://localhost:8501"}
        })
