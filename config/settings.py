# config/settings.py
"""
Central configuration for your fitness agent
Edit this file to change models, paths, and settings
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).parent.parent

# Groq settings
GROQ_API_KEY = os.getenv("GROQ_API_KEY")  # Get from https://console.groq.com
GROQ_MODEL = "openai/gpt-oss-120b"  # default model

# Available Groq models
GROQ_MODELS = {
    "GPT OSS 120B": "openai/gpt-oss-120b",
    "Llama 3 70B": "llama-3.3-70b-versatile",
    "Qwen 3 32B": "qwen/qwen3-32b",
    "Groq compound mini": "groq/compound-mini",
    "Llama 3 8B": "llama-3.1-8b-instant"
}

# ChromaDB settings
CHROMA_PERSIST_DIR = str(BASE_DIR / "chroma_data")

# Embedding model (runs locally)
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Agent settings
MAX_CONVERSATION_TURNS = 10
SIMILARITY_THRESHOLD = 0.7
MAX_TOKENS = 4096
TEMPERATURE = 0.1

# Streamlit settings
PAGE_TITLE = "AI Fitness Coach"
PAGE_ICON = "🏋️"