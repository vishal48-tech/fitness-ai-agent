# config/settings.py
"""
Central configuration for AI Fitness Coach V2
Edit this file to change models, paths, and settings.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).parent.parent

# Groq settings
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.3-70b-versatile"  # default model

# Available Groq models
GROQ_MODELS = {
    "GPT OSS 120B": "openai/gpt-oss-120b",
    "Llama 3 70B": "llama-3.3-70b-versatile",
    "Qwen 3 32B": "qwen/qwen3-32b",
    "Groq compound mini": "groq/compound-mini",
    "Llama 3 8B": "llama-3.1-8b-instant"
}


# Supabase settings
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_PUBLISHABLE_KEY = os.getenv("SUPABASE_PUBLISHABLE_KEY", "")
SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY", "")

# Supabase Auth settings
SUPABASE_AUTH_REDIRECT_URL = os.getenv(
    "SUPABASE_AUTH_REDIRECT_URL",
    "http://localhost:8501"
)

# Session cookie / state key used in Streamlit session_state
SUPABASE_SESSION_KEY = "supabase_session"
SUPABASE_USER_KEY = "supabase_user"

# ChromaDB Cloud settings
CHROMA_API_KEY = os.getenv("CHROMA_API_KEY", "")
CHROMA_TENANT = os.getenv("CHROMA_TENANT", "")
CHROMA_DATABASE = os.getenv("CHROMA_DATABASE", "")

# Agent settings
MAX_CONVERSATION_TURNS = 10
SIMILARITY_THRESHOLD = 0.7
MAX_TOKENS = 4096
TEMPERATURE = 0.1

# Streamlit settings
PAGE_TITLE = "AI Fitness Coach"
PAGE_ICON = "🏋️"
APP_VERSION = "2.0.0"