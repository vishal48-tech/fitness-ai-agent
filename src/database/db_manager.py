# src/database/db_manager.py
"""
Database manager for AI Fitness Coach V2.
Handles profile persistence, workout logging, and chat session/message management.
"""
from typing import Dict, List, Optional, Any
from src.auth.supabase_client import get_supabase

class DBManager:
    """Manages database interactions via Supabase PostgreSQL."""

    @staticmethod
    def get_or_create_profile(user_id: str, email: Optional[str] = None, user_metadata: Optional[dict] = None) -> Dict[str, Any]:
        """Fetch or create a profile for a given user ID."""
        supabase = get_supabase()
        
        # Check if profile already exists
        response = supabase.table("profiles").select("*").eq("id", user_id).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
            
        # Determine a clean display name
        display_name = "Athlete"
        if user_metadata and user_metadata.get("display_name"):
            display_name = user_metadata.get("display_name")
        elif email:
            display_name = email.split("@")[0].capitalize()

        # Otherwise, insert a default profile
        new_profile = {
            "id": user_id,
            "display_name": display_name,
            "goals": "",
            "limitations": "",
            "equipment": "",
            "fitness_level": "beginner"
        }
        insert_response = supabase.table("profiles").insert(new_profile).execute()
        return insert_response.data[0] if insert_response.data else new_profile

    @staticmethod
    def update_profile(
        user_id: str,
        goals: Optional[str] = None,
        limitations: Optional[str] = None,
        equipment: Optional[str] = None,
        fitness_level: Optional[str] = None,
        display_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update a user's fitness profile parameters."""
        supabase = get_supabase()
        update_data = {}
        if goals is not None:
            update_data["goals"] = goals
        if limitations is not None:
            update_data["limitations"] = limitations
        if equipment is not None:
            update_data["equipment"] = equipment
        if fitness_level is not None:
            update_data["fitness_level"] = fitness_level
        if display_name is not None:
            update_data["display_name"] = display_name

        response = supabase.table("profiles").update(update_data).eq("id", user_id).execute()
        return response.data[0] if response.data else {}

    @staticmethod
    def log_workout(
        user_id: str,
        workout_type: str,
        duration: int,
        difficulty: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Log a completed workout session."""
        supabase = get_supabase()
        workout = {
            "user_id": user_id,
            "workout_type": workout_type,
            "duration": duration,
            "difficulty": difficulty or "moderate",
            "notes": notes or ""
        }
        response = supabase.table("workout_logs").insert(workout).execute()
        return response.data[0] if response.data else {}

    @staticmethod
    def get_workout_logs(user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve recent workout logs for a user."""
        supabase = get_supabase()
        response = (
            supabase.table("workout_logs")
            .select("*")
            .eq("user_id", user_id)
            .order("logged_at", desc=True)
            .limit(limit)
            .execute()
        )
        return response.data or []

    @staticmethod
    def create_chat_session(user_id: str, title: str = "New Chat Session") -> Dict[str, Any]:
        """Create a new chat session for user."""
        supabase = get_supabase()
        session = {
            "user_id": user_id,
            "title": title
        }
        response = supabase.table("chat_sessions").insert(session).execute()
        return response.data[0] if response.data else {}

    @staticmethod
    def get_chat_sessions(user_id: str) -> List[Dict[str, Any]]:
        """Get all chat sessions for a user."""
        supabase = get_supabase()
        response = (
            supabase.table("chat_sessions")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )
        return response.data or []

    @staticmethod
    def save_chat_message(
        session_id: str,
        user_id: str,
        role: str,
        content: str
    ) -> Dict[str, Any]:
        """Save an individual chat message in a session."""
        supabase = get_supabase()
        message = {
            "session_id": session_id,
            "user_id": user_id,
            "role": role,
            "content": content
        }
        response = supabase.table("chat_messages").insert(message).execute()
        return response.data[0] if response.data else {}

    @staticmethod
    def get_chat_messages(session_id: str) -> List[Dict[str, Any]]:
        """Retrieve historical chat messages for a session."""
        supabase = get_supabase()
        response = (
            supabase.table("chat_messages")
            .select("*")
            .eq("session_id", session_id)
            .order("created_at", desc=False)
            .execute()
        )
        return response.data or []
