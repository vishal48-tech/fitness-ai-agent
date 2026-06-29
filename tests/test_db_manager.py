"""
tests/test_db_manager.py
Unit tests for src/database/db_manager.py
"""
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Clean cached modules so we can patch imports/configurations cleanly
for mod in ["src.database.db_manager"]:
    if mod in sys.modules:
        del sys.modules[mod]

from src.database.db_manager import DBManager

class TestDBManager:
    @patch("src.database.db_manager.get_supabase")
    def test_get_or_create_profile_existing(self, mock_get_supabase):
        mock_client = MagicMock()
        mock_get_supabase.return_value = mock_client
        
        # Mock supabase.table("profiles").select("*").eq("id", user_id).execute()
        mock_response = MagicMock()
        mock_response.data = [{"id": "user123", "display_name": "Test User", "fitness_level": "advanced"}]
        
        mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response

        res = DBManager.get_or_create_profile("user123")
        assert res["id"] == "user123"
        assert res["fitness_level"] == "advanced"
        
        # Verify that insert was NOT called
        mock_client.table.return_value.insert.assert_not_called()

    @patch("src.database.db_manager.get_supabase")
    def test_get_or_create_profile_new(self, mock_get_supabase):
        mock_client = MagicMock()
        mock_get_supabase.return_value = mock_client
        
        # Select returns nothing
        mock_select_response = MagicMock()
        mock_select_response.data = []
        
        # Insert returns the newly created profile
        mock_insert_response = MagicMock()
        mock_insert_response.data = [{"id": "new_user", "display_name": "New Athlete"}]
        
        mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_select_response
        mock_client.table.return_value.insert.return_value.execute.return_value = mock_insert_response

        res = DBManager.get_or_create_profile("new_user", user_metadata={"display_name": "New Athlete"})
        assert res["id"] == "new_user"
        assert res["display_name"] == "New Athlete"
        
        mock_client.table.return_value.insert.assert_called_once()

    @patch("src.database.db_manager.get_supabase")
    def test_update_profile(self, mock_get_supabase):
        mock_client = MagicMock()
        mock_get_supabase.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.data = [{"id": "user123", "goals": "Build muscle"}]
        mock_client.table.return_value.update.return_value.eq.return_value.execute.return_value = mock_response

        res = DBManager.update_profile("user123", goals="Build muscle")
        assert res["goals"] == "Build muscle"
        mock_client.table.return_value.update.assert_called_once_with({"goals": "Build muscle"})

    @patch("src.database.db_manager.get_supabase")
    def test_log_workout(self, mock_get_supabase):
        mock_client = MagicMock()
        mock_get_supabase.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.data = [{"id": "log123", "workout_type": "HIIT", "duration": 45}]
        mock_client.table.return_value.insert.return_value.execute.return_value = mock_response

        res = DBManager.log_workout("user123", "HIIT", 45, difficulty="hard", notes="Sweated a lot")
        assert res["workout_type"] == "HIIT"
        mock_client.table.return_value.insert.assert_called_once_with({
            "user_id": "user123",
            "workout_type": "HIIT",
            "duration": 45,
            "difficulty": "hard",
            "notes": "Sweated a lot"
        })

    @patch("src.database.db_manager.get_supabase")
    def test_get_workout_logs(self, mock_get_supabase):
        mock_client = MagicMock()
        mock_get_supabase.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.data = [{"workout_type": "Yoga"}]
        # Mock chained calls: select().eq().order().limit().execute()
        (mock_client.table.return_value
         .select.return_value
         .eq.return_value
         .order.return_value
         .limit.return_value
         .execute.return_value) = mock_response

        res = DBManager.get_workout_logs("user123", limit=5)
        assert len(res) == 1
        assert res[0]["workout_type"] == "Yoga"

    @patch("src.database.db_manager.get_supabase")
    def test_save_chat_message(self, mock_get_supabase):
        mock_client = MagicMock()
        mock_get_supabase.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.data = [{"id": "msg_id", "content": "hello"}]
        mock_client.table.return_value.insert.return_value.execute.return_value = mock_response

        res = DBManager.save_chat_message("sess123", "user123", "user", "hello")
        assert res["content"] == "hello"
        mock_client.table.return_value.insert.assert_called_once_with({
            "session_id": "sess123",
            "user_id": "user123",
            "role": "user",
            "content": "hello"
        })
