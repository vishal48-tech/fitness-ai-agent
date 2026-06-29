"""
tests/test_fitness_agent.py
Unit tests for src/agent/fitness_agent.py
"""
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Clean cached modules so we can patch imports/configurations cleanly
for mod in ["src.agent.fitness_agent"]:
    if mod in sys.modules:
        del sys.modules[mod]

from src.agent.fitness_agent import GroqFitnessAgent

class TestFitnessAgent:
    @patch("src.agent.fitness_agent.FitnessMemoryStore")
    @patch("src.agent.fitness_agent.ChatGroq")
    def test_agent_initialization(self, mock_chat_groq, mock_memory_store):
        mock_llm = MagicMock()
        mock_chat_groq.return_value = mock_llm
        
        mock_store = MagicMock()
        mock_memory_store.return_value = mock_store

        agent = GroqFitnessAgent(
            user_id="user123",
            groq_api_key="gsk-key",
            model_name="llama-test-model"
        )
        
        assert agent.user_id == "user123"
        mock_chat_groq.assert_called_once()
        mock_memory_store.assert_called_once_with(user_id="user123")

    @patch("src.agent.fitness_agent.FitnessMemoryStore")
    @patch("src.agent.fitness_agent.ChatGroq")
    def test_chat_stream(self, mock_chat_groq, mock_memory_store):
        mock_llm = MagicMock()
        mock_chat_groq.return_value = mock_llm
        
        # Mock streaming chunks
        chunk1 = MagicMock(content="Hello ")
        chunk2 = MagicMock(content="world!")
        mock_llm.stream.return_value = [chunk1, chunk2]
        
        mock_store = MagicMock()
        mock_memory_store.return_value = mock_store
        mock_store.get_relevant_context.return_value = "Past user liked running"

        agent = GroqFitnessAgent(
            user_id="user123",
            groq_api_key="gsk-key"
        )
        
        profile = {
            "display_name": "John Doe",
            "goals": "Lose weight",
            "limitations": "None",
            "equipment": "Dumbbells",
            "fitness_level": "Intermediate"
        }
        
        generator = agent.chat_stream("Suggest a routine", chat_history=[], user_profile=profile)
        chunks = list(generator)

        assert chunks == ["Hello ", "world!"]
        
        # Verify ChromaDB context was requested
        mock_store.get_relevant_context.assert_called_once_with("Suggest a routine")
        
        # Verify the full exchange was saved to ChromaDB
        mock_store.add_conversation.assert_called_once_with("Suggest a routine", "Hello world!")
