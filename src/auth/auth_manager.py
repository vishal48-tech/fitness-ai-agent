# src/auth/auth_manager.py
"""
AuthManager handles user authentication using the Supabase Client.
Includes sign up, sign in, sign out, checking current session, and Google OAuth.
"""
import secrets
import hashlib
import base64
import os
from typing import Dict, Optional, Any
from src.auth.supabase_client import get_supabase

class AuthManager:
    """Manages authentication actions via Supabase."""

    @staticmethod
    def sign_up(email: str, password: str, display_name: Optional[str] = None) -> Dict[str, Any]:
        """Sign up a new user with email and password."""
        supabase = get_supabase()
        options = {}
        options["data"] = {"display_name": display_name or "User"}
        
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": options
        })
        return response

    @staticmethod
    def sign_in(email: str, password: str) -> Dict[str, Any]:
        """Sign in an existing user with email and password."""
        supabase = get_supabase()
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        return response

    @staticmethod
    def sign_out(jwt: str) -> None:
        """Sign out the current user session using their JWT."""
        supabase = get_supabase()
        # In supabase-py, we sign out using the client's auth object.
        # It handles invalidation based on current active session/client state.
        supabase.auth.sign_out(jwt)

    # @staticmethod
    # def get_google_auth_url() -> str:
    #     """Get the URL to redirect the user to for Google OAuth login.
    #     Generates PKCE code_verifier and stores it for the callback.
    #     """
    #     supabase = get_supabase()
    #     code_verifier, code_challenge = AuthManager._generate_pkce()
    #     AuthManager._save_code_verifier(code_verifier)
        
    #     response = supabase.auth.sign_in_with_oauth({
    #         "provider": "google",
    #         "options": {
    #             "redirect_to": "http://localhost:8501"
    #         }
    #     })
        
    #     if hasattr(response, "url"):
    #         return response.url
    #     elif isinstance(response, dict) and "url" in response:
    #         return response["url"]
    #     return str(response)