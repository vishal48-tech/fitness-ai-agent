# src/memory/chroma_store.py
"""
ChromaDB Cloud memory store for AI Fitness Coach V2.
Uses chromadb.CloudClient — no local storage, no local embedding model.
Embeddings are handled server-side by Chroma Cloud (Qwen3).
"""
import chromadb
import contextlib
import uuid
from datetime import datetime
from typing import List, Dict

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _get_client() -> chromadb.CloudClient:
    """Return a Chroma Cloud client using env vars set by chromadb CLI or .env."""
    return chromadb.CloudClient()


class FitnessMemoryStore:
    """Per-user semantic memory backed by ChromaDB Cloud."""

    def __init__(self, user_id: str = "default"):
        self.user_id = user_id
        self.client = _get_client()
        self._init_collections()

    # ------------------------------------------------------------------
    # Collection management
    # ------------------------------------------------------------------

    def _init_collections(self):
        """Create (or open) per-user collections on Chroma Cloud."""
        uid = self.user_id
        self.conversations = self.client.get_or_create_collection(f"conversations_{uid}")
        self.preferences   = self.client.get_or_create_collection(f"preferences_{uid}")
        self.workouts      = self.client.get_or_create_collection(f"workouts_{uid}")

    # ------------------------------------------------------------------
    # Write helpers
    # ------------------------------------------------------------------

    def add_conversation(self, user_message: str, ai_response: str):
        """Store a conversation exchange."""
        self.conversations.add(
            ids=[f"conv_{uuid.uuid4()}"],
            documents=[f"User: {user_message}\nAssistant: {ai_response}"],
            metadatas=[{
                "user_id": self.user_id,
                "timestamp": datetime.now().isoformat(),
                "type": "conversation",
            }],
        )

    def add_preference(self, preference_type: str, content: str, importance: str = "medium"):
        """Store a user preference or goal."""
        self.preferences.add(
            ids=[f"pref_{uuid.uuid4()}"],
            documents=[content],
            metadatas=[{
                "user_id": self.user_id,
                "preference_type": preference_type,
                "importance": importance,
                "timestamp": datetime.now().isoformat(),
            }],
        )

    def add_workout(self, workout_data: Dict):
        """Log a completed workout."""
        parts = [
            f"Workout: {workout_data.get('type', 'General')}",
            f"Duration: {workout_data.get('duration', 'N/A')} minutes",
            f"Difficulty: {workout_data.get('difficulty', 'moderate')}",
        ]
        if notes := workout_data.get("notes"):
            parts.append(f"Notes: {notes}")

        self.workouts.add(
            ids=[f"workout_{uuid.uuid4()}"],
            documents=["\n".join(parts)],
            metadatas=[{
                "user_id": self.user_id,
                "workout_type": str(workout_data.get("type", "general")),
                "duration": int(workout_data.get("duration", 0)),
                "timestamp": datetime.now().isoformat(),
            }],
        )

    # ------------------------------------------------------------------
    # Read / query helpers
    # ------------------------------------------------------------------

    def _safe_query(self, collection, query: str, n: int = 5) -> List[str]:
        """Query a collection; return list of document strings (empty on error)."""
        try:
            count = collection.count()
            if count == 0:
                return []
            results = collection.query(query_texts=[query], n_results=min(n, count))
            return results["documents"][0] or []
        except Exception as exc:
            logger.debug(f"Query failed on {collection.name}: {exc}")
            return []

    def get_relevant_context(self, query: str) -> str:
        """Retrieve relevant context from all memory stores for the given query."""
        parts: List[str] = []

        if conv_docs := self._safe_query(self.conversations, query, 5):
            parts.append("📝 Related Conversations:")
            parts.extend(f"  • {doc[:200]}" for doc in conv_docs)

        if pref_docs := self._safe_query(self.preferences, query, 3):
            parts.append("🎯 Your Preferences & Goals:")
            parts.extend(f"  • {doc}" for doc in pref_docs)

        if workout_docs := self._safe_query(self.workouts, query, 3):
            parts.append("💪 Recent Workouts:")
            parts.extend(f"  • {doc[:150]}" for doc in workout_docs)

        return "\n".join(parts)

    def get_user_profile_summary(self) -> str:
        """Return a readable profile string from stored preferences and workouts."""
        parts: List[str] = []

        with contextlib.suppress(Exception):
            prefs = self.preferences.get()
            if prefs["documents"]:
                parts.append("## User Profile")
                for doc, meta in zip(prefs["documents"], prefs["metadatas"]):
                    ptype = meta.get("preference_type", "general")
                    parts.append(f"- [{ptype}] {doc}")

        with contextlib.suppress(Exception):
            workouts = self.workouts.get()
            if workouts["ids"]:
                parts.append(f"\n## Workout Stats")
                parts.append(f"- Total workouts logged: {len(workouts['ids'])}")

        return "\n".join(parts) if parts else "New user - no profile yet"

    def get_recent_conversations(self, n: int = 5) -> List[Dict]:
        """Get recent conversations for display."""
        with contextlib.suppress(Exception):
            results = self.conversations.get()
            if results["ids"]:
                convs = sorted(
                    zip(results["ids"], results["documents"], results["metadatas"]),
                    key=lambda x: x[2].get("timestamp", ""),
                    reverse=True,
                )
                return [{"id": c[0], "content": c[1], "metadata": c[2]} for c in list(convs)[:n]]
        return []